import pygame, sys, math
from pygame.locals import *

pygame.init()

# set up window
WINW = WINH = 600
windowSurface = pygame.display.set_mode((WINW, WINH))
pygame.display.set_caption("Graphical Calculator")

# set up color
RED = (200, 0, 0)
BLACK = (0, 0, 0)
SILVER = (140, 140, 140)
GREEN = (0, 100, 0)
WHITE = (255, 255, 255)

# set up constants
CELLSIZE = 10                                                   # Determine the pixel size of smallest square Try to keep CELLSIZE a multiple of 5
MARKINGCELL = 5                                             # tells after how many boxes should be eqaul to 1
XMAXLIMIT = int(WINW/(2*MARKINGCELL*CELLSIZE))     # Maximum x coordinate
XMINLIMIT = -XMAXLIMIT                              # Minimum x coordinate
YMAXLIMIT = XMAXLIMIT                           # Maximum y coordinate
YMINLINIT = -YMAXLIMIT                              # Minimum y coordinate

def drawGrids(color):           # draw the horizontal and vertical grids
	if color == WHITE:            # If numbers' color is chosen WHITE
		nColor = BLACK              # change their background to BLACK
	else:
		nColor = WHITE              # else keep the numbers' background WHITE
	a = XMINLIMIT                   # the value of a is
	n = 1
	NUMBERS = []
	for i in range(CELLSIZE, WINW, CELLSIZE):
		if n % MARKINGCELL == 0:         # for every 10 small squares apart, draw a bold line
			pygame.draw.line(windowSurface, color, (i, 0), (i, WINH), 2)      # make a vertical line
			pygame.draw.line(windowSurface, color, (0, i), (WINH, i), 2)       # make a horizontal line
			a += 1
			if a != 0:              # a == 0 at the origin.
				hNumber = pygame.font.SysFont(None, 24).render(str(a), True, color, nColor)         # Numbering in the horizontal x-axis
				vNumber = pygame.font.SysFont(None, 24).render(str(-a), True, color, nColor)        # Numbering in the vertical x-axis
				hNumRect = hNumber.get_rect()            # hNumRect is for number in horizontal scale
				vNumRect = vNumber.get_rect()             # vNumRect is for number in vertical scale
				hNumRect.topleft = (i-3, 3+MARKINGCELL*CELLSIZE*XMAXLIMIT)
				vNumRect.topleft = (3+MARKINGCELL*CELLSIZE*XMAXLIMIT, i-3)
				NUMBERS.append((hNumber, hNumRect))
				NUMBERS.append((vNumber, vNumRect))
			else:                   # when at origin, draw a bold horizontal and vertical line
				pygame.draw.line(windowSurface, color, (i, 0), (i, WINH), 3)
				pygame.draw.line(windowSurface, color, (0, i), (WINW, i), 3)
		else:               # when
			pygame.draw.line(windowSurface, color, (i, 0), (i, WINH), 1)      # make a vertical line
			pygame.draw.line(windowSurface, color, (0, i), (WINH, i), 1)       # make a horizontal line
		n += 1
	pygame.draw.rect(windowSurface, color, (0, 0, WINW, WINH), 1)        # draw a rectangle at the margin of the graph
	for num, rect in NUMBERS:                                   # loop over NUMBERS and their position i.e rect
		windowSurface.blit(num, rect)                          # draw each number over on their given position

def drawGraph(eqn, color):                    # calculates x and y coordinates of the graph and then plots them
	POINTS = []                                     # holds all the points of the graph as (x, y)
	l = XMAXLIMIT
	for n in range(-WINW, WINW, 2*CELLSIZE):            # n = pixel coordinates
		x = n/(2*MARKINGCELL*CELLSIZE)               # convert pixel coordinate into actual x coordinate
		try:
			y = eval(eqn)
		except ZeroDivisionError:       # if zero divison error occurs
			y = complex(0)              # turn y to complex number so that it will not be appended in the POINTS
		if type(y) != complex and type(x) != complex:           # if both x and y are not complex number
			POINTS.append(((l+x)*MARKINGCELL*CELLSIZE, round((l-y)*MARKINGCELL*CELLSIZE, 1)))
	for p in range(len(POINTS)):
		try:    # error is raised when last point has no other point to join to form a line i.e p+1 raises IndexError
			pygame.draw.line(windowSurface, color, POINTS[p], POINTS[p+1], 2)
		except IndexError:
			pass        # do nothing if IndexError

def formatEqn(rawEqn):             # This function look over the equation iven by the user and corrects some mistake before it is drawn on the graph
	eqn = rawEqn.split()               # remove spaces by spliting in every space converting the string into a list
	eqn = "".join(eqn)              # convert the list back to a string with no space in between
	eqn = eqn.replace("^", "**")            # replace all ^ signs with ** sign as in python ** is for power.
	for i in range(len(eqn)):
		# add * sign between x coordinate and a constant if the user writes 2*x as 2x.
		if eqn[i] == "x":               # check if the current item of the loop is the x-coordinate
			if i != 0:                       # check if the index of x is not 0. If i == 0, checking if [i-1] item (i.e item left to x) of the eqn will raise a index-out-of-range error
				if eqn[i-1].isdigit():              # check if item left to x is a digit
					eqn = eqn[:i]+"*"+eqn[i:]           # if true for above condition, it means the equation is like 2x. So now we slice and put "*" sign between the coefficient and x and make it 2*x
			if i != len(eqn)-1:          # check if the index doesn't indicate the last digit of the equation. If it is the last digit, checking for item right to it i.e i+1 will raise a index-out-of-range error
				if eqn[i+1].isdigit():              # check if item right to x is a digit
					eqn = eqn[:i+1]+"*"+eqn[i+1:]     # if true for above condition, it means the equation is like x2. So now we slice and put "*" sign between the coefficient and x and make it x*2
		# add * sign between any item and ( or ) signs if needed. eg change 2(x-2) into 2*(x-2)
		if eqn[i] == "(":
			if i != 0:                                      # check if ( is not at the beginning of the equation
				if eqn[i-1] .isdigit() or eqn[i-1] == "x":                     # if a number is left to ( like 2(x-2) or x(x-2)
					eqn = eqn[:i]+"*"+eqn[i:]           # then add a * sign and make it like 2*(x-2) or x*(x-2)
		if eqn[i] == ")":
			if i != len(eqn)-1:
				if eqn[i+1] .isdigit() or eqn[i-1] == "x":                     # if a number is right to ) like (x-2)2 or (x-2)x
					eqn = eqn[:i+1]+"*"+eqn[i+1:]           # then add a * sign and make it like (x-2)*2 or (x-2)*x
	# now check for trignometric terms and make some necessary changes
	if "sin" in eqn:
		eqn = eqn.replace("sin", "math.sin")                # sin(x) should be changed to math.sin(x) as sin(x) is calculated useing the imported math module
	if "cos" in eqn:
		eqn = eqn.replace("cos", "math.cos")            # same as of sin
	if "tan" in eqn:
		eqn = eqn.replace("tan", "math.tan")            # same as of sin
	return eqn                                                      # return the corrected equation

def writeText(text, color, rect, size, returnTextInfo):  # Writes text in the following rect coordinates
    font = pygame.font.SysFont("Comic Sans MS", size, True)
    textObj = font.render(text, True, color, BLACK)         # Created text object with given color and a black background
    textRect = textObj.get_rect()
    if returnTextInfo:  # If returnTextInfo == True i.e if user asks for textObj and textRect info
        return textObj, textRect
    textRect.left = rect.left
    textRect.top = rect.top
    windowSurface.blit(textObj, textRect)

def textBox(text, rect):  # Create a textbox
    font = pygame.font.SysFont("Comic Sans MS", 16, True)
    textObj = font.render(text, True, WHITE, BLACK)
    textRect = rect
    windowSurface.blit(textObj, textRect)
    pygame.draw.rect(windowSurface, WHITE, (textRect.left - 4, textRect.top-2, textRect.width + 4, textRect.height+2), 1)
    return textRect

def highlight(rect, color):  # Highlights the rect rectangle
    pygame.draw.rect(windowSurface, color, (rect.left - 4, rect.top - 2, rect.width + 4, rect.height + 2), 2)

# program starts here
text = "Write your equation here"               # default text to be written in the textbox
HIGHLIGHT = [False, "n"]                   # Holds status about whether to highlight something or not
SELECTED = [False, "n"]                        # tells whether the textbox is selected or not
SHIFT = False                                       # tells whether SHIFT key pressed or not
while True:
	x = y = 0               # initial default value for x and y coordinate of the graph
	windowSurface.fill(BLACK)
	# homePage title
	writeText("Calculator", GREEN, pygame.Rect((WINW-200)/2, 100, 250, 30), 44, False)
	writeText("Graphical", GREEN, pygame.Rect((WINW-200)/2, 50, 250, 30), 44, False)
	# Instructions
	writeText("This graphical calculator supports almost all form of equation.", WHITE, pygame.Rect(20, 180, 0, 0), 14,  False)
	writeText("In trignometric equations, use Sin, Cos and Tan as sin(), cos() and tan().", WHITE, pygame.Rect(20, 200, 0, 0), 14, False)
	writeText("For Sec, Cosec and Cot, use them as reciprocal of Sin, Cos and Tan.", WHITE, pygame.Rect(20, 220, 0, 0), 14, False)
	writeText("Finally, thanks Aritra. Without his help, this wasn't possible :)", WHITE, pygame.Rect(20, 240, 0, 0), 14, False)
	writeText("Operation:", SILVER, pygame.Rect(20, 260, 0, 0), 14, False)
	writeText("Symbol:", SILVER, pygame.Rect(20, 285, 0, 0), 14, False)
	writeText("Add      Subtract        Multiply        Power       Divide", WHITE, pygame.Rect(100, 260, 0, 0), 14, False)
	writeText(" +         -            *         ^          /", WHITE, pygame.Rect(100, 285, 0, 0), 18, False)
	writeText("In the graph page, press 'Backspace' key to get back to this page.", WHITE, pygame.Rect(20, 310, 0, 0), 14, False)
	writeText("If curve is not visible, either the curve is out of range, or the points are invalid.", RED, pygame.Rect(20, 330, 0, 0), 14, False)
	writeText("Change the value of CELLSIZE and MARKINGCELL to increase the range of graph.", RED, pygame.Rect(20, 350, 0, 0), 14, False)
	# textBox
	eqnBox = textBox(text, pygame.Rect((WINW/2)-100, WINH-200, 200, 30))
	writeText("y = ", WHITE, pygame.Rect(eqnBox.left-42, eqnBox.top-3, 20, 20), 18, False)
	# Draw Graph button
	drawObj, drawRect = writeText("Draw Graph", WHITE, pygame.Rect(0, 0, 0, 0), 24, True)
	drawRect.left = (WINW-drawRect.width)/2
	drawRect.width += 5
	drawRect.height += 5
	drawRect.top = eqnBox.bottom + 20
	windowSurface.blit(drawObj, drawRect)
	# event handling
	for event in pygame.event.get():
		if event.type == QUIT:
			pygame.quit()
			sys.exit()
		if event.type == KEYDOWN:
			if event.key == K_ESCAPE:
				pygame.quit()
				sys.exit()
			if event.key == K_LSHIFT or event.key == K_RSHIFT:              # if shift key pressed
				SHIFT = True
			if SELECTED == [True, "e"]:             # make change to text value only if the textbox is selected
				if SHIFT:                                      # if shift key is pressed
					if event.key == ord("6"):           # Shift + 6 = ^
						text += "^"
					if event.key == ord("8"):           # Shift + 8 = *
						text += "*"
					if event.key == ord("9"):            # same as above's
						text += "("
					if event.key == ord("0"):
						text += ")"
					if event.key == ord("="):
						text += "+"
				elif event.key == K_BACKSPACE:
					text = text[:-1]
				else:           # for other keys than that of mentioned above
					text += chr(event.key)
		if event.type == KEYUP:
			if event.key == K_LSHIFT or event.key == K_RSHIFT:          # if shift key released,
				SHIFT = False                                   # update SHIFT status to false
		if event.type == MOUSEMOTION:
			x, y = event.pos
			if eqnBox.colliderect((x, y, 0, 0)):            # if over the textBox,
				HIGHLIGHT = [True, "e"]                     # change highlight status to textbox
			elif drawRect.colliderect((x, y, 0, 0)):        # if text over the 'Draw Graph" button,
				HIGHLIGHT = [True, "b"]                 # change highlight status to the button
			else:
				HIGHLIGHT = [False, "n"]                # else highlight none
		if event.type == MOUSEBUTTONDOWN:
			x, y = event.pos
			if eqnBox.colliderect((x, y, 0, 0)):                # if textbox clicked
				SELECTED = [True, "e"]                          # update SELECTED status
				if text == "Write your equation here":       # if this on the textbox, empty it
					text = ""
			elif drawRect.colliderect((x, y, 0, 0)):          # if the button click
				HIGHLIGHT = [True, "b"]                     # update HIGHLIGHT status
				SELECTED = [True, "b"]                      # update SELECTED status
				try:
					eval(formatEqn(text))         # see if evaluating the equation raises any error
				except:
					# show error message if an error is raised while evaluating the equation
					writeText("Invalid equation!", RED, pygame.Rect(eqnBox.right + 5, eqnBox.top, 0, 0), 18, False)             # show a invalid equation text
					pygame.display.update()                         # update the text
					pygame.time.wait(800)                           # then pause display for 800 milliseconds
					SELECTED = [False, "n"]                     # change SELECTED status to none
			else:                                                       # if mouse clicked elsewhere
				# update HIGHLIGHT and SELECTED status to none
				HIGHLIGHT = [False, "n"]
				SELECTED = [False, "n"]
				if text == "":                  # if nothing written on the textbox,
					text = "Write your equation here"           # update textbox to its default text
	if SELECTED == [True, "e"]:             # if textBox selected
		highlight(eqnBox, RED)              # highlight it
	if HIGHLIGHT[0]:                            # if the highlight status is True
		if HIGHLIGHT[1] == "b":             # if the highlight status is for draw graph button
			highlight(drawRect, RED)
		if HIGHLIGHT[1] == "e":             # if the highlight status is for textbox
			highlight(eqnBox, RED)
	pygame.display.update()
	# codes below is for graph
	while SELECTED == [True, "b"]:
		# draw a white background
		windowSurface.fill(WHITE)
		# draw the graph grids with lines of given color
		drawGrids(GREEN)
		# calculate the points of the graph and plot them on the graph
		drawGraph(formatEqn(text), RED)
		# event handling
		for event in pygame.event.get():
			if event.type == QUIT:
				pygame.quit()
				sys.exit()
			if event.type == KEYDOWN:
				if event.key == K_ESCAPE:
					pygame.quit()
					sys.exit()
				if event.key == K_BACKSPACE:
					# while going back to starting page
					SELECTED = [False, "n"]             # This will break the current while loop
					text = "Write your equation here"
		pygame.display.update()
