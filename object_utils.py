from dataclasses import dataclass
from enum import Enum
import pygame
import random

import game_data

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

def can_add_new_object(state: game_data.GameState, new_obj_type: ObjectType) -> bool:
    if not state.objects: return True

    if new_obj_type == ObjectType.RED_BALL:
        last_red = -1
        for idx in range(len(state.objects) - 1, -1, -1):
            if state.objects[idx].obj_type == ObjectType.RED_BALL:
                last_red = idx
                break
        if last_red == -1:
            return True
        else:
            return (state.objects[last_red].x + state.objects[last_red].w <=
                    state.game_settings.arena_right_x() - state.min_obstacle_dist)
    else:
        return (state.objects[-1].x + state.objects[-1].w <=
                state.game_settings.arena_right_x() - state.min_crystal_dist)


def draw_crystal(screen: pygame.Surface,
                 state: game_data.GameState,
                 center_x: int,
                 center_y: int,
                 width: int,
                 height: int):
    rhombus_color = state.crystal_colors[state.color_variant()]
    vertices = [
        (center_x, center_y - height // 2),  # Top vertex
        (center_x + width // 2, center_y),   # Right vertex
        (center_x, center_y + height // 2),  # Bottom vertex
        (center_x - width // 2, center_y)    # Left vertex
    ]
    pygame.draw.polygon(screen, rhombus_color, vertices)


def rect_circle_collision(rect_x, rect_y, rect_w, rect_h, circle_x, circle_y, circle_r):
    # Find the closest point on the rectangle to the circle center
    closest_x = max(rect_x, min(circle_x, rect_x + rect_w))
    closest_y = max(rect_y, min(circle_y, rect_y + rect_h))

    # Calculate the distance between the circle center and the closest point
    distance = (closest_x - circle_x) ** 2 + (closest_y - circle_y) ** 2

    # Check if the distance is less than or equal to the circle's radius
    # Add some slack in order to not count border touches
    return distance <= (circle_r - 5) ** 2


def object_collides_with_human(obj: FlyingObject, state: game_data.GameState) -> bool:
    if obj.obj_type == ObjectType.RED_BALL:
        return rect_circle_collision(state.human_x,
                                     state.human_y,
                                     state.human_w,
                                     state.human_h,
                                     obj.x,
                                     obj.y,
                                     obj.w // 2)
    elif obj.obj_type == ObjectType.CRYSTAL:
        return (not (obj.left_side() > state.human_x + state.human_w or
                     obj.right_side() < state.human_x) and
                not (obj.upper_side() > state.human_y + state.human_h or
                    obj.lower_side() < state.human_y))

    return False


def move_game_objects(state: game_data.GameState):
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


def add_game_objects(state: game_data.GameState):
    new_obj_type = (ObjectType.RED_BALL
                    if random.random() <= state.obstacle_prob()
                    else ObjectType.CRYSTAL)
    if not state.objects or can_add_new_object(state, new_obj_type):
        if new_obj_type == ObjectType.RED_BALL:
            state.objects.append(FlyingObject(
                obj_type = ObjectType.RED_BALL,
                x = (state.game_settings.arena_right_x() +
                     int(random.random() *
                         (state.max_obstacle_dist - state.min_obstacle_dist))
                ),
                y = state.obstacle_y,
                w = 2 * state.obstacle_r,
                h = 2 * state.obstacle_r))
        else:
            state.objects.append(FlyingObject(
                obj_type = ObjectType.CRYSTAL,
                x = (state.game_settings.arena_right_x() +
                     int(random.random() *
                         (state.max_crystal_dist - state.min_crystal_dist))
                ),
                y = (state.game_settings.arena_lower_y() -
                     state.crystal_h // 2 -
                     int(random.random() *
                         (state.game_settings.arena_lower_y() - state.crystal_high_y))
                ),
                w = state.crystal_w,
                h = state.crystal_h))

    while state.objects and state.objects[0].right_side() < 0:
        state.objects.pop(0)


def draw_game_objects(screen: pygame.Surface, state: game_data.GameState):

    background_color = state.background_colors[state.color_variant()]
    screen.fill(background_color)

    # Write number of lives
    font = pygame.font.Font(None, 36)  # None uses the default font.
    text = font.render(f'Lives: {state.human_lives}, Crystals: {state.human_crystals}', True, (255, 255, 255))  # Text, antialias, color
    screen.blit(text, (10, 10))  # Position at x=10, y=10

    # Draw the game field bounds
    pygame.draw.rect(screen,
                     state.game_settings.border_color if not state.is_hit else 'red',
                     pygame.Rect(
                         state.game_settings.screen_border,
                         state.game_settings.screen_border,
                         state.game_settings.screen_w - 2 * state.game_settings.screen_border,
                         state.game_settings.screen_h - 2 * state.game_settings.screen_border),
                     state.game_settings.border_w)

    curr_human_sprite = state.get_current_human_sprite()
    if curr_human_sprite:
        screen.blit(curr_human_sprite, (state.human_x, state.human_y))
    else:
        color = 'yellow' if not state.is_hit else 'red'
        square_rect = pygame.Rect(state.human_x, state.human_y, state.human_w, state.human_h)  # x, y, width, height
        pygame.draw.rect(screen, color, square_rect)
    circle_color = state.obstacle_colors[state.color_variant()]
    for obj in state.objects:
        if (obj.left_side() >= state.game_settings.arena_left_x() and
            obj.right_side() <= state.game_settings.arena_right_x()):
            if obj.obj_type == ObjectType.RED_BALL:
                pygame.draw.circle(screen, circle_color, (obj.x, obj.y), obj.w // 2)
            elif not obj.has_hit:
                draw_crystal(screen, state, obj.x, obj.y, obj.w, obj.h)
