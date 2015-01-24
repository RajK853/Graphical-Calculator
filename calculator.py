import sys
import math
import pygame
from pygame.locals import *

pygame.init()

# set up window
WINW = WINH = 600
assert WINW > 400 and WINH > 400, "Window's width and height too small."
windowSurface = pygame.display.set_mode((WINW, WINH))
pygame.display.set_caption("Graphical Calculator")

# set up color
RED = (200, 0, 30)      # custom red
BLACK = (0, 0, 0)
SILVER = (140, 140, 140)
GREEN = (0, 100, 0)
WHITE = (255, 255, 255)
BLUE = (0, 100, 200)            # custom blue

# set up constants
CELLSIZE = 10  # Determine the pixel size of smallest square. Try to keep CELLSIZE a multiple of 5
MARKINGCELL = 5  # tells how many boxes should be equal to value 1 in the measurement scale


def drawGrids(color):  # draw the horizontal and vertical grids
	global origin
	if color == WHITE:  # If numbers' color is chosen WHITE
		nColor = BLACK  # change their background to BLACK
	else:
		nColor = WHITE  # else keep the numbers' background WHITE
	a = -int(WINW / (2 * MARKINGCELL * CELLSIZE))  # a = minimum vaue of x-coordinate and y coordinate. Value of a will be the numbers to be labeled
	n = 1
	NUMBERS = []                # stores numbers to be written on the axes and their rectangle values
	for i in range(CELLSIZE, WINW, CELLSIZE):
		if n % MARKINGCELL == 0:  # for every MARKINGCELL small squares apart, draw a bold line
			a += 1
			if a != 0:  # when not at origin. a == 0 at the origin.
				pygame.draw.line(windowSurface, color, (i, 0), (i, WINH), 2)  # make a vertical line
				pygame.draw.line(windowSurface, color, (0, i), (WINW, i), 2)  # make a horizontal line
				hNumber = pygame.font.SysFont(None, 20).render(str(a), True, color,
				                                               nColor)  # Numbering in the horizontal x-axis
				vNumber = pygame.font.SysFont(None, 20).render(str(-a), True, color,
				                                               nColor)  # Numbering in the vertical x-axis
				hNumRect = hNumber.get_rect()  # hNumRect is for number in horizontal scale
				vNumRect = vNumber.get_rect()  # vNumRect is for number in vertical scale
				hNumRect.topleft = (i - 3, 0)  # y coordinates in horizontal line will be later changed to origin's y
				vNumRect.topleft = (0, i - 3)  # x coordinates in vertical line will be later changed to origin's x
				NUMBERS.append((hNumber, hNumRect))
				NUMBERS.append((vNumber, vNumRect))
			else:
				# when at origin, draw a bold horizontal and vertical line
				pygame.draw.line(windowSurface, color, (i, 0), (i, WINH), 3)
				pygame.draw.line(windowSurface, color, (0, i), (WINW, i), 3)
				origin = i  # pixel coordinate of origin saved
		else:  # ordinary lines
			pygame.draw.line(windowSurface, color, (i, 0), (i, WINH), 1)  # make a vertical line
			pygame.draw.line(windowSurface, color, (0, i), (WINH, i), 1)  # make a horizontal line
		n += 1
	pygame.draw.rect(windowSurface, color, (0, 0, WINW, WINH), 1)  # draw a rectangle at the margin of the graph
	for num, rect in NUMBERS:  # loop over NUMBERS and their position i.e rect
		if rect.top == 0:  # top = 0 means y = 0 which is for numbering at x-axis
			rect.top = origin + 3  # y coordinate of numbers at x-axis kept little bit below from the x-axis line
		if rect.left == 0:  # left = 0 means x = 0 which is for numbering at y-axis
			rect.left = origin + 3  # x coordinate of numbers at y-axis kept little bit left from the y-axis line
		windowSurface.blit(num, rect)  # draw each number over on their given position


def drawGraph(eqn, color):  # calculates x and y coordinates of the graph and then plots them
	global ALLPOINTS
	POINTS = []  # holds all the points of the graph as (x, y)
	max = int(WINW / (2 * MARKINGCELL * CELLSIZE))  # max = maximum x and y coordinate value.
	for n in range(-WINW, WINW):  # n = pixel coordinates for each point which will be 1 pixel apart from its nearby points
		x = n / (2 * MARKINGCELL * CELLSIZE)  # convert pixel coordinate into actual x coordinate
		try:
			y = eval(eqn)
		except (ValueError, ZeroDivisionError):  # if zero divison error occurs by dividing with zero or ValueError occurs for log(negative x)
			y = complex(0)  # turn y to complex number so that it can be treated differently later
		if type(y) == complex:  # if the y coordinate is a complex number because of the ZeroDivisionError or y was root of negative x
			POINTS.append((round((max + x) * MARKINGCELL * CELLSIZE), y))  # adding the complex y coordinate directly to the POINTS list
		else:  # if ordinary point.
			# converts the x and y coordiantes into pixels
			POINTS.append((round((max + x) * MARKINGCELL * CELLSIZE), round((max - y) * MARKINGCELL * CELLSIZE)))
	# loop over each point in POINTS and plot them in the graph
	INVALIDPOINTS = []          # holds the imaginary points which will be remoed after the graph is plotted
	for p in range(len(POINTS)):
		try:  # error is raised when last point has no other point to join to form a line i.e p+1 raises IndexError
			if type(POINTS[p][1]) == complex or type(POINTS[p + 1][1]) == complex:  # if one of the terminal point of the line has a complex y coordinate
				# don't plot the point with y coordinate a complex number
				if type(POINTS[p][1]) == complex:               # check if the starting point of the line is a complex number
					if POINTS[p] not in INVALIDPOINTS:          # append the point only if the invalid point is not present in the INVALIDPOINTS
						INVALIDPOINTS.append(POINTS[p])
				else:                                                           # else the final point of the line is a complex number
					if POINTS[p+1] not in INVALIDPOINTS:
						INVALIDPOINTS.append(POINTS[p+1])
			else:  # if ordinary point
				pygame.draw.line(windowSurface, color, POINTS[p], POINTS[p + 1], 2)     # draw line joining the current point and next point
		except (IndexError, TypeError):  # indexError occurs when the last point with index p is achieved and there is not p+1 index in POINTS list
			pass  # do nothing
	for points in INVALIDPOINTS:
		# loops over each point in the INVALIDPOINTS and removes them one by one
		POINTS.remove(points)
	ALLPOINTS += POINTS             # store points of current equation to ALLPOINTS list


def formatEqn(rawEqn):  # Looks over the equation given by the user and corrects some mistake before it is drawn on the graph
	eqn = rawEqn.split()  # remove spaces by splitting in every space converting the string into a list
	eqn = "".join(eqn)  # convert the list back to a string with no space in between
	eqn = eqn.replace("^", "**")  # replace all ^ signs with ** sign as in python ** is for power.
	for i in range(len(eqn)-1, -1, -1):
	# we loop backward from last item to 1st because changing ^ to ** will change length of eqn and might be problem while looping from index 0 to last index
		# add * sign between x coordinate or exponential e and a constant if the user writes 2*x as 2x or 2*e as 2e.
		if eqn[i] == "e":  # check if the current item of the loop is the  e
			if i != 0:  # check if the index of  e is not 0. If i == 0, checking if [i-1] item (i.e item left to e) of the eqn will raise a index-out-of-range error
				if eqn[i - 1].isdigit():  # check if item left to e is a digit
					# if true for above condition, it means the equation is like 2e. So now we slice and put "*" sign between the coefficient and e and make it 2*e
					eqn = eqn[:i] + "*" + eqn[i:]
		if eqn[i] == "x":  # check if the current item of the loop is the x or e
			if i != 0:  # check if the index of x or e is not 0. If i == 0, checking if [i-1] item (i.e item left to x or e) of the eqn will raise a index-out-of-range error
				if eqn[i-1].isdigit():  # check if item left to x or e is a digit
					# if true for above condition, it means the equation is like 2x or 2e. So now we slice and put "*" sign between the coefficient and x and make it 2*x or 2*e
					eqn = eqn[:i] + "*" + eqn[i:]
			if i != len(eqn)-1:  # check if the index doesn't indicate the last digit of the equation. If it is the last digit, checking for item right to it i.e i+1 will raise a index-out-of-range error
				if eqn[i+1].isdigit():  # check if item right to x is a digit
					# if true for above condition, it means the equation is like x2 . So now we slice and put "*" sign between the coefficient and x and make it x*2
					eqn = eqn[:i+1] + "*" + eqn[i+1:]
		# add * sign between any item and ( or ) signs if needed. eg change 2(x-2) into 2*(x-2)
		if eqn[i] == "(":
			if i != 0:  # check if ( is not at the beginning of the equation
				if eqn[i-1].isdigit() or eqn[i-1] == "x" or eqn[i-1] == ")":  # if a number or x is left to ( like 2(x-2) or x(x-2) or (x-1)(x+2)
					eqn = eqn[:i] + "*" + eqn[i:]  # then add a * sign and make it like 2*(x-2) or x*(x-2) or (x-1)*(x+2)
		if eqn[i] == ")":
			if i != len(eqn) - 1:               # ) is not the last item as in (x-2)
				if eqn[i+1].isdigit() or eqn[i+1] == "x":  # if a number or x is right to ) like (x-2)2 or (x-2)x
					eqn = eqn[:i+1] + "*" + eqn[i+1:]  # then add a * sign and make it like (x-2)*2 or (x-2)*x
	# now check for trignometric terms and make some necessary changes
	if "sin" in eqn:
		eqn = eqn.replace("sin", "math.sin(")  # sin(x) should be changed to math.sin(x)
		if "sin((" in eqn:  # check if the sin(x) eqn is changed to math.sin((x).
			eqn = eqn.replace("sin((", "sin(")  # if math.sin((x) present, rremove one (
	if "cos" in eqn:
		eqn = eqn.replace("cos", "math.cos(")  # same as of sin
		if "cos((" in eqn:  # same as of sin((x)
			eqn = eqn.replace("cos((", "cos(")
	if "tan" in eqn:
		eqn = eqn.replace("tan", "math.tan(")  # same as of sin
		if "tan((" in eqn:  # same as of sin((x)
			eqn = eqn.replace("tan((", "tan(")
	# now check for exponential and logarithmic equations and make necessary changes
	if "e" in eqn:  # check for exponential expression
		eqn = eqn.replace("e", "math.e")
	if "log" in eqn:
		eqn = eqn.replace("log", "math.log")
	# check if there is equal number of ( and ) to check incase if user typed sin(x or ((x-2)+5
	if eqn.count("(") != eqn.count(")"):
		toAdd = abs(eqn.count("(") - eqn.count(")"))  # determines how many brackets are missing and needed to be added
		if eqn.count("(") > eqn.count(")"):  # if there are more ( than ) like ((x-2+4
			eqn += toAdd * ")"  # if yes, add required number of ) at the end of the equation
		else:  # if there are more ) than ( like (x-2))
			eqn = toAdd * "(" + eqn  # add required number of ( at the begining of the equation
	if eqn == "":               # "SyntaxError: unexpected EOF while parsing" arises if eqn is empty which happens when textbox has only spaces
		return "0"
	else:               # if eqn is not empty, return eqn
		return eqn  # return the corrected equation


def writeText(text, surface, color, rect, size, returnTextInfo):  # Writes text in the following rect coordinates
	font = pygame.font.SysFont("Comic Sans MS", size, True)
	textObj = font.render(text, True, color)  # Created text object with given color and a black background
	textRect = textObj.get_rect()
	textRect.left = rect.left
	textRect.top = rect.top
	if returnTextInfo:  # If returnTextInfo == True i.e if user asks for textObj and textRect info
		return textObj, textRect
	surface.blit(textObj, textRect)


def textBox(text, color, rect):  # Create a textbox
	font = pygame.font.SysFont("Comic Sans MS", 16, True)
	textObj = font.render(text, True, color, BLACK)
	textRect = rect
	windowSurface.blit(textObj, textRect)
	# draw a rectangule for textbox
	pygame.draw.rect(windowSurface, WHITE, (textRect.left - 4, textRect.top - 2, textRect.width + 4, textRect.height + 2), 1)
	return textRect


def highlight(rect, color):  # Highlights the rect rectangle
	pygame.draw.rect(windowSurface, color, (rect.left - 4, rect.top - 2, rect.width + 4, rect.height + 2), 2)


def zoomButtons(color):
	global CELLSIZE, MARKINGCELL, zoomIn, zoomOut
	transparentSurface = windowSurface.convert_alpha()
	transparentSurface.fill((0, 0, 0, 0))  # Fill transparentSurface with a totally transparent background color
	OPAQUE = (100,)  # Tells how much opaque our zoom buttons should .
	color += OPAQUE  # convert the color into a transparent color by adding a fourth item in the color tuple
	writeText("-", transparentSurface, color, pygame.Rect(10, -10, 0, 0), 34, False)  # write - sign  for zoomOut symbol
	writeText("+", transparentSurface, color, pygame.Rect(55, -9, 0, 0), 34, False)  # write + sign for zoomIn symbol
	zoomOut = pygame.draw.circle(transparentSurface, color, (20, 20), 20, 4)  # make a circle for zoonOut button
	zoomIn = pygame.draw.circle(transparentSurface, color, (65, 20), 20, 4)  # make a circle for zoomIn button
	windowSurface.blit(transparentSurface, (0, 0, WINH, WINH))


def makeButton(text, size, rect, centerx, centery):  # creates a button with given text written on it
	buttonObj, buttonRect = writeText(text, windowSurface, WHITE, rect, size,
	                                  True)  # Writes the text of the button and returns its rectangle value and text object
	if centerx:  # if user want to put the button horizontally at mid of the screen
		buttonRect.centerx = WINW / 2
	if centery:  # if user want to put the button vertically at mid of the screen
		buttonRect.centery = WINH / 2
	# make rectangle abit larger than the text
	buttonRect.width += 5
	buttonRect.height += 3
	windowSurface.blit(buttonObj, buttonRect)
	return buttonRect  # return the buttonRect value


def instructions(HIGHLIGHT):                # displays information about the program
	while True:
		windowSurface.fill(BLACK)
		# Instructions
		writeText("This graphical calculator supports almost all form of equation.", windowSurface, WHITE,
		          pygame.Rect(25, 150, 0, 0), 14, False)
		writeText("Use Sin, Cos and Tan as sin(), cos() and tan().", windowSurface, WHITE, pygame.Rect(25, 170, 0, 0),
		          14, False)
		writeText("For Sec, Cosec and Cot, use them as reciprocal of Sin, Cos and Tan.", windowSurface, WHITE,
		          pygame.Rect(25, 190, 0, 0), 14, False)
		writeText("For exponential and logarithm use e^() & log(x, base).", windowSurface,WHITE,
		          pygame.Rect(25, 210, 0, 0), 14, False)
		writeText("Operation:", windowSurface, SILVER, pygame.Rect(25, 230, 0, 0), 14, False)
		writeText("Symbol:", windowSurface, SILVER, pygame.Rect(25, 255, 0, 0), 14, False)
		writeText("Add      Subtract        Multiply        Power       Divide", windowSurface, WHITE,
		          pygame.Rect(105, 230, 0, 0), 14, False)
		writeText(" +         -            *         ^          /", windowSurface, WHITE, pygame.Rect(105, 255, 0, 0),
		          18, False)
		writeText("If curve is not visible, either the curve is out of range, or the points are invalid.",
		          windowSurface, RED, pygame.Rect(25, 300, 0, 0), 14, False)
		writeText("Use the zoom in or zoom out buttons to increase the range of graph.", windowSurface, RED,
		          pygame.Rect(25, 320, 0, 0), 14, False)
		# draw a back button
		backRect = makeButton("Back", 24, pygame.Rect(25, 60, 0, 0), False, False)
		# event handling the QUIT and KEYDOWN events to close the program. and MOUSEMOTION
		# event to highlight the Back button and MOUSEBUTTONDOWN event to use the Back button
		for event in pygame.event.get():
			if event.type == QUIT:
				pygame.quit()
				sys.exit()
			if event.type == MOUSEMOTION:
				xm, ym = event.pos
				if backRect.colliderect((xm, ym, 0, 0)):
					HIGHLIGHT = [True, "b"]             # change highlight status to back button if move over it
				else:
					HIGHLIGHT = [False, "n"]            # else change highlight option to none
			if event.type == MOUSEBUTTONDOWN:
				xm, ym = event.pos
				if backRect.colliderect((xm, ym, 0, 0)):
					return                  # if back button clicked, go out of this function
			if event.type == KEYDOWN:
				if event.key == K_ESCAPE:
					pygame.quit()
					sys.exit()
		# highlighting the back button
		if HIGHLIGHT[0]:
			highlight(backRect, RED)
		pygame.display.update()


def getDirections():            # generates the list of directions to look for the points
	dir = [[0, 0]]
	for d in [1]:               # the values in the list are the pixel values around the mouse where points will be searched from ALLPOINTS list
		dir += [-d, -d], [0, -d], [d, -d], [d, 0], [d, d], [0, d], [-d, d], [0, -d]        # make all possible order for given d pixel
	return dir


def isOnCurve(x, y, dir):            # returns true if mouse is over the curve or line
	# Creating a rectangle around the mouse and looping over each point and checking if the point collide with the rect
	# was  effective. But there are around or even more than 1000 points in ALLPOINTS. So it slowed down the program alot.
	# So instead of looping over those 1000 points, we create some possible points at certain pixel around the mouse position and check if
	# one of those points is in the ALLPOINTS. This process is abit fast as we have to loop over less items compared to over 1000 points.
	for xdir, ydir in dir:
	# checks at given pixels distance around the mouse in all direction
		if (x-xdir, y-ydir) in ALLPOINTS:                           # if any of the point in the ALLPOINTS in the 1 pixel radius around the mouse
			return True               # return True
	return False                    # else return False


def showPoint(x, y):     # displays the point of the curve where the mouse is over
	# convert the pixel position of the mouse into x and y coordinates of the graph
	points = (round((x-origin)/(CELLSIZE*MARKINGCELL), 1), round((origin-y)/(CELLSIZE*MARKINGCELL), 1))
	# write a text with the above points
	pointObj, pointRect = writeText("(%s, %s)" % points, windowSurface, BLACK, pygame.Rect(x+5, y-20, 0, 0), 14, True)
	# check if the rectangle passes across the window screen
	if pointRect.right > WINW:          # if rect passes across the right side of the screen
		pointRect.right = WINW
	if pointRect.top < 0:                   # if rect passes across the top side of the screen
		pointRect.top = 0
	# draw a white rectangle over which the points will be shown
	pygame.draw.rect(windowSurface, WHITE, pointRect)
	# draw the points over the white rectangle
	windowSurface.blit(pointObj, pointRect)

def main():
	global ALLPOINTS, CELLSIZE, MARKINGCELL
	# program starts here
	text1 = text2 = "Write your equation here"  # default texts to be written in the textboxes
	HIGHLIGHT = [False, "n"]  # Holds status about whether to highlight something or not
	SELECTED = [False, "n"]  # tells whether the textbox is selected or not
	SHIFT = False  # tells whether SHIFT key pressed or not
	mouseOnCurve = False          # tells if mouse is over the curve
	dir = getDirections()           # gets direction to use for isOnCurve function
	while True:  # main program loop
		windowSurface.fill(BLACK)
		# homePage title
		writeText("Calculator", windowSurface, GREEN, pygame.Rect(10 + (WINW)/4, 110, 250, 30), 60, False)
		writeText("Graphical", windowSurface, GREEN, pygame.Rect(15 + (WINW)/4, 50, 250, 30), 60, False)
		# instruction to come back from the graph
		writeText("Press 'Backspace' key to get back to this page.", windowSurface, WHITE,pygame.Rect((WINW/4) - 10, 250, 100, 0), 14, False)
		writeText("Place the cursor over the curve to see its point.", windowSurface, WHITE,pygame.Rect((WINW/4) - 10, 275, 100, 0), 14, False)
		# textBox
		eqnBox1 = textBox(text1, RED, pygame.Rect((WINW / 2) - 100, WINH - 250, 200, 30))
		eqnBox2 = textBox(text2, BLUE, pygame.Rect((WINW / 2) - 100, WINH - 200, 200, 30))
		writeText("y = ", windowSurface, RED, pygame.Rect(eqnBox1.left - 42, eqnBox1.top - 3, 20, 20), 18, False)
		writeText("y = ", windowSurface, BLUE, pygame.Rect(eqnBox2.left - 42, eqnBox2.top - 3, 20, 20), 18, False)
		# Draw Graph button
		drawRect = makeButton("Draw Graph", 24, pygame.Rect(0, eqnBox2.bottom + 10, 0, 0), True, False)
		# Help Button
		helpRect = makeButton("Help", 24, pygame.Rect(WINW - 135, 60, 0, 0), False, False)
		# event handling
		for event in pygame.event.get():
			if event.type == QUIT:
				pygame.quit()
				sys.exit()
			if event.type == KEYDOWN:
				if event.key == K_ESCAPE:
					pygame.quit()
					sys.exit()
				if event.key == K_LSHIFT or event.key == K_RSHIFT:  # if shift key pressed
					SHIFT = True
				if SELECTED[0]:  # make change to text value only if the textbox is selected
					if SELECTED[1] == "e1":
						text = text1
					else:
						text = text2
					if SHIFT:  # if shift key is pressed
						if event.key == ord("6"):  # Shift + 6 = ^
							text += "^"
						if event.key == ord("8"):  # Shift + 8 = *
							text += "*"
						if event.key == ord("9"):  # same as above's
							text += "("
						if event.key == ord("0"):
							text += ")"
						if event.key == ord("="):
							text += "+"
					elif event.key == K_BACKSPACE:              # slice and remove the last item
						text = text[:-1]
					elif event.key == K_TAB:
						if SELECTED[0]:             # change selection of textbox by pressing Tab
							if SELECTED[1] == "e1":         # is 1st textbox was selected before the tab was clicked
								# store the current string in text to text1
								text1 = text
								# store 2nd textbox's strings to text variable
								text = text2
								# change the selection to 2nd textbox if the 1st textbox is selected
								SELECTED[1] = "e2"
								if text1 == "":  # if nothing written on the 1st textbox,
									text1 = "Write your equation here"  # update 1st textbox to its default text
							elif SELECTED[1] == "e2":
								# store the current string in text to text2
								text2 = text
								# store 1st textbox's strings to text variable
								text = text1
								# change the selection to 1st textbox if the 2nd textbox is selected
								SELECTED[1] = "e1"
								if text2 == "":         # same as for 1st textbox
									text2 = "Write your equation here"
					else:  # for other keys than that of mentioned above
						text += chr(event.key)
					if SELECTED[1] == "e1":
						text1 = text
					else:
						text2 = text
			if event.type == KEYUP:
				if event.key == K_LSHIFT or event.key == K_RSHIFT:  # if shift key released,
					SHIFT = False  # update SHIFT status to false
			if event.type == MOUSEMOTION:
				xm, ym = event.pos
				if eqnBox1.colliderect((xm, ym, 0, 0)):  # if over the 1st textBox,
					HIGHLIGHT = [True, "e1"]  # change highlight status to 1st textbox
				elif eqnBox2.colliderect((xm, ym, 0, 0)):  # if over the 2nd textBox,
					HIGHLIGHT = [True, "e2"]  # change highlight status to 2nd textbox
				elif drawRect.colliderect((xm, ym, 0, 0)):  # if text over the 'Draw Graph" button,
					HIGHLIGHT = [True, "d"]  # change highlight status to the button
				elif helpRect.colliderect((xm, ym, 0, 0)):
					HIGHLIGHT = [True, "h"]
				else:
					HIGHLIGHT = [False, "n"]  # else highlight none
			if event.type == MOUSEBUTTONDOWN:
				xm, ym = event.pos
				if eqnBox1.colliderect((xm, ym, 0, 0)):  # if 1st textbox clicked
					SELECTED = [True, "e1"]  # update SELECTED status
					if text2 == "":         # if 2nd text box is empty
						text2 = "Write your equation here"      # update it
				elif eqnBox2.colliderect((xm, ym, 0, 0)):  # if 2nd textbox clicked
					SELECTED = [True, "e2"]  # update SELECTED status
					if text1 == "":         # if 1st text box is empty
						text1 = "Write your equation here"  #  update it
				elif helpRect.colliderect((xm, ym, 0, 0)):
					# go to instructions function if help button clicked
					instructions(HIGHLIGHT)
				elif drawRect.colliderect((xm, ym, 0, 0)):  # if the button click
					HIGHLIGHT = [True, "d"]  # update HIGHLIGHT status
					SELECTED = [True, "d"]  # update SELECTED status
					errorIn = []            # holds in which text NameError occurs
					for i in range(len([text1, text2])):
						try:
							x = 1.111  # value of x put to a number to eval and check the equation
							eval(formatEqn([text1, text2][i]))  # see if evaluating the equation raises NameError
						except (NameError, TypeError):
							if i == 0:                          # if index is 0
								errorIn.append("1")             # there was error in 1st textBox
							else:                               # if index is not 0 i.e 1
								errorIn.append("2")             # there was error in 2nd textBox
					if len(errorIn) == 2:        # if there is error in both textboxes
						# show error message if an error is raised while evaluating the equation
						writeText("Invalid equation!", windowSurface, RED, pygame.Rect(eqnBox1.right + 5, eqnBox1.top, 0, 0),18, False)     # show error message beside 1st textbox
						writeText("Invalid equation!", windowSurface, RED, pygame.Rect(eqnBox2.right + 5, eqnBox2.top, 0, 0),18, False)     # show error message beside 2nd textbox
						pygame.display.update()  # update the text before pausing the display
						pygame.time.wait(800)
						SELECTED = [False, "n"]  # change SELECTED status to none
				else:  # if mouse clicked elsewhere
					if text1 == "":  # if nothing written on the 1st textbox,
						text1 = "Write your equation here"  # update 1st textbox to its default text
					if text2 == "":         # same as for 1st textbox
						text2 = "Write your equation here"
					# update HIGHLIGHT and SELECTED status to none
					HIGHLIGHT = [False, "n"]
					SELECTED = [False, "n"]
		if SELECTED[0]:  # if any textBox selected
			if SELECTED[1] == "e1":
				if text1 == "Write your equation here":  # if this on the textbox, empty it
					text1 = ""
				highlight(eqnBox1, RED)  # highlight 1st textbox
			elif SELECTED[1] == "e2":
				if text2 == "Write your equation here":  # if this on the textbox, empty it
					text2 = ""
				highlight(eqnBox2, BLUE)
		if HIGHLIGHT[0]:  # if the highlight status is True
			if HIGHLIGHT[1] == "d":  # if the highlight status is for draw graph button
				highlight(drawRect, WHITE)
			if HIGHLIGHT[1] == "e1":  # if the highlight status is for 1st textbox
				highlight(eqnBox1, RED)
			if HIGHLIGHT[1] == "e2":  # if the highlight status is for 2nd textbox
				highlight(eqnBox2, BLUE)
			if HIGHLIGHT[1] == "h":  # if the highlight status is for help button
				highlight(helpRect, WHITE)
		pygame.display.update()
		# codes below is for graph
		while SELECTED == [True, "d"]:
			ALLPOINTS = []                  # stores points of the equations
			EVENT = False                   # tells if any event happened. Set it to false
			windowSurface.fill(WHITE)
			# draw the graph grids with lines of given color
			drawGrids(GREEN)
			# loop over both textboxes and only draw graph of the one with a valid equation
			if "1" not in errorIn:	              # if the equation in the 1st textbox don't have error
				# calculate the points of the graph of the 1st equation and plot them on the graph
				drawGraph(formatEqn(text1), RED)
			if "2" not in errorIn:               # if the equation in the 2nd textbox don't have error
				# calculate the points of the graph  of the 2nd equation and plot them on the graph
				drawGraph(formatEqn(text2), BLUE)
			# draw zoom buttons
			zoomButtons(RED)
			# the program will only loop over the event handling part until any event ocuurs
			# this will speed up the program as the graph will not be draw again and again even if the program is idle
			while not EVENT:
				for event in pygame.event.get():
					if event.type == QUIT:
						pygame.quit()
						sys.exit()
					if event.type == KEYDOWN:
						EVENT = True
						if event.key == K_ESCAPE:
							pygame.quit()
							sys.exit()
						if event.key == K_BACKSPACE:
							# while going back to starting page
							SELECTED = [False, "n"]  # This will break the current while loop
							# return graph values to default
							MARKINGCELL = 5
							CELLSIZE = 10
					if event.type == MOUSEMOTION:
						xm, ym = event.pos
						mouseOnCurve = isOnCurve(xm, ym, dir)           # check if mouse is over any point of the curve
					if event.type == MOUSEBUTTONDOWN:
						EVENT = True
						xm, ym = event.pos
						if zoomOut.colliderect((xm, ym, 0, 0)):  # if clicked on zoomout button
							# zoom out is achieved by reducing the marking intervals between each number intervals in the axes
							if 2 < MARKINGCELL <= 15:  # Limit the value of MARKINGCELL from 2-15 or else the numbering in the graph will overlap or disappear
								# reduce MARKINGCELL value so that now numbers are marked in the axes at less interval
								MARKINGCELL -= 1
						elif zoomIn.colliderect((xm, ym, 0, 0)):  # if clicked on zoomIn button
							# zoom in is achieved by doing the opposite of zoom out
							if MARKINGCELL < 15:  # Increase MARKINGCELL value only if it is less than 15
								MARKINGCELL += 1
				if mouseOnCurve:            # if mouse is over the curve
					EVENT = True
					showPoint(xm, ym)               # show the point over which the mouse is
				pygame.display.update()

if __name__ == "__main__":
	main()
