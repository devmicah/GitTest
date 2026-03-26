import sys
import random
import time
import os
from collections import deque
import threading

class SnakeGame:
    def __init__(self, width=20, height=15):
        self.width = width
        self.height = height
        self.snake = deque([(height // 2, width // 2)])
        self.direction = (0, 1)  # Start moving right
        self.food = self.generate_food()
        self.score = 0
        self.game_over = False
        self.paused = False
        
    def generate_food(self):
        while True:
            food = (random.randint(1, self.height - 2), random.randint(1, self.width - 2))
            if food not in self.snake:
                return food
    
    def move(self):
        if self.paused:
            return
            
        head = self.snake[0]
        new_head = (head[0] + self.direction[0], head[1] + self.direction[1])
        
        # Check collision with walls
        if (new_head[0] <= 0 or new_head[0] >= self.height - 1 or
            new_head[1] <= 0 or new_head[1] >= self.width - 1):
            self.game_over = True
            return
        
        # Check collision with self
        if new_head in self.snake:
            self.game_over = True
            return
        
        self.snake.appendleft(new_head)
        
        # Check if food is eaten
        if new_head == self.food:
            self.score += 10
            self.food = self.generate_food()
        else:
            self.snake.pop()
    
    def change_direction(self, new_direction):
        # Prevent reversing direction
        if (new_direction[0] * -1, new_direction[1] * -1) != self.direction:
            self.direction = new_direction
    
    def render(self):
        # Clear screen (works on Unix and Windows)
        os.system('clear' if os.name == 'posix' else 'cls')
        
        # Create game board
        board = [[' ' for _ in range(self.width)] for _ in range(self.height)]
        
        # Draw borders
        for i in range(self.height):
            board[i][0] = '█'
            board[i][self.width - 1] = '█'
        for j in range(self.width):
            board[0][j] = '█'
            board[self.height - 1][j] = '█'
        
        # Draw snake
        for i, segment in enumerate(self.snake):
            if i == 0:
                board[segment[0]][segment[1]] = '●'  # Head
            else:
                board[segment[0]][segment[1]] = '○'  # Body
        
        # Draw food
        board[self.food[0]][self.food[1]] = '★'
        
        # Print board
        for row in board:
            print(''.join(row))
        
        print(f"\nScore: {self.score}")
        print("Controls: w=up, s=down, a=left, d=right, q=quit")
        print("Don't hit the walls or yourself!")
        if self.paused:
            print("\n*** PAUSED - Press any direction key to continue ***")

# Global variables for input handling
current_input = None
input_lock = threading.Lock()

def input_thread():
    """Thread to handle keyboard input"""
    global current_input
    try:
        # Try to use getch for better input handling
        try:
            import msvcrt
            # Windows
            while True:
                if msvcrt.kbhit():
                    key = msvcrt.getch().decode('utf-8').lower()
                    with input_lock:
                        current_input = key
                time.sleep(0.01)
        except ImportError:
            # Unix-like systems
            import tty
            import termios
            fd = sys.stdin.fileno()
            old_settings = termios.tcgetattr(fd)
            try:
                tty.setcbreak(fd)
                while True:
                    key = sys.stdin.read(1).lower()
                    with input_lock:
                        current_input = key
            finally:
                termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
    except:
        # Fallback to simple input
        while True:
            try:
                key = input().lower()
                if key:
                    with input_lock:
                        current_input = key[0]
            except:
                break

def main():
    global current_input
    
    print("=" * 50)
    print("Welcome to Snake Game!")
    print("=" * 50)
    print("\nControls:")
    print("  w = Move Up")
    print("  s = Move Down")
    print("  a = Move Left")
    print("  d = Move Right")
    print("  q = Quit Game")
    print("\nPress Enter to start...")
    input()
    
    game = SnakeGame()
    
    # Start input thread
    input_handler = threading.Thread(target=input_thread, daemon=True)
    input_handler.start()
    
    last_move_time = time.time()
    move_delay = 0.15  # Seconds between moves
    
    try:
        while not game.game_over:
            game.render()
            
            # Check for input
            with input_lock:
                if current_input:
                    key = current_input
                    current_input = None
                    
                    if key == 'q':
                        print("\nGame quit by user.")
                        return
                    elif key == 'w':
                        game.change_direction((-1, 0))
                        game.paused = False
                    elif key == 's':
                        game.change_direction((1, 0))
                        game.paused = False
                    elif key == 'a':
                        game.change_direction((0, -1))
                        game.paused = False
                    elif key == 'd':
                        game.change_direction((0, 1))
                        game.paused = False
            
            # Move snake if enough time has passed
            current_time = time.time()
            if current_time - last_move_time >= move_delay:
                game.move()
                last_move_time = current_time
            
            time.sleep(0.01)  # Small delay to prevent CPU spinning
        
        # Game over
        game.render()
        print("\n" + "="*game.width)
        print("GAME OVER!")
        print(f"Final Score: {game.score}")
        print("="*game.width)
        
    except KeyboardInterrupt:
        print("\n\nGame interrupted. Thanks for playing!")

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"\nAn error occurred: {e}")
        import traceback
        traceback.print_exc()

# Made with Bob
