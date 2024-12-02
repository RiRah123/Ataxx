import numpy as np
import random
from collections import deque
from kivy.uix.image import Image
from kivy.core.audio import SoundLoader

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
