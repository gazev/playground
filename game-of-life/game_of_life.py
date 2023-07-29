import pygame
from os import sys

import numpy as np

from config import *
from colors import *

class GameOfLife:
    def __init__(self):
        pygame.init()
        pygame.display.set_caption("Game of Life")

        # attributes
        self._running = False
        self.width, self.height = WIDTH, HEIGTH
        self.nr_blobs = self.width / BLOB_SIZE * self.height / BLOB_SIZE
        self.matrix = np.zeros((self.width // BLOB_SIZE, self.height // BLOB_SIZE))

        self._screen = pygame.display.set_mode((self.width, self.height))
        self._clock = pygame.time.Clock()
    
    def run(self):
        while True:
            restart = False
            self.get_player_config()

            while not restart:
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        pygame.quit()
                        sys.exit(0)
                    if event.type == pygame.KEYDOWN:
                        if event.key == pygame.K_RETURN:
                            self._running = not self._running
                        if event.key == pygame.K_r:
                            self.reset()
                            self.draw_new_grid()
                            self._running = False
                            restart = True
                            continue
                
                if self._running:
                    self.calculate_new_matrix()
                    self.draw_new_grid()

                self._clock.tick(10)

                pygame.display.update()


    def get_player_config(self):
        while not self._running:
            if pygame.mouse.get_pressed()[0]:
                x, y = (coord // BLOB_SIZE for coord in pygame.mouse.get_pos())
                if not self.matrix[x][y]:
                    pygame.draw.rect(self._screen, WHITE, pygame.Rect(x * BLOB_SIZE, y * BLOB_SIZE, BLOB_SIZE, BLOB_SIZE))
                    self.matrix[x][y] = 1

            if pygame.mouse.get_pressed()[2]:
                x, y = (coord // BLOB_SIZE for coord in pygame.mouse.get_pos())
                if self.matrix[x][y]:
                    pygame.draw.rect(self._screen, BLACK, pygame.Rect(x * BLOB_SIZE, y * BLOB_SIZE, BLOB_SIZE, BLOB_SIZE))
                    self.matrix[x][y] = 0

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    os.exit(0)
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_RETURN:
                        self._running = True

            pygame.display.update()
        
    
    def reset(self):
        self.matrix = np.zeros((self.width // BLOB_SIZE, self.height // BLOB_SIZE))

    def draw_new_grid(self):
        for x in range(len(self.matrix)):
            for y in range(len(self.matrix[0])):
                if self.matrix[x][y]:
                    pygame.draw.rect(self._screen, WHITE, pygame.Rect(x * BLOB_SIZE, y * BLOB_SIZE, BLOB_SIZE, BLOB_SIZE))
                else:
                    pygame.draw.rect(self._screen, BLACK, pygame.Rect(x * BLOB_SIZE, y * BLOB_SIZE, BLOB_SIZE, BLOB_SIZE))

    def calculate_new_matrix(self):
        new_matrix = self.matrix.copy()

        for x in range(len(self.matrix)):
            for y in range(len(self.matrix[0])):
                self.update_cell(new_matrix, x, y)
            
        self.matrix = new_matrix

    def update_cell(self, new_matrix, x, y):
        # alive cell
        if self.matrix[x][y]:
            live_neighbors = self.get_live_neighbors(x, y)
            if live_neighbors < 2 or live_neighbors > 3:
                new_matrix[x, y] = 0
        else:
            if self.get_live_neighbors(x, y) == 3:
                new_matrix[x][y] = 1
    
    def get_live_neighbors(self, x, y):
        count = 0

        neighbor_offsets = [(-1, -1), (-1, 0), (-1, 1),
                            (0, -1),           (0, 1),
                            (1, -1),  (1, 0),  (1, 1)]

        for dx, dy in neighbor_offsets:
            try:
                count += self.matrix[x + dx][y + dy]
            except IndexError:
                pass

        return int(count)

game = GameOfLife()
game.run()