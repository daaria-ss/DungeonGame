WIDTH, HEIGHT = SIZE = 600, 600
FPS = 60
TILE = 50
TURN = 1
LOSE = False
PANEL_IMAGE_SIZE = (32, 32)
PANEL_HEIGHT = 50

# colors
BLACK = (0, 0, 0)
HP_COLOR = (0, 255, 0)
DAMAGE_COLOR = (255, 0, 0)
ACTION_POINTS_COLOR = (0, 0, 255)
PANEL_COLOR = (64, 64, 64)


def apply(coords):
    return coords[0], coords[1] + PANEL_HEIGHT
