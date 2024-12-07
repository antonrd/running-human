import pygame

import game_data
import object_utils
import player_interactions
import screen_drawing


pygame.init()

state = game_data.GameState()
screen = pygame.display.set_mode((state.game_settings.screen_w, state.game_settings.screen_h))
clock = pygame.time.Clock()


while state.game_running:
    if state.human_lives > 0:
        if state.hit_pause_left > 0:
            state.hit_pause_left -= 1
            clock.tick(30)
            continue
        else:
            state.is_hit = False

    if state.game_mode in [game_data.GameMode.MENU, game_data.GameMode.PAUSE]:
        # Check for pressed buttons.
        player_interactions.handle_menu_interactions(state)
        if not state.game_running:
            break
    elif state.game_mode == game_data.GameMode.PLAY:
        # Check for pressed buttons.
        player_interactions.handle_play_interactions(state)
        # Add new objects to the game at random, clean up objects that are not visible.
        object_utils.add_game_objects(state)
        # Move the existing objects, check for collisions.
        object_utils.move_game_objects(state)

    # Draw the screen
    if state.game_mode in [game_data.GameMode.MENU, game_data.GameMode.PAUSE]:
        screen_drawing.draw_menu_screen(screen, state)
    elif state.game_mode == game_data.GameMode.PLAY:
        screen_drawing.draw_game_objects(screen, state)

    if state.human_lives == 0:
        state.game_mode = game_data.GameMode.MENU
        state.is_game_over = True

    pygame.display.flip()  # Refresh on-screen display
    clock.tick(30)

pygame.quit()
