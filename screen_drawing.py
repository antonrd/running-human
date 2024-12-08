import pygame

import game_data
import object_utils
import player_interactions


def draw_crystal(screen: pygame.Surface,
                 state: game_data.GameState,
                 center_x: int,
                 center_y: int,
                 width: int,
                 height: int):
    if state.crystal_frame:
        screen.blit(state.crystal_frame, (center_x - width // 2, center_y - height // 2))
    else:
        rhombus_color = state.crystal_colors[state.color_variant()]
        vertices = [
            (center_x, center_y - height // 2),  # Top vertex
            (center_x + width // 2, center_y),   # Right vertex
            (center_x, center_y + height // 2),  # Bottom vertex
            (center_x - width // 2, center_y)    # Left vertex
        ]
        pygame.draw.polygon(screen, rhombus_color, vertices)


def draw_obstacle(screen: pygame.Surface,
                  state: game_data.GameState,
                  obj: object_utils.FlyingObject):
    if state.fire_frame:
        screen.blit(state.fire_frame, (obj.x - obj.w // 2, obj.y - obj.h // 2))
    else:
        circle_color = state.obstacle_colors[state.color_variant()]
        pygame.draw.circle(screen, circle_color, (obj.x, obj.y), obj.w // 2)


def draw_game_objects(screen: pygame.Surface, state: game_data.GameState):

    background_color = state.background_colors[state.color_variant()]
    screen.fill(background_color)

    # Write number of lives
    font = pygame.font.Font(None, 36)  # None uses the default font.
    heart_rect = screen.blit(state.heart_frame, (60, 8))
    text_lives = font.render(f'{state.human_lives}', True, (255, 255, 255))
    lives_rect = screen.blit(text_lives, (heart_rect.right + 10, 10))

    crystal_rect = screen.blit(state.small_crystal_frame, (lives_rect.right + 20, 8))
    text_crystals = font.render(f'{state.human_crystals}', True, (255, 255, 255))
    screen.blit(text_crystals, (crystal_rect.right + 10, 10))

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
    for obj in state.objects:
        if (obj.left_side() >= state.game_settings.arena_left_x() and
            obj.right_side() <= state.game_settings.arena_right_x()):
            if obj.obj_type == object_utils.ObjectType.RED_BALL:
                draw_obstacle(screen, state, obj)
            elif not obj.has_hit:
                draw_crystal(screen, state, obj.x, obj.y, obj.w, obj.h)


def draw_menu_screen(screen: pygame.Surface, state: game_data.GameState):
    if state.game_mode == game_data.GameMode.MENU:
        state.menu_items = [game_data.MenuItem.NEW_GAME,
                            game_data.MenuItem.EXIT]
    else:
        state.menu_items = [game_data.MenuItem.RESUME_GAME,
                            game_data.MenuItem.NEW_GAME,
                            game_data.MenuItem.EXIT]

    menu_item_w, menu_item_h = 200, 50

    # Calculate position to center the rectangle
    menu_item_x = (state.game_settings.screen_w - menu_item_w) // 2
    menu_top_y = 300
    menu_color = 'white'

    if state.is_game_over:
        font = pygame.font.Font(None, 64)  # None uses the default font.
        rect = pygame.Rect(0, 0, state.game_settings.screen_w, 400)
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

        rect = pygame.Rect(menu_item_x,
                           menu_top_y + idx * (menu_item_h + 20),
                           menu_item_w,
                           menu_item_h)
        # Draw the rectangle for the menu item
        pygame.draw.rect(screen, menu_color, rect, 5)
        # Render the text
        text = font.render(player_interactions.MENU_TEXTS[menu_item], True, menu_color)
        # Get the rectangle of the text and center it inside the rectangle
        text_rect = text.get_rect(center=rect.center)
        # Draw the text
        screen.blit(text, text_rect)
