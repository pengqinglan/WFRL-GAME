#!/usr/bin/python
# -*- coding: utf8 -*-

# Import a library of functions called 'pygame'
import pygame
from Environment import Environment
from game.rectangle import Rectangle
import pickle
import game.node

taskCount=10
env = Environment(taskCount)

# dbfile = open('env-12', 'rb')
# env = pickle.load(dbfile)
# dbfile.close()
# taskCount = env.workflow.taskCount

deadline = env.workflow.DeadLine
# env.workflow.print()

# Initialize the game engine
pygame.init()
pygame.font.init()

# Font
myfont  = pygame.font.SysFont('Comic Sans MS', 30)
font2   = pygame.font.SysFont('Comic Sans MS', 20)
bigfont = pygame.font.SysFont('Comic Sans MS', 60)

# Define the colors we will use in RGB format
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
BLUE = (17,238,238)
GREEN = (0, 255, 0)
RED = (255, 0, 0)
GRAY = (170, 170, 170)

# Set the height and width of the screen
size = [1200, 700]
screen = pygame.display.set_mode(size)


# Loop until the user clicks the close button.
done = False
clock = pygame.time.Clock()

# get workflow task nodes
nodes, edges = game.node.initNodes(env)

frame = 0
selection = 0
tasksToSchedule = []
message = ''
message_err = ''
workflowDone = False


while not done:

    tasksToSchedule = env.getNewTasks()
    if len(tasksToSchedule) != 0:
        taskNo = tasksToSchedule[0]
        message = 'Task t_'+str(taskNo)+' to schedule, estimate time (small): '+str(env.workflow.taskSize[taskNo])

    for e in pygame.event.get():
        if e.type == 3: # key event
            if e.key == 276 and selection > 0: # left
                selection = selection - 1
            if e.key == 275 and selection < 8: # right
                selection = selection + 1
            if e.key == 32:                    # space
                if (len(tasksToSchedule) > 0):
                    isSucc, msg = env.scheduleTask(tasksToSchedule[0], selection)
                    if isSucc:
                        message_err = ''
                        message = msg
                    else:
                        message_err = msg
                pass
            if e.key == 114:                   # R reset workflow
                env.reset()
                workflowDone = False
            if e.key == 115:
                env.saveWorkflow()

    # This limits the while loop to a max of 10 times per second.
    # Leave this out and we will use all CPU we can.
    clock.tick(60)

    # Game enviroment time process
    frame = frame + 1
    if frame == 6:
        frame = 0
        if not workflowDone:
            env.timeProcess()
            workflowDone = env.isDone()


    # Clear the screen and set the screen background
    screen.fill(WHITE)

    # ======== Status and Message part ========
    cost = env.getCurrentCost()
    time = env.currentTime

    textsurface = myfont.render(message, False, BLACK)
    screen.blit(textsurface, (700, 60))
    textsurface = myfont.render(message_err, False, RED)
    screen.blit(textsurface, (700, 85))

    textsurface = myfont.render("TotalSize: " + str(env.totalSize), False, BLACK)
    screen.blit(textsurface, (500, 20))
    textsurface = myfont.render("Time: "+str(round(time,2)), False, BLACK)
    screen.blit(textsurface, (700, 20))
    textsurface = myfont.render("Cost: " + str(round(cost,2)), False, RED)
    screen.blit(textsurface, (830, 20))
    textsurface = myfont.render("DeadLine: " + str(round(deadline-time, 2)), False, RED)
    screen.blit(textsurface, (980, 20))

    textsurface = myfont.render("Press 'R' to reset scheduling", False, RED)
    screen.blit(textsurface, (750, 630))
    textsurface = myfont.render("Press 'S' to save workflow", False, RED)
    screen.blit(textsurface, (750, 660))

    # ======== Selection Arrow start ========
    x = 20
    y = 50
    for i in range(9):
        if i == selection:
            color = RED
        else:
            color = WHITE
        x = x + 70
        pygame.draw.polygon(screen, color,
                            [[x, y], [x+20, y], [x+20, y+20], [x+30, y+20], [x+10, y+35], [x-10, y+20], [x, y+20]], 5)
    # ======== Selection Arrow end ========

    # ======== VM status start ========
    x = 10
    y = 630
    y2 = 650
    y3 = 670
    for i in range(len(env.resourcePool)):
        x = x + 70
        if env.resourcePool[i].taskNo == -1:  # idle
            textsurface = font2.render('idle', False, (0, 255, 0))
        else:
            textsurface = font2.render('task: '+str(env.resourcePool[i].taskNo), False, (255, 0, 0))
        screen.blit(textsurface, (x, y))
        textsurface = font2.render('vm_'+str(i), False, BLACK)
        screen.blit(textsurface, (x, y2))
        textsurface = font2.render(env.resourcePool[i].type, False, BLACK)
        screen.blit(textsurface, (x, y3))

    rets = Rectangle.getRectangles(env)
    for i in range(len(rets)):
        pygame.draw.rect(screen, rets[i].color, [rets[i].x, rets[i].y, rets[i].width, rets[i].height])
    # ======== VM status end ========

    # ======== Workflow display start ========
    for edge in edges:
        p1 = edge[0]
        p2 = edge[1]
        pygame.draw.line(screen, RED, [nodes[p1].x-3, nodes[p1].y-3], [nodes[p2].x-3, nodes[p2].y-3], 3)

    for i in range(len(nodes)):
        taskNo = nodes[i].taskNo
        if taskNo in env.finishedTasks:
            circleColor = GRAY
        else:
            circleColor = BLUE
        if (len(tasksToSchedule) > 0):
            if taskNo == tasksToSchedule[0]:
                circleColor = RED
        if taskNo in env.runningTasks:
            circleColor = GREEN
        pygame.draw.circle(screen, circleColor, [nodes[i].x - 5, nodes[i].y - 5], 20)
        textsurface = myfont.render('t_' + str(taskNo), False, (0, 0, 0))
        screen.blit(textsurface, (nodes[i].x - 16, nodes[i].y - 16))
    # ======== Workflow display start ========


    # ======== Game Over start ========
    remainTime = deadline - time
    if workflowDone:
        if remainTime >= 0:
            textsurface = bigfont.render('DeadLine Meet, You Win!', False, BLACK)
            screen.blit(textsurface, (300, 200))
    if remainTime <= 0:
        workflowDone = True
        textsurface = bigfont.render('DeadLine Missing, Game Over!', False, BLACK)
        screen.blit(textsurface, (300, 200))
    # ======== Game Over start ========

    # Go ahead and update the screen with what we've drawn.
    # This MUST happen after all the other drawing commands.
    pygame.display.flip()

# Be IDLE friendly
pygame.quit()