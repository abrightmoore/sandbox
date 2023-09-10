#  @TheWorldFoundry
import time
import random
import pygame
pygame.init()

class Clickable:
	''' An onscreen bitmap dimensioned element that can be clicked
	'''
	def __init__(self, pos, size, colour, method, icon):
		self.pos = pos
		self.size = size
		self.size_original = [size[0],size[1]]
		self.colour = colour
		self.colour_border = [0x00, 0x00, 0x00, 0xff]
		self.method = method
		self.icon = icon
		self.age = 0
	
	def half_size(self):
		self.size[0] = self.size_original[0] #  >> 1
		self.size[1] = self.size_original[1] #  >> 1
	
	def is_clicked(self, click_pos):
		# is the click_pos within the clickable?
		result = True
		for i in xrange(0, len(click_pos)):  # Check if each dimension is within bounds
			result = result and (self.pos[i] <= click_pos[i] < self.pos[i]+self.size[i])
		return result
	
	def draw(self, surface, origin):
		self.age += 1
		dx = (self.size_original[0]-self.size[0])>>1
		dy = (self.size_original[1]-self.size[1])>>1
		if self.icon == None:  # No icon? draw the colour
			r,g,b,a = self.colour
			if a > 0:  # Only draw if alpha > 0
				pygame.draw.rect(surface, self.colour, [origin[0]+self.pos[0]+dx, origin[1]+self.pos[1]+dy, self.size[0], self.size[1]])
				pygame.draw.rect(surface, self.colour_border, [origin[0]+self.pos[0]+dx, origin[1]+self.pos[1]+dy, self.size[0], self.size[1]],1)
		else:
			surface.blit(pygame.transform.scale(self.icon, self.size), [origin[0]+self.pos[0]+dx, origin[1]+self.pos[1]+dy])
		if self.size[0] < self.size_original[0] and self.age%1 == 0:
			self.size[0] += 1
			self.size[1] += 1

	def perform(self):
		self.method()

#  Globals
working_file = "_curimage.png"
output_folder = "images/"
img = pygame.image.load(working_file)  # pygame.Surface(img_sz, pygame.SRCALPHA)
img_sz = [img.get_width(),img.get_height()]
img_copy = pygame.Surface(img_sz, pygame.SRCALPHA)

def save():
	pygame.image.save(img, output_folder+"image_"+str(time.time()).replace(".","_")+".png")
	pygame.image.save(img, working_file)

def clear():
	img.fill([0x00, 0x00, 0x00, 0xff])
	
def store():
	img_copy.blit(img, [0,0])
	
def restore():
	img.blit(img_copy, [0,0])

def rotate():
	global img
	img = pygame.transform.rotate(img, 90)

def up():
	temp = pygame.Surface((img.get_width(),img.get_height()),pygame.SRCALPHA)
	temp.blit(img,[0,0])
	img.blit(temp,[0,0],[0,1,img.get_width(),img.get_height()-1])
	img.blit(temp,[0,img.get_height()-1],[0,0,img.get_width(),1])

def down():
	temp = pygame.Surface((img.get_width(),img.get_height()),pygame.SRCALPHA)
	temp.blit(img,[0,0])
	img.blit(temp,[0,1],[0,0,img.get_width(),img.get_height()-1])
	img.blit(temp,[0,0],[0,img.get_height()-1,img.get_width(),1])

def left():
	temp = pygame.Surface((img.get_width(),img.get_height()),pygame.SRCALPHA)
	temp.blit(img,[0,0])
	img.blit(temp,[0,0],[1,0,img.get_width()-1,img.get_height()])
	img.blit(temp,[img.get_width()-1,0],[0,0,1,img.get_height()])

def right():
	temp = pygame.Surface((img.get_width(),img.get_height()),pygame.SRCALPHA)
	temp.blit(img,[0,0])
	img.blit(temp,[1,0],[0,0,img.get_width()-1,img.get_height()])
	img.blit(temp,[0,0],[img.get_width()-1,0,1,img.get_height()])

def mirror_vertical():
	temp = pygame.Surface((img.get_width(),img.get_height()),pygame.SRCALPHA)
	temp.blit(img,[0,0])
	temp = pygame.transform.flip(temp, False, True)
	img.blit(temp,[0, img.get_height()>>1], [0, img.get_height()>>1, img.get_width(), img.get_height()>>1])

def mirror_horizontal():
	temp = pygame.Surface((img.get_width(),img.get_height()),pygame.SRCALPHA)
	temp.blit(img,[0,0])
	temp = pygame.transform.flip(temp, True, False)
	img.blit(temp,[img.get_width()>>1, 0], [img.get_width()>>1, 0, img.get_width()>>1, img.get_height()])

def picker():
	pass

def dice():
	pass

def transparent():
	pass

def editor():
	size = [768,688]
	
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
		"lavender"       : [0xc8, 0xbf, 0xe7, 0xff],
		"transparent"    : [0x00, 0x00, 0x00, 0x00]
	}
	colours_ordered = [
		"black",
		"white",
		"light yellow",
		"rose",
		"lavender",
		"light grey",
		"grey",
		"brown",
		"dark red",
		"red",

		"orange",
		"yellow",
		"gold",

		"lime",
		"green",
		"turquoise",
		"light turquoise",
		"blue-grey",
		"indigo",
		"purple",
		"transparent"
	]
	save_icon = pygame.image.load("save.png")
	clear_icon = pygame.image.load("clear.png")
	store_icon = pygame.image.load("store.png")
	restore_icon = pygame.image.load("restore.png")
	rotate_icon = pygame.image.load("rotate.png")
	up_icon = pygame.image.load("up.png")
	down_icon = pygame.image.load("down.png")
	left_icon = pygame.image.load("left.png")
	right_icon = pygame.image.load("right.png")
	mirrorh_icon = pygame.image.load("mirrorh.png")
	mirrorv_icon = pygame.image.load("mirrorv.png")
	picker_icon = pygame.image.load("picker.png")
	dice_icon = pygame.image.load("dice.png")
	
	controls_clickables = {}
	controls = [ ("Save", "lime", save, save_icon),
				("Clear", "yellow", clear, clear_icon),
				("Store","orange", store, store_icon),
				("Restore","red", restore, restore_icon),
				("Rotate","purple", rotate, rotate_icon),
				("Up","purple", up, up_icon),
				("Down","purple", down, down_icon),
				("Left","purple", left, left_icon),
				("Right","purple", right, right_icon),
				("Mirror Horizontal","purple", mirror_horizontal, mirrorh_icon),
				("Mirror Vertical","purple", mirror_vertical, mirrorv_icon),
				("Picker","purple", picker, picker_icon),
				("Dice","purple", dice, dice_icon),
			]
	d = 32
	y = d*3
	for (c, colour, method, icon) in controls:
		controls_clickables[c] = Clickable([size[1]+4, y], [d, d], colours[colour], method, icon)
		y += d+8
		if c == "Store":
			y += 40
	
	colour_clickables = {}
	h = int(size[1]/len(colours))
	y = 0
	for colour in colours_ordered:
		colour_clickables[colour] = Clickable([size[0]-h,y],[h,h],colours[colour], None, None)
		y += h
	#  print colour_clickables
	
	# Set up a pixel grid based on the image size
	character_size = img_sz
	pixel_clickables = {}
	h = int(size[1]/character_size[0])
	for y in xrange(0, character_size[1]):
		for x in xrange(0, character_size[0]):
			# pixel_clickables[(x, y)] = Clickable([x*h,y*h],[h,h],colours["light yellow"], None, None)
			pixel_clickables[(x, y)] = Clickable([x*h,y*h],[h,h],img.get_at((x,y)), None, None)
	# img.fill(colours["light yellow"])
	
	surface = pygame.display.set_mode(size, pygame.SRCALPHA)
	
	selected = None
	
	logo = pygame.image.load("logo.png")
	# Gameloop
	keepGoing = True
	iterations = 0
	picker_active = False
	clock = pygame.time.Clock()
	
	underlay = pygame.image.load("underlay.png")
	changed = True
	while keepGoing:
		iterations += 1
		
		if changed == True:
			surface.fill(colours["black"])
			surface.blit(underlay,[0,0])
			
			for clickables in [colour_clickables, pixel_clickables, controls_clickables]:
				for clickable in clickables:
					clickables[clickable].draw(surface, [0,0])
			
			surface.blit(img, [size[1]+4, 0])
			surface.blit(pygame.transform.scale(img, [32,32]), [size[1]+4, img.get_height()+1])
			surface.blit(img_copy, [size[1]+4, img.get_height()+36+166])
			surface.blit(pygame.transform.scale(img_copy, [32,32]), [size[1]+4, img.get_height()*2+38+166])
			
			pygame.draw.line(surface, colours["grey"], [size[1],0], [size[1],size[1]], 1)

			if iterations < 1000:
				surface.blit(logo, [(size[1]>>1)-(logo.get_width()>>1), (size[1]>>1)-(logo.get_height()>>1)])
			
		pygame.display.update()
		changed = False
		# print "Frame", iterations
		for event in pygame.event.get():
			if event.type == pygame.QUIT:
				keepGoing = False
			elif event.type == pygame.MOUSEBUTTONUP:
				changed = True
				if event.button == 1: # 1 == Left
					(px,py) = event.pos
					
					clickables = controls_clickables
					for clickable in clickables:
						if clickables[clickable].is_clicked(event.pos):
							clickables[clickable].half_size()
							clickables[clickable].perform()
							if clickable == "Clear":
								picker_active = False
								for c in pixel_clickables:
									if selected is not None:
										pixel_clickables[c].colour = selected.colour
									else:
										pixel_clickables[c].colour = colours["black"]
									for p in pixel_clickables:
										img.set_at(p, pixel_clickables[p].colour)
							if clickable == "Dice":
								picker_active = False
								for c in pixel_clickables:
									pixel_clickables[c].colour = colour_clickables[random.choice(colour_clickables.keys())].colour
									for p in pixel_clickables:
										img.set_at(p, pixel_clickables[p].colour)
							if clickable == "Picker":
								picker_active = True
							if clickable in ["Restore", "Rotate", "Up", "Down", "Left", "Right", "Mirror Horizontal", "Mirror Vertical"]:
								picker_active = False
								for p in pixel_clickables:
									pixel_clickables[p].colour = img.get_at(p)
					
					clickables = colour_clickables
					for clickable in clickables:
						# print clickable
						if clickables[clickable].is_clicked(event.pos):
							picker_active = False
							if selected is not None:
								selected.colour_border = colours["black"]
							selected = clickables[clickable]
							selected.colour_border = colours["white"]
							selected.half_size()

					clickables = pixel_clickables
					for clickable in clickables:
						if clickables[clickable].is_clicked(event.pos):
							if picker_active:  # Change nothing, we're selecting
								for c in colour_clickables:
									if (clickables[clickable].colour[0],clickables[clickable].colour[1],clickables[clickable].colour[2]) == (colour_clickables[c].colour[0],colour_clickables[c].colour[1],colour_clickables[c].colour[2]):  # Match!
										if selected is not None:
											selected.colour_border = colours["black"]
										selected = colour_clickables[c]
										selected.colour_border = colours["white"]
										selected.half_size()
								picker_active = False
							elif selected is not None:
								clickables[clickable].colour = selected.colour
								img.set_at(clickable, selected.colour)
								clickables[clickable].half_size()
		clock.tick(30)
editor()
