#  @TheWorldFoundry
import pygame
pygame.init()

class Clickable:
	''' An onscreen bitmap dimensioned element that can be clicked
	'''
	def __init__(self, pos, size, colour):
		self.pos = pos
		self.size = size
		self.colour = colour
		self.colour_border = [0x00, 0x00, 0x00, 0xff]
		
	def is_clicked(self, click_pos):
		# is the click_pos within the clickable?
		result = True
		for i in xrange(0, len(click_pos)):  # Check if each dimension is within bounds
			result = result and (self.pos[i] <= click_pos[i] < self.pos[i]+self.size[i])
		return result
	
	def draw(self, surface, origin):
		pygame.draw.rect(surface, self.colour, [origin[0]+self.pos[0], origin[1]+self.pos[1], self.size[0], self.size[1]])
		pygame.draw.rect(surface, self.colour_border, [origin[0]+self.pos[0], origin[1]+self.pos[1], self.size[0], self.size[1]],1)

def editor():
	size = [880,800]
	
	# Set up a tool and colour palette
	colours = {
		"black"          : [0x00, 0x00, 0x00, 0xff],
		"grey"           : [0x7f, 0x7f, 0x7f, 0xff],
		"dark red"       : [0x88, 0x00, 0x15, 0xff],
		"red"            : [0xed, 0x1c, 0x24, 0xff],
		"orange"         : [0xff, 0x7f, 0x27, 0xff],
		"yellow"         : [0xff, 0xf2, 0x00, 0xff],
		"green"          : [0x22, 0xb1, 0x4c, 0xff],
		"turquoise"      : [0x00, 0xa2, 0xe8, 0xff],
		"indigo"         : [0x3f, 0x48, 0xcc, 0xff],
		"purple"         : [0xa3, 0x49, 0xa4, 0xff],
		"white"          : [0xff, 0xff, 0xff, 0xff],
		"light grey"     : [0xc3, 0xc3, 0xc3, 0xff],
		"brown"          : [0xb9, 0x7a, 0x57, 0xff],
		"rose"           : [0xff, 0xae, 0xc9, 0xff],
		"gold"           : [0xff, 0xc9, 0x0e, 0xff],
		"light yellow"   : [0xef, 0xe4, 0xb0, 0xff],
		"lime"           : [0xb5, 0xe6, 0x1d, 0xff],
		"light turquoise": [0x99, 0xd9, 0xea, 0xff],
		"blue-grey"      : [0x70, 0x92, 0xbe, 0xff],
		"lavender"       : [0xc8, 0xbf, 0xe7, 0xff]
	}
	colour_clickables = {}
	h = int(size[1]/len(colours))
	y = 0
	for colour in colours:
		colour_clickables[(size[0]-h, y)] = Clickable([size[0]-h,y],[h,h],colours[colour])
		y += h
	#  print colour_clickables
	
	# Set up a pixel grid based on the image size
	character_size = [16,16]
	pixel_clickables = {}
	h = int(size[1]/character_size[0])
	for y in xrange(0, character_size[1]):
		for x in xrange(0, character_size[0]):
			pixel_clickables[(x*h, y*h)] = Clickable([x*h,y*h],[h,h],colours["light yellow"])
	
	surface = pygame.display.set_mode(size, pygame.SRCALPHA)
	
	selected = None
	
	# Gameloop
	keepGoing = True
	iterations = 0
	while keepGoing:
		iterations += 1
		
		for clickables in [colour_clickables, pixel_clickables]:
			for clickable in clickables:
				clickables[clickable].draw(surface, [0,0])
		
		pygame.display.update()

		for event in pygame.event.get():
			if event.type == pygame.QUIT:
				keepGoing = False
			elif event.type == pygame.MOUSEBUTTONUP:
				if event.button == 1: # 1 == Left
					(px,py) = event.pos
					clickables = colour_clickables
					for clickable in clickables:
						# print clickable
						if clickables[clickable].is_clicked(event.pos):
							selected = clickables[clickable]
					clickables = pixel_clickables
					for clickable in clickables:
						if clickables[clickable].is_clicked(event.pos):
							if selected is not None:
								clickables[clickable].colour = selected.colour

editor()
