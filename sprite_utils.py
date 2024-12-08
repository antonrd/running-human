import pygame

def load_walk_right_sprite(output_w: int = None, output_h: int = None) -> list:
    try:
        sprite_sheet = pygame.image.load("./assets/sprites/private/human-walk-right.png")
    except FileNotFoundError as e:
        print(f'Could not load human walking sprite: {e}')
        return []

    # sprite_sheet_width, sprite_sheet_height = sprite_sheet.get_size()

    # print(sprite_sheet_width, sprite_sheet_height)

    frame_width = 18
    frame_height = 16
    num_frames = 4

    frames = []
    for i in range(num_frames):
        frame_rect = pygame.Rect(i * frame_width, 0, frame_width, frame_height)
        frame_surface = sprite_sheet.subsurface(frame_rect)  # Extract frame
        if output_w and output_h:
            frame_surface = pygame.transform.scale(frame_surface, (output_w, output_h))
        frames.append(frame_surface)

    return frames

def load_fire_frame(output_w: int = None, output_h: int = None) -> pygame.Surface:
    try:
        fire_frame = pygame.image.load('./assets/fire_pixel_art_40x40.png')
    except FileNotFoundError as e:
        print(f'Could not load fire 40x40 image: {e}')
        return None

    if output_w and output_h:
        fire_frame = pygame.transform.scale(fire_frame, (output_w, output_h))

    return fire_frame
