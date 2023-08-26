#  @TheWorldFoundry

import pygame
import math
pygame.init()

class PaperLens:
	'''  Convenience class that returns a scaled image when requested, with caching
	'''
	
	def __init__(self, img):
		self.base_image = [img]
		
		# Flipbook animation
		self.frame = 0
		self.frames_max = 1
		self.animation_type = 0 # Linear
		self.animation_direction = 1 # Bouncy
		self.init_cache()
	
	def init_cache(self):
		self.cache = { ((self.base_image[self.frame].get_width(),self.base_image[self.frame].get_height()), self.frame) : self.base_image[self.frame] } 
	
	def add_frame(self, img):
		self.base_image.append(img)
		self.cache[((self.base_image[self.frames_max].get_width(),self.base_image[self.frames_max].get_height()), self.frames_max)] = self.base_image[self.frames_max] 
		self.frames_max += 1
		
	def tick(self):
		self.frame = self.frame+self.animation_direction
		if self.animation_type == 1: 
			if self.frame == 0 or self.frame == self.frames_max-1:
				self.animation_direction = self.animation_direction * -1
		self.frame = self.frame%self.frames_max
		
	def get_scaled(self, size):
		if size not in self.cache:
			width_scale, height_scale = size
			self.cache[((size,self.frame), self.frame)] = pygame.transform.scale(self.base_image[self.frame], [width_scale, height_scale])
		return self.cache[(size,self.frame)]
		
	def destroy_cache(self):
		self.cache = self.init_cache()

class CharacterCellLens:
	'''
		This is a render helper whose job is to place a lens over an object
	'''
	def __init__(self, id):
		self.id = id #  TODO: This is where to protect against file system read exploits.
		self.filename = str(id)+".png"
		self.paper = PaperLens(pygame.image.load(self.filename))
	
	def draw2D(self, display, pos, size):
		#  Each character knows how to render itself to the display at the specified pixel position
		display.blit(self.paper.get_scaled(size), pos)
		
	def tick(self):
		self.paper.tick()

class View2DLens:
	'''
		This is a region that may contain things.
		In the simplest use case, this is a one-layer 2D plane with row x column cells holding a display element.
		Other metadata may be present on the object
	'''
	
	def __init__(self):
		self.width = 50
		self.height = 25
		self.layer = 1
		self.time = 1
		self.cell_width = 8
		self.cell_height = 8
		self.things = {}
		
	def set_size(self, size, cell_size):
		self.width, self.height, self.layer, self.time = size
		self.cell_width, self.cell_height = cell_size
		
	def set_at(self, pos, thing):
		#  Add this thing to the position at the end of the list
		if pos in self.things:
			self.things[pos].append(thing)  #  TODO: Optimise for search
		self.things[pos] = [thing]

	def get_at(self, pos, thing):
		if pos in self.things:
			return self.things[pos]
	
	def fill(self, thing):
		for col in xrange(0, self.height):
			for row in xrange(0, self.width):
				self.set_at((row,col), thing)
	
	def get_template2D(self):
		return pygame.Surface((self.cell_width*self.width, self.cell_height*self.height), pygame.SRCALPHA)
	
	def get_image2D(self, surface):
		#  Render this view to a suitably sized surface
		if surface == None:
			surface = self.get_template2D()
		#  For each pos we know about, render the thing to the image
		for pos in self.things:
			 for ob in self.things[pos]:
				if ob is not None:
					x, y = pos
					px = x*self.cell_width
					py = surface.get_height()-(y+1)*self.cell_height  #  Top left is 0
					ob.draw2D(surface, (px, py), (self.cell_width, self.cell_height))
		return surface

class RendererLens:
	#  The renderer draws the view to the display at the intended position and location.
	def __init__(self, display):
		self.view = None
		self.display = display
		self.display.convert()
	
	def set_view(self, view):
		self.view = view
	
	def draw(self, pos, size):
		#  draws the nominated view into the rectangle zone on the display, scaling as appropriate
		
		# Handle scaling the 
		self.display.blit(pygame.transform.scale(self.view.get_image2D(None), size), pos)

def test_harness():
	player_display = pygame.display.set_mode((800, 400),pygame.SRCALPHA)  # Pygame
	r1 = RendererLens(player_display)
	r2 = RendererLens(player_display)
	r1.set_view(View2DLens())
	r2.set_view(View2DLens())
	# Fill with a pattern
	c = CharacterCellLens("tile1")
	c.paper.add_frame(pygame.image.load("tile2.png"))
	r1.view.fill(c)
	r2.view.fill(CharacterCellLens("tile2"))

	d = CharacterCellLens("tile3")
	d.paper.add_frame(pygame.image.load("tile2.png"))
	r2.view.set_at((10,20),d)
	
	# Gameloop
	keepGoing = True
	iterations = 0
	angle = math.pi/180.0
	while keepGoing:
		iterations += 1
		dx = 200.0*math.sin(angle*float(iterations))
		dy = 50.0*math.cos(angle*float(iterations*2.0))
		r1.draw([0,0],[800,400])
		r2.draw([200+dx,50+dy],[400,200])
		pygame.display.update()

		for event in pygame.event.get():
			if event.type == pygame.QUIT:
				keepGoing = False
			elif event.type == pygame.MOUSEBUTTONUP:
				if event.button == 1: # 1 == Left
					(px,py) = event.pos
		c.tick()
		d.tick()

		
test_harness()
