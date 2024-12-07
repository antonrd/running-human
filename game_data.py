from dataclasses import dataclass, field
from enum import Enum

import sprite_utils

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
    game_settings: GameSettings = field(default_factory=lambda: GameSettings())
    # Position on screen where the human is.
    human_w: int = 100
    human_h: int = 100
    human_x_in_arena: int = 300

    human_x: int = field(init=False)
    human_y: int = field(init=False)

    human_curr_sprite_idx: int = 0
    human_sprites: list = field(init=False)

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
