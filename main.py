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
import numpy as np
import random
from collections import deque
import json

class SimpleNN:
    def __init__(self, input_size, hidden_size, output_size):
        self.w1 = np.random.randn(input_size, hidden_size) / np.sqrt(input_size)
        self.w2 = np.random.randn(hidden_size, output_size) / np.sqrt(hidden_size)

    def forward(self, x):
        self.z1 = np.dot(x, self.w1)
        self.a1 = np.tanh(self.z1)
        self.z2 = np.dot(self.a1, self.w2)
        return self.z2

    def backward(self, x, y, learning_rate=0.01):
        self.forward(x)
        delta2 = self.z2 - y
        delta1 = np.dot(delta2, self.w2.T) * (1 - np.tanh(self.z1)**2)
        self.w2 -= learning_rate * np.outer(self.a1, delta2)
        self.w1 -= learning_rate * np.outer(x, delta1)

class AtaxxAI:
    def __init__(self, rows, cols):
        self.rows = rows
        self.cols = cols
        self.model = SimpleNN(rows * cols, 64, 1)
        self.memory = deque(maxlen=10000)
        self.epsilon = 1.0
        self.epsilon_min = 0.01
        self.epsilon_decay = 0.995
        self.gamma = 0.95

    def get_state(self, board_state):
        return np.array(board_state).flatten()

    def get_action(self, state, valid_moves):
        if np.random.rand() <= self.epsilon:
            return random.choice(valid_moves)
        
        q_values = []
        for move in valid_moves:
            next_state = self.apply_move(state.reshape(self.rows, self.cols), move)
            q_values.append(self.model.forward(next_state.flatten()))
        
        return valid_moves[np.argmax(q_values)]

    def apply_move(self, state, move):
        src_row, src_col, target_row, target_col = move
        new_state = state.copy()
        new_state[target_row][target_col] = 2  # AI player
        if max(abs(src_row - target_row), abs(src_col - target_col)) == 2:
            new_state[src_row][src_col] = 0
        return new_state

    def remember(self, state, action, reward, next_state, done):
        self.memory.append((state, action, reward, next_state, done))

    def replay(self, batch_size):
        if len(self.memory) < batch_size:
            return
        minibatch = random.sample(self.memory, batch_size)
        for state, action, reward, next_state, done in minibatch:
            target = reward
            if not done:
                target = reward + self.gamma * np.max(self.model.forward(next_state))
            target_f = self.model.forward(state)
            target_f[0] = target
            self.model.backward(state, target_f)
        if self.epsilon > self.epsilon_min:
            self.epsilon *= self.epsilon_decay
class AICharacter:
    def __init__(self, game_screen):
        self.game_screen = game_screen
        self.images = {
            'neutral': './image/bot/neutral_robot.png',
            'happy': './image/bot/happy_robot.png',
            'sad': './image/bot/sad_robot.png'
        }
        self.sounds = {
            'happy': './sound/bot/happy.mp3',
            'sad': './sound/bot/sad.mp3'
        }
        self.current_emotion = 'neutral'
        self.image_widget = Image(source=self.images['neutral'])
        self.position_character()
        self.game_screen.add_widget(self.image_widget)

    def position_character(self):
        # Position the character at the top-right of the grid
        self.image_widget.size_hint = (None, None)
        self.image_widget.size = (150, 150)  # Increased size from 100x100 to 150x150
        self.image_widget.pos = (
            self.game_screen.grid_x + self.game_screen.cell_size * self.game_screen.cols - 350,  # Move 50 pixels to the right
            self.game_screen.grid_y + self.game_screen.cell_size * self.game_screen.rows + 50   # Move 50 pixels up
        )

    def change_emotion(self, emotion):
        if emotion in self.images:
            self.current_emotion = emotion
            self.image_widget.source = self.images[emotion]
            self.play_sound(emotion)

    def play_sound(self, emotion):
        if emotion in self.sounds:
            sound = SoundLoader.load(self.sounds[emotion])
            if sound:
                sound.play()

    def evaluate_outcome(self, result):
        if result > 0:  # AI wins
            self.change_emotion('happy')
        elif result < 0:  # AI loses
            self.change_emotion('sad')
        else:  # Draw
            self.change_emotion('neutral')

class AtaxxStartScreen(BoxLayout):
    settings = {
        "board_level": "Level 1",
        "play_mode": "Player vs Player",
        "timer_mode": "Unlimited",
        "timer_minutes": 5,  # Default to 1 minute for limited timers
    }
    levels = []

    def __init__(self, screen_manager, **kwargs):
        super().__init__(**kwargs)
        self.screen_manager = screen_manager  # Add ScreenManager reference
        self.orientation = "vertical"
        self.spacing = 20
        self.padding = [20, 40, 20, 40]
        self.load_levels()
        self.mark_start_cells()

        # Layered Background
        with self.canvas.before:
            Color(0, 0, 0, 1)  # Black base
            self.bg_base = Rectangle(size=self.size, pos=self.pos)

            Color(0.1, 0.5, 0.1, 1)  # Green overlay
            self.bg_overlay = Rectangle(size=self.size, pos=self.pos, source="./image/grid_pattern.jpg")

        self.bind(size=self._update_bg, pos=self._update_bg)

        # FloatLayout to handle positioning
        layout = FloatLayout()

        # Title (Positioned Lower)
        self.title = Label(
            text="Ataxx",
            font_size="90sp",
            bold=True,
            font_name="./font/retro_drip.ttf",  # Custom retro font
            color=(0.8, 1, 0.8, 1),  # Glow green
            size_hint=(None, None),
            size=(400, 100),  # Fixed size for better positioning
            pos_hint={"center_x": 0.5, "top": 0.65},  # Adjust top position to move title downward
        )
        layout.add_widget(self.title)
        self.animate_title()

        # Button Layout (GridLayout inside FloatLayout)
        button_layout = GridLayout(
            cols=2,
            spacing=40,
            size_hint=(0.8, None),  # Adjust size
            height=200,  # Fixed height for the button grid
            pos_hint={"center_x": 0.5, "y": 0.1},  # Position at the bottom
        )

        # Add buttons to the grid
        button_layout.add_widget(self.create_button("Start Game", self.start_game))
        button_layout.add_widget(self.create_button("Configuration Settings", self.open_config_popup))
        button_layout.add_widget(self.create_button("Exit Game", self.exit_game))
        button_layout.add_widget(self.create_button("Make New Level", self.open_make_new_level_screen))

        layout.add_widget(button_layout)

        # Add the layout to the main widget
        self.add_widget(layout)

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

    def animate_title(self):
        anim = (
            Animation(color=(1, 1, 1, 1), duration=0.7) +
            Animation(color=(0.8, 1, 0.8, 1), duration=0.7)
        )
        anim.repeat = True
        anim.start(self.title)

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

    def play_background_music(self):
        self.music = SoundLoader.load('./sound/start_screen_music.mp3')
        if self.music:
            print("Music loaded successfully:", self.music.source)
            self.music.loop = True
            self.music.volume = 0.05
            self.music.play()
            print("Music is playing.")
        else:
            print("Failed to load music.")


    def open_config_popup(self, instance):
        popup_layout = BoxLayout(orientation="vertical", spacing=10, padding=10)

        # Game board selection
        popup_layout.add_widget(Label(text="Select Game Board Level:", font_size="16sp"))
        
        # Create the spinner first
        board_spinner = Spinner(
            text=self.settings["board_level"],
            values=[level["name"] for level in self.levels],  # Use updated levels
            size_hint=(1, None),
            height=44,
        )
        popup_layout.add_widget(board_spinner)

        # Now call reload_board_spinner_values with the spinner instance
        self.reload_board_spinner_values(board_spinner)  # Pass the spinner to reload levels

        def update_level_spinner(spinner, text):
            self.settings["board_level"] = text
            print(f"Board level changed to: {text}")

        board_spinner.bind(text=update_level_spinner)

        # Play mode selection
        popup_layout.add_widget(Label(text="Select Play Mode:", font_size="16sp"))
        mode_spinner = Spinner(
            text=self.settings["play_mode"],
            values=["Player vs Player", "Player vs Computer"],
            size_hint=(1, None),
            height=44,
        )
        popup_layout.add_widget(mode_spinner)

        # Timer mode
        popup_layout.add_widget(Label(text="Timer Mode:", font_size="16sp"))
        timer_layout = BoxLayout(orientation="horizontal", spacing=10)
        unlimited_checkbox = CheckBox(group="timer", active=self.settings["timer_mode"] == "Unlimited")
        limited_checkbox = CheckBox(group="timer", active=self.settings["timer_mode"] == "Limited")
        timer_layout.add_widget(Label(text="Unlimited", font_size="14sp"))
        timer_layout.add_widget(unlimited_checkbox)
        timer_layout.add_widget(Label(text="Limited", font_size="14sp"))
        timer_layout.add_widget(limited_checkbox)
        popup_layout.add_widget(timer_layout)

        # Slider for limited timer with dynamic label
        slider_layout = BoxLayout(orientation="vertical", spacing=10)
        slider_label = Label(
            text=f"Set Time (Minutes) for Each Player: {self.settings.get('timer_minutes', 1)}",
            font_size="14sp"
        )
        slider_layout.add_widget(slider_label)
        timer_slider = Slider(min=1, max=10, value=self.settings.get("timer_minutes", 1), size_hint=(1, None), height=44)
        slider_layout.add_widget(timer_slider)
        popup_layout.add_widget(slider_layout)

        # Bind slider value to update label text
        def update_slider_label(instance, value):
            slider_label.text = f"Set Time (Minutes) for Each Player: {int(value)}"

        timer_slider.bind(value=update_slider_label)

        # Checkbox callback to toggle slider visibility and functionality
        def toggle_slider(*args):
            if limited_checkbox.active:
                slider_layout.opacity = 1
                timer_slider.disabled = False
                slider_label.text = f"Set Time (Minutes) for Each Player: {int(timer_slider.value)}"
            else:
                slider_layout.opacity = 0.5
                timer_slider.disabled = True
                slider_label.text = "Set Time (Minutes) for Each Player: Unlimited"

        # Initial state based on the current setting
        toggle_slider()

        unlimited_checkbox.bind(active=toggle_slider)
        limited_checkbox.bind(active=toggle_slider)

        # Save button
        def save_settings(*args):
            self.settings["board_level"] = board_spinner.text
            self.settings["play_mode"] = mode_spinner.text
            if limited_checkbox.active:
                self.settings["timer_mode"] = "Limited"
                self.settings["timer_minutes"] = int(timer_slider.value)
            else:
                self.settings["timer_mode"] = "Unlimited"
                self.settings["timer_minutes"] = None

            # Map selected level to size and board
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

        # Create and open popup
        config_popup = Popup(
            title="Configuration Settings",
            content=popup_layout,
            size_hint=(0.8, 0.8),
        )
        config_popup.open()
    
    def open_make_new_level_screen(self, instance):
        make_new_level_screen = Screen(name="make_new_level_screen")
        make_new_level_screen.add_widget(MakeNewLevelScreen(self))
        self.screen_manager.add_widget(make_new_level_screen)
        self.screen_manager.current = "make_new_level_screen"
    
    def reload_board_spinner_values(self, board_spinner):
        """Reload the spinner's values dynamically after levels are updated."""
        self.load_levels()  # Reload levels from the file
        board_spinner.values = [level["name"] for level in self.levels]  # Update spinner values

    def start_game(self, instance):
        selected_level_name = self.settings["board_level"]
        selected_level = next((level for level in self.levels if level["name"] == selected_level_name), None)
        if not selected_level:
            print(f"Error: Level '{selected_level_name}' not found!")
            return

        # Check if the game is against the computer
        is_vs_computer = self.settings["play_mode"] == "Player vs Computer"

        # Check if the game screen already exists
        existing_game_screen = self.screen_manager.get_screen("game_screen") if "game_screen" in self.screen_manager.screen_names else None

        if existing_game_screen:
            print("Resetting existing game screen...")
            existing_game_screen.clear_widgets()  # Clear widgets from the screen
            existing_game_screen.add_widget(GameScreen(selected_level, self.settings, is_vs_computer))  # Add a new game instance
        else:
            print("Starting new game screen...")
            game_screen = Screen(name="game_screen")
            game_screen.add_widget(GameScreen(selected_level, self.settings, is_vs_computer))  # Create and add a new game screen
            self.screen_manager.add_widget(game_screen)

        # Transition to the game screen
        self.screen_manager.current = "game_screen"
    
    def exit_game(self, instance):
        print("Exiting the game...")
        App.get_running_app().stop()

class GameScreen(FloatLayout):
    def __init__(self, selected_level, settings, is_vs_computer=False, **kwargs):
        super().__init__(**kwargs)
        self.circle_references = {}
        self.selected_circle = None  # Stores the coordinates of the selected circle
        self.ai_character = None

        # Extract timer settings from the passed configuration
        self.is_vs_computer = is_vs_computer  # Flag for AI mode
        self.settings = settings
        if self.settings["timer_mode"] == "Limited":
            self.player_1_time = self.settings["timer_minutes"] * 60  # Convert minutes to seconds
            self.player_2_time = self.settings["timer_minutes"] * 60  # Convert minutes to seconds
        else:
            self.player_1_time = None  # Unlimited timer
            self.player_2_time = None  # Unlimited timer
        self.active_player = 1  # Start with Player 1

        # Extract grid size from the level
        cols = selected_level["size"][1]  # Number of columns
        rows = selected_level["size"][0]  # Number of rows
        self.cols = cols
        self.rows = rows
        self.board_state = [[0 for _ in range(cols)] for _ in range(rows)]  # 0: Empty, 1: Player 1, 2: Player 2

        # Calculate cell size dynamically, ensuring it fits the screen
        padding = 10  # Optional padding around the grid
        cell_size = min((scr_w - 2 * padding) // cols, (scr_h - 2 * padding) // rows)
        self.cell_size = cell_size

        # Calculate grid dimensions
        grid_width = cell_size * cols
        grid_height = cell_size * rows

        # Adjust the grid position
        offset_x = 200  # Adjust this value as needed
        grid_x = (grid_width / 2) + offset_x  # Move grid slightly to the right
        grid_y = grid_height / 2  # Center vertically
        self.grid_x = grid_x
        self.grid_y = grid_y

        # Layered Background
        with self.canvas.before:
            Color(0, 0, 0, 1)  # Black base
            self.bg_base = Rectangle(size=self.size, pos=self.pos)

            Color(0.1, 0.5, 0.1, 1)  # Green overlay
            self.bg_overlay = Rectangle(size=self.size, pos=self.pos, source="./image/grid_pattern.jpg")

        self.bind(size=self._update_bg, pos=self._update_bg)

        # Clear and Reset Game Functionality
        self.reset_game(selected_level)

        # Calculate initial piece counts from the starting board
        self.player_1_count = sum(cell == 1 for row in selected_level["board"] for cell in row)
        self.player_2_count = sum(cell == 2 for row in selected_level["board"] for cell in row)

        # Add Player 1 text and timer
        self.player_1_label = Label(
            text="Player 1",
            font_size="24sp",
            bold=True,
            color=(1, 0, 0, 1),  # Red for Player 
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

        # Add Player 2 text and timer
        self.player_2_label = Label(
            text="Player 2",
            font_size="24sp",
            bold=True,
            color=(0, 0, 1, 1),  # Blue for Player 1
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

        # Draw the grid (lines)
        with self.canvas:
            Color(0.8, 0.8, 0.8, 1)  # Gray color for grid lines
            for i in range(rows + 1):
                y = grid_y + i * cell_size
                Line(points=[grid_x, y, grid_x + grid_width, y], width=2)
            for j in range(cols + 1):
                x = grid_x + j * cell_size
                Line(points=[x, grid_y, x, grid_y + grid_height], width=2)

        # Add clickable cells
        self.cells = []
        for row_idx in range(rows):
            row = []
            for col_idx in range(cols):
                cell = self.create_cell_widget(row_idx, col_idx, cell_size, grid_x, grid_y)
                row.append(cell)
            self.cells.append(row)

        # Start timer updates
        self.timer_event = Clock.schedule_interval(self.update_timer, 1)
        
        if self.is_vs_computer:
            self.ai_character = AICharacter(self)


    def reset_game(self, selected_level):
        """Reset the game to its initial state."""
        # Clear all cells visually and remove their references
        for (row, col) in list(self.circle_references.keys()):
            self.clear_cell(row, col)

        # Clear circle references and reset board state
        self.circle_references.clear()
        self.board_state = [[0 for _ in range(self.cols)] for _ in range(self.rows)]

        # Redraw the starting positions
        for row_idx, row in enumerate(selected_level["board"]):
            for col_idx, cell_value in enumerate(row):
                if cell_value == 9:  # Untraversable cell
                    self.board_state[row_idx][col_idx] = 9
                    with self.canvas.before:
                        Color(0.5, 0.5, 0.5, 1)  # Gray for untraversable cells
                        Rectangle(
                            pos=(
                                self.grid_x + col_idx * self.cell_size,
                                self.grid_y + row_idx * self.cell_size,
                            ),
                            size=(self.cell_size, self.cell_size),
                        )
                elif cell_value == 1:  # Player 1
                    self.board_state[row_idx][col_idx] = 1
                    self.draw_circle(
                        self.grid_x, self.grid_y, col_idx, row_idx, self.cell_size, (1, 0, 0, 1),
                        is_starting_cell=True, owner=1
                    )
                elif cell_value == 2:  # Player 2
                    self.board_state[row_idx][col_idx] = 2
                    self.draw_circle(
                        self.grid_x, self.grid_y, col_idx, row_idx, self.cell_size, (0, 0, 1, 1),
                        is_starting_cell=True, owner=2
                    )

    def _update_bg(self, *args):
        """Update the background size and position."""
        self.bg_base.size = self.size
        self.bg_base.pos = self.pos
        self.bg_overlay.size = self.size
        self.bg_overlay.pos = self.pos

    def create_cell_widget(self, row, col, cell_size, grid_x, grid_y):
        """Create a clickable area for each cell with hover effects."""
        cell_value = self.board_state[row][col]

        # Untraversable cell
        if cell_value == 9:
            with self.canvas.before:
                Color(0.5, 0.5, 0.5, 1)  # Gray color for untraversable cells
                Rectangle(pos=(grid_x + col * cell_size, grid_y + row * cell_size), size=(cell_size, cell_size))
            return None  # Do not add a clickable widget

        # Traversable cells
        cell_button = Button(
            size_hint=(None, None),
            size=(cell_size, cell_size),
            pos=(grid_x + col * cell_size, grid_y + row * cell_size),
            background_normal="",
            background_color=(0, 0, 0, 0),  # Transparent background
        )
        cell_button.cell_coords = (col, row)  # Assign coordinates to the button

        with cell_button.canvas.before:
            Color(0.2, 0.6, 0.2, 0.5)  # Initial color for traversable cells
            RoundedRectangle(size=cell_button.size, pos=cell_button.pos, radius=[10])

        def hover_effect(instance, touch):
            if instance.collide_point(*touch.pos):
                instance.canvas.before.clear()
                with instance.canvas.before:
                    Color(0.3, 0.8, 0.3, 1)  # Highlight color
                    RoundedRectangle(size=instance.size, pos=instance.pos, radius=[10])

        def unhover_effect(instance, touch):
            instance.canvas.before.clear()
            with instance.canvas.before:
                Color(0.2, 0.6, 0.2, 0.5)  # Reset color
                RoundedRectangle(size=instance.size, pos=instance.pos, radius=[10])

        cell_button.bind(on_touch_down=hover_effect, on_touch_up=unhover_effect)
        cell_button.bind(on_press=self.on_cell_click)
        self.add_widget(cell_button)
        return cell_button

    def draw_circle(self, grid_x, grid_y, col, row, cell_size, color, is_starting_cell=False, owner=None):
        """Draw a circle representing a player's piece with shadow and store detailed references."""
        center_x = grid_x + col * cell_size + cell_size / 2
        center_y = grid_y + row * cell_size + cell_size / 2
        radius = cell_size * 0.4

        with self.canvas:
            # Add shadow
            shadow_color = Color(0, 0, 0, 0.5)  # Shadow color
            shadow = Ellipse(pos=(center_x - radius - 5, center_y - radius - 5), size=(radius * 2, radius * 2))

            # Add circle with color
            circle_color = Color(*color)  # Circle color
            circle = Ellipse(pos=(center_x - radius, center_y - radius), size=(radius * 2, radius * 2))

        # Store the circle, shadow, and additional details
        self.circle_references[(row, col)] = {
            'circle': circle,
            'shadow': shadow,
            'color': circle_color,
            'is_starting_cell': is_starting_cell,
            'owner': owner  # Set the owner for correct validation
        }

    def format_time(self, time_seconds):
        """Format time as MM:SS or 'Unlimited'."""
        if time_seconds is None:
            return ""
        minutes = time_seconds // 60
        seconds = time_seconds % 60
        return f"{minutes:02}:{seconds:02}"

    def update_timer(self, dt):
        """Update the active player's timer."""        
        if self.settings["timer_mode"] == "Unlimited":
            return  # Do nothing if the timer is unlimited
        
        if self.active_player == 1:
            if self.player_1_time > 0:
                self.player_1_time -= 1
                self.player_1_timer.text = self.format_time(self.player_1_time)
            else:
                print("Player 1's time is up!")
                Clock.unschedule(self.update_timer)  # Stop the timer
                self.end_game(winner=2)  # Player 2 wins
        elif self.active_player == 2:
            if self.player_2_time > 0:
                self.player_2_time -= 1
                self.player_2_timer.text = self.format_time(self.player_2_time)
            else:
                print("Player 2's time is up!")
                Clock.unschedule(self.update_timer)  # Stop the timer
                self.end_game(winner=1)  # Player 1 wins

    def on_cell_click(self, instance):
        target_col, target_row = instance.cell_coords  # Get clicked cell's coordinates

        # First click: Select a piece
        if self.selected_circle is None:
            if self.board_state[target_row][target_col] == self.active_player:
                self.selected_circle = (target_row, target_col)
                self.add_glow_effect(target_row, target_col)
                self.add_valid_cell_glow(target_row, target_col)
            else:
                print("Invalid selection: Please select your piece.")
            return

        # Second click: Move the selected piece
        src_row, src_col = self.selected_circle
        distance = max(abs(src_row - target_row), abs(src_col - target_col))

        # Check if the target cell is occupied or an obstacle
        if self.board_state[target_row][target_col] != 0:
            print("Invalid move: Target cell is occupied or blocked.")
            self.remove_glow_effect()  # Remove glowing effect
            self.remove_valid_cell_glow()  # Stop valid cell glow
            self.selected_circle = None  # Deselect the circle
            return

        # Check for valid movement (adjacent or jump)
        if distance == 1:  # Movement
            self.remove_glow_effect()  # Stop glowing
            self.remove_valid_cell_glow()  # Stop valid cell glow
            self.animate_movement(src_row, src_col, target_row, target_col, is_jump=False)
            self.selected_circle = None  # Reset selection
        elif distance == 2:  # Jump
            self.remove_glow_effect()  # Stop glowing
            self.remove_valid_cell_glow()  # Stop valid cell glow
            self.animate_jump(src_row, src_col, target_row, target_col)
            self.selected_circle = None  # Reset selection
        else:
            # Invalid move: Deselect the current piece
            print("Invalid move: Target cell is not valid.")
            self.remove_glow_effect()  # Remove glowing effect
            self.remove_valid_cell_glow()  # Stop valid cell glow
            self.selected_circle = None  # Deselect the circle

    def add_valid_cell_glow(self, row, col):
        """Add glowing effect to valid neighboring cells based on movement rules."""
        self.valid_glow_references = []  # Store references for cleanup

        for target_row in range(self.rows):
            for target_col in range(self.cols):
                # Calculate the distance based on the movement definition
                distance = max(abs(row - target_row), abs(col - target_col))

                # Valid movement: distance of 1 (adjacent) or 2 (jump) and traversable
                if (distance == 1 or distance == 2) and self.board_state[target_row][target_col] == 0:
                    cell_x = self.grid_x + target_col * self.cell_size
                    cell_y = self.grid_y + target_row * self.cell_size

                    # Add a glowing rectangle to highlight the valid cell
                    with self.canvas:
                        Color(1, 1, 0, 0.5)  # Yellow translucent glow
                        glow_rect = RoundedRectangle(
                            pos=(cell_x, cell_y),
                            size=(self.cell_size, self.cell_size),
                            radius=[10]
                        )
                    self.valid_glow_references.append(glow_rect)

    def remove_valid_cell_glow(self):
        """Remove glowing effect from all valid neighboring cells."""
        if not hasattr(self, 'valid_glow_references') or not self.valid_glow_references:
            return

        for glow_rect in self.valid_glow_references:
            self.canvas.remove(glow_rect)

        self.valid_glow_references = []

    def add_glow_effect(self, row, col):
        """Add glowing effect to the selected circle."""
        references = self.circle_references.get((row, col))
        if not references:
            print(f"No circle found at ({row}, {col}) for glowing effect.")
            return

        circle = references['circle']  # The circle itself

        # Animate the translucent glow behind the piece
        with self.canvas:
            Color(1, 1, 1, 0.5)  # White translucent glow
            glow_circle = Ellipse(
                pos=(circle.pos[0] - 10, circle.pos[1] - 10),  # Slightly larger than the circle
                size=(circle.size[0] + 20, circle.size[1] + 20)
            )
        references['glow_circle'] = glow_circle

    def remove_glow_effect(self):
        """Remove glowing effect from the selected circle."""
        if self.selected_circle is None:
            return

        row, col = self.selected_circle
        references = self.circle_references.get((row, col))
        if not references:
            return

        # Remove the translucent glow circle
        glow_circle = references.pop('glow_circle', None)
        if glow_circle:
            self.canvas.remove(glow_circle)

    def complete_move(self, src_row, src_col, target_row, target_col, is_jump):
        """Complete the move by updating the board state and UI."""
        color = (1, 0, 0, 1) if self.active_player == 1 else (0, 0, 1, 1)
        self.draw_circle(self.grid_x, self.grid_y, target_col, target_row, self.cell_size, color)
        self.convert_adjacent_pieces(target_row, target_col)

        # Mark the source cell as unoccupied
        
        if is_jump:
            self.board_state[src_row][src_col] = 0
            self.clear_cell(src_row, src_col)  # Clear the original circle

        self.board_state[target_row][target_col] = self.active_player

        # Update the target cell to the active player
        self.board_state[target_row][target_col] = self.active_player

        sound = SoundLoader.load('./sound/jump.wav' if is_jump else './sound/move.mp3')
        if sound:
            sound.play()

        # Update piece counts and switch turns
        self.update_piece_counts()
        self.switch_turn()
        self.check_game_end()
        
    def convert_adjacent_pieces(self, row, col):
        """Convert all adjacent opponent pieces to the current player's color with animation."""
        opponent = 2 if self.active_player == 1 else 1
        color = (1, 0, 0, 1) if self.active_player == 1 else (0, 0, 1, 1)

        # Define relative positions for adjacent cells
        directions = [
            (-1, 0),  # Up
            (1, 0),   # Down
            (0, -1),  # Left
            (0, 1),   # Right
            (-1, -1), # Top-left
            (-1, 1),  # Top-right
            (1, -1),  # Bottom-left
            (1, 1),   # Bottom-right
        ]

        conversion_happened = False  # Track if any conversions occur

        for d_row, d_col in directions:
            adj_row = row + d_row
            adj_col = col + d_col

            # Check if the adjacent cell is within bounds and contains an opponent piece
            if 0 <= adj_row < self.rows and 0 <= adj_col < self.cols:
                if self.board_state[adj_row][adj_col] == opponent:
                    # Convert opponent piece to the active player's piece
                    self.board_state[adj_row][adj_col] = self.active_player
                    # Animate the conversion
                    self.animate_piece_conversion(adj_row, adj_col, color)
                    conversion_happened = True  # Mark that a conversion occurred
        
        if conversion_happened:
            sound = SoundLoader.load('./sound/conversion.mp3')
            if sound:
                sound.volume = 0.5
                sound.play()

    def animate_piece_conversion(self, row, col, target_color):
        """Animate the color transition of a piece during conversion."""
        references = self.circle_references.get((row, col))
        if not references:
            return  # No circle to animate

        color_instruction = references['color']

        # Define the animation
        anim = Animation(r=target_color[0], g=target_color[1], b=target_color[2], a=target_color[3], duration=0.5)
        
        def finalize_conversion(*_):
            """Finalize the animation to ensure consistency."""
            color_instruction.rgba = target_color

        anim.bind(on_complete=finalize_conversion)
        anim.start(color_instruction)

    def clear_cell(self, row, col):
        """Clear a cell by removing all visual elements, including shadows and circles."""
        # Remove the circle and shadow if they exist in the circle references
        if (row, col) in self.circle_references:
            references = self.circle_references.pop((row, col))
            
            # Remove the circle if it exists
            circle = references.get('circle')
            if circle and circle in self.canvas.children:
                self.canvas.remove(circle)

            # Remove the shadow if it exists
            shadow = references.get('shadow')
            if shadow and shadow in self.canvas.children:
                self.canvas.remove(shadow)

        # Redraw the grid background
        cell_x = self.grid_x + col * self.cell_size
        cell_y = self.grid_y + row * self.cell_size

        with self.canvas.before:
            Color(0, 0, 0, 0)  # Fully transparent
            Rectangle(pos=(cell_x, cell_y), size=(self.cell_size, self.cell_size))

        self.canvas.ask_update()

    def animate_movement(self, src_row, src_col, target_row, target_col, is_jump=False):
        """Animate adjacent movement or jumping, with distinct styles."""
        target_x = self.grid_x + target_col * self.cell_size + self.cell_size / 2
        target_y = self.grid_y + target_row * self.cell_size + self.cell_size / 2

        # Create the circle to animate
        with self.canvas:
            Color(1, 0, 0, 1) if self.active_player == 1 else Color(0, 0, 1, 1)
            moving_circle = Ellipse(pos=(target_x - self.cell_size / 4, target_y - self.cell_size / 4),
                                    size=(self.cell_size / 2, self.cell_size / 2))

        if is_jump:
            # Distinct animation for jumps
            anim = (
                Animation(size=(self.cell_size * 0.6, self.cell_size * 0.6), duration=0.2) +
                Animation(size=(self.cell_size / 2, self.cell_size / 2), duration=0.3)
            )
        else:
            # Simple movement for adjacent pieces
            anim = Animation(pos=(target_x - self.cell_size / 4, target_y - self.cell_size / 4), duration=0.3)

        anim.bind(on_complete=lambda *_: self.complete_move(src_row, src_col, target_row, target_col, is_jump))
        anim.start(moving_circle)

    def animate_jump(self, src_row, src_col, target_row, target_col):
        """Animate a jump based on the selected circle."""
        # if self.selected_circle is None or (src_row, src_col) != self.selected_circle:
        #     print("Error: The source circle does not match the selected circle.")
        #     return

        # Retrieve the source circle's reference
        references = self.circle_references.get((src_row, src_col))
        if not references:
            print(f"No circle found at ({src_row}, {src_col}) to animate jump.")
            return

        # Extract metadata
        src_circle = references['circle']
        src_color = references['color']
        src_owner = references['owner']
        src_x, src_y = src_circle.pos
        src_size = src_circle.size

        # Calculate the target position
        target_x = self.grid_x + target_col * self.cell_size + self.cell_size / 2 - src_size[0] / 2
        target_y = self.grid_y + target_row * self.cell_size + self.cell_size / 2 - src_size[1] / 2

        # Create a temporary circle for the animation
        with self.canvas:
            Color(r=src_color.r, g=src_color.g, b=src_color.b, a=src_color.a)
            jumping_circle = Ellipse(pos=(src_x, src_y), size=src_size)

        # Define the jump animation with a bounce effect
        anim = (
            Animation(pos=(target_x, target_y), duration=0.5, t="out_bounce") +
            Animation(size=src_size, duration=0.2)  # Restore the size after the bounce
        )

        def finalize_jump(*_):
            """Finalize the jump by removing the animated circle and completing the move."""
            # Validate the current circle at the source matches the expected owner and color
            current_references = self.circle_references.get((src_row, src_col))
            if current_references:
                current_color = current_references['color']
                current_owner = current_references['owner']
                # Compare the colors and owner
                if (
                    current_owner == src_owner
                    and current_color.rgba == src_color.rgba
                ):
                    # Clear the source cell if everything matches
                    self.clear_cell(src_row, src_col)
                else:
                    print(
                        f"Skipping removal: Owner or color mismatch for circle at "
                        f"({src_row}, {src_col}). Expected color: {src_color.rgba}, "
                        f"Found color: {current_color.rgba}."
                    )
            else:
                print(f"No current references found at ({src_row}, {src_col}).")

            # Remove the temporary animated circle
            if jumping_circle in self.canvas.children:
                self.canvas.remove(jumping_circle)

            # Complete the move and update the game state
            self.complete_move(src_row, src_col, target_row, target_col, is_jump=True)

        # Bind the animation completion
        anim.bind(on_complete=finalize_jump)
        anim.start(jumping_circle)

    def switch_turn(self):
        """Switch to the other player and ensure UI reflects the correct active player."""
        if self.active_player == 1:
            self.active_player = 2
            # Update label colors
            self.player_1_label.color = (0.5, 0.5, 0.5, 1)  # Dim Player 1
            self.player_2_label.color = (0, 0, 1, 1)  # Highlight Player 2
            if self.is_vs_computer:
                Clock.schedule_once(lambda dt: self.trigger_ai_move(), 1.5)
        else:
            self.active_player = 1
            # Update label colors
            self.player_2_label.color = (0.5, 0.5, 0.5, 1)  # Dim Player 2
            self.player_1_label.color = (1, 0, 0, 1)  # Highlight Player 1
        
        # Debug: Print the current active player for verification
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

        move = self.ai.get_action(state, valid_moves)
        src_row, src_col, target_row, target_col = move

        # Apply the move
        distance = max(abs(src_row - target_row), abs(src_col - target_col))
        if distance == 1:
            self.animate_movement(src_row, src_col, target_row, target_col, is_jump=False)
        elif distance == 2:
            self.animate_jump(src_row, src_col, target_row, target_col)

        # Update the board state
        self.board_state = self.ai.apply_move(self.board_state, move)

        # Calculate reward (e.g., difference in piece count)
        reward = self.calculate_reward()

        # Remember the move for learning
        next_state = self.ai.get_state(self.board_state)
        done = self.check_game_end()
        self.ai.remember(state, move, reward, next_state, done)

        # Train the model
        self.ai.replay(32)

        result = self.calculate_ai_result()  # Implement this method to determine the AI's performance
        if self.ai_character:
            self.ai_character.evaluate_outcome(result)
    
    def calculate_ai_result(self):
        # Implement logic to determine if AI is winning, losing, or drawing
        ai_pieces = sum(row.count(2) for row in self.board_state)
        player_pieces = sum(row.count(1) for row in self.board_state)
        return ai_pieces - player_pieces


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
                if self.board_state[row][col] == 2:  # AI's pieces
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
        """Update the piece count labels for each player."""
        player_1_count = sum(cell == 1 for row in self.board_state for cell in row)
        player_2_count = sum(cell == 2 for row in self.board_state for cell in row)
        self.player_1_piece_count.text = f"Pieces: {player_1_count}"
        self.player_2_piece_count.text = f"Pieces: {player_2_count}"
    
    def check_game_end(self):
        """Check if the game should end based on the conditions."""
        # Count the number of pieces for each player
        player_1_count = sum(cell == 1 for row in self.board_state for cell in row)
        player_2_count = sum(cell == 2 for row in self.board_state for cell in row)

        # Check if a player has no pieces left
        if player_1_count == 0:
            self.end_game(winner=2)  # Player 2 wins
            return
        elif player_2_count == 0:
            self.end_game(winner=1)  # Player 1 wins
            return

        # Check if all remaining pieces belong to one player
        total_pieces = player_1_count + player_2_count
        total_cells = sum(cell != 9 for row in self.board_state for cell in row)  # Exclude untraversable cells
        if player_1_count == total_cells or player_2_count == total_cells:
            winner = 1 if player_1_count == total_cells else 2
            self.end_game(winner=winner)
            return

        # Check if no valid moves exist for either player
        if not self.has_valid_moves(1) and not self.has_valid_moves(2):
            # Determine winner by piece count
            winner = 1 if player_1_count > player_2_count else 2
            self.end_game(winner=winner)


    def has_valid_moves(self, player):
        """Check if the given player has any valid moves."""
        directions = [
            (-1, 0), (1, 0), (0, -1), (0, 1),  # Adjacent
            (-2, 0), (2, 0), (0, -2), (0, 2),  # Jumps
            (-1, -1), (-1, 1), (1, -1), (1, 1),  # Diagonal adjacent
            (-2, -2), (-2, 2), (2, -2), (2, 2),  # Diagonal jumps
        ]
        for row_idx, row in enumerate(self.board_state):
            for col_idx, cell in enumerate(row):
                if cell == player:
                    for d_row, d_col in directions:
                        target_row = row_idx + d_row
                        target_col = col_idx + d_col
                        if 0 <= target_row < self.rows and 0 <= target_col < self.cols:
                            if self.board_state[target_row][target_col] == 0:  # Empty cell
                                return True
        return False

    def end_game(self, winner):
        """Switch to the end game screen and display the winner."""
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
        self.remaining_time = 10  # Countdown duration

        # Background
        with self.canvas.before:
            Color(0, 0, 0, 1)
            self.bg_base = Rectangle(size=self.size, pos=self.pos)
            Color(0.1, 0.5, 0.1, 1)
            self.bg_overlay = Rectangle(size=self.size, pos=self.pos, source="./image/grid_pattern.jpg")
        self.bind(size=self._update_bg, pos=self._update_bg)

        # Game Over Label
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

        # Winner Label
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

        # Timer Label
        self.timer_label = Label(
            text=f"Returning to the main start screen in {self.remaining_time} seconds",
            font_size="20sp",
            color=(1, 1, 1, 1),
            size_hint=(None, None),
            pos_hint={"center_x": 0.5, "center_y": 0.3},
        )
        self.add_widget(self.timer_label)

        # Start Timer
        Clock.schedule_interval(self.update_timer, 1)

    def animate_label(self, label, light_color, dark_color):
        anim = Animation(color=light_color, duration=0.7) + Animation(color=dark_color, duration=0.7)
        anim.repeat = True
        anim.start(label)

    def update_timer(self, dt):
        """Update the countdown timer and return to the start screen when time runs out."""
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
        self.grid = [[0 for _ in range(cols)] for _ in range(rows)]  # 0: Empty, 1: Player 1, etc.
        self.ataxx_start_screen = ataxx_start_screen  # Reference to the start screen

        # Use the same background as GameScreen
        with self.canvas.before:
            Color(0, 0, 0, 1)  # Black base
            self.bg_base = Rectangle(size=self.size, pos=self.pos)
            Color(0.1, 0.5, 0.1, 1)  # Green overlay
            self.bg_overlay = Rectangle(size=self.size, pos=self.pos, source="./image/grid_pattern.jpg")
        self.bind(size=self._update_bg, pos=self._update_bg)

        # Calculate grid dimensions and positioning
        padding = 10  # Optional padding
        cell_size = min((scr_w - 2 * padding) // cols, (scr_h - 2 * padding) // rows)
        self.cell_size = cell_size

        grid_width = cell_size * cols
        grid_height = cell_size * rows
        offset_x = 200  # Adjust as needed
        self.grid_x = (grid_width / 2) + offset_x
        self.grid_y = grid_height / 2

        # Draw the grid with lighting
        self.draw_grid_with_lighting()

        # Add buttons
        self.add_widget(self.create_button("Back to Start", self.go_back, 0.3))
        self.add_widget(self.create_button("Save Level", self.save_level, 0.7))
        self.show_description_popup()
        
    def _update_bg(self, *args):
        """Update the background size and position."""
        self.bg_base.size = self.size
        self.bg_base.pos = self.pos
        self.bg_overlay.size = self.size
        self.bg_overlay.pos = self.pos
    
    def show_description_popup(self):
        """Display a popup with instructions and level requirements."""
        # Popup content layout
        content = BoxLayout(orientation="vertical", padding=20, spacing=10)

        # Add instructions
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
            text_size=(600, None),  # Wrap text within the popup width
            size_hint_y=None
        )
        instructions.bind(texture_size=lambda instance, value: setattr(instructions, 'height', value[1]))  # Dynamic height
        content.add_widget(instructions)

        # Add "OK" button to dismiss the popup
        ok_button = Button(
            text="OK",
            size_hint=(1, None),
            height=50,
            background_color=(0.2, 0.8, 0.2, 1)
        )
        content.add_widget(ok_button)

        # Create the popup
        popup = Popup(
            title="Level Creation Instructions",
            content=content,
            size_hint=(0.8, 0.7),  # Adjusted size for better content fitting
            auto_dismiss=False  # Prevent accidental dismissal
        )

        # Bind the "OK" button to close the popup
        ok_button.bind(on_press=popup.dismiss)

        # Open the popup
        popup.open()

    def draw_grid_with_lighting(self):
        """Draw the grid lines with a light green glow effect."""
        with self.canvas:
            # Light green glow behind the grid
            Color(0.1, 1, 0.1, 0.2)  # Light green with transparency
            for i in range(self.rows + 1):
                y = self.grid_y + i * self.cell_size
                Line(points=[self.grid_x, y, self.grid_x + self.cols * self.cell_size, y], width=5)  # Glowing lines
            for j in range(self.cols + 1):
                x = self.grid_x + j * self.cell_size
                Line(points=[x, self.grid_y, x, self.grid_y + self.rows * self.cell_size], width=5)

            # Main grid lines
            Color(0.8, 0.8, 0.8, 1)  # Light gray for grid lines
            for i in range(self.rows + 1):
                y = self.grid_y + i * self.cell_size
                Line(points=[self.grid_x, y, self.grid_x + self.cols * self.cell_size, y], width=2)
            for j in range(self.cols + 1):
                x = self.grid_x + j * self.cell_size
                Line(points=[x, self.grid_y, x, self.grid_y + self.rows * self.cell_size], width=2)

        # Add clickable cells
        for row in range(self.rows):
            for col in range(self.cols):
                cell_button = Button(
                    size_hint=(None, None),
                    size=(self.cell_size, self.cell_size),
                    pos=(self.grid_x + col * self.cell_size, self.grid_y + row * self.cell_size),
                    background_normal="",
                    background_color=(0, 0, 0, 0),  # Transparent button
                )
                cell_button.bind(on_press=lambda instance, r=row, c=col: self.toggle_cell(r, c))
                self.add_widget(cell_button)

    def toggle_cell(self, row, col):
        """
        Toggle cell state between:
        0: Empty (Traversable), 1: Player 1 (Blue Circle), 
        2: Player 2 (Red Circle), 3: Non-Traversable (Gray Block).
        """
        current_state = self.grid[row][col]
        new_state = (current_state + 1) % 4  # Cycle through states
        self.grid[row][col] = new_state  # Update the grid state

        # Calculate cell position
        x = self.grid_x + col * self.cell_size
        y = self.grid_y + row * self.cell_size
        radius = self.cell_size * 0.4

        with self.canvas:
            # Clear the specific cell area
            Color(0, 0, 0, 1)  # Black background for clearing
            Rectangle(pos=(x, y), size=(self.cell_size, self.cell_size))
            print(new_state)
            # Draw the new state
            if new_state == 1:  # Player 1 (Blue Circle)
                Color(0, 0, 1, 1)
                Ellipse(pos=(x + self.cell_size / 2 - radius, y + self.cell_size / 2 - radius),
                        size=(radius * 2, radius * 2))
            elif new_state == 2:  # Player 2 (Red Circle)
                Color(1, 0, 0, 1)
                Ellipse(pos=(x + self.cell_size / 2 - radius, y + self.cell_size / 2 - radius),
                        size=(radius * 2, radius * 2))
            elif new_state == 3:  # Non-Traversable (Gray Block)
                Color(0.5, 0.5, 0.5, 1)
                Rectangle(pos=(x, y), size=(self.cell_size, self.cell_size))
            
        # Play the sound effect
        sound = SoundLoader.load('./sound/change-item.mp3')
        if sound:
            sound.volume = 0.5  # Set the volume (0.0 to 1.0)
            sound.play()
        else:
            print("Failed to load sound: change-item.mp3")

    def clear_visual_cell(self, x, y):
        """Clear any visual elements in the cell."""
        with self.canvas.before:
            Color(0, 0, 0, 0)  # Transparent color
            Rectangle(pos=(x, y), size=(self.cell_size, self.cell_size))

    def create_button(self, text, callback, x_position):
        """Create a styled button with consistent coloring and glow effect."""
        button_layout = BoxLayout(
            size_hint=(None, None),
            size=(200, 50),
            pos_hint={"center_x": x_position, "center_y": 0.1}
        )
        with button_layout.canvas.before:
            button_layout.bg_color = Color(0.2, 0.6, 0.2, 1)  # Initial color for the button background
            button_layout.bg_rect = RoundedRectangle(size=button_layout.size, pos=button_layout.pos, radius=[10])
        button_layout.bind(
            size=lambda instance, value: setattr(button_layout.bg_rect, 'size', value),
            pos=lambda instance, value: setattr(button_layout.bg_rect, 'pos', value)
        )

        # Create the button itself
        btn = Button(
            text=text,
            font_size="16sp",
            background_normal="",
            background_color=(0, 0, 0, 0),  # Transparent background
            color=(1, 1, 1, 1),  # Button text color
        )
        btn.bind(on_press=callback)

        # Add glow animation to the button and background
        self.animate_button_and_background(btn, button_layout.bg_color)

        button_layout.add_widget(btn)
        return button_layout

    def animate_button_and_background(self, button, bg_color):
        """Animate the button and its background color to create a glow effect."""
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
        """Validate the level constraints and save the level if valid."""
        # Constraint validation
        def validate_constraints(grid):
            player1_count = sum(cell == 1 for row in grid for cell in row)
            player2_count = sum(cell == 2 for row in grid for cell in row)
            empty_count = sum(cell == 0 for row in grid for cell in row)

            # Each player must have at least one piece
            if player1_count == 0 or player2_count == 0:
                return "Each player must have at least one starting piece."
            # Player counts must match
            if player1_count != player2_count:
                return "Player 1 and Player 2 must have the same number of starting pieces."
            # There must be at least one empty cell
            if empty_count == 0:
                return "The level must have at least one empty (traversable) cell."
            return None  # Valid

        # Check constraints
        error_message = validate_constraints(self.grid)
        if error_message:
            self.show_error_popup(error_message)
            return

        # Open the save level popup if constraints are met
        self.open_save_level_popup()

    def show_error_popup(self, error_message):
        """Display an error message popup."""
        content = BoxLayout(orientation="vertical", spacing=10, padding=10)
        content.add_widget(Label(text=error_message, font_size="16sp", halign="center", valign="middle"))
        ok_button = Button(text="OK", size_hint=(1, None), height=50, background_color=(0.8, 0.2, 0.2, 1))
        content.add_widget(ok_button)

        # Create the popup
        popup = Popup(
            title="Invalid Level",
            content=content,
            size_hint=(0.8, 0.4),
            auto_dismiss=False
        )

        # Close popup on OK button press
        ok_button.bind(on_press=popup.dismiss)
        popup.open()

        sound = SoundLoader.load('./sound/error.mp3')
        if sound:
            sound.volume = 0.5  # Set the volume (0.0 to 1.0)
            sound.play()
        else:
            print("Failed to load sound: change-item.mp3")


    def open_save_level_popup(self):
        """Open the popup to save the level."""
        # Popup content
        content = BoxLayout(orientation="vertical", spacing=10)

        # Text input for the level name
        level_name_input = TextInput(
            hint_text="Enter level name",
            multiline=False,
            size_hint=(1, None),
            height=44
        )
        content.add_widget(level_name_input)

        # Buttons for save and cancel
        button_layout = BoxLayout(orientation="horizontal", spacing=10, size_hint=(1, None), height=50)
        cancel_button = Button(text="Cancel", background_color=(0.8, 0.2, 0.2, 1))
        save_button = Button(text="Save", background_color=(0.2, 0.8, 0.2, 1))
        button_layout.add_widget(cancel_button)
        button_layout.add_widget(save_button)
        content.add_widget(button_layout)

        # Create the popup
        popup = Popup(
            title="Save Level",
            content=content,
            size_hint=(0.8, 0.2),
            auto_dismiss=False
        )

        # Cancel button closes the popup
        cancel_button.bind(on_press=popup.dismiss)

        def save_level_to_file(instance):
            """Save the level to a file and show a success message."""
            level_name = level_name_input.text.strip()
            if not level_name:
                self.show_error_popup("Level name cannot be empty.")
                return

            # Convert grid values and save the level
            converted_grid = [[9 if cell == 3 else cell for cell in row] for row in self.grid]
            new_level = {"name": level_name, "size": [self.rows, self.cols], "board": converted_grid}

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

            # Show success popup
            self.show_success_popup(level_name)

        # Bind save functionality
        save_button.bind(on_press=save_level_to_file)
        popup.open()
    
    def show_success_popup(self, level_name):
        """Display a success message popup after saving a level."""
        content = BoxLayout(orientation="vertical", spacing=10, padding=10)
        success_message = (
            f"Level '{level_name}' has been successfully saved.\n"
            "It is now playable and can be selected in the Configuration Settings."
        )
        content.add_widget(Label(text=success_message, font_size="16sp", halign="center", valign="middle"))
        
        # OK button to dismiss the popup
        ok_button = Button(
            text="OK",
            size_hint=(1, None),
            height=50,
            background_color=(0.2, 0.8, 0.2, 1)
        )
        content.add_widget(ok_button)

        # Create and display the popup
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
        """Navigate back to the start screen."""
        screen_manager = App.get_running_app().root  # Get the ScreenManager
        if screen_manager:
            screen_manager.current = "start_screen"
        else:
            print("Error: ScreenManager not found!")
    
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