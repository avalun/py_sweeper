import pygame
import sys
import random
from pygame.locals import *

pygame.init()

# Global variables with game parameters
FPS = 60
WINDOWNAME = "Sweeper"
MINES = 15
WIDTH = 15
HEIGHT = 15
SQUARESIZE = 32
BORDERSIZE = 32
MAXADJMINES = 4
DISPLAYWIDTH = WIDTH * SQUARESIZE + 2 * BORDERSIZE
DISPLAYHEIGHT = HEIGHT * SQUARESIZE + 3 * BORDERSIZE
FONT = pygame.font.Font("res/digital-7.ttf", 54)


# Spritesheet Class
class Spritesheet:
    def __init__(self, filename):
            self.sheet = pygame.image.load(filename)

    # Load a specific image from a specific rectangle
    def image_at(self, rectangle, colorkey = None):
        "Loads image from x,y,x+offset,y+offset"
        rect = pygame.Rect(rectangle)
        image = pygame.Surface(rect.size).convert()
        image.blit(self.sheet, (0, 0), rect)
        if colorkey is not None:
            if colorkey is -1:
                colorkey = image.get_at((0,0))
            image.set_colorkey(colorkey, pygame.RLEACCEL)
        return image

spritesheet = Spritesheet('res/spritesheet.png')

# Colors
GREY = (160, 160, 160)
BLACK = (0, 0, 0)
RED = (255, 0, 0)


def main():
    # Variables
    global DISPLAYSURF, fpsClock
    down_x = 0  # used to store x coordinate of mouse event
    down_y = 0  # used to store y coordinate of mouse event

    # Flags
    f_minesgenerated = False
    f_lost = False
    f_mousedown = False
    f_won = False
    f_lock = False

    # Set up display
    DISPLAYSURF = pygame.display.set_mode((DISPLAYWIDTH, DISPLAYHEIGHT))
    pygame.display.set_caption(WINDOWNAME)
    DISPLAYSURF.fill(GREY)

    # Instantiate clock
    fpsClock = pygame.time.Clock()

    # Get Necessary classes
    board = Field(WIDTH, HEIGHT)
    topbar = Topbar()

    # Check if Player has won
    def checkwon():
        for x in range(WIDTH):
            for y in range(HEIGHT):
                if not board.field[x][y].mine:
                    if not board.field[x][y].revealed:
                        return False
        return True

    def countmarked():
        i = 0
        for n in range(WIDTH):
            for m in range(HEIGHT):
                if board.field[m][n].marked:
                    i += 1
        return i

    # Main game loop
    while True:
        # Handle events
        for event in pygame.event.get():
            if event.type == QUIT:
                pygame.quit()
                sys.exit()

            # Press of mouse Button
            elif event.type == MOUSEBUTTONDOWN:
                # Left
                if event.button == 1:
                    down_x, down_y = event.pos
                    if in_board(down_x, down_y):
                        f_mousedown = True
                        down_x = (down_x - BORDERSIZE) // SQUARESIZE
                        down_y = (down_y - 2 * BORDERSIZE) // SQUARESIZE
                        board.click(down_x, down_y)

            # Release of mouse Button
            elif event.type == MOUSEBUTTONUP:
                up_x, up_y = event.pos
                if (WIDTH // 2) * SQUARESIZE + BORDERSIZE <= up_x <= (WIDTH // 2) * SQUARESIZE + BORDERSIZE + SQUARESIZE and BORDERSIZE <= up_y <= BORDERSIZE + SQUARESIZE:
                    # Flags
                    f_minesgenerated = False
                    f_lost = False
                    f_mousedown = False
                    f_won = False
                    f_lock = False

                    # Get Necessary classes
                    board = Field(WIDTH, HEIGHT)
                    topbar = Topbar()
                if in_board(up_x, up_y) and not f_lock:
                    up_x = (up_x - BORDERSIZE) // SQUARESIZE
                    up_y = (up_y - 2 * BORDERSIZE) // SQUARESIZE
                    # Leftclick
                    if event.button == 1:
                        f_mousedown = False
                        # Check if position of Click and Release are the same
                        if up_x != down_x or up_y != down_y:
                            board.click(down_x, down_y)
                        else:
                            if not f_minesgenerated:
                                board.generateMines(MINES, up_x, up_y)
                                f_minesgenerated = True
                                topbar.setClock()
                            f_lost = board.reveal(up_x, up_y)
                            f_won = checkwon()
                            if f_won:
                                f_lock = True
                                topbar.stopClock()
                            if f_lost:
                                f_lock = True
                                board.reveal_all()
                                topbar.stopClock()
                    # Rightclick
                    elif event.button == 3:
                        board.flag(up_x, up_y)

        # Draw updated Squares
        for x in range(WIDTH):
            for y in range(HEIGHT):
                if board.field[x][y].updated:
                    DISPLAYSURF.blit(board.field[x][y].getImg(), (x * SQUARESIZE + BORDERSIZE, y * SQUARESIZE + 2 * BORDERSIZE))
                board.field[x][y].updated = False

        # Draw Topbar
        topbar.draw(DISPLAYSURF, countmarked())
        # Draw Smileyface
        smiley = spritesheet.image_at(picIndex(4, 0))
        if f_won:
            smiley = spritesheet.image_at(picIndex(4, 1))
        elif f_lost:
            smiley = spritesheet.image_at(picIndex(5, 1))
        elif f_mousedown:
            smiley = spritesheet.image_at(picIndex(5, 0))
        DISPLAYSURF.blit(smiley, ((WIDTH // 2) * SQUARESIZE + BORDERSIZE, BORDERSIZE))

        # Update display and wait a clock tick
        pygame.display.update()
        fpsClock.tick(FPS)


def picIndex(x, y):
    return (x*32, y*32, 32, 32)


def in_board(x, y):
    return BORDERSIZE < x < BORDERSIZE + WIDTH * SQUARESIZE and BORDERSIZE * 2 < y < BORDERSIZE * 2 + HEIGHT * SQUARESIZE

class Topbar:
    def __init__(self):
        self.starttime = 0
        self.nowtime = 0
        self.stopped = True

    def setClock(self):
        self.starttime = pygame.time.get_ticks()
        self.stopped = False

    def stopClock(self):
        self.stopped = True

    def draw(self, surface, marked):
        # Left Box
        pygame.draw.rect(DISPLAYSURF, BLACK, (BORDERSIZE, BORDERSIZE // 2, 3 * SQUARESIZE, (1.5 * BORDERSIZE) // 1))
        minesleft = FONT.render(str(MINES - marked), 0, RED)
        surface.blit(minesleft, (BORDERSIZE, BORDERSIZE // 2))
        # Right Box
        pygame.draw.rect(DISPLAYSURF, BLACK, ((WIDTH - 3) * SQUARESIZE + BORDERSIZE, BORDERSIZE // 2, 3 * SQUARESIZE, (1.5 * BORDERSIZE) // 1))
        if not self.stopped:
            self.nowtime = pygame.time.get_ticks()
        time = FONT.render(str((self.nowtime - self.starttime) // 1000), 0, RED)
        surface.blit(time, ((WIDTH - 3) * SQUARESIZE + BORDERSIZE, BORDERSIZE // 2))


class Square:
    def __init__(self, x, y):
        self.position = (x, y)
        self.mine = False
        self.adjacentMines = 0
        self.revealed = False
        self.marked = False
        self.updated = True
        self.clicked = False

    # Return the correct image for this square
    def getImg(self):
        if not self.revealed:
            if self.marked:
                return spritesheet.image_at(picIndex(1, 0))
            if self.clicked:
                return spritesheet.image_at(picIndex(4, 2))
            return spritesheet.image_at(picIndex(0, 0))
        elif self.mine:
            return spritesheet.image_at(picIndex(2, 0))
        else:
            switcher = {
                1: spritesheet.image_at(picIndex(0, 1)),
                2: spritesheet.image_at(picIndex(1, 1)),
                3: spritesheet.image_at(picIndex(2, 1)),
                4: spritesheet.image_at(picIndex(3, 1)),
                5: spritesheet.image_at(picIndex(0, 2)),
                6: spritesheet.image_at(picIndex(1, 2)),
                7: spritesheet.image_at(picIndex(2, 2)),
                8: spritesheet.image_at(picIndex(3, 2)),
            }
            return switcher.get(self.adjacentMines, spritesheet.image_at(picIndex(3, 0)))


class Field:
    def __init__(self, width, height):
        self.field = [[Square(x, y) for x in range(width)] for y in range(height)]
        self.width = width
        self.height = height

    # Check if you could place a mine here given the max allowed mines in the neighborhood
    def neighborsUnderAllowedMines(self, x, y):
        for displacex in range(-1, 2):
            for displacey in range(-1, 2):
                if 0 <= x + displacex < self.width and 0 <= y + displacey < self.height:
                    if self.field[x + displacex][y + displacey].adjacentMines >= MAXADJMINES:
                        return False
        return True

    # Recursively reveal empty squares and their neighbors
    def reveal(self, x, y):
        # Only update not marked and not revealed squares
        if not self.field[x][y].marked and not self.field[x][y].revealed:
            self.field[x][y].revealed = True
            self.field[x][y].updated = True
            # Case: Field is a mine -> Stop execution and inform game that player lost
            if self.field[x][y].mine:
                return True
            # Case: No adjacent mines -> Reveal neighbors
            if self.field[x][y].adjacentMines == 0:
                for displacex in range(-1, 2):
                    for displacey in range(-1, 2):
                        if 0 <= x + displacex < self.width and 0 <= y + displacey < self.height:
                            if not self.field[x + displacex][y + displacey].revealed:
                                self.reveal(x + displacex, y + displacey)
        return False

    # Reveal all Squares
    def reveal_all(self):
        for x in range(WIDTH):
            for y in range(HEIGHT):
                self.field[x][y].revealed = True
                self.field[x][y].updated = True

    # Mark a square
    def flag(self, x, y):
        if not self.field[x][y].revealed:
            self.field[x][y].marked = not self.field[x][y].marked
            self.field[x][y].updated = True

    # Flip clicked state of a square
    def click(self, x, y):
        self.field[x][y].clicked = not self.field[x][y].clicked
        self.field[x][y].updated = True

    # Generate mines but make sure that at the click position and surrounding squares no mines are generated
    def generateMines(self, number, clickx, clicky):
        random.seed()
        for i in range(number):
            while True:
                # Get random position for mines
                x = random.randrange(self.width)
                y = random.randrange(self.width)
                # Make sure that no mines next to click will be generated
                while (clickx - 1) <= x <= (clickx + 1) and (clicky - 1) <= y <= (clicky + 1):
                    x = random.randrange(self.width)
                    y = random.randrange(self.width)

                # If a field without a mine is found break and create a mine
                if not self.field[x][y].mine and self.neighborsUnderAllowedMines(x, y):
                    break

            self.field[x][y].mine = True

            # Add mine to the adjacentMines int of surrounding Squares
            for displacex in range(-1, 2):
                for displacey in range(-1, 2):
                    if 0 <= x + displacex < self.width and 0 <= y + displacey < self.height:
                        self.field[x + displacex][y + displacey].adjacentMines += 1

if __name__ == '__main__':
    main()
