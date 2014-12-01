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
CELLSIZE = 5                # Try to keep CELLSIZE a multiple of 5
XMAXLIMIT = int(WINW/(20*CELLSIZE))     # Maximum x coordinate
XMINLIMIT = -XMAXLIMIT                              # Minimum x coordinate
YMAXLIMIT = XMAXLIMIT                           # Maximum y coordinate
YMINLINIT = -YMAXLIMIT                              # Minimum y coordinate

def drawGrids(color):           # draw the horizontal and vertical grids
	if color == WHITE:
		nColor = BLACK
	else:
		nColor = WHITE
	a = XMINLIMIT
	n = 1
	NUMBERS = []
	for i in range(CELLSIZE, WINW, CELLSIZE):
		if n % 10 == 0:         # for every 10 small squares apart, draw a bold line
			pygame.draw.line(windowSurface, color, (i, 0), (i, WINH), 2)      # make a vertical line
			pygame.draw.line(windowSurface, color, (0, i), (WINH, i), 2)       # make a horizontal line
			a += 1
			if a != 0:
				hNumber = pygame.font.SysFont(None, 24).render(str(a), True, color, nColor)
				vNumber = pygame.font.SysFont(None, 24).render(str(-a), True, color, nColor)
				hNumRect = hNumber.get_rect()            # hNumRect is for number in horizontal scale
				vNumRect = vNumber.get_rect()             # vNumRect is for number in vertical scale
				hNumRect.topleft = (i-3, 3+10*CELLSIZE*XMAXLIMIT)
				vNumRect.topleft = (3+10*CELLSIZE*XMAXLIMIT, i-3)
				NUMBERS.append((hNumber, hNumRect))
				NUMBERS.append((vNumber, vNumRect))
			else:
				pygame.draw.line(windowSurface, color, (i, 0), (i, WINH), 3)
				pygame.draw.line(windowSurface, color, (0, i), (WINW, i), 3)
		else:
			pygame.draw.line(windowSurface, color, (i, 0), (i, WINH), 1)      # make a vertical line
			pygame.draw.line(windowSurface, color, (0, i), (WINH, i), 1)       # make a horizontal line
		n += 1
	pygame.draw.rect(windowSurface, color, (0, 0, WINW, WINH), 1)
	for num, rect in NUMBERS:
		windowSurface.blit(num, rect)

def drawGraph(constants, rule, color):                    # calculates x and y coordinates of the graph and then plots them
	global x
	POINTS = []
	l = XMAXLIMIT
	for n in range(-WINW, WINW, 2*CELLSIZE):            # n = pixel coordinates
		x = n/(20*CELLSIZE)               # convert pixel coordinate into actual x coordinate
		first = True
		aNum = sNum = mNum = dNum = pNum = 0
		for r in rule.split("."):
			if rule.index(r) == 0 and first:
				if constants["x"] == 0:
					y = 0
				else:
					y = x
				first = False
			if r == "a":
				y += constants[r][aNum]
				aNum += 1
			if r == "s":
				y -= constants[r][sNum]
				sNum += 1
			if r == "m":
				y *= constants[r][mNum]
				mNum += 1
			if r == "d":
				y /= constants[r][dNum]
				dNum += 1
			if r == "p":
				y = (y)**constants[r][pNum]
				pNum += 1
			elif r == "sin":
				y = math.sin(y)
			elif r == "cos":
				y = math.cos(y)
			elif r == "tan":
				y = math.tan(y)
		POINTS.append(((l+x)*10*CELLSIZE, round((l-y)*10*CELLSIZE, 1)))
	for p in range(len(POINTS)):
		try:
			pygame.draw.line(windowSurface, color, POINTS[p], POINTS[p+1], 2)
		except:                 # when last point has no other point to join and form a line
			pass

def generateRawEqn(eqn):
	eqn = eqn.split()               # split at spaces to remove them
	eqn = "".join(eqn)              # convert the list back to a string with no space in between
	SYMBOLS = {"(" : "b", ")" : "b", "+" : "a", "-" : "s", "x" : "x", "/" : "d", "^" : "p"}
	rawEqn = ""         # store converted equation as symbols. For eg (2*x+3) will be converted to m2xa3 where m2 means multiply 2 and a3 means add 3.
	num = ""              # stores the current number over which the program is looping
	prev = ""             # tells what item was there just before the current item the program is looping
	if "x" not in eqn:
		return eqn
	for i in range(len(eqn)):               # loop over the equation
		if (not eqn[i].isdigit()) and eqn[i] != "*":
			if eqn[i] == "-" and prev == "*":
				rawEqn += eqn[i]
			else:
				rawEqn += SYMBOLS[eqn[i]]
				prev = eqn[i]
			num = ""
			# The code between this and above comment was shortened from 16 lin to 4 line
		if eqn[i] == "*":
			if prev.isdigit():
				rawEqn = rawEqn[:-1]+"m"+num
			else:
				rawEqn += "m"
				prev = "*"
		if eqn[i].isdigit():
			num += eqn[i]
			if prev in ["*", "+", "-", "/", "^"]:
				try:
					if eqn[i+1] == "*":
						if prev == "-":
							prev = num
							num = str(-1*int(num))
						elif prev == "+":
							rawEqn = rawEqn[:-1]
							prev = num
						else:
							rawEqn += num
							num = ""
					else:
						rawEqn += num
						num = ""
				except:
					rawEqn += num
			else:
				prev = num
	return rawEqn

def generateRuleAndConstant(rawEqn):
	constants = {"p" : [], "d" : [], "m" : [], "a" : [], "s" : [], "x" : 1}                  # BODMAS rule change to BPDMAS rule where P = Increase power by an integer
	rule = ""
	try:
		num = eval(rawEqn)
		if num < 0:
			constants["s"].append(-num)
			rule += "s."
			constants["x"] = 0
			return constants, rule
		else:
			constants["a"].append(num)
			rule += "a."
			constants["x"] = 0
			return constants, rule
	except:
		pass
	if "b" in rawEqn and rawEqn.count("b") == 2:                    # if the only 2"b" symbols for bracket are present
		b1 = rawEqn.find("b")
		b2 = rawEqn.rfind("b")
		inBracket = rawEqn[b1+1:b2]                                 # slice the terms inside the brackets(b) in the rawEqn
		for j in ["p", "d", "m", "a", "s"]:
			for i in range(0, len(inBracket)):                        # loops over the terms in the inBracket
				if inBracket[i] == j:
					rule += j+"."
					num = ""
					try:
						while inBracket[i+1].isdigit():
							num += inBracket[i+1]
							i += 1
					except:
						pass
					i -= 1
					num = int(num)
					constants[j].append(num)
	try:
		outBracket =rawEqn[0:b1]+rawEqn[b2+1:]             # slice and get terms outside the brackets
	except:     # above wil raise error is there were not brackets in the equation
		outBracket = rawEqn             # if there was not bracket in the equation, use the whole rawEqn
	for j in ["p", "d", "m", "a", "s"]:
		for i in range(0, len(outBracket)):                        # loops over the terms in the outBracket
			if outBracket[i] == j:
				rule += j+"."
				num = ""
				try:                        # using try-except statement because outBracket will encounter the error "index out of range" when it reaches 2nd last term
					while outBracket[i+1].isdigit() or outBracket[i+1] == "-":
						num += outBracket[i+1]
						i += 1
				except:
					pass
				i -= 1
				num = int(num)
				constants[j].append(num)
	return constants, rule

def writeText(text, color, rect, size, returnTextInfo):  # Writes text in the following rect coordinates
    font = pygame.font.SysFont("Comic Sans MS", size, True)
    textObj = font.render(text, True, color, BLACK)
    textRect = textObj.get_rect()
    if returnTextInfo:  # If returnTextInfo == True
        return textObj, textRect
    textRect.left = rect.left
    textRect.top = rect.top
    windowSurface.blit(textObj, textRect)

def textBox(text, rect):  # Create a textbox
    font = pygame.font.SysFont("Comic Sans MS", 16)
    textObj = font.render(text, True, WHITE, BLACK)
    #textRect = textObj.get_rect()
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
	# Instruction
	writeText("Right now the number of equation this graphical calculator can plot is limited.", WHITE, pygame.Rect(20, 180, 0, 0), 14,  False)
	writeText("It only supports equation with only one 'x' coordinate.", WHITE, pygame.Rect(20, 200, 0, 0), 14, False)
	writeText("Only one pair of bracket is supported in a equation.", WHITE, pygame.Rect(20, 220, 0, 0), 14, False)
	writeText("This program supports equation with any power but doesn't support roots.", WHITE, pygame.Rect(20, 240, 0, 0), 14, False)
	writeText("Operation:", SILVER, pygame.Rect(20, 270, 0, 0), 14, False)
	writeText("Symbol:", SILVER, pygame.Rect(20, 295, 0, 0), 14, False)
	writeText("Add      Subtract        Multiply        Power       Divide", WHITE, pygame.Rect(100, 270, 0, 0), 14, False)
	writeText(" +         -            *         ^          /", WHITE, pygame.Rect(100, 295, 0, 0), 18, False)
	writeText("In the graph page, you can press 'Backspace' key to get back to this page.", WHITE, pygame.Rect(20, 320, 0, 0), 14, False)
	writeText("If curve is not visible in graph, try changing the value of CELLSIZE variable.", RED, pygame.Rect(20, 340, 0, 0), 14, False)
	# textBox
	eqnBox = textBox(text, pygame.Rect((WINW/2)-100, WINH-200, 200, 30))
	writeText("y = ", WHITE, pygame.Rect(eqnBox.left-42, eqnBox.top-3, 20, 20), 18, False)
	# Draw Grpah button
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
			if event.key == K_LSHIFT or event.key == K_RSHIFT:
				SHIFT = True
			if SELECTED == [True, "e"]:
				if SHIFT:
					if event.key == ord("6"):           # Shift + 6 = ^
						text += "^"
					if event.key == ord("8"):           # Shift + 8 = *
						text += "*"
					if event.key == ord("9"):
						text += "("
					if event.key == ord("0"):
						text += ")"
					if event.key == ord("="):
						text += "+"
				elif event.key == ord("x") or chr(event.key).isdigit() or event.key == ord("-") or event.key == ord("/") or event.key == K_SPACE:
					text += chr(event.key)
				elif event.key == K_BACKSPACE:
					text = text[:-1]
		if event.type == KEYUP:
			if event.key == K_LSHIFT or event.key == K_RSHIFT:
				SHIFT = False
		if event.type == MOUSEMOTION:
			x, y = event.pos
			#if not SELECTED[0]:
			if eqnBox.colliderect((x, y, 0, 0)):
				HIGHLIGHT = [True, "e"]
			elif drawRect.colliderect((x, y, 0, 0)):
				HIGHLIGHT = [True, "b"]
			else:
				HIGHLIGHT = [False, "n"]
		if event.type == MOUSEBUTTONDOWN:
			x, y = event.pos
			if eqnBox.colliderect((x, y, 0, 0)):
				SELECTED = [True, "e"]
				if text == "Write your equation here":
					text = ""
			elif drawRect.colliderect((x, y, 0, 0)):
				HIGHLIGHT = [True, "b"]
				SELECTED = [True, "b"]
				if text == "":
					text = "0"
				try:
					constants, rule = generateRuleAndConstant(generateRawEqn(text))
				except:
					writeText("Unsupported equation!", RED, pygame.Rect(eqnBox.right + 5, eqnBox.top, 0, 0), 18, False)
					pygame.display.update()
					pygame.time.wait(800)
					SELECTED = [False, "n"]
			else:
				HIGHLIGHT = [False, "n"]
				SELECTED = [False, "n"]
				if text == "":
					text = "Write your equation here"
	if SELECTED == [True, "e"]:
		highlight(eqnBox, RED)
	if HIGHLIGHT[0]:
		if HIGHLIGHT[1] == "b":
			highlight(drawRect, RED)
		if HIGHLIGHT[1] == "e":
			highlight(eqnBox, RED)
	pygame.display.update()
	while SELECTED == [True, "b"]:
		windowSurface.fill(WHITE)
		drawGrids(GREEN)
		drawGraph(constants, rule, RED)
		for event in pygame.event.get():
			if event.type == QUIT:
				pygame.quit()
				sys.exit()
			if event.type == KEYDOWN:
				if event.key == K_ESCAPE:
					pygame.quit()
					sys.exit()
				if event.key == K_BACKSPACE:
					SELECTED = [False, "n"]
					text = "Write your equation here"
		pygame.display.update()
