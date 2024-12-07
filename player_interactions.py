import pygame

import game_data


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
