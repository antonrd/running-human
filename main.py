from dataclasses import dataclass
from enum import Enum
import pygame
import random

pygame.init()

screen_w = 1280
screen_h = 720
screen_border = 50
border_w = 5

arena_upper_y = screen_border + border_w
arena_lower_y = screen_h - screen_border - border_w
arena_left_x = screen_border + border_w
arena_right_x = screen_w - screen_border - border_w
border_color = (255, 255, 255)

# playing_area_w = screen_w - 2 * screen_border
# playing_area_h = screen_h - 2 * screen_border
screen = pygame.display.set_mode((screen_w, screen_h))

clock = pygame.time.Clock()

# Position on screen where the human is.
human_w = 100
human_h = 100
human_x = 300 + screen_border
human_y = arena_lower_y - human_h

# Jump settings
jump_h = 300
jump_step = 15

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
            return curr_objects[last_red].x + curr_objects[last_red].w <= arena_right_x - min_obstacle_dist
    else:
        return curr_objects[-1].x + curr_objects[-1].w <= arena_right_x - min_crystal_dist


def draw_crystal(center_x: int, center_y: int, width: int, height: int):
    rhombus_color = 'purple'
    vertices = [
        (center_x, center_y - height // 2),  # Top vertex
        (center_x + width // 2, center_y),   # Right vertex
        (center_x, center_y + height // 2),  # Bottom vertex
        (center_x - width // 2, center_y)    # Left vertex
    ]
    pygame.draw.polygon(screen, rhombus_color, vertices)



obstacle_ratio = 4
crystal_ratio = 1
total_obj_ratio = obstacle_ratio + crystal_ratio
obstacle_prob = obstacle_ratio / float(total_obj_ratio)

# Parameters for how to create flying object.
min_obstacle_dist = 500
max_obstacle_dist = 2000

min_crystal_dist = 100
max_crystal_dist = 1000

# Flying object sizes
obstacle_r = 20
obstacle_y = arena_lower_y - 20
obstacle_step = 10

crystal_w = 40
crystal_h = 60
crystal_step = 10
crystal_high_y = arena_lower_y - jump_h

objects = []

class JumpDir(Enum):
    UP = 1
    DOWN = 2
    NONE = 3

in_jump = False
jump_dir = JumpDir.NONE

# game_over = False
# Indicates whether the player hit an obstacle.
is_hit = False
# Number of lives to start with.
human_lives = 3
# Number of collected crystals.
human_crystals = 0

class GameMode(Enum):
    MENU = 1
    PLAY = 2
    PAUSE = 3

class MenuItem(Enum):
    NEW_GAME = 1
    EXIT = 2
    RESUME_GAME = 3

menu_items = [MenuItem.NEW_GAME, MenuItem.EXIT]
MENU_TEXTS = {
    MenuItem.NEW_GAME: 'New Game',
    MenuItem.EXIT: 'Exit Game',
    MenuItem.RESUME_GAME: 'Resume Game',
}
curr_menu_item_idx = 0

game_mode = GameMode.MENU

game_running = True
is_game_over = False

while game_running:
    is_hit = False
    # Process player inputs.
    background_color = 'black'

    if game_mode in [GameMode.MENU, GameMode.PAUSE]:
        if game_mode == GameMode.MENU:
            menu_items = [MenuItem.NEW_GAME, MenuItem.EXIT]
        else:
            menu_items = [MenuItem.RESUME_GAME, MenuItem.NEW_GAME, MenuItem.EXIT]

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                raise SystemExit
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_UP:
                    curr_menu_item_idx = (curr_menu_item_idx + len(menu_items) - 1) % len(menu_items)
                elif event.key == pygame.K_DOWN:
                    curr_menu_item_idx = (curr_menu_item_idx + len(menu_items) + 1) % len(menu_items)
                elif event.key == pygame.K_RETURN:
                    if menu_items[curr_menu_item_idx] == MenuItem.NEW_GAME:
                        game_mode = GameMode.PLAY
                        objects = []
                        in_jump = False
                        jump_dir = JumpDir.NONE
                        is_hit = False
                        human_lives = 3
                        human_crystals = 0
                        is_game_over = False
                        break
                    elif menu_items[curr_menu_item_idx] == MenuItem.RESUME_GAME:
                        game_mode = GameMode.PLAY
                        break
                    elif menu_items[curr_menu_item_idx] == MenuItem.EXIT:
                        game_running = False
                        break

        if not game_running:
            break

    elif game_mode == GameMode.PLAY:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                raise SystemExit
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_UP:
                    if not in_jump:
                        in_jump = True
                        jump_dir = JumpDir.UP
                        human_y -= jump_step
                if event.key == pygame.K_p:
                    game_mode = GameMode.PAUSE
                    curr_menu_item_idx = 0
        if in_jump:
            if jump_dir == JumpDir.UP:
                # If the jump is at its highest point, start going down.
                if human_y <= arena_lower_y - human_h - jump_h:
                    jump_dir = JumpDir.DOWN
                    human_y += jump_step
                else:
                    human_y -= jump_step
            else:
                if human_y == arena_lower_y - human_h:
                    in_jump = False
                    jump_dir = JumpDir.NONE
                else:
                    human_y += jump_step

        new_obj_type = ObjectType.RED_BALL if random.random() <= obstacle_prob else ObjectType.CRYSTAL
        if not objects or can_add_new_object(objects, new_obj_type):
            if new_obj_type == ObjectType.RED_BALL:
                objects.append(FlyingObject(obj_type = ObjectType.RED_BALL,
                                            x = arena_right_x + random.random() * (max_obstacle_dist - min_obstacle_dist),
                                            y = obstacle_y,
                                            w = 2 * obstacle_r,
                                            h = 2 * obstacle_r))
            else:
                objects.append(FlyingObject(obj_type = ObjectType.CRYSTAL,
                                            x = arena_right_x + random.random() * (max_crystal_dist - min_crystal_dist),
                                            y = arena_lower_y - crystal_h // 2 - random.random() * (arena_lower_y - crystal_high_y),
                                            w = crystal_w,
                                            h = crystal_h))

        while objects and objects[0].right_side() < 0:
            objects.pop(0)

        for obj in objects:
            if (not (obj.left_side() > human_x + human_w or obj.right_side() < human_x) and
                not (obj.upper_side() > human_y + human_h or obj.lower_side() < human_y)):
                if not obj.has_hit:
                    if obj.obj_type == ObjectType.RED_BALL:
                        human_lives -= 1
                    else:
                        human_crystals += 1

                if obj.obj_type == ObjectType.RED_BALL:
                    is_hit = True

                obj.has_hit = True

            if obj.obj_type == ObjectType.RED_BALL:
                obj.x -= obstacle_step
            else:
                obj.x -= crystal_step

    if human_lives == 0:
        game_mode = GameMode.MENU
        is_game_over = True

    # Draw the screen
    if game_mode in [GameMode.MENU, GameMode.PAUSE]:
        if game_mode == GameMode.MENU:
            menu_items = [MenuItem.NEW_GAME, MenuItem.EXIT]
        else:
            menu_items = [MenuItem.RESUME_GAME, MenuItem.NEW_GAME, MenuItem.EXIT]

        menu_item_w, menu_item_h = 200, 50

        # Calculate position to center the rectangle
        menu_item_x = (screen_w - menu_item_w) // 2
        menu_top_y = 300
        menu_color = 'white'

        if is_game_over:
            font = pygame.font.Font(None, 64)  # None uses the default font.
            rect = pygame.Rect(0, 0, screen_w, 400)
            game_over_text = font.render('GAME OVER', True, (255, 255, 255))  # Text, antialias, color
            game_over_rect = game_over_text.get_rect(center=rect.center)
            screen.blit(game_over_text, game_over_rect)
            is_game_over = False

        font = pygame.font.Font(None, 36)

        # rect_y = (screen_h - menu_item_h) // 2
        for idx, menu_item in enumerate(menu_items):
            if idx == curr_menu_item_idx:
                menu_color = 'yellow'
            else:
                menu_color = 'white'

            rect = pygame.Rect(menu_item_x, menu_top_y + idx * (menu_item_h + 20), menu_item_w, menu_item_h)
            # Draw the rectangle
            pygame.draw.rect(screen, menu_color, rect, 5)
            # pygame.draw.rect(screen, menu_color, pygame.Rect(screen_border, screen_border, screen_w - 2 * screen_border, screen_h - 2 * screen_border), border_w)
            # Render the text
            text = font.render(MENU_TEXTS[menu_items[idx]], True, menu_color)
            # Get the rectangle of the text and center it inside the rectangle
            text_rect = text.get_rect(center=rect.center)
            # Draw the text
            screen.blit(text, text_rect)
    elif game_mode == GameMode.PLAY:
        screen.fill(background_color)  # Fill the display with a solid color

        # Write number of lives
        font = pygame.font.Font(None, 36)  # None uses the default font.
        text = font.render(f'Lives: {human_lives}, Crystals: {human_crystals}', True, (255, 255, 255))  # Text, antialias, color
        screen.blit(text, (10, 10))  # Position at x=10, y=10

        pygame.draw.rect(screen, border_color, pygame.Rect(screen_border, screen_border, screen_w - 2 * screen_border, screen_h - 2 * screen_border), border_w)
        color = 'yellow' if not is_hit else 'red'
        square_rect = pygame.Rect(human_x, human_y, human_w, human_h)  # x, y, width, height
        pygame.draw.rect(screen, color, square_rect)
        circle_color = 'red'
        for obj in objects:
            if obj.left_side() >= arena_left_x and obj.right_side() <= arena_right_x:
                if obj.obj_type == ObjectType.RED_BALL:
                    pygame.draw.circle(screen, circle_color, (obj.x, obj.y), obj.w // 2)
                elif not obj.has_hit:
                    draw_crystal(obj.x, obj.y, obj.w, obj.h)

    pygame.display.flip()  # Refresh on-screen display
    clock.tick(60)         # wait until next frame (at 60 FPS)

pygame.quit()
