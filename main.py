# Classical game from the github repossitory recreational mathematics with python by beltoforion
# https://github.com/beltoforion/recreational_mathematics_with_python/tree/master
# Quantum version added and inspired by hackaton 2019

import pygame
import numpy as np

col_about_to_die = (200, 200, 225)
col_alive = (255, 255, 215)
col_background = (10, 10, 40)
col_grid = (30, 30, 60)

# Patterns
# This is just so we have something consistent to start with, right now all patterns start at the top_leftm
# but we can obviously change this later on
patterns = {
    "glider": np.array([[0,1,0],[0,0,1],[1,1,1]]),
    "blinker": np.array([[1,1,1]]),
    "gosper_glider_gun": np.array([
        [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,0,0,0,0,0,0,0,0,0,0,0,0,0],
        [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,0,1,0,0,0,0,0,0,0,0,0,0,0,0,0],
        [0,0,0,0,0,0,0,0,0,0,0,0,1,1,0,0,0,0,0,0,1,1,0,0,0,0,0,0,0,0,0,0,0,0,1,1,0,0],
        [0,0,0,0,0,0,0,0,0,0,0,1,0,0,0,1,0,0,0,0,1,1,0,0,0,0,0,0,0,0,0,0,0,0,1,1,0,0],
        [1,1,0,0,0,0,0,0,0,0,1,0,0,0,0,0,1,0,0,0,1,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
        [1,1,0,0,0,0,0,0,0,0,1,0,0,0,1,0,1,1,0,0,0,0,1,0,1,0,0,0,0,0,0,0,0,0,0,0,0,0],
        [0,0,0,0,0,0,0,0,0,0,1,0,0,0,0,0,1,0,0,0,0,0,0,0,1,0,0,0,0,0,0,0,0,0,0,0,0,0],
        [0,0,0,0,0,0,0,0,0,0,0,1,0,0,0,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
        [0,0,0,0,0,0,0,0,0,0,0,0,1,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0]
    ])
}

# Place classical pattern
def place_pattern(cells, pattern_name, top_left):
    pattern = patterns[pattern_name]
    y, x = top_left
    cells[y:y+pattern.shape[0], x:x+pattern.shape[1]] = pattern

# Place quantum pattern (superposition)
# Each cell is represented by a superposition of two complex amplitudes: alive_amp and dead_amp
# The probability of a cell being alive is |alive_amp|^2 and the probability of a cell being dead is |dead_amp|^2
# To maintain a valid quantum superposition, these probabilities need to sum to 1.
# In this function we initialize cells according to the given pattern: alive cells get an amlitude of pattern/sqrt(2)
# This is a simple starting point to get a 50/50 superposition since (1/sqrt(2))^2 = 1/2
def place_pattern_quantum(dead_amp, alive_amp, pattern_name, top_left):
    pattern = patterns[pattern_name]
    y, x = top_left
    alive_amp[y:y+pattern.shape[0], x:x+pattern.shape[1]] = pattern / np.sqrt(2)
    dead_amp[y:y+pattern.shape[0], x:x+pattern.shape[1]] = np.sqrt(1 - (pattern/np.sqrt(2))**2)

# Classical update
# This function updates the grid of cells according to Conway's Game of Life rules and draws cells
def update_classical(surface, cur, sz):
    nxt = np.zeros_like(cur)
    for r, c in np.ndindex(cur.shape): # iterate over all (row, column) positions in the grid
        num_alive = np.sum(cur[r-1:r+2, c-1:c+2]) - cur[r, c] # count alive neighbors
        # Apply classical GoL rules
        if cur[r, c] == 1 and (num_alive < 2 or num_alive > 3):
            col = col_about_to_die
        elif (cur[r, c] == 1 and 2 <= num_alive <= 3) or (cur[r, c] == 0 and num_alive == 3):
            nxt[r, c] = 1
            col = col_alive
        else:
            col = col_background
        # Draw the cell
        pygame.draw.rect(surface, col, (c*sz, r*sz, sz-1, sz-1))
    # Return the next state
    return nxt

# Quantum update (probabilistic, simple)
# Each cell has a superposition with alive_amp (amplitude to be alive) and dead_amp (amplitude to be dead)
# Uses the squared magnitude of amplitudes to determine a probabilistic number of alive neighbors
# Updates each cell to a new amplitude based on a simple quantum-inspired rule
def update_quantum(surface, alive_amp, dead_amp, sz):
    # Initialize new amplitude arrays, these will store the updated amplitudes for the next generation
    nxt_alive = np.zeros_like(alive_amp, dtype=complex)
    nxt_dead = np.zeros_like(dead_amp, dtype=complex)

    # The alive_amp looks something like this:
    #   [[0.707, 0, 0.707],
    #   [0, 0, 0],
    #   [0.707, 0, 0.707]]
    # This is the current state of the quantum grid
    # In this case the loop goes through 9 tuples of row and column coordinates in the grid.
    for r, c in np.ndindex(alive_amp.shape):
        # Loop through the grid and calculate probability of cell being alive.
        p_alive = np.abs(alive_amp[r, c])**2
        # Select a 3 x 3 block centered on (r,c)
        # Does not yet deal with wrapping and edge cases
        neighbors = alive_amp[r-1:r+2, c-1:c+2]
        # Compute array of alive probabilities of all 9 cells in the block
        # Sum these probabilities and remove the center cell, leaving only the neighbors
        # So this is the expected number of alive neighbors in a probabilistic sense
        num_alive_prob = np.sum(np.abs(neighbors)**2) - p_alive

        # Simple quantum-inspired Life rule
        # This decides how the current cell should evolve based on the expected number of alive neighbors
        # Case where the expected number of alive neighbors is 2 or 3
        # In classical game a cell survives if it has 2 or 3 alive neighbors, otherwise it dies. Instead we use
        # probabilities, just a simple starting case.
        if 2 <= num_alive_prob <= 3:
            nxt_alive[r, c] = np.sqrt(0.8) # High probability of being alive in the next step
            nxt_dead[r, c] = np.sqrt(0.2) # Low probability of being dead in the next step
            col = col_alive
        # Sets a low amplitude for being alive in the next step and a high for being dead.
        else:
            nxt_alive[r, c] = np.sqrt(0.2)
            nxt_dead[r, c] = np.sqrt(0.8)
            # If the cell was more likely alive now, use the about to die color, otherwise background for dead cells
            # So if probability of cell being alive before is higher than being dead the cell is about to die in this
            # case and otherwise probability of staying dead.
            col = col_about_to_die if p_alive>0.5 else col_background

        pygame.draw.rect(surface, col, (c*sz, r*sz, sz-1, sz-1))

    return nxt_alive, nxt_dead

# Main loop
def main():
    dimx, dimy, cellsize = 100, 70, 8
    # Ask the user whether to run classical or quantum GoL and show available predefined patterns
    # For now only working with some example patterns since this is just a first setup
    mode = input("Choose mode: [C]lassical or [Q]uantum: ").upper()
    print("Available patterns:", ", ".join(patterns.keys()))
    pattern_name = input("Choose a pattern to place: ").lower()
    # Initialize Pygame, set window title and initialize surface (drawing area)
    pygame.init()
    surface = pygame.display.set_mode((dimx*cellsize, dimy*cellsize))
    pygame.display.set_caption("Game of Life - Classical / Quantum")
    # Initialize the grid depending on classical or quantum mode
    if mode == "C":
        cells = np.zeros((dimy, dimx))
        place_pattern(cells, pattern_name, (1,1))
    else:
        alive_amp = np.zeros((dimy, dimx), dtype=complex)
        dead_amp = np.ones((dimy, dimx), dtype=complex)
        place_pattern_quantum(dead_amp, alive_amp, pattern_name, (1,1))
    # Main loop setup
    running = True
    clock = pygame.time.Clock() # used to control frame rate
    # Main loop
    # Keeps the simulation running until user closes window
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        surface.fill(col_grid)
        # Update cells
        if mode == "C":
            cells = update_classical(surface, cells, cellsize)
        else:
            alive_amp, dead_amp = update_quantum(surface, alive_amp, dead_amp, cellsize)

        pygame.display.update()
        clock.tick(10)  # control speed

    pygame.quit()

if __name__ == "__main__":
    main()