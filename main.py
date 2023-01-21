from kivy.config import Config
Config.set('graphics', 'width', '355')
Config.set('graphics', 'height', '655')

from kivy.lang import Builder
from kivy.app import App
from kivy import platform
from kivy.core.window import Window
from kivy.core.audio import SoundLoader
from kivy.properties import NumericProperty, ObjectProperty, StringProperty
from kivy.uix.relativelayout import RelativeLayout
from kivy.graphics.context_instructions import Color
from kivy.graphics.vertex_instructions import Line, Quad, Triangle
from kivy.properties import Clock

Builder.load_file("menu.kv")

class MainWidget(RelativeLayout):
    from transforms import transform, transform_2D, transform_perspective
    from user_actions import keyboard_closed, on_keyboard_down, on_keyboard_up, on_touch_down, on_touch_up
    from tile_generation import get_line_x_from_index, get_line_y_from_index, get_tile_coordinates, update_tiles, generate_tiles_coordinates, pre_fill_tile_coordinates

    menu_widget = ObjectProperty()
    perspective_point_x = NumericProperty(0)
    perspective_point_y = NumericProperty(0)

    V_NB_LINES = 16 # 16 for desktop | 8 for mobile
    V_LINES_SPACING = 0.5 # 0.2 for desktop | 0.5 for mobile
    vertical_lines = []

    H_NB_LINES = 12
    H_LINES_SPACING = 0.12
    horizontal_lines = []

    SPEED = 0.5 # 0.6 for desktop | 0.5 for mobile
    current_offset_y = 0
    current_y_loop = 0

    SPEED_X = 3.5 # 1.8 for desktop | 3.5 for mobile
    current_speed_x = 0
    current_offset_x = 0

    tiles = []
    NB_TILES = 20
    tiles_coordinates = []

    bg_image = "bg_vertical.jpg"
    score = NumericProperty(0)
    final_score = 0
    previous_score = 0
    score_txt = StringProperty()
    final_score_txt = StringProperty()

    sound_begin = None
    galaxy = None
    gameover_impact = None
    music1 = None

    SHIP_WIDTH = 0.2 # 0.1 for desktop | 0.2 for mobile
    SHIP_HEIGHT = 0.035
    SHIP_BASE_Y = 0.04
    ship = None
    ship_nose = None
    ship_coordinates = [(0,0), (0,0), (0,0)]

    state_game_over = False
    state_game_has_started = False

    menu_title = StringProperty("COSMIC DIVE")
    menu_button1_title = StringProperty("EASY")
    menu_button2_title = StringProperty("MEDIUM")
    menu_button3_title = StringProperty("HARD")
    button_width = 0.5
    menu_title_over = StringProperty("GAME OVER")
    menu_button_title_over = StringProperty("RESTART")

    def __init__(self, **kwargs):
        super(MainWidget, self).__init__(**kwargs)
        self.init_audio()
        self.init_vertical_lines()
        self.init_horizontal_lines()
        self.init_tiles()
        self.init_ship()
        self.init_ship_nose()
        self.reset_game()

        if self.is_desktop:            
            self._keyboard = Window.request_keyboard(self.keyboard_closed, self)
            self._keyboard.bind(on_key_down=self.on_keyboard_down)
            self._keyboard.bind(on_key_up=self.on_keyboard_up)

            self.bg_image = "bg_horizontal.jpg"
            self.V_LINES_SPACING = 0.2
            self.SPEED_X = 1.7
            self.SHIP_WIDTH = 0.1
            self.menu_title = "C   O   S   M   I   C       D    I   V   E"
            self.menu_button_title = "PLAY"
            self.menu_title_over = "G  A  M  E    O  V  E  R"
            self.menu_button_title_over = "RESTART"
            self.button_width = 0.15

        Clock.schedule_interval(self.update, 1/60)
        self.galaxy.play()

    def reset_game(self):
        self.current_offset_y = 0
        self.current_y_loop = 0
        self.current_speed_x = 0
        self.current_offset_x = 0
        self.tiles_coordinates = []
        self.pre_fill_tile_coordinates()
        self.generate_tiles_coordinates()
        self.state_game_over = False
        self.previous_score = self.final_score
        self.score = 0
        self.score_txt = "SCORE: 0"

    def is_desktop(self):
        if platform in ('linux', 'win', 'macosx'):
            return True
        return False

    def init_audio(self):
        self.sound_begin = SoundLoader.load("begin.wav")
        self.galaxy = SoundLoader.load("galaxy.wav")
        self.gameover_impact = SoundLoader.load("gameover_impact.wav")
        self.music1 = SoundLoader.load("music1.wav")

        self.sound_begin.volume = .5
        self.galaxy.volume = .5
        self.gameover_impact.volume = .6
        self.music1.volume = 1

    def check_ship_collision(self):
        for i in range(0, len(self.tiles_coordinates)):
            ti_x, ti_y = self.tiles_coordinates[i]
            if ti_y > self.current_y_loop + 1:
                return False
            if self.check_ship_collision_with_tile(ti_x, ti_y):
                return True
        return False

    def check_ship_collision_with_tile(self, ti_x, ti_y):
        xmin, ymin = self.get_tile_coordinates(ti_x, ti_y)
        xmax, ymax = self.get_tile_coordinates(ti_x + 1, ti_y + 1)

        px, py = self.ship_coordinates[1]
        if xmin <= px <= xmax and ymin <= py <= ymax:
            return True
        return False

    def init_ship(self):
        with self.canvas:
            Color(0,0,0)
            self.ship = Triangle()

    def init_ship_nose(self):
        with self.canvas:
            Color(0,0,0)
            self.ship_nose = Triangle()

    def update_ship_nose(self):
        center_x = self.width / 2
        base_y = self.SHIP_BASE_Y * self.height
        ship_quarter_width = self.SHIP_WIDTH * self.width / 4
        ship_height = self.SHIP_HEIGHT * self.height

        x1, y1 = self.transform(center_x - ship_quarter_width, (base_y + ship_height) / 2.1)
        x2, y2 = self.transform(center_x, base_y + ship_height + (ship_height/1.1))
        x3, y3 = self.transform(center_x + ship_quarter_width, (base_y + ship_height) / 2.1)

        self.ship_nose.points = [x1,y1,x2,y2,x3,y3]

    def update_ship(self):
        center_x = self.width / 2
        base_y = self.SHIP_BASE_Y * self.height
        ship_half_width = self.SHIP_WIDTH * self.width / 2
        ship_height = self.SHIP_HEIGHT * self.height

        self.ship_coordinates[0] = (center_x - ship_half_width, base_y)
        self.ship_coordinates[1] = (center_x, base_y + ship_height)
        self.ship_coordinates[2] = (center_x + ship_half_width, base_y)

        x1, y1 = self.transform(*self.ship_coordinates[0])
        x2, y2 = self.transform(*self.ship_coordinates[1])
        x3, y3 = self.transform(*self.ship_coordinates[2])
        self.ship.points = [x1,y1,x2,y2,x3,y3]
    
    def init_vertical_lines(self):
        with self.canvas:
            Color(1,1,1,0.3)
            for i in range(0, self.V_NB_LINES):
                self.vertical_lines.append(Line())
                
    def update_vertical_lines(self):
        start_index = -int(self.V_NB_LINES/2)+1
        for i in range(start_index, start_index + self.V_NB_LINES):
            line_x = self.get_line_x_from_index(i)
            x1, y1 = self.transform(line_x, 0)
            x2, y2 = self.transform(line_x, self.height)
            self.vertical_lines[i].points = [int(x1), int(y1), int(x2), int(y2)]
        
    def init_horizontal_lines(self):
        with self.canvas:
            Color(1,1,1,0.3)
            for i in range(0, self.H_NB_LINES):
                self.horizontal_lines.append(Line())

    def update_horizontal_lines(self):
        start_index = -int(self.V_NB_LINES/2)+1
        end_index = start_index + self.V_NB_LINES-1

        xmin = self.get_line_x_from_index(start_index)
        xmax = self.get_line_x_from_index(end_index)
        for i in range(0, self.H_NB_LINES):
            line_y = self.get_line_y_from_index(i)
            x1, y1 = self.transform(xmin, line_y)
            x2, y2 = self.transform(xmax, line_y)
            self.horizontal_lines[i].points = [x1, y1, x2, y2]

    def init_tiles(self):
        with self.canvas:
            Color(1,1,1)
            for i in range(0, self.NB_TILES):
                self.tiles.append(Quad())

    def on_menu_button1_pressed(self):
        self.sound_begin.play()
        self.music1.play()
        self.reset_game()
        self.state_game_has_started = True
        self.menu_widget.opacity = 0
        self.current_speed_x = 0
        self.SPEED = 0.6
        self.sound_begin.play()

    def on_menu_button2_pressed(self):
        self.sound_begin.play()
        self.music1.play()
        self.reset_game()
        self.state_game_has_started = True
        self.menu_widget.opacity = 0
        self.current_speed_x = 0
        self.SPEED = 0.75

    def on_menu_button3_pressed(self):
        self.sound_begin.play()
        self.music1.play()
        self.reset_game()
        self.state_game_has_started = True
        self.menu_widget.opacity = 0
        self.current_speed_x = 0
        self.SPEED = 0.925
        self.sound_begin.play()
        
    def update(self, dt):
        time_factor = dt * 60
        self.update_vertical_lines()
        self.update_horizontal_lines()
        self.update_tiles()
        self.update_ship_nose()
        self.update_ship()

        if not self.state_game_over and self.state_game_has_started:
            speed_y = self.SPEED * self.height / 100
            self.current_offset_y += speed_y * time_factor

            spacing_y = self.H_LINES_SPACING * self.height
            while self.current_offset_y >= spacing_y:
                self.current_offset_y -= spacing_y
                self.current_y_loop += 1
                if self.current_y_loop % 20 == 0:
                    self.SPEED += 0.02
                if self.current_y_loop % 3 == 0:
                    self.score += 1
                    self.score_txt = "SCORE: " + str(self.score)
                self.generate_tiles_coordinates()

            speed_x = self.current_speed_x * self.width / 100
            self.current_offset_x += speed_x * time_factor

        if not self.check_ship_collision() and not self.state_game_over:
            self.final_score = self.score
            if self.final_score >= self.previous_score:
                self.final_score_txt = "BEST: " + str(self.final_score)
            self.music1.stop()
            self.menu_widget.opacity = 1
            self.state_game_over = True
            self.menu_title = self.menu_title_over
            self.menu_button_title = self.menu_button_title_over
            self.gameover_impact.play()

class GalaxyApp(App):
    pass

GalaxyApp().run()
