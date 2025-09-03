import tkinter as tk
import time
import random

class GameOfLife:
    """
    Implements Conway's Game of Life using the Tkinter library for the graphical interface.
    """
    def __init__(self, canvas_width, canvas_height, cell_size=10):
        """
        Initializes the Game of Life application window and board.

        Args:
            canvas_width (int): The width of the canvas in pixels.
            canvas_height (int): The height of the canvas in pixels.
            cell_size (int, optional): The size of each cell in pixels. Defaults to 10.
        """
        # Window setup
        self.root = tk.Tk()
        self.root.title("Conway's Game of Life")

        # Game parameters
        self.canvas_width = canvas_width
        self.canvas_height = canvas_height
        self.cell_size = cell_size
        self.columns = self.canvas_width // self.cell_size
        self.rows = self.canvas_height // self.cell_size
        self.running = False
        self.speed_ms = 100  # Update speed in milliseconds

        # UI elements
        self.canvas = tk.Canvas(self.root, width=self.canvas_width, height=self.canvas_height, bg="white")
        self.canvas.pack()
        self.canvas.bind("<Button-1>", self.toggle_cell)

        button_frame = tk.Frame(self.root)
        button_frame.pack()

        self.start_button = tk.Button(button_frame, text="Start", command=self.start)
        self.start_button.pack(side=tk.LEFT)

        self.stop_button = tk.Button(button_frame, text="Stop", command=self.stop)
        self.stop_button.pack(side=tk.LEFT)

        self.reset_button = tk.Button(button_frame, text="Reset", command=self.create_board)
        self.reset_button.pack(side=tk.LEFT)

        # Game state
        self.board = self.create_board()
        self.draw_board()

    def create_board(self, initial_state="random"):
        """
        Creates or resets the game board with a new set of cells.

        Args:
            initial_state (str, optional): The initial state of the board.
                Can be "random" or "empty". Defaults to "random".

        Returns:
            list: A 2D list representing the game board.
        """
        board = [[0 for _ in range(self.columns)] for _ in range(self.rows)]
        if initial_state == "random":
            for y in range(self.rows):
                for x in range(self.columns):
                    if random.random() < 0.2:  # 20% chance of being alive
                        board[y][x] = 1
        self.board = board
        self.draw_board()
        return self.board

    def toggle_cell(self, event):
        """
        Toggles the state of a cell (alive/dead) when the user clicks on the canvas.

        Args:
            event (tk.Event): The click event object.
        """
        if not self.running:
            x = event.x // self.cell_size
            y = event.y // self.cell_size
            if 0 <= x < self.columns and 0 <= y < self.rows:
                self.board[y][x] = 1 - self.board[y][x]  # Toggle 0 to 1, or 1 to 0
                self.draw_board()

    def calculate_next_generation(self):
        """
        Calculates the state of the next generation of the board based on the rules
        of Conway's Game of Life.
        """
        next_board = [[0 for _ in range(self.columns)] for _ in range(self.rows)]
        for y in range(self.rows):
            for x in range(self.columns):
                alive_neighbors = self.count_alive_neighbors(x, y)
                current_cell_state = self.board[y][x]

                if current_cell_state == 1:
                    # An alive cell with 2 or 3 neighbors stays alive.
                    if alive_neighbors == 2 or alive_neighbors == 3:
                        next_board[y][x] = 1
                    else:
                        # An alive cell dies from underpopulation (<2) or overpopulation (>3).
                        next_board[y][x] = 0
                else:
                    # A dead cell with exactly 3 neighbors becomes alive (reproduction).
                    if alive_neighbors == 3:
                        next_board[y][x] = 1
                    else:
                        # A dead cell remains dead.
                        next_board[y][x] = 0
        self.board = next_board

    def count_alive_neighbors(self, x, y):
        """
        Counts the number of alive neighbors for a given cell.

        Args:
            x (int): The x-coordinate (column) of the cell.
            y (int): The y-coordinate (row) of the cell.

        Returns:
            int: The number of alive neighbors.
        """
        alive_neighbors = 0
        for i in range(-1, 2):
            for j in range(-1, 2):
                if i == 0 and j == 0:
                    continue
                neighbor_x = x + j
                neighbor_y = y + i
                if 0 <= neighbor_x < self.columns and 0 <= neighbor_y < self.rows:
                    if self.board[neighbor_y][neighbor_x] == 1:
                        alive_neighbors += 1
        return alive_neighbors

    def draw_board(self):
        """
        Draws the current state of the board on the canvas.
        """
        self.canvas.delete("all")
        for y in range(self.rows):
            for x in range(self.columns):
                if self.board[y][x] == 1:
                    x1 = x * self.cell_size
                    y1 = y * self.cell_size
                    x2 = x1 + self.cell_size
                    y2 = y1 + self.cell_size
                    self.canvas.create_rectangle(x1, y1, x2, y2, fill="black", outline="gray")
                else:
                    x1 = x * self.cell_size
                    y1 = y * self.cell_size
                    x2 = x1 + self.cell_size
                    y2 = y1 + self.cell_size
                    self.canvas.create_rectangle(x1, y1, x2, y2, fill="white", outline="gray")

    def start(self):
        """Starts the game simulation."""
        if not self.running:
            self.running = True
            self.update()

    def stop(self):
        """Stops the game simulation."""
        self.running = False

    def update(self):
        """
        Updates the game state and redraws the board. This method is called repeatedly
        to drive the simulation.
        """
        if self.running:
            self.calculate_next_generation()
            self.draw_board()
            self.root.after(self.speed_ms, self.update)

    def run(self):
        """Starts the main Tkinter event loop."""
        self.root.mainloop()

if __name__ == "__main__":
    game = GameOfLife(350, 250, cell_size=4)
    game.run()
