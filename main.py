import pygame
from pygame_widgets import TextBox, Slider
import math
from queue import PriorityQueue
import time

pygame.init()
WIDTH = 800
WIN = pygame.display.set_mode((WIDTH, 900))
pygame.display.set_caption("A* Path Finding Algorithm")


slider_speed = Slider(WIN, 50, 820, 350, 20, min=0, max=1, step=0.05,initial=0)
output_slider = TextBox(WIN, 50, 860, 350, 20, fontSize=15)

RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 255, 0)
YELLOW = (255, 255, 0)
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
PURPLE = (128, 0, 128)
ORANGE = (255, 165, 0)
GREY = (128, 128, 128)
TURQUOISE = (64, 224, 208)


class Spot:
    def __init__(self, row, col, width, total_rows):
        self.row = row
        self.col = col
        self.x = row * width
        self.y = col * width
        self.color = WHITE
        self.neighbors = []
        self.width = width
        self.total_rows = total_rows

    def get_pos(self):
        return self.row, self.col

    def is_closed(self):
        return self.color == RED

    def is_open(self):
        return self.color == GREEN

    def is_barrier(self):
        return self.color == BLACK

    def is_start(self):
        return self.color == ORANGE

    def is_end(self):
        return self.color == TURQUOISE

    def reset(self):
        self.color = WHITE

    def make_start(self):
        self.color = ORANGE

    def make_closed(self):
        self.color = RED

    def make_open(self):
        self.color = GREEN

    def make_barrier(self):
        self.color = BLACK

    def make_end(self):
        self.color = TURQUOISE

    def make_path(self):
        self.color = PURPLE

    def draw(self, win):
        pygame.draw.rect(
            win, self.color, (self.x, self.y, self.width, self.width))

    def update_neighbors(self, grid):
        self.neighbors = []
        # DOWN
        if self.row < self.total_rows - 1 and not grid[self.row + 1][self.col].is_barrier():
            self.neighbors.append(grid[self.row + 1][self.col])

        if self.row > 0 and not grid[self.row - 1][self.col].is_barrier():  # UP
            self.neighbors.append(grid[self.row - 1][self.col])

        # RIGHT
        if self.col < self.total_rows - 1 and not grid[self.row][self.col + 1].is_barrier():
            self.neighbors.append(grid[self.row][self.col + 1])

        if self.col > 0 and not grid[self.row][self.col - 1].is_barrier():  # LEFT
            self.neighbors.append(grid[self.row][self.col - 1])

    def __lt__(self, other):
        return False

# manhattan distance


def h(p1, p2):
    x1, y1 = p1
    x2, y2 = p2
    return abs(x1-x2)+abs(y1-y2)


def reconstruct_path(came_from, current, draw):

    while current in came_from:
        current = came_from[current]
        current.make_path()
        draw()
    """
    for node in came_from:
        node.make_path()
        draw()
    """


def draw(win, grid, rows, width, slider_speed, output_slider):
    win.fill(WHITE)
    for row in grid:
        for spot in row:
            spot.draw(win)
    draw_grid(win, rows, width)
    #output_slider.setText(str(slider_speed.getValue()))
    slider_speed.draw()
    output_slider.draw()
    pygame.display.update()


def algorithm(draw, grid, start, end,time_):
    count = 0
    open_set = PriorityQueue()
    open_set.put((0, count, start))
    came_from = {}
    g_score = {spot: float("inf") for row in grid for spot in row}
    g_score[start] = 0
    f_score = {spot: float("inf") for row in grid for spot in row}
    f_score[start] = h(start.get_pos(), end.get_pos())

    open_set_hash = {start}

    while not open_set.empty():
        time.sleep(time_)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
        current = open_set.get()[2]
        open_set_hash.remove(current)

        if current == end:
            reconstruct_path(came_from, end, draw)
            end.make_end()
            return True

        for neighbor in current.neighbors:
            temp_g_score = g_score[current] + 1

            if temp_g_score < g_score[neighbor]:
                came_from[neighbor] = current
                g_score[neighbor] = temp_g_score
                f_score[neighbor] = temp_g_score + \
                    h(neighbor.get_pos(), end.get_pos())
                if neighbor not in open_set_hash:
                    count += 1
                    open_set.put((f_score[neighbor], count, neighbor))
                    open_set_hash.add(neighbor)
                    neighbor.make_open()

        draw()

        if current != start:
            current.make_closed()
        
    return False


def make_grid(rows, width):
    grid = []
    gap = width//rows
    for i in range(rows):
        grid.append([])
        for j in range(rows):
            spot = Spot(i, j, gap, rows)
            grid[i].append(spot)

    return grid


def draw_grid(win, rows, width):
    gap = width//rows
    for i in range(rows):
        pygame.draw.line(win, GREY, (0, i*gap), (width, i*gap))
        for j in range(rows):
            pygame.draw.line(win, GREY, (i*gap, 0), (i*gap, width))
    pygame.draw.line(win, GREY, (0, width), (width, width))


def get_clicked_pos(pos, rows, width):
    gap = width // rows
    y, x = pos
    row = y//gap
    col = x//gap
    return row, col


def main(win, width):
    ROWS = 50
    grid = make_grid(ROWS, width)
    start = None
    end = None
    run = True
    started = False
    time_ = 0
    output_slider.setText("Adjust Algorithm Progressing Speed")
    output_slider.draw()
    while run:
        draw(win, grid, ROWS, width, slider_speed, output_slider)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False

            if started:
                continue

            if pygame.mouse.get_pressed()[0]:  # left mouse key index 0
                pos = pygame.mouse.get_pos()
                if pos[0] <= 800 and pos[1] <= 800:
                    row, col = get_clicked_pos(pos, ROWS, width)
                    spot = grid[row][col]
                    if not start and spot != end:
                        start = spot
                        spot.make_start()

                    elif not end and spot != start:
                        end = spot
                        spot.make_end()

                    elif spot != end and spot != start:
                        spot.make_barrier()

            elif pygame.mouse.get_pressed()[2]:  # left mouse key index 2
                pos = pygame.mouse.get_pos()
                row, col = get_clicked_pos(pos, ROWS, width)
                spot = grid[row][col]
                spot.reset()
                if spot == start:
                    start = None
                if spot == end:
                    end = None

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE and start and end:
                    for row in grid:
                        for spot in row:
                            spot.update_neighbors(grid)
                    algorithm(lambda: draw(win, grid, ROWS, width,slider_speed,output_slider),
                              grid, start, end,time_)

                if event.key == pygame.K_c:
                    start = None
                    end = None
                    grid = make_grid(ROWS, width)
        
        slider_speed.listen(pygame.event.get())
        slider_speed.draw()
        time_ = 1.0-slider_speed.getValue()
        pygame.display.update()
    pygame.quit()


main(WIN, WIDTH)
