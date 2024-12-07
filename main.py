from dataclasses import dataclass, field
from enum import Enum
import pygame
import random

import sprite_utils

pygame.init()

@dataclass
class GameSettings:
    screen_w: int = 1280
    screen_h: int = 720
    screen_border: int = 50
    border_w: int = 5
    border_color: tuple[int, int, int] = (255, 255, 255)

    def arena_upper_y(self):
        return self.screen_border + self.border_w

    def arena_lower_y(self):
        return self.screen_h - self.screen_border - self.border_w

    def arena_left_x(self):
        return self.screen_border + self.border_w

    def arena_right_x(self):
        return self.screen_w - self.screen_border - self.border_w

class JumpDir(Enum):
    UP = 1
    DOWN = 2
    NONE = 3

class GameMode(Enum):
    MENU = 1
    PLAY = 2
    PAUSE = 3

class MenuItem(Enum):
    NEW_GAME = 1
    EXIT = 2
    RESUME_GAME = 3

@dataclass
class GameState:
    game_settings: GameSettings
    # Position on screen where the human is.
    human_w: int = 100
    human_h: int = 100
    human_x_in_arena: int = 300

    human_x: int = field(init=False)
    human_y: int = field(init=False)

    human_curr_sprite_idx: int = 0
    human_sprites: list = field(init=False)

    # The human sprite will change each 3 frames.
    def get_current_human_sprite(self):
        if self.human_sprites:
            return self.human_sprites[self.human_curr_sprite_idx // 3]

    def move_next_human_sprite(self):
        if self.human_sprites:
            self.human_curr_sprite_idx = (self.human_curr_sprite_idx + 1) % (3 * len(self.human_sprites))

    # Jump settings
    jump_h: int = 300
    jump_step: int = 30

    obstacle_ratio: int = 4
    crystal_ratio: int = 1
    def total_obj_ratio(self):
        return self.obstacle_ratio + self.crystal_ratio

    def obstacle_prob(self):
        return self.obstacle_ratio / float(self.total_obj_ratio())

    # Parameters for how to create flying object.
    min_obstacle_dist: int = 500
    max_obstacle_dist: int = 2000

    min_crystal_dist: int = 100
    max_crystal_dist: int  = 1000

    # Flying object sizes
    obstacle_r: int = 20
    obstacle_y: int = field(init=False)
    obstacle_step: int = 15

    crystal_w: int = 40
    crystal_h: int = 60
    crystal_step: int = 15
    crystal_high_y: int = field(init=False)

    in_jump: bool = False
    jump_dir: JumpDir = JumpDir.NONE

    # Indicates whether the player hit an obstacle.
    is_hit: bool = False
    # Number of lives to start with.
    human_lives: int = 3
    # Number of collected crystals.
    human_crystals: int = 0
    # Indicates the time for which a hit was shown.
    # The game pauses for a while to show it.
    hit_pause_left: int = 0
    # How many iterations should a pause after a hit last.
    hit_pause_length: int = 20

    curr_menu_item_idx: int = 0

    game_mode: GameMode = GameMode.MENU

    game_running: bool = True
    is_game_over: bool = False

    # Specifies how the background should change when the human collects crystals
    background_colors: list[tuple[int, int, int]] = field(default_factory=lambda: [(0, 0, 0), (30, 30, 30)])
    obstacle_colors: list[tuple[int, int, int]] = field(default_factory=lambda: [(211, 51, 68), (26, 246, 66)])
    crystal_colors: list[tuple[int, int, int]] = field(default_factory=lambda: [(151, 57, 240), (246, 26, 96)])
    crystal_change_background: int = 50

    def color_variant(self):
        return (self.human_crystals // self.crystal_change_background) % 2

    # Holds the incoming objects
    objects: list = field(default_factory=list)
    # Holds the items in the menu to be displayed
    menu_items: list = field(default_factory=lambda: [MenuItem.NEW_GAME, MenuItem.EXIT])

    def __post_init__(self):
        self.human_x = self.human_x_in_arena + self.game_settings.screen_border
        self.human_y = self.game_settings.arena_lower_y() - self.human_h
        self.obstacle_y = self.game_settings.arena_lower_y() - self.obstacle_r
        self.crystal_high_y = self.game_settings.arena_lower_y() - self.jump_h

    def reset(self):
        self.game_mode = GameMode.PLAY
        self.objects = []
        self.menu_items = [MenuItem.NEW_GAME, MenuItem.EXIT]
        self.in_jump = False
        self.jump_dir = JumpDir.NONE
        self.is_hit = False
        self.human_lives = 3
        self.human_crystals = 0
        self.is_game_over = False
        self.human_y = self.game_settings.arena_lower_y() - self.human_h
        self.human_sprites = sprite_utils.load_walk_right_sprite(output_w=self.human_w, output_h=self.human_h)


settings = GameSettings()
state = GameState(game_settings=settings)

screen = pygame.display.set_mode((settings.screen_w, settings.screen_h))
clock = pygame.time.Clock()

class ObjectType(Enum):
    RED_BALL = 1
    CRYSTAL = 2

@dataclass
class FlyingObject:
    """Describes a flying object."""
    obj_type: ObjectType
    x: int
    y: int
    w: int
    h: int
    has_hit: bool = False

    def left_side(self):
        return self.x - self.w // 2

    def right_side(self):
        return self.x + self.w // 2

    def lower_side(self):
        return self.y + self.h // 2

    def upper_side(self):
        return self.y - self.h // 2

def can_add_new_object(curr_objects: list[FlyingObject], new_obj_type: ObjectType) -> bool:
    if not curr_objects: return True

    if new_obj_type == ObjectType.RED_BALL:
        last_red = -1
        for idx in range(len(curr_objects) - 1, -1, -1):
            if curr_objects[idx].obj_type == ObjectType.RED_BALL:
                last_red = idx
                break
        if last_red == -1:
            return True
        else:
            return (curr_objects[last_red].x + curr_objects[last_red].w <=
                    settings.arena_right_x() - state.min_obstacle_dist)
    else:
        return (curr_objects[-1].x + curr_objects[-1].w <=
                settings.arena_right_x() - state.min_crystal_dist)


def draw_crystal(center_x: int, center_y: int, width: int, height: int):
    rhombus_color = state.crystal_colors[state.color_variant()]
    vertices = [
        (center_x, center_y - height // 2),  # Top vertex
        (center_x + width // 2, center_y),   # Right vertex
        (center_x, center_y + height // 2),  # Bottom vertex
        (center_x - width // 2, center_y)    # Left vertex
    ]
    pygame.draw.polygon(screen, rhombus_color, vertices)


MENU_TEXTS = {
    MenuItem.NEW_GAME: 'New Game',
    MenuItem.EXIT: 'Exit Game',
    MenuItem.RESUME_GAME: 'Resume Game',
}

def handle_menu_interactions(state: GameState):
    if state.game_mode == GameMode.MENU:
        state.menu_items = [MenuItem.NEW_GAME, MenuItem.EXIT]
    else:
        state.menu_items = [MenuItem.RESUME_GAME, MenuItem.NEW_GAME, MenuItem.EXIT]

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            raise SystemExit
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_UP:
                state.curr_menu_item_idx = (state.curr_menu_item_idx + len(state.menu_items) - 1) % len(state.menu_items)
            elif event.key == pygame.K_DOWN:
                state.curr_menu_item_idx = (state.curr_menu_item_idx + len(state.menu_items) + 1) % len(state.menu_items)
            elif event.key == pygame.K_RETURN:
                if state.menu_items[state.curr_menu_item_idx] == MenuItem.NEW_GAME:
                    state.reset()
                    break
                elif state.menu_items[state.curr_menu_item_idx] == MenuItem.RESUME_GAME:
                    state.game_mode = GameMode.PLAY
                    break
                elif state.menu_items[state.curr_menu_item_idx] == MenuItem.EXIT:
                    state.game_running = False
                    break


def handle_play_interactions(state: GameState):
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            raise SystemExit
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_UP:
                if not state.in_jump:
                    state.in_jump = True
                    state.jump_dir = JumpDir.UP
                    state.human_y -= state.jump_step
            if event.key == pygame.K_p:
                state.game_mode = GameMode.PAUSE
                state.curr_menu_item_idx = 0
    if state.in_jump:
        if state.jump_dir == JumpDir.UP:
            # If the jump is at its highest point, start going down.
            if state.human_y <= settings.arena_lower_y() - state.human_h - state.jump_h:
                state.jump_dir = JumpDir.DOWN
                state.human_y += state.jump_step
            else:
                state.human_y -= state.jump_step
        else:
            if state.human_y == settings.arena_lower_y() - state.human_h:
                state.in_jump = False
                state.jump_dir = JumpDir.NONE
            else:
                state.human_y += state.jump_step


def add_game_objects(state: GameState):
    new_obj_type = ObjectType.RED_BALL if random.random() <= state.obstacle_prob() else ObjectType.CRYSTAL
    if not state.objects or can_add_new_object(state.objects, new_obj_type):
        if new_obj_type == ObjectType.RED_BALL:
            state.objects.append(FlyingObject(
                obj_type = ObjectType.RED_BALL,
                x = settings.arena_right_x() + int(random.random() * (state.max_obstacle_dist - state.min_obstacle_dist)),
                y = state.obstacle_y,
                w = 2 * state.obstacle_r,
                h = 2 * state.obstacle_r))
        else:
            state.objects.append(FlyingObject(
                obj_type = ObjectType.CRYSTAL,
                x = settings.arena_right_x() + int(random.random() * (state.max_crystal_dist - state.min_crystal_dist)),
                y = settings.arena_lower_y() - state.crystal_h // 2 - int(random.random() * (settings.arena_lower_y() - state.crystal_high_y)),
                w = state.crystal_w,
                h = state.crystal_h))

    while state.objects and state.objects[0].right_side() < 0:
        state.objects.pop(0)


def rect_circle_collision(rect_x, rect_y, rect_w, rect_h, circle_x, circle_y, circle_r):
    # Find the closest point on the rectangle to the circle center
    closest_x = max(rect_x, min(circle_x, rect_x + rect_w))
    closest_y = max(rect_y, min(circle_y, rect_y + rect_h))

    # Calculate the distance between the circle center and the closest point
    distance = (closest_x - circle_x) ** 2 + (closest_y - circle_y) ** 2

    # Check if the distance is less than or equal to the circle's radius
    # Add some slack in order to not count border touches
    return distance <= (circle_r - 5) ** 2


def object_collides_with_human(obj: FlyingObject, state: GameState) -> bool:
    if obj.obj_type == ObjectType.RED_BALL:
        return rect_circle_collision(state.human_x,
                                     state.human_y,
                                     state.human_w,
                                     state.human_h,
                                     obj.x,
                                     obj.y,
                                     obj.w // 2)
    elif obj.obj_type == ObjectType.CRYSTAL:
        return (not (obj.left_side() > state.human_x + state.human_w or obj.right_side() < state.human_x) and
            not (obj.upper_side() > state.human_y + state.human_h or obj.lower_side() < state.human_y))

    return False


def move_game_objects(state: GameState):
    # Indicate that the human sprite should move one index up and
    # potentially to change to a new image.
    state.move_next_human_sprite()

    for obj in state.objects:
        if obj.obj_type == ObjectType.RED_BALL:
            obj.x -= state.obstacle_step
        else:
            obj.x -= state.crystal_step

        if object_collides_with_human(obj, state):
            if not obj.has_hit:
                if obj.obj_type == ObjectType.RED_BALL:
                    state.human_lives -= 1
                else:
                    state.human_crystals += 1

                if obj.obj_type == ObjectType.RED_BALL:
                    state.is_hit = True
                    state.hit_pause_left = state.hit_pause_length

            obj.has_hit = True


def draw_menu_screen(screen: pygame.Surface, state: GameState):
    if state.game_mode == GameMode.MENU:
        state.menu_items = [MenuItem.NEW_GAME, MenuItem.EXIT]
    else:
        state.menu_items = [MenuItem.RESUME_GAME, MenuItem.NEW_GAME, MenuItem.EXIT]

    menu_item_w, menu_item_h = 200, 50

    # Calculate position to center the rectangle
    menu_item_x = (settings.screen_w - menu_item_w) // 2
    menu_top_y = 300
    menu_color = 'white'

    if state.is_game_over:
        font = pygame.font.Font(None, 64)  # None uses the default font.
        rect = pygame.Rect(0, 0, settings.screen_w, 400)
        game_over_text = font.render('GAME OVER', True, (255, 255, 255))  # Text, antialias, color
        game_over_rect = game_over_text.get_rect(center=rect.center)
        screen.blit(game_over_text, game_over_rect)
        state.is_game_over = False

    font = pygame.font.Font(None, 36)

    for idx, menu_item in enumerate(state.menu_items):
        if idx == state.curr_menu_item_idx:
            menu_color = 'yellow'
        else:
            menu_color = 'white'

        rect = pygame.Rect(menu_item_x, menu_top_y + idx * (menu_item_h + 20), menu_item_w, menu_item_h)
        # Draw the rectangle
        pygame.draw.rect(screen, menu_color, rect, 5)
        # Render the text
        text = font.render(MENU_TEXTS[state.menu_items[idx]], True, menu_color)
        # Get the rectangle of the text and center it inside the rectangle
        text_rect = text.get_rect(center=rect.center)
        # Draw the text
        screen.blit(text, text_rect)


def draw_game_objects(screen: pygame.Surface, state: GameState):

    background_color = state.background_colors[state.color_variant()]
    screen.fill(background_color)

    # Write number of lives
    font = pygame.font.Font(None, 36)  # None uses the default font.
    text = font.render(f'Lives: {state.human_lives}, Crystals: {state.human_crystals}', True, (255, 255, 255))  # Text, antialias, color
    screen.blit(text, (10, 10))  # Position at x=10, y=10

    # Draw the game field bounds
    pygame.draw.rect(screen,
                        settings.border_color if not state.is_hit else 'red',
                        pygame.Rect(
                            settings.screen_border,
                            settings.screen_border,
                            settings.screen_w - 2 * settings.screen_border,
                            settings.screen_h - 2 * settings.screen_border),
                        settings.border_w)

    curr_human_sprite = state.get_current_human_sprite()
    if curr_human_sprite:
        screen.blit(curr_human_sprite, (state.human_x, state.human_y))
    else:
        color = 'yellow' if not state.is_hit else 'red'
        square_rect = pygame.Rect(state.human_x, state.human_y, state.human_w, state.human_h)  # x, y, width, height
        pygame.draw.rect(screen, color, square_rect)
    circle_color = state.obstacle_colors[state.color_variant()]
    for obj in state.objects:
        if obj.left_side() >= settings.arena_left_x() and obj.right_side() <= settings.arena_right_x():
            if obj.obj_type == ObjectType.RED_BALL:
                pygame.draw.circle(screen, circle_color, (obj.x, obj.y), obj.w // 2)
            elif not obj.has_hit:
                draw_crystal(obj.x, obj.y, obj.w, obj.h)


while state.game_running:
    if state.human_lives > 0:
        if state.hit_pause_left > 0:
            state.hit_pause_left -= 1
            clock.tick(60)
            continue
        else:
            state.is_hit = False

    if state.game_mode in [GameMode.MENU, GameMode.PAUSE]:
        # Check for pressed buttons.
        handle_menu_interactions(state)
        if not state.game_running:
            break
    elif state.game_mode == GameMode.PLAY:
        # Check for pressed buttons.
        handle_play_interactions(state)
        # Add new objects to the game at random, clean up objects that are not visible.
        add_game_objects(state)
        # Move the existing objects, check for collisions.
        move_game_objects(state)

    # Draw the screen
    if state.game_mode in [GameMode.MENU, GameMode.PAUSE]:
        draw_menu_screen(screen, state)
    elif state.game_mode == GameMode.PLAY:
        draw_game_objects(screen, state)

    if state.human_lives == 0:
        state.game_mode = GameMode.MENU
        state.is_game_over = True

    pygame.display.flip()  # Refresh on-screen display
    clock.tick(30)

pygame.quit()
