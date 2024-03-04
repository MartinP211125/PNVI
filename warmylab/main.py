# Wormy (a Nibbles clone)
# By Al Sweigart al@inventwithpython.com
# http://inventwithpython.com/pygame
# Released under a "Simplified BSD" license
import asyncio
import random, pygame, sys
from pygame.locals import *

FPS = 15
WINDOWWIDTH = 640
WINDOWHEIGHT = 480
CELLSIZE = 20
assert WINDOWWIDTH % CELLSIZE == 0, "Window width must be a multiple of cell size."
assert WINDOWHEIGHT % CELLSIZE == 0, "Window height must be a multiple of cell size."
CELLWIDTH = int(WINDOWWIDTH / CELLSIZE)
CELLHEIGHT = int(WINDOWHEIGHT / CELLSIZE)

#             R    G    B
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
DARKGREEN = (0, 155, 0)
DARKGRAY = (40, 40, 40)
BGCOLOR = BLACK

UP = 'up'
DOWN = 'down'
LEFT = 'left'
RIGHT = 'right'

HEAD = 0  # syntactic sugar: index of the worm's head


def main():
    global FPSCLOCK, DISPLAYSURF, BASICFONT

    pygame.init()
    FPSCLOCK = pygame.time.Clock()
    DISPLAYSURF = pygame.display.set_mode((WINDOWWIDTH, WINDOWHEIGHT))
    BASICFONT = pygame.font.Font('freesansbold.ttf', 18)
    pygame.display.set_caption('Wormy')
    showStartScreen()
    while True:
        runGame()
        showGameOverScreen()


def runGame():
    global bonusPoints, blink1, blink2, blink_flag
    # Set a random start point.
    wormCoords = initializeWorm()
    blink_flag = 0
    blink1 = 0
    blink2 = 0
    direction = RIGHT
    bonusPoints = 0
    ticks = 0
    stga = 0
    ltga = 0

    # Start the apple in a random place.
    secondWorm = None
    apple = getRandomLocation()
    shortTimedGlowingApple = resetApple()
    longTimeGlowingApple = resetApple()
    secondDirection = direction
    while True:  # main game loop
        for event in pygame.event.get():  # event handling loop
            if event.type == QUIT:
                terminate()
            elif event.type == KEYDOWN:
                if (event.key == K_LEFT or event.key == K_a) and direction != RIGHT:
                    direction = LEFT
                elif (event.key == K_RIGHT or event.key == K_d) and direction != LEFT:
                    direction = RIGHT
                elif (event.key == K_UP or event.key == K_w) and direction != DOWN:
                    direction = UP
                elif (event.key == K_DOWN or event.key == K_s) and direction != UP:
                    direction = DOWN
                elif event.key == K_ESCAPE:
                    terminate()

        if pygame.time.get_ticks():
            ticks = ticks + 1
            stga = stga + 1
            ltga = ltga + 1

        if ticks / FPS == 20 and secondWorm is None:
            secondWorm = initializeWorm()

        if stga / FPS == 5 and shortTimedGlowingApple['x'] == -1:
            shortTimedGlowingApple = getRandomLocation()
            stat = 0
        elif stga / FPS == 5 and shortTimedGlowingApple['x'] != -1:
            shortTimedGlowingApple = resetApple()

        if ltga / FPS == 7 and longTimeGlowingApple['x'] == -1:
            longTimeGlowingApple = getRandomLocation()

        if checkForValidMove(wormCoords) == 1:
            return

        if checkIfAppleEaten(wormCoords, apple) == 0:
            apple = getRandomLocation()
        elif checkIfAppleEaten(wormCoords, shortTimedGlowingApple) == 0:
            shortTimedGlowingApple = resetApple()
            bonusPoints = bonusPoints + 2
        elif checkIfAppleEaten(wormCoords, longTimeGlowingApple) == 0:
            longTimeGlowingApple = resetApple()
            ltga = 0
            bonusPoints = bonusPoints + 2
        elif secondWorm is not None and checkForCollisionBetweenWorms(wormCoords, secondWorm) == 1:
            del secondWorm[-1]
        else:
            del wormCoords[-1]

        if secondWorm is not None:
            secondDirection = getDirection(secondWorm, secondDirection)
            if checkForCollisionBetweenWorms(secondWorm, wormCoords) == 0:
                del secondWorm[-1]
            else:
                del wormCoords[-1]
            Move(secondDirection, secondWorm, apple, len(wormCoords) - 3, shortTimedGlowingApple, longTimeGlowingApple, wormCoords, 1)
        Move(direction, wormCoords, apple, len(wormCoords) - 3, shortTimedGlowingApple, longTimeGlowingApple, secondWorm, 0)
        FPSCLOCK.tick(FPS)


def initializeWorm():
    startx = random.randint(5, CELLWIDTH - 6)
    starty = random.randint(5, CELLHEIGHT - 6)
    Worm = [{'x': startx, 'y': starty},
            {'x': startx - 1, 'y': starty},
            {'x': startx - 2, 'y': starty}]
    return Worm


def SecondWormInBorderCheck(worm, startingDirection, newDirection):
    head_x, head_y = worm[HEAD]['x'], worm[HEAD]['y']

    if (
            (head_y <= 2 and newDirection == UP) or
            (head_y >= CELLHEIGHT - 3 and newDirection == DOWN) or
            (head_x <= 2 and newDirection == LEFT) or
            (head_x >= CELLWIDTH - 3 and newDirection == RIGHT)
    ):
        return startingDirection

    for wormBody in worm[1:]:
        if (
                (newDirection == LEFT and wormBody['x'] == head_x - 1 and wormBody['y'] == head_y) or
                (newDirection == UP and wormBody['x'] == head_x and wormBody['y'] == head_y - 1) or
                (newDirection == DOWN and wormBody['x'] == head_x + 1 and wormBody['y'] == head_y) or
                (newDirection == RIGHT and wormBody['x'] == head_x and wormBody['y'] == head_y + 1)
        ):
            return newDirection
            break
    return newDirection


def getDirection(worm, direction):
    dir = random.randint(0, 3)
    dirUp = [UP, LEFT, RIGHT]
    dirDown = [DOWN, LEFT, RIGHT]
    dirRight = [RIGHT, DOWN, UP]
    dirLeft = [LEFT, DOWN, UP]
    newDirection = None
    if dir > 2:
        dir = 0
    if direction == UP:
        newDirection = dirUp[dir]
    elif direction == DOWN:
        newDirection = dirDown[dir]
    elif direction == LEFT:
        newDirection = dirLeft[dir]
    else:
        newDirection = dirRight[dir]

    return SecondWormInBorderCheck(worm, direction, newDirection)


def Move(direction, worm, apple, score, shortTimeGlowingApple=None, longTimeGlowingApple=None, secondWorm=None, id=None):
    head_x, head_y = worm[HEAD]['x'], worm[HEAD]['y']
    if direction == UP and head_y - 1 >= 0:
        newHead = {'x': worm[HEAD]['x'], 'y': worm[HEAD]['y'] - 1}
    elif direction == DOWN and head_y + 1 <= CELLHEIGHT - 1:
        newHead = {'x': worm[HEAD]['x'], 'y': worm[HEAD]['y'] + 1}
    elif direction == LEFT and head_x - 1 >= 0:
        newHead = {'x': worm[HEAD]['x'] - 1, 'y': worm[HEAD]['y']}
    elif direction == RIGHT and head_x + 1 <= CELLWIDTH - 1:
        newHead = {'x': worm[HEAD]['x'] + 1, 'y': worm[HEAD]['y']}
    else:
        newHead = {'x': worm[HEAD]['x'], 'y': worm[HEAD]['y']}
    worm.insert(0, newHead)
    DISPLAYSURF.fill(BGCOLOR)
    drawGrid()
    drawScore(score + bonusPoints)
    if id == 0:
        drawWorm(worm, DARKGREEN)
        if secondWorm is not None:
            drawWorm(secondWorm, (255, 0, 0))
    else:
        drawWorm(secondWorm, DARKGREEN)
        if secondWorm is not None:
            drawWorm(worm, (255, 0, 0))
    drawApple(apple)
    if blink_flag <=3:
        if blink1 == 0 and shortTimeGlowingApple is not None:
            drawGlowingApple(shortTimeGlowingApple)
            setBlink(1, blink2, blink_flag)
        elif shortTimeGlowingApple is not None and blink1 == 1:
            drawApple(shortTimeGlowingApple)
            setBlink(0, blink2, blink_flag)
        if blink2 == 0 and longTimeGlowingApple is not None:
            drawGlowingApple(longTimeGlowingApple)
            setBlink(blink1, 1, blink_flag)
        elif longTimeGlowingApple is not None and blink2 == 1:
            drawApple(longTimeGlowingApple)
            setBlink(blink1, 0, blink_flag)
        setBlink(blink1, blink2, blink_flag + 1)
    else:
        setBlink(blink1, blink2, blink_flag+1)
    if blink_flag == 6:
        setBlink(blink1, blink2, 0)
    pygame.display.update()


def setBlink(num, num2, num3):
    global blink1, blink2, blink_flag
    blink1 = num
    blink2 = num2
    blink_flag = num3


def drawPressKeyMsg():
    pressKeySurf = BASICFONT.render('Press a key to play.', True, DARKGRAY)
    pressKeyRect = pressKeySurf.get_rect()
    pressKeyRect.topleft = (WINDOWWIDTH - 200, WINDOWHEIGHT - 30)
    DISPLAYSURF.blit(pressKeySurf, pressKeyRect)


def drawGlowingApple(apple):
    if apple['x'] != -1:
        x = apple['x'] * CELLSIZE
        y = apple['y'] * CELLSIZE
        appleRect = pygame.Rect(x, y, CELLSIZE, CELLSIZE)
        pygame.draw.rect(DISPLAYSURF, RED, appleRect)
        pygame.draw.rect(DISPLAYSURF, (196, 180, 84), appleRect, 2)


def Buttons():
    global StartRect, QuitRect
    Start = BASICFONT.render('Start from the beginning.', True, WHITE)
    StartRect = Start.get_rect()
    Quit = BASICFONT.render('Quit.', True, WHITE)
    QuitRect = Quit.get_rect()
    StartRect.topleft = (WINDOWWIDTH - 425, WINDOWHEIGHT - 125)
    QuitRect.topleft = (WINDOWWIDTH - 345, WINDOWHEIGHT - 100)
    DISPLAYSURF.blit(Start, StartRect)
    DISPLAYSURF.blit(Quit, QuitRect)


def checkForValidMove(wormCoords):
    if wormCoords[HEAD]['x'] == -1 or wormCoords[HEAD]['x'] == CELLWIDTH or wormCoords[HEAD]['y'] == -1 or \
            wormCoords[HEAD]['y'] == CELLHEIGHT:
        return 1
    for wormBody in wormCoords[1:]:
        if wormBody['x'] == wormCoords[HEAD]['x'] and wormBody['y'] == wormCoords[HEAD]['y']:
            return 1


def checkIfAppleEaten(wormCoords, apple):
    if apple is not None:
        if wormCoords[HEAD]['x'] == apple['x'] and wormCoords[HEAD]['y'] == apple['y']:
            return 0
        else:
            return 1


def checkForCollisionBetweenWorms(secondWorm, firstWorm):
    return any(fWorm['x'] == secondWorm[HEAD]['x'] and fWorm['y'] == secondWorm[HEAD]['y'] for fWorm in firstWorm[1:])


def checkForKeyPress():
    if len(pygame.event.get(QUIT)) > 0:
        terminate()

    keyUpEvents = pygame.event.get(KEYUP)
    if len(keyUpEvents) == 0:
        return None
    if keyUpEvents[0].key == K_ESCAPE:
        terminate()
    return keyUpEvents[0].key


def checkForMouseClick():
    if len(pygame.event.get(QUIT)) > 0:
        terminate()
    mouseClick = pygame.event.get(MOUSEBUTTONDOWN)
    if len(mouseClick) == 0:
        return None
    elif StartRect.collidepoint(pygame.mouse.get_pos()):
        runGame()
        showGameOverScreen()
    elif QuitRect.collidepoint(pygame.mouse.get_pos()):
        terminate()


def showStartScreen():
    titleFont = pygame.font.Font('freesansbold.ttf', 100)
    titleSurf1 = titleFont.render('Wormy!', True, WHITE, DARKGREEN)
    titleSurf2 = titleFont.render('Wormy!', True, GREEN)

    degrees1 = 0
    degrees2 = 0
    while True:
        DISPLAYSURF.fill(BGCOLOR)
        rotatedSurf1 = pygame.transform.rotate(titleSurf1, degrees1)
        rotatedRect1 = rotatedSurf1.get_rect()
        rotatedRect1.center = (WINDOWWIDTH / 2, WINDOWHEIGHT / 2)
        DISPLAYSURF.blit(rotatedSurf1, rotatedRect1)

        rotatedSurf2 = pygame.transform.rotate(titleSurf2, degrees2)
        rotatedRect2 = rotatedSurf2.get_rect()
        rotatedRect2.center = (WINDOWWIDTH / 2, WINDOWHEIGHT / 2)
        DISPLAYSURF.blit(rotatedSurf2, rotatedRect2)

        drawPressKeyMsg()

        if checkForKeyPress():
            pygame.event.get()  # clear event queue
            return
        pygame.display.update()
        FPSCLOCK.tick(FPS)
        degrees1 += 3  # rotate by 3 degrees each frame
        degrees2 += 7  # rotate by 7 degrees each frame


def terminate():
    pygame.quit()
    sys.exit()


def getRandomLocation():
    return {'x': random.randint(0, CELLWIDTH - 1), 'y': random.randint(0, CELLHEIGHT - 1)}


def resetApple():
    return {'x': -1, 'y': -1}


def showGameOverScreen():
    gameOverFont = pygame.font.Font('freesansbold.ttf', 150)
    gameSurf = gameOverFont.render('Game', True, WHITE)
    overSurf = gameOverFont.render('Over', True, WHITE)
    gameRect = gameSurf.get_rect()
    overRect = overSurf.get_rect()
    gameRect.midtop = (WINDOWWIDTH / 2, 10)
    overRect.midtop = (WINDOWWIDTH / 2, gameRect.height + 10 + 25)

    DISPLAYSURF.blit(gameSurf, gameRect)
    DISPLAYSURF.blit(overSurf, overRect)
    Buttons()
    pygame.display.update()
    pygame.time.wait(500)
    checkForMouseClick()  # clear out any key presses in the event queue

    while True:
        if checkForMouseClick():
            pygame.event.get()  # clear event queue
            return


def drawScore(score):
    scoreSurf = BASICFONT.render('Score: %s' % (score), True, WHITE)
    scoreRect = scoreSurf.get_rect()
    scoreRect.topleft = (WINDOWWIDTH - 120, 10)
    DISPLAYSURF.blit(scoreSurf, scoreRect)


def drawWorm(wormCoords, color):
    if wormCoords is not None:
        for coord in wormCoords:
            x = coord['x'] * CELLSIZE
            y = coord['y'] * CELLSIZE
            wormSegmentRect = pygame.Rect(x, y, CELLSIZE, CELLSIZE)
            pygame.draw.rect(DISPLAYSURF, color, wormSegmentRect)
            wormInnerSegmentRect = pygame.Rect(x + 4, y + 4, CELLSIZE - 8, CELLSIZE - 8)
            pygame.draw.rect(DISPLAYSURF, GREEN, wormInnerSegmentRect)


def drawApple(coord):
    x = coord['x'] * CELLSIZE
    y = coord['y'] * CELLSIZE
    appleRect = pygame.Rect(x, y, CELLSIZE, CELLSIZE)
    pygame.draw.rect(DISPLAYSURF, RED, appleRect)


def drawGrid():
    for x in range(0, WINDOWWIDTH, CELLSIZE):  # draw vertical lines
        pygame.draw.line(DISPLAYSURF, DARKGRAY, (x, 0), (x, WINDOWHEIGHT))
    for y in range(0, WINDOWHEIGHT, CELLSIZE):  # draw horizontal lines
        pygame.draw.line(DISPLAYSURF, DARKGRAY, (0, y), (WINDOWWIDTH, y))


if __name__ == '__main__':
    main()
