from kivy_config_helper import config_kivy

scr_w, scr_h = config_kivy(window_width=800, window_height=600, simulate_device=False, simulate_dpi=192, simulate_density=1.0)

from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.popup import Popup
from kivy.uix.spinner import Spinner
from kivy.uix.slider import Slider
from kivy.uix.checkbox import CheckBox
from kivy.graphics import Line, Ellipse, Color, Rectangle, RoundedRectangle
from kivy.uix.image import Image
from kivy.animation import Animation
from kivy.core.audio import SoundLoader
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.uix.textinput import TextInput
from kivy.clock import Clock
from ai_avatar import AtaxxAI, AICharacter
import json

# This class that I created below is responsible for the front screen of the Ataxx game
class AtaxxStartScreen(BoxLayout):
    settings = {
        "board_level": "Level 1",
        "play_mode": "Player vs Player",
        "timer_mode": "Unlimited",
        "timer_minutes": 5,
    }
    levels = []

    def __init__(self, screen_manager, **kwargs):
        super().__init__(**kwargs)
        self.screen_manager = screen_manager
        self.orientation = "vertical"
        self.spacing = 20
        self.padding = [20, 40, 20, 40]
        self.load_levels()
        self.mark_start_cells()

        # In order to integrate the grid pattern as part of the game background, I had to refer to the following documentation.
        # I used this background pretty much in all of the screens and used this source for documentation each time:
        #  https://stackoverflow.com/questions/67005587/displaying-a-background-image-in-kivy
        with self.canvas.before:
            Color(0, 0, 0, 1)
            self.bg_base = Rectangle(size=self.size, pos=self.pos)
            Color(0.1, 0.5, 0.1, 1)
            self.bg_overlay = Rectangle(size=self.size, pos=self.pos, source="./image/grid_pattern.jpg")
        self.bind(size=self._update_bg, pos=self._update_bg)

        layout = FloatLayout()

        # In order to support the custom font that utilized several times throughout this application,
        # I referred to the following documentation located below:
        # https://www.geeksforgeeks.org/how-to-add-custom-fonts-in-kivy-python/
        self.title = Label(
            text="Ataxx",
            font_size="90sp",
            bold=True,
            font_name="./font/retro_drip.ttf",
            color=(0.8, 1, 0.8, 1),
            size_hint=(None, None),
            size=(400, 100),
            pos_hint={"center_x": 0.5, "top": 0.65},
        )
        layout.add_widget(self.title)

        self.animate_title()

        button_layout = GridLayout(
            cols=2,
            spacing=40,
            size_hint=(0.8, None),
            height=200,
            pos_hint={"center_x": 0.5, "y": 0.1},
        )

        button_layout.add_widget(self.create_button("Start Game", self.start_game))
        button_layout.add_widget(self.create_button("Configuration Settings", self.open_config_popup))
        button_layout.add_widget(self.create_button("Exit Game", self.exit_game))
        button_layout.add_widget(self.create_button("Make New Level", self.open_make_new_level_screen))

        layout.add_widget(button_layout)

        self.add_widget(layout)

    # I referred to the following documentation in order to understand how to load a text file 
    # as a JSON in Python for Kivy:
    # https://www.geeksforgeeks.org/convert-text-file-to-json-in-python/
    def load_levels(self):
        try:
            with open("levels.txt", "r") as file:
                self.levels = json.load(file)
                print("Levels loaded successfully:", self.levels)
        except FileNotFoundError:
            print("Error: levels.txt file not found.")
            self.levels = []
        except json.JSONDecodeError as e:
            print(f"Error decoding JSON: {e}")
            self.levels = []
    
    def mark_start_cells(self):
        for level in self.levels:
            board = level.get("board", [])
            team_a_start = []
            team_b_start = []
            for row_idx, row in enumerate(board):
                for col_idx, cell in enumerate(row):
                    if cell == 1:
                        team_a_start.append((row_idx, col_idx))
                    elif cell == 2:
                        team_b_start.append((row_idx, col_idx))
            level["team_a_start"] = team_a_start
            level["team_b_start"] = team_b_start

    def _update_bg(self, *args):
        self.bg_base.size = self.size
        self.bg_base.pos = self.pos
        self.bg_overlay.size = self.size
        self.bg_overlay.pos = self.pos

    # I referred to the following documentation in order to understand how to animate the
    # title on the front screen for kivy:
    # https://www.youtube.com/watch?v=i8OU93pHiS0
    def animate_title(self):
        anim = (
            Animation(color=(1, 1, 1, 1), duration=0.7) +
            Animation(color=(0.8, 1, 0.8, 1), duration=0.7)
        )
        anim.repeat = True
        anim.start(self.title)

    # I referred to the offical documentation on Kivy buttons in order to understand how 
    # to have their colors change dynamically throughout the course of the application
    # and present this to the user. The link to that is located below:
    # https://kivy.org/doc/stable-2.2.0/api-kivy.uix.button.html
    def create_button(self, text, on_press_callback=None):
        button_layout = BoxLayout(
            size_hint=(0.6, None),
            height=70,
            pos_hint={"center_x": 0.5},
        )
        with button_layout.canvas.before:
            button_layout.bg_color = Color(0.1, 0.6, 0.1, 1)
            button_layout.bg_rect = RoundedRectangle(size=button_layout.size, pos=button_layout.pos, radius=[20])
        button_layout.bind(size=lambda instance, value: setattr(button_layout.bg_rect, 'size', value))
        button_layout.bind(pos=lambda instance, value: setattr(button_layout.bg_rect, 'pos', value))
        btn = Button(
            text=text,
            font_size="20sp",
            bold=True,
            background_normal="",
            background_color=(0, 0, 0, 0),
            color=(1, 1, 1, 1),
            padding=[20, 10],
        )
        if on_press_callback:
            btn.bind(on_press=on_press_callback)
        self.animate_button_and_background(btn, button_layout.bg_color)
        button_layout.add_widget(btn)
        return button_layout

    def animate_button_and_background(self, button, bg_color):
        anim = (
            Animation(color=(1, 1, 1, 1), duration=0.7) +
            Animation(color=(0.8, 1, 0.8, 1), duration=0.7)
        )
        anim.repeat = True
        anim.start(button)
        anim_bg = (
            Animation(rgb=(0.0, 0.4, 0.0), duration=0.7) +
            Animation(rgb=(0.1, 0.7, 0.1), duration=0.7)
        )
        anim_bg.repeat = True
        anim_bg.start(bg_color)

    # I referred to the documentation below in order to be able to play background music for this application.
    # I used this documentation several times for the other areas where I needed to use sound 
    # https://kivy.org/doc/stable-2.2.0/api-kivy.core.audio.html
    def play_background_music(self):
        self.music = SoundLoader.load('./sound/start_screen_music.mp3')
        if self.music:
            print("Music loaded successfully:", self.music.source)
            self.music.loop = True
            self.music.volume = 0.10
            self.music.play()
            print("Music is playing.")
        else:
            print("Failed to load music.")

    # I referred to the offical documentation for the Kivy Popup in order to be able to integrate within my application.
    # Specifically, I used to understand how other components like a slider or button could be integrated within here
    # https://kivy.org/doc/stable/api-kivy.uix.popup.html
    def open_config_popup(self, instance):
        popup_layout = BoxLayout(orientation="vertical", spacing=10, padding=10)

        popup_layout.add_widget(Label(text="Select Game Board Level:", font_size="16sp"))
        board_spinner = Spinner(
            text=self.settings["board_level"],
            values=[level["name"] for level in self.levels],
            size_hint=(1, None),
            height=44,
        )
        popup_layout.add_widget(board_spinner)

        self.reload_board_spinner_values(board_spinner)

        def update_level_spinner(spinner, text):
            self.settings["board_level"] = text
            print(f"Board level changed to: {text}")

        board_spinner.bind(text=update_level_spinner)

        popup_layout.add_widget(Label(text="Select Play Mode:", font_size="16sp"))
        mode_spinner = Spinner(
            text=self.settings["play_mode"],
            values=["Player vs Player", "Player vs Computer"],
            size_hint=(1, None),
            height=44,
        )
        popup_layout.add_widget(mode_spinner)

        popup_layout.add_widget(Label(text="Timer Mode:", font_size="16sp"))
        timer_layout = BoxLayout(orientation="horizontal", spacing=10)
        unlimited_checkbox = CheckBox(group="timer", active=self.settings["timer_mode"] == "Unlimited")
        limited_checkbox = CheckBox(group="timer", active=self.settings["timer_mode"] == "Limited")
        timer_layout.add_widget(Label(text="Unlimited", font_size="14sp"))
        timer_layout.add_widget(unlimited_checkbox)
        timer_layout.add_widget(Label(text="Limited", font_size="14sp"))
        timer_layout.add_widget(limited_checkbox)
        popup_layout.add_widget(timer_layout)

        slider_layout = BoxLayout(orientation="vertical", spacing=10)
        slider_label = Label(
            text=f"Set Time (Minutes) for Each Player: {self.settings.get('timer_minutes', 1)}",
            font_size="14sp"
        )
        slider_layout.add_widget(slider_label)
        timer_slider = Slider(
            min=1,
            max=10,
            value=self.settings.get("timer_minutes", 1) or 1,
            size_hint=(1, None),
            height=44,
        )
        slider_layout.add_widget(timer_slider)
        popup_layout.add_widget(slider_layout)

        def update_slider_label(instance, value):
            slider_label.text = f"Set Time (Minutes) for Each Player: {int(value)}"

        timer_slider.bind(value=update_slider_label)

        # I referred to the following documentation in order to able to integrate a slider into the
        # save settings popup where the user can adjust the number of minutes for a given game
        # https://kivy.org/doc/stable-2.2.0/api-kivy.uix.slider.html
        def toggle_slider(*args):
            if limited_checkbox.active:
                slider_layout.opacity = 1
                timer_slider.disabled = False
                slider_label.text = f"Set Time (Minutes) for Each Player: {int(timer_slider.value)}"
            else:
                slider_layout.opacity = 0.5
                timer_slider.disabled = True
                slider_label.text = "Set Time (Minutes) for Each Player: Unlimited"

        toggle_slider()

        unlimited_checkbox.bind(active=toggle_slider)
        limited_checkbox.bind(active=toggle_slider)

        def save_settings(*args):
            self.settings["board_level"] = board_spinner.text
            self.settings["play_mode"] = mode_spinner.text
            if limited_checkbox.active:
                self.settings["timer_mode"] = "Limited"
                self.settings["timer_minutes"] = int(timer_slider.value)
            else:
                self.settings["timer_mode"] = "Unlimited"
                self.settings["timer_minutes"] = 1

            selected_level = next((level for level in self.levels if level["name"] == self.settings["board_level"]), None)
            if selected_level:
                print("Selected Level Config:")
                print("Size:", selected_level["size"])
                print("Board:", selected_level["board"])
            else:
                print("Level not found!")

            print("Saved Settings:", self.settings)
            config_popup.dismiss()

        save_button = Button(
            text="Save Settings",
            size_hint=(1, None),
            height=50,
            background_color=(0.2, 0.8, 0.2, 1),
        )
        save_button.bind(on_press=save_settings)
        popup_layout.add_widget(save_button)

        config_popup = Popup(
            title="Configuration Settings",
            content=popup_layout,
            size_hint=(0.8, 0.8),
        )
        config_popup.open()
    
    # I had to refer to the documentation of Screen Manager similar to the previous projects in order to understand how to 
    # navigate to the make new level screen in my game. I also used in other areas of the application as well and kept
    # referring to this docementation
    # https://kivy.org/doc/stable/api-kivy.uix.screenmanager.html
    def open_make_new_level_screen(self, instance):
        make_new_level_screen = Screen(name="make_new_level_screen")
        make_new_level_screen.add_widget(MakeNewLevelScreen(self))
        self.screen_manager.add_widget(make_new_level_screen)
        self.screen_manager.current = "make_new_level_screen"
    
    def reload_board_spinner_values(self, board_spinner):
        self.load_levels()
        board_spinner.values = [level["name"] for level in self.levels]

    def start_game(self, instance):
        selected_level_name = self.settings["board_level"]
        selected_level = next((level for level in self.levels if level["name"] == selected_level_name), None)
        if not selected_level:
            print(f"Error: Level '{selected_level_name}' not found!")
            return

        is_vs_computer = self.settings["play_mode"] == "Player vs Computer"
        existing_game_screen = self.screen_manager.get_screen("game_screen") if "game_screen" in self.screen_manager.screen_names else None

        if existing_game_screen:
            print("Resetting existing game screen...")
            existing_game_screen.clear_widgets()
            existing_game_screen.add_widget(GameScreen(selected_level, self.settings, is_vs_computer))
        else:
            print("Starting new game screen...")
            game_screen = Screen(name="game_screen")
            game_screen.add_widget(GameScreen(selected_level, self.settings, is_vs_computer))
            self.screen_manager.add_widget(game_screen)

        self.screen_manager.current = "game_screen"
    
    def exit_game(self, instance):
        print("Exiting the game...")
        App.get_running_app().stop()

# This class is responsible for implementing the game logic on the board for the Ataxx game
class GameScreen(FloatLayout):
    def __init__(self, selected_level, settings, is_vs_computer=False, **kwargs):
        super().__init__(**kwargs)
        self.circle_references = {}
        self.selected_circle = None
        self.ai_character = None
        
        self.is_vs_computer = is_vs_computer
        self.settings = settings
        if self.settings["timer_mode"] == "Limited":
            self.player_1_time = self.settings["timer_minutes"] * 60
            self.player_2_time = self.settings["timer_minutes"] * 60
        else:
            self.player_1_time = None
            self.player_2_time = None
        self.active_player = 1

        cols = selected_level["size"][1]
        rows = selected_level["size"][0]
        self.cols = cols
        self.rows = rows
        self.board_state = [[0 for _ in range(cols)] for _ in range(rows)]

        padding = 10
        cell_size = min((scr_w - 2 * padding) // cols, (scr_h - 2 * padding) // rows)
        self.cell_size = cell_size

        grid_width = cell_size * cols
        grid_height = cell_size * rows

        offset_x = 200
        grid_x = (grid_width / 2) + offset_x
        grid_y = grid_height / 2
        self.grid_x = grid_x
        self.grid_y = grid_y

        with self.canvas.before:
            Color(0, 0, 0, 1)
            self.bg_base = Rectangle(size=self.size, pos=self.pos)
            Color(0.1, 0.5, 0.1, 1)
            self.bg_overlay = Rectangle(size=self.size, pos=self.pos, source="./image/grid_pattern.jpg")

        self.bind(size=self._update_bg, pos=self._update_bg)

        self.reset_game(selected_level)
        self.player_1_count = sum(cell == 1 for row in selected_level["board"] for cell in row)
        self.player_2_count = sum(cell == 2 for row in selected_level["board"] for cell in row)

        # I referred to the following Youtube Tutorial in order to understand how to have dynamic
        # labels that change consistently throughout the course of my Kivy game. Both of these labels
        # were applied to update the number of pieces for player 1 and player 2 on the board
        # https://www.youtube.com/watch?v=7Sks1Ld1DWY
        self.player_1_label = Label(
            text="Player 1",
            font_size="24sp",
            bold=True,
            color=(1, 0, 0, 1),
            pos=(grid_x - 250, grid_y + grid_height / 2 + 40),
            size_hint=(None, None),
        )
        self.player_1_piece_count = Label(
            text=f"Pieces: {self.player_1_count}",
            font_size="20sp",
            color=(1, 1, 1, 1),
            pos=(grid_x - 250, grid_y + grid_height / 2 - 60),
            size_hint=(None, None),
        )
        self.player_1_timer = Label(
            text=self.format_time(self.player_1_time),
            font_size="20sp",
            color=(1, 1, 1, 1),
            pos=(grid_x - 250, grid_y + grid_height / 2 - 20),
            size_hint=(None, None),
        )

        self.add_widget(self.player_1_label)
        self.add_widget(self.player_1_piece_count)
        self.add_widget(self.player_1_timer)

        self.player_2_label = Label(
            text="Player 2",
            font_size="24sp",
            bold=True,
            color=(0, 0, 1, 1),
            pos=(grid_x + grid_width + 150, grid_y + grid_height / 2 + 40),
            size_hint=(None, None),
        )
        self.player_2_piece_count = Label(
            text=f"Pieces: {self.player_2_count}",
            font_size="20sp",
            color=(1, 1, 1, 1),
            pos=(grid_x + grid_width + 150, grid_y + grid_height / 2 - 60),
            size_hint=(None, None),
        )
        self.player_2_timer = Label(
            text=self.format_time(self.player_2_time),
            font_size="20sp",
            color=(1, 1, 1, 1),
            pos=(grid_x + grid_width + 150, grid_y + grid_height / 2 - 20),
            size_hint=(None, None),
        )

        self.add_widget(self.player_2_label)
        self.add_widget(self.player_2_piece_count)
        self.add_widget(self.player_2_timer)

        # I had to refer to the offical Kivy documentation in order to understand how to draw the lines
        # that were necessary for this game such that they were a in grid based format
        with self.canvas:
            Color(0.8, 0.8, 0.8, 1)
            for i in range(rows + 1):
                y = grid_y + i * cell_size
                Line(points=[grid_x, y, grid_x + grid_width, y], width=2)
            for j in range(cols + 1):
                x = grid_x + j * cell_size
                Line(points=[x, grid_y, x, grid_y + grid_height], width=2)

        self.cells = []
        for row_idx in range(rows):
            row = []
            for col_idx in range(cols):
                cell = self.create_cell_widget(row_idx, col_idx, cell_size, grid_x, grid_y)
                row.append(cell)
            self.cells.append(row)

        self.timer_event = Clock.schedule_interval(self.update_timer, 1)
        
        # I used the is_vs_computer tracker numerous time through the application to determine whether
        # or not the user was in the player vs computer mode. If they were in that mode, then it
        # the appropiate ai related components of the game are introduced like the AI character
        # below
        if self.is_vs_computer:
            self.ai_character = AICharacter(self)


    def reset_game(self, selected_level):
        for (row, col) in list(self.circle_references.keys()):
            self.clear_cell(row, col)
        self.circle_references.clear()
        self.board_state = [[0 for _ in range(self.cols)] for _ in range(self.rows)]
        for row_idx, row in enumerate(selected_level["board"]):
            for col_idx, cell_value in enumerate(row):
                if cell_value == 9:
                    self.board_state[row_idx][col_idx] = 9
                    with self.canvas.before:
                        Color(0.5, 0.5, 0.5, 1)
                        Rectangle(
                            pos=(
                                self.grid_x + col_idx * self.cell_size,
                                self.grid_y + row_idx * self.cell_size,
                            ),
                            size=(self.cell_size, self.cell_size),
                        )
                elif cell_value == 1:
                    self.board_state[row_idx][col_idx] = 1
                    self.draw_circle(
                        self.grid_x, self.grid_y, col_idx, row_idx, self.cell_size, (1, 0, 0, 1),
                        is_starting_cell=True, owner=1
                    )
                elif cell_value == 2:
                    self.board_state[row_idx][col_idx] = 2
                    self.draw_circle(
                        self.grid_x, self.grid_y, col_idx, row_idx, self.cell_size, (0, 0, 1, 1),
                        is_starting_cell=True, owner=2
                    )

    def _update_bg(self, *args):
        self.bg_base.size = self.size
        self.bg_base.pos = self.pos
        self.bg_overlay.size = self.size
        self.bg_overlay.pos = self.pos

    # I referred to the following documentation that shows how to build an array based
    # grid in Python and how it can be clicked upon throughout the course of the application.
    # I used this documentation as a source in order to understand how to create a similar
    # grid based structure for this game in Kivy
    # https://learn.arcade.academy/en/latest/chapters/28_array_backed_grids/array_backed_grids.html
    def create_cell_widget(self, row, col, cell_size, grid_x, grid_y):
        cell_value = self.board_state[row][col]
        if cell_value == 9:
            with self.canvas.before:
                Color(0.5, 0.5, 0.5, 1)
                Rectangle(pos=(grid_x + col * cell_size, grid_y + row * cell_size), size=(cell_size, cell_size))
            return None

        cell_button = Button(
            size_hint=(None, None),
            size=(cell_size, cell_size),
            pos=(grid_x + col * cell_size, grid_y + row * cell_size),
            background_normal="",
            background_color=(0, 0, 0, 0),
        )
        cell_button.cell_coords = (col, row)

        with cell_button.canvas.before:
            Color(0.2, 0.6, 0.2, 0.5)
            RoundedRectangle(size=cell_button.size, pos=cell_button.pos, radius=[10])

        # I referred to the following documentation in order understand how to have
        # a mouse hover effect for the appropiate traversable cells in Kivy
        # https://stackoverflow.com/questions/58190402/implement-a-kivy-button-mouseover-event
        def hover_effect(instance, touch):
            if instance.collide_point(*touch.pos):
                instance.canvas.before.clear()
                with instance.canvas.before:
                    Color(0.3, 0.8, 0.3, 1)
                    RoundedRectangle(size=instance.size, pos=instance.pos, radius=[10])

        def unhover_effect(instance, touch):
            instance.canvas.before.clear()
            with instance.canvas.before:
                Color(0.2, 0.6, 0.2, 0.5)
                RoundedRectangle(size=instance.size, pos=instance.pos, radius=[10])

        cell_button.bind(on_touch_down=hover_effect, on_touch_up=unhover_effect)
        cell_button.bind(on_press=self.on_cell_click)
        self.add_widget(cell_button)
        return cell_button

    # I referred to the following Stack Over flow post in order to understand how to draw
    # the appropiate circle within my Kivy application
    # https://stackoverflow.com/questions/72118415/kivy-draw-circle-to-middle-of-screen-on-startup
    def draw_circle(self, grid_x, grid_y, col, row, cell_size, color, is_starting_cell=False, owner=None):
        center_x = grid_x + col * cell_size + cell_size / 2
        center_y = grid_y + row * cell_size + cell_size / 2
        radius = cell_size * 0.4

        with self.canvas:
            shadow_color = Color(0, 0, 0, 0.5)
            shadow = Ellipse(pos=(center_x - radius - 5, center_y - radius - 5), size=(radius * 2, radius * 2))

            circle_color = Color(*color)
            circle = Ellipse(pos=(center_x - radius, center_y - radius), size=(radius * 2, radius * 2))

        self.circle_references[(row, col)] = {
            'circle': circle,
            'shadow': shadow,
            'color': circle_color,
            'is_starting_cell': is_starting_cell,
            'owner': owner
        }

    def format_time(self, time_seconds):
        if time_seconds is None:
            return ""
        minutes = time_seconds // 60
        seconds = time_seconds % 60
        return f"{minutes:02}:{seconds:02}"

    # I referred to the following Stack Over flow post in order to understand 
    # how to implement the timers for each player in Kivy and have them be
    # delivered to the user at the begining of the game
    def update_timer(self, dt):
        if self.settings["timer_mode"] == "Unlimited":
            return
        
        if self.active_player == 1:
            if self.player_1_time > 0:
                self.player_1_time -= 1
                self.player_1_timer.text = self.format_time(self.player_1_time)
            else:
                print("Player 1's time is up!")
                Clock.unschedule(self.update_timer)
                self.end_game(winner=2)
        elif self.active_player == 2:
            if self.player_2_time > 0:
                self.player_2_time -= 1
                self.player_2_timer.text = self.format_time(self.player_2_time)
            else:
                print("Player 2's time is up!")
                Clock.unschedule(self.update_timer)
                self.end_game(winner=1)

    def on_cell_click(self, instance):
        if self.is_vs_computer and self.active_player == 2:
            print("It's the AI's turn. Please wait.")
            return
        target_col, target_row = instance.cell_coords

        if self.selected_circle is None:
            if self.board_state[target_row][target_col] == self.active_player:
                self.selected_circle = (target_row, target_col)
                self.add_glow_effect(target_row, target_col)
                self.add_valid_cell_glow(target_row, target_col)
            else:
                print("Invalid selection: Please select your piece.")
            return

        src_row, src_col = self.selected_circle
        distance = max(abs(src_row - target_row), abs(src_col - target_col))

        if self.board_state[target_row][target_col] != 0:
            print("Invalid move: Target cell is occupied or blocked.")
            self.remove_glow_effect()
            self.remove_valid_cell_glow()
            self.selected_circle = None
            return

        if distance == 1:
            self.remove_glow_effect()
            self.remove_valid_cell_glow()
            self.animate_movement(src_row, src_col, target_row, target_col, is_jump=False)
            self.selected_circle = None
        elif distance == 2:
            self.remove_glow_effect()
            self.remove_valid_cell_glow()
            self.animate_jump(src_row, src_col, target_row, target_col)
            self.selected_circle = None
        else:
            print("Invalid move: Target cell is not valid.")
            self.remove_glow_effect()
            self.remove_valid_cell_glow()
            self.selected_circle = None

    # I have to refer to the Kivy doucmentation on graphics in order to understand how to
    # display the tranversable cells for a praticular circle upon clicking it
    # https://kivy.org/doc/stable/api-kivy.graphics.html
    def add_valid_cell_glow(self, row, col):
        # I created this array in order to store all the references for the 
        # expandable tranversable cells so that I could display theme at ease
        # for a praticular instance of a clicked circle and then removing those
        # cells later on
        self.valid_glow_references = []

        for target_row in range(self.rows):
            for target_col in range(self.cols):
                distance = max(abs(row - target_row), abs(col - target_col))

                if (distance == 1 or distance == 2) and self.board_state[target_row][target_col] == 0:
                    cell_x = self.grid_x + target_col * self.cell_size
                    cell_y = self.grid_y + target_row * self.cell_size

                    with self.canvas:
                        Color(1, 1, 0, 0.5)
                        glow_rect = RoundedRectangle(
                            pos=(cell_x, cell_y),
                            size=(self.cell_size, self.cell_size),
                            radius=[10]
                        )

                    self.valid_glow_references.append(glow_rect)

    def remove_valid_cell_glow(self):
        if not hasattr(self, 'valid_glow_references') or not self.valid_glow_references:
            return

        for glow_rect in self.valid_glow_references:
            self.canvas.remove(glow_rect)

        self.valid_glow_references = []

    # I had to refer to the following stackover flow on eclipse in order
    # to understand how to have the current active circle for a praticular
    # player be visually glowed on screen
    # https://kivy.org/doc/stable/api-kivy.graphics.html
    def add_glow_effect(self, row, col):
        references = self.circle_references.get((row, col))
        if not references:
            print(f"No circle found at ({row}, {col}) for glowing effect.")
            return
        circle = references['circle']

        with self.canvas:
            Color(1, 1, 1, 0.5)
            glow_circle = Ellipse(
                pos=(circle.pos[0] - 10, circle.pos[1] - 10),
                size=(circle.size[0] + 20, circle.size[1] + 20)
            )
        references['glow_circle'] = glow_circle

    def remove_glow_effect(self):
        if self.selected_circle is None:
            return

        row, col = self.selected_circle
        references = self.circle_references.get((row, col))
        if not references:
            return

        glow_circle = references.pop('glow_circle', None)
        if glow_circle:
            self.canvas.remove(glow_circle)

    def complete_move(self, src_row, src_col, target_row, target_col, is_jump):
        color = (1, 0, 0, 1) if self.active_player == 1 else (0, 0, 1, 1)
        self.draw_circle(self.grid_x, self.grid_y, target_col, target_row, self.cell_size, color)

        self.board_state[target_row][target_col] = self.active_player

        self.convert_adjacent_pieces(target_row, target_col)

        if is_jump:
            self.board_state[src_row][src_col] = 0
            self.clear_cell(src_row, src_col)

        sound = SoundLoader.load('./sound/jump.wav' if is_jump else './sound/move.mp3')
        if sound:
            sound.play()

        self.update_piece_counts()
        self.switch_turn()
        
        self.check_game_end()        

    def convert_adjacent_pieces(self, row, col):
        opponent = 2 if self.active_player == 1 else 1
        color = (1, 0, 0, 1) if self.active_player == 1 else (0, 0, 1, 1)
        directions = [
            (-1, 0),
            (1, 0),
            (0, -1),
            (0, 1),
            (-1, -1),
            (-1, 1),
            (1, -1),
            (1, 1),
        ]

        conversion_happened = False

        for d_row, d_col in directions:
            adj_row = row + d_row
            adj_col = col + d_col

            if 0 <= adj_row < self.rows and 0 <= adj_col < self.cols:
                if self.board_state[adj_row][adj_col] == opponent:
                    self.board_state[adj_row][adj_col] = self.active_player
                    self.animate_piece_conversion(adj_row, adj_col, color)
                    conversion_happened = True
        
        if conversion_happened:
            sound = SoundLoader.load('./sound/conversion.mp3')
            if sound:
                sound.volume = 0.5
                sound.play()

    def clear_cell(self, row, col):
        if (row, col) in self.circle_references:
            references = self.circle_references.pop((row, col))
            
            circle = references.get('circle')
            if circle and circle in self.canvas.children:
                self.canvas.remove(circle)

            shadow = references.get('shadow')
            if shadow and shadow in self.canvas.children:
                self.canvas.remove(shadow)

        cell_x = self.grid_x + col * self.cell_size
        cell_y = self.grid_y + row * self.cell_size

        with self.canvas.before:
            Color(0, 0, 0, 0)
            Rectangle(pos=(cell_x, cell_y), size=(self.cell_size, self.cell_size))

        self.canvas.ask_update()
    
    # I referred to the documentation on animation from Kivy in order to understand how to implement
    # the animation for the animate_piece_conversion, animate_movement, and animate_jump
    # that are located below. I used components of the grid based structure in order to 
    # integrate it withinthe Kivy animation
    # https://kivy.org/doc/stable/api-kivy.animation.html
    def animate_piece_conversion(self, row, col, target_color):
        references = self.circle_references.get((row, col))
        if not references:
            return 

        color_instruction = references['color']

        anim = Animation(r=target_color[0], g=target_color[1], b=target_color[2], a=target_color[3], duration=0.5)
        
        def finalize_conversion(*_):
            color_instruction.rgba = target_color

        anim.bind(on_complete=finalize_conversion)
        anim.start(color_instruction)

    def animate_movement(self, src_row, src_col, target_row, target_col, is_jump=False):
        target_x = self.grid_x + target_col * self.cell_size + self.cell_size / 2
        target_y = self.grid_y + target_row * self.cell_size + self.cell_size / 2

        with self.canvas:
            Color(1, 0, 0, 1) if self.active_player == 1 else Color(0, 0, 1, 1)
            moving_circle = Ellipse(pos=(target_x - self.cell_size / 4, target_y - self.cell_size / 4),
                                    size=(self.cell_size / 2, self.cell_size / 2))

        anim = Animation(pos=(target_x - self.cell_size / 4, target_y - self.cell_size / 4), duration=0.3)

        anim.bind(on_complete=lambda *_: self.complete_move(src_row, src_col, target_row, target_col, is_jump))
        anim.start(moving_circle)

    def animate_jump(self, src_row, src_col, target_row, target_col):
        if self.selected_circle is None or (src_row, src_col) != self.selected_circle:
            print("Error: The source circle does not match the selected circle.")
            return

        references = self.circle_references.get((src_row, src_col))
        if not references:
            print(f"No circle found at ({src_row}, {src_col}) to animate jump.")
            return
        
        src_circle = references['circle']
        src_color = references['color']
        src_owner = references['owner']
        src_x, src_y = src_circle.pos
        src_size = src_circle.size

        target_x = self.grid_x + target_col * self.cell_size + self.cell_size / 2 - src_size[0] / 2
        target_y = self.grid_y + target_row * self.cell_size + self.cell_size / 2 - src_size[1] / 2

        with self.canvas:
            Color(r=src_color.r, g=src_color.g, b=src_color.b, a=src_color.a)
            jumping_circle = Ellipse(pos=(src_x, src_y), size=src_size)

        anim = (
            Animation(pos=(target_x, target_y), duration=0.5, t="out_bounce") +
            Animation(size=src_size, duration=0.2)
        )

        def finalize_jump(*_):
            current_references = self.circle_references.get((src_row, src_col))
            if current_references:
                current_color = current_references['color']
                current_owner = current_references['owner']
                if (
                    current_owner == src_owner
                    and current_color.rgba == src_color.rgba
                ):
                    self.clear_cell(src_row, src_col)
                else:
                    print(
                        f"Skipping removal: Owner or color mismatch for circle at "
                        f"({src_row}, {src_col}). Expected color: {src_color.rgba}, "
                        f"Found color: {current_color.rgba}."
                    )
            else:
                print(f"No current references found at ({src_row}, {src_col}).")

            if jumping_circle in self.canvas.children:
                self.canvas.remove(jumping_circle)

            self.complete_move(src_row, src_col, target_row, target_col, is_jump=True)

        anim.bind(on_complete=finalize_jump)
        anim.start(jumping_circle)

    # I referred to the following red post in order to easily be able to implement the 
    # two player functionality in this game and have the player be able to switch
    # their turns:
    # https://www.reddit.com/r/learnprogramming/comments/17cvdx/python_how_do_i_swap_players_in_a_2player_game/
    def switch_turn(self):
        if self.active_player == 1:
            self.active_player = 2
            self.player_1_label.color = (0.5, 0.5, 0.5, 1)
            self.player_2_label.color = (0, 0, 1, 1)
            if self.is_vs_computer:
                Clock.schedule_once(lambda dt: self.trigger_ai_move(), 1.5)
        else:
            self.active_player = 1
            self.player_2_label.color = (0.5, 0.5, 0.5, 1)
            self.player_1_label.color = (1, 0, 0, 1)
        
        print(f"Active Player: {self.active_player}")    

    def trigger_ai_move(self):
        if not hasattr(self, 'ai'):
            self.ai = AtaxxAI(self.rows, self.cols)

        if self.active_player != 2:
            print("It's not the AI's turn.")
            return

        state = self.ai.get_state(self.board_state)
        valid_moves = self.get_valid_moves()
        
        if not valid_moves:
            print("AI has no valid moves.")
            self.switch_turn()
            return

        # I had to refer to the following documentation in order to implement the AI mechansim of the avatar
        # where I built a simple neural network architecture in a manner that it selects the move which maximizes 
        # the positive difference in the total pieces between the two teams
        # https://medium.com/technology-invention-and-more/how-to-build-a-simple-neural-network-in-9-lines-of-python-code-cc8f23647ca1
        move = self.ai.get_action(state, valid_moves)
        src_row, src_col, target_row, target_col = move

        distance = max(abs(src_row - target_row), abs(src_col - target_col))
        if distance == 1:
            self.animate_movement(src_row, src_col, target_row, target_col, is_jump=False)
        elif distance == 2:
            self.animate_jump(src_row, src_col, target_row, target_col)

        self.board_state = self.ai.apply_move(self.board_state, move)

        reward = self.calculate_reward()

        next_state = self.ai.get_state(self.board_state)
        done = self.check_game_end()
        self.ai.remember(state, move, reward, next_state, done)

        self.ai.replay(32)

        result = self.calculate_ai_result()
        if self.ai_character:
            self.ai_character.evaluate_outcome(result)
    
    def calculate_ai_result(self):
        ai_pieces = sum(row.count(2) for row in self.board_state)
        player_pieces = sum(row.count(1) for row in self.board_state)
        return ai_pieces - player_pieces
    
    # I had to refer to the documentation on Attax to understand what the valid
    # moves where for this game and be able to implement in a grid base approach
    # as you can see below
    # http://www.linuxonly.nl/docs/4/0_Ataxx.html
    def get_valid_moves(self):
        valid_moves = []
        directions = [
            (-1, 0), (1, 0), (0, -1), (0, 1),
            (-2, 0), (2, 0), (0, -2), (0, 2),
            (-1, -1), (-1, 1), (1, -1), (1, 1),
            (-2, -2), (-2, 2), (2, -2), (2, 2)
        ]
        
        for row in range(self.rows):
            for col in range(self.cols):
                if self.board_state[row][col] == 2:
                    for d_row, d_col in directions:
                        target_row, target_col = row + d_row, col + d_col
                        if 0 <= target_row < self.rows and 0 <= target_col < self.cols:
                            if self.board_state[target_row][target_col] == 0:
                                valid_moves.append((row, col, target_row, target_col))
        return valid_moves

    def calculate_reward(self):
        ai_pieces = sum(row.count(2) for row in self.board_state)
        player_pieces = sum(row.count(1) for row in self.board_state)
        return ai_pieces - player_pieces

    def update_piece_counts(self):
        player_1_count = sum(cell == 1 for row in self.board_state for cell in row)
        player_2_count = sum(cell == 2 for row in self.board_state for cell in row)
        self.player_1_piece_count.text = f"Pieces: {player_1_count}"
        self.player_2_piece_count.text = f"Pieces: {player_2_count}"
    
    # I had to refer to these rules set for Attax to understand the various different
    # winning conditions for Attax and be able to implement it within this game:
    # https://skatgame.net/mburo/ggsa/ax.rules
    def check_game_end(self):
        player_1_count = sum(cell == 1 for row in self.board_state for cell in row)
        player_2_count = sum(cell == 2 for row in self.board_state for cell in row)

        if player_1_count == 0:
            self.end_game(winner=2)
            return
        elif player_2_count == 0:
            self.end_game(winner=1)
            return

        total_pieces = player_1_count + player_2_count
        total_cells = sum(cell != 9 for row in self.board_state for cell in row)
        if player_1_count == total_cells or player_2_count == total_cells:
            winner = 1 if player_1_count == total_cells else 2
            self.end_game(winner=winner)
            return

        if not self.has_valid_moves(1) and not self.has_valid_moves(2):
            winner = 1 if player_1_count > player_2_count else 2
            self.end_game(winner=winner)


    def has_valid_moves(self, player):
        directions = [
            (-1, 0), (1, 0), (0, -1), (0, 1),
            (-2, 0), (2, 0), (0, -2), (0, 2),
            (-1, -1), (-1, 1), (1, -1), (1, 1),
            (-2, -2), (-2, 2), (2, -2), (2, 2),
        ]
        for row_idx, row in enumerate(self.board_state):
            for col_idx, cell in enumerate(row):
                if cell == player:
                    for d_row, d_col in directions:
                        target_row = row_idx + d_row
                        target_col = col_idx + d_col
                        if 0 <= target_row < self.rows and 0 <= target_col < self.cols:
                            if self.board_state[target_row][target_col] == 0:
                                return True
        return False

    def end_game(self, winner):
        screen_manager = self.parent.parent
        if not screen_manager:
            print("Error: ScreenManager not found!")
            return

        end_screen = Screen(name="end_screen")
        end_game_screen = EndGameScreen(winner, screen_manager)
        end_screen.add_widget(end_game_screen)
        screen_manager.add_widget(end_screen)
        screen_manager.current = "end_screen"
        Clock.schedule_once(self.play_game_over_sound, 1)
    
    def play_game_over_sound(self, *args):
        """Play the game over sound."""
        game_over_sound = SoundLoader.load('./sound/game-over.mp3')
        if game_over_sound:
            game_over_sound.volume = 0.8
            game_over_sound.play()

class EndGameScreen(FloatLayout):
    def __init__(self, winner, screen_manager, **kwargs):
        super().__init__(**kwargs)
        self.screen_manager = screen_manager
        self.remaining_time = 10

        with self.canvas.before:
            Color(0, 0, 0, 1)
            self.bg_base = Rectangle(size=self.size, pos=self.pos)
            Color(0.1, 0.5, 0.1, 1)
            self.bg_overlay = Rectangle(size=self.size, pos=self.pos, source="./image/grid_pattern.jpg")
        self.bind(size=self._update_bg, pos=self._update_bg)

        # Similar to beforen, I referred to the following documentation located below 
        # to support the custom font that utilized several times throughout this application:
        # https://www.geeksforgeeks.org/how-to-add-custom-fonts-in-kivy-python/
        self.title = Label(
            text="Game Over",
            font_size="90sp",
            bold=True,
            font_name="./font/retro_drip.ttf",
            color=(0.8, 1, 0.8, 1),
            size_hint=(1, 0.3),
            pos_hint={"center_x": 0.5, "center_y": 0.7},
        )
        self.add_widget(self.title)
        self.animate_label(self.title, (1, 1, 1, 1), (0.8, 1, 0.8, 1))

        dark_color = (0.5, 0, 0, 1) if winner == 1 else (0, 0, 0.5, 1)
        light_color = (1, 0, 0, 1) if winner == 1 else (0, 0, 1, 1)
        self.winner_label = Label(
            text=f"Player {winner} Wins!",
            font_size="50sp",
            bold=True,
            font_name="./font/retro_drip.ttf",
            color=dark_color,
            size_hint=(None, None),
            pos_hint={"center_x": 0.5, "center_y": 0.5},
        )
        self.add_widget(self.winner_label)
        self.animate_label(self.winner_label, light_color, dark_color)

        # I had to refer Clock Kivy documentation again to have a countdown for 
        # returning back to the start screen after a selected period of time on the
        # main screen
        # https://kivy.org/doc/stable/api-kivy.clock.html
        self.timer_label = Label(
            text=f"Returning to the main start screen in {self.remaining_time} seconds",
            font_size="20sp",
            color=(1, 1, 1, 1),
            size_hint=(None, None),
            pos_hint={"center_x": 0.5, "center_y": 0.3},
        )
        self.add_widget(self.timer_label)

        Clock.schedule_interval(self.update_timer, 1)

    def animate_label(self, label, light_color, dark_color):
        anim = Animation(color=light_color, duration=0.7) + Animation(color=dark_color, duration=0.7)
        anim.repeat = True
        anim.start(label)

    def update_timer(self, dt):
        print(f"Time left: {self.remaining_time}")
        if self.remaining_time > 0:
            self.remaining_time -= 1
            self.timer_label.text = f"Returning to the main start screen in {self.remaining_time} seconds"
        else:
            print("Transitioning to start screen...")
            Clock.unschedule(self.update_timer)
            if self.screen_manager:
                self.screen_manager.current = "start_screen"
            else:
                print("Error: ScreenManager is None!")

    def _update_bg(self, *args):
        self.bg_base.size = self.size
        self.bg_base.pos = self.pos
        self.bg_overlay.size = self.size
        self.bg_overlay.pos = self.pos

class MakeNewLevelScreen(FloatLayout):
    def __init__(self, ataxx_start_screen, rows=7, cols=7, **kwargs):
        super().__init__(**kwargs)
        self.rows = rows
        self.cols = cols
        self.grid = [[0 for _ in range(cols)] for _ in range(rows)]
        self.ataxx_start_screen = ataxx_start_screen
        self.circle_references = {}

        with self.canvas.before:
            Color(0, 0, 0, 1)
            self.bg_base = Rectangle(size=self.size, pos=self.pos)
            Color(0.1, 0.5, 0.1, 1)
            self.bg_overlay = Rectangle(size=self.size, pos=self.pos, source="./image/grid_pattern.jpg")
        self.bind(size=self._update_bg, pos=self._update_bg)

        padding = 10
        cell_size = min((scr_w - 2 * padding) // cols, (scr_h - 2 * padding) // rows)
        self.cell_size = cell_size

        grid_width = cell_size * cols
        grid_height = cell_size * rows
        offset_x = 200
        self.grid_x = (grid_width / 2) + offset_x
        self.grid_y = grid_height / 2

        self.draw_grid_with_lighting()

        self.add_widget(self.create_button("Back to Start", self.go_back, 0.3))
        self.add_widget(self.create_button("Save Level", self.save_level, 0.7))
        self.show_description_popup()
        
    def _update_bg(self, *args):
        self.bg_base.size = self.size
        self.bg_base.pos = self.pos
        self.bg_overlay.size = self.size
        self.bg_overlay.pos = self.pos
    
    # I had to refer to the following documentation in order to understand how to
    # implement a popup menu for the start of the make a level screen
    # https://www.google.com//search?udm=14&q=kivy+popup
    #
    # I had to refer to the following documentation as well to have it be implemented
    # within a Box Layout structure:
    # https://kivy.org/doc/stable/api-kivy.uix.boxlayout.html
    def show_description_popup(self):
        content = BoxLayout(orientation="vertical", padding=20, spacing=10)
        instructions = Label(
            text=(
                "[b]How to Use:[/b]\n\n"
                "• Click on cells to cycle through states:\n"
                "   0: Empty (traversable)\n"
                "   1: Player 1 start (blue)\n"
                "   2: Player 2 start (red)\n"
                "   3: Non-traversable (gray block).\n\n"
                "[b]Requirements for a Level:[/b]\n\n"
                "• Each player must have the same, non-zero number of starting pieces.\n"
                "• At least some free spaces (state 0) must be available for moves.\n"
                "• Ensure the layout allows players to move and interact effectively."
            ),
            font_size="16sp",
            markup=True,
            halign="left",
            valign="top",
            text_size=(600, None),
            size_hint_y=None
        )
        instructions.bind(texture_size=lambda instance, value: setattr(instructions, 'height', value[1]))
        content.add_widget(instructions)

        ok_button = Button(
            text="OK",
            size_hint=(1, None),
            height=50,
            background_color=(0.2, 0.8, 0.2, 1)
        )
        content.add_widget(ok_button)

        popup = Popup(
            title="Level Creation Instructions",
            content=content,
            size_hint=(0.8, 0.7),
            auto_dismiss=False
        )

        ok_button.bind(on_press=popup.dismiss)

        popup.open()

    # I referred to this documentation on Kivy's page on Line in order to understand how to 
    # draw a grid based line to before but this time with glowing. I added this to the 
    # Make a New Level Screen:
    # https://kivy.org/doc/stable/examples/gen__canvas__lines_extended__py.html
    def draw_grid_with_lighting(self):
        with self.canvas:
            Color(0.1, 1, 0.1, 0.2)
            for i in range(self.rows + 1):
                y = self.grid_y + i * self.cell_size
                Line(points=[self.grid_x, y, self.grid_x + self.cols * self.cell_size, y], width=5)
            for j in range(self.cols + 1):
                x = self.grid_x + j * self.cell_size
                Line(points=[x, self.grid_y, x, self.grid_y + self.rows * self.cell_size], width=5)

            Color(0.8, 0.8, 0.8, 1)
            for i in range(self.rows + 1):
                y = self.grid_y + i * self.cell_size
                Line(points=[self.grid_x, y, self.grid_x + self.cols * self.cell_size, y], width=2)
            for j in range(self.cols + 1):
                x = self.grid_x + j * self.cell_size
                Line(points=[x, self.grid_y, x, self.grid_y + self.rows * self.cell_size], width=2)

        for row in range(self.rows):
            for col in range(self.cols):
                cell_button = Button(
                    size_hint=(None, None),
                    size=(self.cell_size, self.cell_size),
                    pos=(self.grid_x + col * self.cell_size, self.grid_y + row * self.cell_size),
                    background_normal="",
                    background_color=(0, 0, 0, 0),
                )
                cell_button.bind(on_press=lambda instance, r=row, c=col: self.toggle_cell(r, c))
                self.add_widget(cell_button)

    def toggle_cell(self, row, col):
        current_state = self.grid[row][col]
        new_state = (current_state + 1) % 4
        self.grid[row][col] = new_state

        x = self.grid_x + col * self.cell_size
        y = self.grid_y + row * self.cell_size
        radius = self.cell_size * 0.4

        with self.canvas:
            Color(0, 0, 0, 1)
            Rectangle(pos=(x, y), size=(self.cell_size, self.cell_size))
            print(new_state)
            if new_state == 1:
                Color(0, 0, 1, 1)
                Ellipse(pos=(x + self.cell_size / 2 - radius, y + self.cell_size / 2 - radius),
                        size=(radius * 2, radius * 2))
            elif new_state == 2:
                Color(1, 0, 0, 1)
                Ellipse(pos=(x + self.cell_size / 2 - radius, y + self.cell_size / 2 - radius),
                        size=(radius * 2, radius * 2))
            elif new_state == 3:
                Color(0.5, 0.5, 0.5, 1)
                Rectangle(pos=(x, y), size=(self.cell_size, self.cell_size))
            
        sound = SoundLoader.load('./sound/change-item.mp3')
        if sound:
            sound.volume = 0.5
            sound.play()
        else:
            print("Failed to load sound: change-item.mp3")

    def clear_visual_cell(self, x, y):
        with self.canvas.before:
            Color(0, 0, 0, 0)
            Rectangle(pos=(x, y), size=(self.cell_size, self.cell_size))

    # Like before on the title screen, I had to refer to the offical documentation on Kivy 
    # buttons  in order to understand how to have their colors change dynamically 
    # on this page. The link to that is located below:
    # https://kivy.org/doc/stable-2.2.0/api-kivy.uix.button.html
    def create_button(self, text, callback, x_position):
        button_layout = BoxLayout(
            size_hint=(None, None),
            size=(200, 50),
            pos_hint={"center_x": x_position, "center_y": 0.1}
        )
        with button_layout.canvas.before:
            button_layout.bg_color = Color(0.2, 0.6, 0.2, 1)
            button_layout.bg_rect = RoundedRectangle(size=button_layout.size, pos=button_layout.pos, radius=[10])
        button_layout.bind(
            size=lambda instance, value: setattr(button_layout.bg_rect, 'size', value),
            pos=lambda instance, value: setattr(button_layout.bg_rect, 'pos', value)
        )

        btn = Button(
            text=text,
            font_size="16sp",
            background_normal="",
            background_color=(0, 0, 0, 0),
            color=(1, 1, 1, 1),
        )
        btn.bind(on_press=callback)

        self.animate_button_and_background(btn, button_layout.bg_color)

        button_layout.add_widget(btn)
        return button_layout

    def animate_button_and_background(self, button, bg_color):
        button_anim = (
            Animation(color=(1, 1, 1, 1), duration=0.7) +
            Animation(color=(0.8, 1, 0.8, 1), duration=0.7)
        )
        button_anim.repeat = True
        button_anim.start(button)

        bg_anim = (
            Animation(rgb=(0.2, 0.8, 0.2), duration=0.7) +
            Animation(rgb=(0.1, 0.6, 0.1), duration=0.7)
        )
        bg_anim.repeat = True
        bg_anim.start(bg_color)

    def save_level(self, instance):
        def validate_constraints(grid):
            player1_count = sum(cell == 1 for row in grid for cell in row)
            player2_count = sum(cell == 2 for row in grid for cell in row)
            empty_count = sum(cell == 0 for row in grid for cell in row)

            if player1_count == 0 or player2_count == 0:
                return "Each player must have at least one starting piece."
            if player1_count != player2_count:
                return "Player 1 and Player 2 must have the same number of starting pieces."
            if empty_count == 0:
                return "The level must have at least one empty (traversable) cell."
            return None 

        error_message = validate_constraints(self.grid)
        if error_message:
            self.show_error_popup(error_message)
            return

        self.open_save_level_popup()

    def show_error_popup(self, error_message):
        content = BoxLayout(orientation="vertical", spacing=10, padding=10)
        content.add_widget(Label(text=error_message, font_size="16sp", halign="center", valign="middle"))
        ok_button = Button(text="OK", size_hint=(1, None), height=50, background_color=(0.8, 0.2, 0.2, 1))
        content.add_widget(ok_button)

        popup = Popup(
            title="Invalid Level",
            content=content,
            size_hint=(0.8, 0.4),
            auto_dismiss=False
        )

        ok_button.bind(on_press=popup.dismiss)
        popup.open()

        sound = SoundLoader.load('./sound/error.mp3')
        if sound:
            sound.volume = 0.5
            sound.play()
        else:
            print("Failed to load sound: change-item.mp3")

    # I had to refer to the offical kivy documentation on how to 
    # be able have the save level popup appear for the user
    # on the screen. Here is the documentation to that
    # https://kivy.org/doc/stable/api-kivy.uix.popup.html
    #
    # I also had to refer to the text inut documentation
    # to have the user save the name level
    # https://kivy.org/doc/stable/api-kivy.uix.textinput.html
    def open_save_level_popup(self):
        content = BoxLayout(orientation="vertical", spacing=10)

        level_name_input = TextInput(
            hint_text="Enter level name",
            multiline=False,
            size_hint=(1, None),
            height=44
        )
        content.add_widget(level_name_input)

        button_layout = BoxLayout(orientation="horizontal", spacing=10, size_hint=(1, None), height=50)
        cancel_button = Button(text="Cancel", background_color=(0.8, 0.2, 0.2, 1))
        save_button = Button(text="Save", background_color=(0.2, 0.8, 0.2, 1))
        button_layout.add_widget(cancel_button)
        button_layout.add_widget(save_button)
        content.add_widget(button_layout)

        popup = Popup(
            title="Save Level",
            content=content,
            size_hint=(0.8, 0.2),
            auto_dismiss=False
        )

        cancel_button.bind(on_press=popup.dismiss)

        def save_level_to_file(instance):
            level_name = level_name_input.text.strip()
            if not level_name:
                self.show_error_popup("Level name cannot be empty.")
                return

            converted_grid = [[9 if cell == 3 else cell for cell in row] for row in self.grid]
            new_level = {"name": level_name, "size": [self.rows, self.cols], "board": converted_grid}

            # I had to refer to the following documentation to understand how to
            # append and write to the levels.txt file with the level created
            # https://stackoverflow.com/questions/21763772/how-to-write-and-save-into-a-text-file-from-textinput-using-kivy
            try:
                with open("levels.txt", "r") as file:
                    levels = json.loads(file.read())
            except (FileNotFoundError, json.JSONDecodeError):
                levels = []

            levels.append(new_level)
            with open("levels.txt", "w") as file:
                json.dump(levels, file, indent=4)

            print(f"Level '{level_name}' saved successfully.")
            popup.dismiss()

            self.show_success_popup(level_name)

        save_button.bind(on_press=save_level_to_file)
        popup.open()
    
    # I had to refer to the following documentation again in order to understand how to
    # implement a popup menu for the start of the make a level screen.
    # This time I wanted to use it for creating the success menu on the game
    # https://www.google.com//search?udm=14&q=kivy+popup
    def show_success_popup(self, level_name):
        content = BoxLayout(orientation="vertical", spacing=10, padding=10)
        success_message = (
            f"Level '{level_name}' has been successfully saved.\n"
            "It is now playable and can be selected in the Configuration Settings."
        )
        content.add_widget(Label(text=success_message, font_size="16sp", halign="center", valign="middle"))
        
        ok_button = Button(
            text="OK",
            size_hint=(1, None),
            height=50,
            background_color=(0.2, 0.8, 0.2, 1)
        )
        content.add_widget(ok_button)

        success_popup = Popup(
            title="Level Saved",
            content=content,
            size_hint=(0.8, 0.4),
            auto_dismiss=False
        )

        success_popup_sound = SoundLoader.load('./sound/successful.mp3')
        if success_popup_sound:
            success_popup_sound.volume = 0.8
            success_popup_sound.play()
    
        ok_button.bind(on_press=success_popup.dismiss)
        ok_button.bind(on_press=self.go_back)
        success_popup.open()

    def go_back(self, instance):
        self.reset_board()
        screen_manager = App.get_running_app().root
        if screen_manager:
            screen_manager.current = "start_screen"
        else:
            print("Error: ScreenManager not found!")

    def reset_board(self):
        for row in range(self.rows):
            for col in range(self.cols):
                x = self.grid_x + col * self.cell_size
                y = self.grid_y + row * self.cell_size
                self.clear_visual_cell(x, y)

        self.grid = [[0 for _ in range(self.cols)] for _ in range(self.rows)]

        self.draw_grid_with_lighting()

    def clear_visual_cell(self, x, y):
        with self.canvas:
            Color(0, 0, 0, 1)
            Rectangle(pos=(x, y), size=(self.cell_size, self.cell_size))

        row = int((y - self.grid_y) // self.cell_size)
        col = int((x - self.grid_x) // self.cell_size)
        if (row, col) in self.circle_references:
            del self.circle_references[(row, col)]

class AtaxxApp(App):
    def build(self):
        screen_manager = ScreenManager()
        start_screen = Screen(name="start_screen")
        ataxx_start_screen = AtaxxStartScreen(screen_manager)
        start_screen.add_widget(ataxx_start_screen)
        screen_manager.add_widget(start_screen)
        ataxx_start_screen.play_background_music()
        return screen_manager

if __name__ == "__main__":
    AtaxxApp().run()