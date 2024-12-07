import pygame

import game_data
import object_utils

pygame.init()

state = game_data.GameState()
screen = pygame.display.set_mode((state.game_settings.screen_w, state.game_settings.screen_h))
clock = pygame.time.Clock()


MENU_TEXTS = {
    game_data.MenuItem.NEW_GAME: 'New Game',
    game_data.MenuItem.EXIT: 'Exit Game',
    game_data.MenuItem.RESUME_GAME: 'Resume Game',
}

def handle_menu_interactions(state: game_data.GameState):
    if state.game_mode == game_data.GameMode.MENU:
        state.menu_items = [game_data.MenuItem.NEW_GAME,
                            game_data.MenuItem.EXIT]
    else:
        state.menu_items = [game_data.MenuItem.RESUME_GAME,
                            game_data.MenuItem.NEW_GAME,
                            game_data.MenuItem.EXIT]

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
                if state.menu_items[state.curr_menu_item_idx] == game_data.MenuItem.NEW_GAME:
                    state.reset()
                    break
                elif state.menu_items[state.curr_menu_item_idx] == game_data.MenuItem.RESUME_GAME:
                    state.game_mode = game_data.GameMode.PLAY
                    break
                elif state.menu_items[state.curr_menu_item_idx] == game_data.MenuItem.EXIT:
                    state.game_running = False
                    break


def handle_play_interactions(state: game_data.GameState):
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            raise SystemExit
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_UP:
                if not state.in_jump:
                    state.in_jump = True
                    state.jump_dir = game_data.JumpDir.UP
                    state.human_y -= state.jump_step
            if event.key == pygame.K_p:
                state.game_mode = game_data.GameMode.PAUSE
                state.curr_menu_item_idx = 0
    if state.in_jump:
        if state.jump_dir == game_data.JumpDir.UP:
            # If the jump is at its highest point, start going down.
            if (state.human_y <=
                state.game_settings.arena_lower_y() - state.human_h - state.jump_h):
                state.jump_dir = game_data.JumpDir.DOWN
                state.human_y += state.jump_step
            else:
                state.human_y -= state.jump_step
        else:
            if state.human_y == state.game_settings.arena_lower_y() - state.human_h:
                state.in_jump = False
                state.jump_dir = game_data.JumpDir.NONE
            else:
                state.human_y += state.jump_step


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
        text = font.render(MENU_TEXTS[menu_item], True, menu_color)
        # Get the rectangle of the text and center it inside the rectangle
        text_rect = text.get_rect(center=rect.center)
        # Draw the text
        screen.blit(text, text_rect)


while state.game_running:
    if state.human_lives > 0:
        if state.hit_pause_left > 0:
            state.hit_pause_left -= 1
            clock.tick(60)
            continue
        else:
            state.is_hit = False

    if state.game_mode in [game_data.GameMode.MENU, game_data.GameMode.PAUSE]:
        # Check for pressed buttons.
        handle_menu_interactions(state)
        if not state.game_running:
            break
    elif state.game_mode == game_data.GameMode.PLAY:
        # Check for pressed buttons.
        handle_play_interactions(state)
        # Add new objects to the game at random, clean up objects that are not visible.
        object_utils.add_game_objects(state)
        # Move the existing objects, check for collisions.
        object_utils.move_game_objects(state)

    # Draw the screen
    if state.game_mode in [game_data.GameMode.MENU, game_data.GameMode.PAUSE]:
        draw_menu_screen(screen, state)
    elif state.game_mode == game_data.GameMode.PLAY:
        object_utils.draw_game_objects(screen, state)

    if state.human_lives == 0:
        state.game_mode = game_data.GameMode.MENU
        state.is_game_over = True

    pygame.display.flip()  # Refresh on-screen display
    clock.tick(30)

pygame.quit()
