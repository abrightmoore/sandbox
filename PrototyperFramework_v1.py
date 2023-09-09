#  @TheWorldFoundry

import pygame
import time
import math
import random
import glob
import os
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
			self.cache[(size,self.frame)] = pygame.transform.scale(self.base_image[self.frame], [width_scale, height_scale])
		return self.cache[(size,self.frame)]
		
	def destroy_cache(self):
		self.cache = self.init_cache()

class CharacterCellLens:
	'''
		This is a render helper whose job is to place a lens over an object
	'''
	def __init__(self, id):
		self.id = str(id.replace("\\"," ").replace("/"," ")) #  TODO: This is where to protect against file system read exploits.
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
		self.debug = 0
		self.width = 50
		self.height = 25
		self.layer = 1
		self.time = 1
		self.cell_width = 8
		self.cell_height = 8
		self.things = {}
		self.invalidate()
		self.colour_bg = (0,0,0,255)
		self.display_scale_factor_x = 1.0  # When the view gets drawn, this holds the 'scale' applied
		self.display_scale_factor_y = 1.0

	def invalidate(self):
		self.surface_cache = None

	def get_cells(self):
		return list(self.things.keys())

	def set_size(self, size, cell_size):
		self.invalidate()  # Invalidate cache
		self.width, self.height, self.layer, self.time = size
		self.cell_width, self.cell_height = cell_size
		
	def set_at(self, pos, thing):
		self.invalidate()  # Invalidate cache
		#  Add this thing to the position at the end of the list
		if pos in self.things:
			self.things[pos].append(thing)  #  TODO: Optimise for search
		else:
			self.things[pos] = [thing]

	def remove(self, pos, thing):
		self.invalidate()  # Invalidate cache
		if pos in self.things:
#			for i in xrange(0, len(self.things[pos])):
			if thing in self.things[pos]:
#				if self.things[pos][i] == thing:
#					self.things[pos][i] = None
				ar = self.things[pos]
				ar.remove(thing)

	def get_at(self, pos):
		if pos in self.things:
			return self.things[pos]
		else:
			return []
	
	def erase_at(self, pos):
		self.invalidate()  # Invalidate cache
		if pos in self.things:
			self.things[pos] = []
			del self.things[pos]
	
	def fill(self, thing):
		self.invalidate()  # Invalidate cache
		for col in xrange(0, self.height):
			for row in xrange(0, self.width):
				self.set_at((row,col), thing)
	
	def fill_area(self, thing, pos, size, chance):
		self.invalidate()  # Invalidate cache
		
		x,y = pos
		width, height = size
		
		for col in xrange(y, y+height):
			for row in xrange(x, x+width):
				if random.random() <= chance:
					self.set_at((row,col), thing)

	def draw_label(self, label, pos):
		self.invalidate()
		x, y = pos
		label.place(self, pos)

	def get_template2D(self):
		surf = pygame.Surface((self.cell_width*self.width, self.cell_height*self.height), pygame.SRCALPHA)
		surf.fill(self.colour_bg)
		return surf
	
	def get_image2D(self, surface):
		if self.surface_cache != None:
			return self.surface_cache
			
		#  Otherwise Render this view to a suitably sized surface
		if surface == None:
			surface = self.get_template2D()
		#  For each pos we know about, render the thing to the image
		for pos in self.things:
			if len(self.things[pos]) > 0:
				x, y = pos
				px = x*self.cell_width
				py = surface.get_height()-(y+1)*self.cell_height  #  Top left is 0

				for ob in self.things[pos]:

					if ob is not None:
						ob.draw2D(surface, (px, py), (self.cell_width, self.cell_height))

				if self.debug > 0 and len(self.things[pos]) > 1:  # Are there more than two items in this location?
					pygame.draw.rect(surface, (255,0,0,255), [px, py, self.cell_width, self.cell_height], 1)
				
		self.surface_cache = surface
		return surface

class Clickable:
	''' An onscreen bitmap dimensioned element that can be checked to see if it has been clicked
	'''
	def __init__(self, pos, size):
		self.pos = pos
		self.size = size
		
	def is_clicked(self, click_pos):
		# is the click_pos within the clickable?
		result = True
		for i in xrange(0, len(click_pos)):  # Check if each dimension is within bounds
			result = result and (self.pos[i] <= click_pos[i] < self.pos[i]+self.size[i])
		return result
	
	def draw(self, surface, colour, origin):
		pygame.draw.rect(surface, colour, [origin[0]+self.pos[0], origin[1]+self.pos[1], self.size[0], self.size[1]], 0)

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
		img = self.view.get_image2D(None)
		self.display.blit(pygame.transform.scale(img, size), pos)
		sx, sy = size
		self.view.display_scale_factor_x = float(sx)/float(img.get_width())  #  Cache the scale factor on the view we've rendered
		self.view.display_scale_factor_y = float(sx)/float(img.get_height())
		

class Tiles:
	def __init__(self):
		self.tiles = {}
	
	def add(self, name, tile):
		self.tiles[name.replace("\\"," ").replace("/"," ")] = tile
		
	def get(self, name):
		return self.tiles[name]
		
	def list(self):
		return [key for key in self.tiles]

	def create_from_dir(self, path, method):
		game_cells = glob.glob(os.path.join(path, "*.png"))
		for fn in game_cells:
			fn = fn.replace(".png","")
			t = method(fn)
			self.add(fn, t)

class TileAssets:
	def __init__(self, namespace):
		self.namespace = namespace
		self.tiles = Tiles()
		self.tiles.create_from_dir(namespace, CharacterCellLens)
	
	def get(self, id):
		return self.tiles.get(self.namespace+" "+id)

class Font:
	def __init__(self, directory):
		self.font_tiles = Tiles()
		self.font_tiles.create_from_dir(directory, CharacterCellLens)
		self.namespace = directory
	
	def get_tile(self, k):
		return self.font_tiles.get(k)

class Label:
	def __init__(self, text, font):
		self.text = text
		self.len = len(text)
		self.font = font
	
	def place(self, view, pos):
		x,y = pos
		for c in self.text:
			view.erase_at((x, y))
			view.set_at((x, y), self.font.get_tile(self.font.namespace+" "+str(c)))
			x += 1

class Score:
	def __init__(self, name, value, digits, font):
		self.value = value
		self.name = name
		self.font = font
		self.digits = digits

	def place(self, view, pos):
		x,y = pos
		val = str(self.value).zfill(self.digits)
		for c in val:
			view.erase_at((x, y))
			view.set_at((x, y), self.font.get_tile(self.font.namespace+" "+str(c)))
			x += 1
			
	def add(self, delta):
		self.value += delta

class Entity:
	''' An instance of a tile with a position
		Movement goes here
		Responding to Input intents goes here
	'''
	def __init__(self, id, tile_type, pos):
		self.id = id
		self.tile_type = tile_type  # I want to know what this is so I can examine its properties
		self.pos = pos  # Where in the world is this thing x,y coords
		

# Custom stuff

def space_station_horror_game():
	size = width,height = 800,800  # Pygame. This is the 'screen' size
	r = RendererLens(pygame.display.set_mode(size, pygame.SRCALPHA))
	r.set_view(View2DLens())
	play_size = 40  # This is how many 'cells' are in the play area. It doesn't HAVE to be square, but why make life hard?
	r.view.set_size( (play_size, play_size, 1, 1), (width/play_size, height/play_size))

	# Set up tiles
	namespace = "space_station_horror_game"  #  This is the namespace of the assets for this game
	
	tiles = TileAssets(namespace)
	#  tiles = Tiles()  # 
	#  tiles.create_from_dir(namespace, CharacterCellLens)
	r.view.cell_width = r.view.cell_height = 16

	player = tiles.get("player")
	wall = tiles.get("wall")
	coins = tiles.get("coins")
	floor = tiles.get("floor")
	#player = tiles.get(namespace+" player")
	#wall = tiles.get(namespace+" wall")
	#coins = tiles.get(namespace+" coins")
	#floor = tiles.get(namespace+" floor")
	
	player_pos = play_size>>1, play_size>>1  # Player starts in the middle
	
	r.view.fill_area(floor, [0, 0], [play_size, play_size], 1.0 )
	r.view.fill_area(coins, [0, 0], [play_size, play_size], 0.04 )
	r.view.fill_area(wall, [0, 0], [play_size, play_size], 0.4 )
	for y in xrange((play_size>>1)-2, (play_size>>1)+3):
		for x in xrange((play_size>>1)-2, (play_size>>1)+3):
			r.view.erase_at((x,y))
	r.view.fill_area(floor, [(play_size>>1)-2, (play_size>>1)-2], [5, 5], 1.0 )
	r.view.set_at(player_pos, player)
	
	font = Font("font")
	lbl_game_over = Label("game_over", font)
	lbl_score = Label("score_", font)
	lbl_lives = Label("lives_", font)
	score_lives = Score("lives", 1, 1, font)
	score_points = Score("score", 0, 10, font)
	
	clock = pygame.time.Clock()
	keepGoing = True
	iterations = 0
	pause = False
	while keepGoing:
		iterations += 1
		
		r.draw([0,0],[width, height])
		
		r.view.draw_label(lbl_lives, [0, 0])
		r.view.draw_label(score_lives, [len(lbl_lives.text)+1, 0])
		#r.view.erase_at((len(lbl_pilots.text)+2, play_size-1))
		for x in xrange(0, score_lives.value):
			r.view.erase_at((len(lbl_lives.text)+3+x, 0))
			r.view.set_at((len(lbl_lives.text)+3+x, play_size-1), player)
		r.view.draw_label(lbl_score, [0, play_size-1])
		r.view.draw_label(score_points, [len(lbl_score.text)+2, play_size-1])

			
		pygame.display.update()

		for event in pygame.event.get():
			if event.type == pygame.QUIT:
				keepGoing = False
			elif event.type == pygame.MOUSEBUTTONUP:
				if event.button == 1: # 1 == Left
					(px,py) = event.pos
					py = height-py  # Invert because bottom of screen is row 0
					cell_x = int(px/(r.view.cell_width * r.view.display_scale_factor_x))
					cell_y = int(py/(r.view.cell_height * r.view.display_scale_factor_y))
					x,y = player_pos
					new_player_pos = player_pos
					if cell_x < x and 0 < x:  # Move left
						new_player_pos = x-1, y
					if cell_y > y and y < play_size-1:  # Move up
						new_player_pos = x, y+1
					if cell_x > x and x < play_size-1:  # Move right
						new_player_pos = x+1, y
					if cell_y < y and 0 < y:  # Move down
						new_player_pos = x, y-1
					target = r.view.get_at(new_player_pos)
					if wall not in target:
						if floor in target:
							r.view.remove(player_pos, player)
							r.view.set_at(new_player_pos, player)
							if coins in target:
								score_points.add(10)
								r.view.remove(new_player_pos, coins)
							player_pos = new_player_pos
					
					# Check what's in the new position
					
					

					
		clock.tick(30)

space_station_horror_game()



def oliver_maze_game():
	size = width,height = 800,800  # Pygame
	r = RendererLens(pygame.display.set_mode(size, pygame.SRCALPHA))
	r.set_view(View2DLens())
	play_size = 20
	r.view.set_size( (play_size, play_size, 1, 1), (width/play_size, height/play_size))

	# Set up tiles
	namespace = "maze_game"
	tiles = Tiles()
	tiles.create_from_dir(namespace, CharacterCellLens)
	r.view.cell_width = r.view.cell_height = 16

	player = tiles.get(namespace+" player")
	wall = tiles.get(namespace+" wall")
	coins = tiles.get(namespace+" coins")
	floor = tiles.get(namespace+" floor")
	
	player_pos = play_size>>1, play_size>>1  # Player starts in the middle
	
	r.view.fill_area(floor, [0, 0], [play_size, play_size], 1.0 )
	r.view.fill_area(coins, [0, 0], [play_size, play_size], 0.04 )
	r.view.fill_area(wall, [0, 0], [play_size, play_size], 0.4 )
	for y in xrange((play_size>>1)-2, (play_size>>1)+3):
		for x in xrange((play_size>>1)-2, (play_size>>1)+3):
			r.view.erase_at((x,y))
	r.view.fill_area(floor, [(play_size>>1)-2, (play_size>>1)-2], [5, 5], 1.0 )
	r.view.set_at(player_pos, player)
	
	font = Font("font")
	lbl_game_over = Label("game_over", font)
	lbl_score = Label("score_", font)
	lbl_lives = Label("lives_", font)
	score_lives = Score("lives", 1, 1, font)
	score_points = Score("score", 0, 10, font)
	
	clock = pygame.time.Clock()
	keepGoing = True
	iterations = 0
	pause = False
	while keepGoing:
		iterations += 1
		
		r.draw([0,0],[width, height])
		
		r.view.draw_label(lbl_lives, [0, 0])
		r.view.draw_label(score_lives, [len(lbl_lives.text)+1, 0])
		#r.view.erase_at((len(lbl_pilots.text)+2, play_size-1))
		for x in xrange(0, score_lives.value):
			r.view.erase_at((len(lbl_lives.text)+3+x, 0))
			r.view.set_at((len(lbl_lives.text)+3+x, play_size-1), player)
		r.view.draw_label(lbl_score, [0, play_size-1])
		r.view.draw_label(score_points, [len(lbl_score.text)+2, play_size-1])

			
		pygame.display.update()

		for event in pygame.event.get():
			if event.type == pygame.QUIT:
				keepGoing = False
			elif event.type == pygame.MOUSEBUTTONUP:
				if event.button == 1: # 1 == Left
					(px,py) = event.pos
					py = height-py  # Invert because bottom of screen is row 0
					cell_x = int(px/(r.view.cell_width * r.view.display_scale_factor_x))
					cell_y = int(py/(r.view.cell_height * r.view.display_scale_factor_y))
					x,y = player_pos
					new_player_pos = player_pos
					if cell_x < x and 0 < x:  # Move left
						new_player_pos = x-1, y
					if cell_y > y and y < play_size-1:  # Move up
						new_player_pos = x, y+1
					if cell_x > x and x < play_size-1:  # Move right
						new_player_pos = x+1, y
					if cell_y < y and 0 < y:  # Move down
						new_player_pos = x, y-1
					target = r.view.get_at(new_player_pos)
					if wall not in target:
						if floor in target:
							r.view.remove(player_pos, player)
							r.view.set_at(new_player_pos, player)
							if coins in target:
								score_points.add(10)
								r.view.remove(new_player_pos, coins)
							player_pos = new_player_pos
					
					# Check what's in the new position
					
					

					
		clock.tick(30)

oliver_maze_game()



def saucer_attack():  #  Messing about space-themed salvage
	size = width,height = 800,800  # Pygame
	r = RendererLens(pygame.display.set_mode(size, pygame.SRCALPHA))
	r.set_view(View2DLens())
	play_size = 20
	r.view.set_size( (play_size, play_size, 1, 1), (width/play_size, height/play_size))
	
	# Set up tiles
	tiles = Tiles()
	tiles.create_from_dir("saucer_attack", CharacterCellLens)

	enemy_base1 = tiles.get("saucer_attack enemy_base")
	enemy_base2 = tiles.get("saucer_attack enemy_base1")
	enemy_base3 = tiles.get("saucer_attack enemy_base2")

	enemy_left = tiles.get("saucer_attack enemy_left")
	enemy_right = tiles.get("saucer_attack enemy_right")
	enemy_lander = tiles.get("saucer_attack enemy_lander")
	enemy_missile = tiles.get("saucer_attack enemy_missile")
	land = tiles.get("saucer_attack land")
	missile = tiles.get("saucer_attack missile")
	pilot = tiles.get("saucer_attack pilot")
	ship = tiles.get("saucer_attack ship")
	ship_pos = play_size>>1, 1  # Player starts in the middle
	explode1 = tiles.get("saucer_attack explode1")
	explode2 = tiles.get("saucer_attack explode2")
	explode3 = tiles.get("saucer_attack explode3")

	font = Font("font")
	lbl_game_name = Label("saucer_attack", font)
	lbl_game_over = Label("game_over", font)
	lbl_start = Label("start", font)
	lbl_score = Label("score_", font)
	lbl_pilots = Label("pilots_", font)
	score_pilots = Score("pilots", 1, 1, font)

	score_points = Score("score", 0, 10, font)

	r.view.fill_area(land, [0, 0], [play_size, 1], 1.0 )

	r.view.fill_area(enemy_left, [0, play_size-3], [play_size>>1, 1], 0.5 )
	r.view.fill_area(enemy_right, [play_size>>1, play_size-3], [play_size>>1, 1], 0.5 )
	r.view.fill_area(enemy_missile, [0, play_size-4], [play_size, 1], 1.0 )
	r.view.fill_area(missile, [0, 2], [play_size, 1], 1.0 )

	r.view.set_at(ship_pos, ship)

	keepGoing = True
	iterations = 0
	cooldown = 100
	last_shot = 0
	pause = False
	game_over_flag = False
	tick_rate = 40   # TODO reduce this as levels go up to increase game speed
	tick_rate_min = 10
	level = 1
	level_handled = 0
	while keepGoing:
		if pause == False:
			# Draw the screen
			r.view.draw_label(lbl_pilots, [0, play_size-1])
			r.view.draw_label(score_pilots, [len(lbl_pilots.text)+1, play_size-1])
			#r.view.erase_at((len(lbl_pilots.text)+2, play_size-1))
			for x in xrange(0, score_pilots.value):
				r.view.erase_at((len(lbl_pilots.text)+3+x, play_size-1))
				r.view.set_at((len(lbl_pilots.text)+3+x, play_size-1), pilot)
			r.view.draw_label(lbl_score, [0, play_size-2])
			r.view.draw_label(score_points, [len(lbl_score.text)+2, play_size-2])

			# Scan the screen and process any updates based on what we find.
			if iterations%tick_rate == 0:  # Delay - change this to be timing based TODO
				remove_list = []
				new_list = []

				for pos in r.view.get_cells():  # This should be an iterator
					x,y = pos
					cell = r.view.get_at(pos)
					
					missile_exploded = False
					enemy_destroyed = False
					
					if explode3 in cell:
						remove_list.append((pos, explode3))
					if explode2 in cell:
						remove_list.append((pos, explode2))
						new_list.append((pos, explode3))
					if explode1 in cell:
						remove_list.append((pos, explode1))
						new_list.append((pos, explode2))

					if enemy_base3 in cell:  # Move randomly left and right
						if missile in cell:
							remove_list.append((pos, enemy_base3))
							score_points.add(2500)
							remove_list.append((pos, missile))
							new_list.append((pos, explode1))
							new_list.append(((x+1,y), explode2))
							new_list.append(((x-1,y), explode2))
							new_list.append(((x,y-1), explode3))
							missile_exploded = True
							enemy_destroyed = True
						else:
							if random.random() > 0.95:  # Fire megalaser
								new_list.append(((x,y), enemy_missile))
								new_list.append(((x,y-1), enemy_missile))
								new_list.append(((x,y-2), enemy_missile))
								new_list.append(((x,y-3), enemy_missile))
								
							if x == 0:
								remove_list.append((pos, enemy_base3))
								new_list.append(((x+1,y), enemy_base3))
							elif x == play_size-1:
								remove_list.append((pos, enemy_base3))
								new_list.append(((x-1,y), enemy_base3))
							else:
								remove_list.append((pos, enemy_base3))
								new_list.append(((x+random.randint(-1,1),y), enemy_base3))

					if enemy_base2 in cell:  # Move randomly left and right
						if missile in cell:
							remove_list.append((pos, enemy_base2))
							new_list.append((pos, enemy_base3))
							score_points.add(2000)
							remove_list.append((pos, missile))
							new_list.append((pos, explode1))
							new_list.append(((x+1,y), explode2))
							new_list.append(((x-1,y), explode2))
							new_list.append(((x,y-1), explode3))
							missile_exploded = True
							enemy_destroyed = True
						else:
							if random.random() > 0.95:  # Fire megalaser
								new_list.append(((x,y), enemy_missile))
								new_list.append(((x,y-1), enemy_missile))
								new_list.append(((x,y-2), enemy_missile))
								new_list.append(((x,y-3), enemy_missile))
								
							if x == 0:
								remove_list.append((pos, enemy_base2))
								new_list.append(((x+1,y), enemy_base2))
							elif x == play_size-1:
								remove_list.append((pos, enemy_base2))
								new_list.append(((x-1,y), enemy_base2))
							else:
								remove_list.append((pos, enemy_base2))
								new_list.append(((x+random.randint(-1,1),y), enemy_base2))

					if enemy_base1 in cell:  # Move randomly left and right
						if missile in cell:
							remove_list.append((pos, enemy_base1))
							new_list.append((pos, enemy_base2))
							score_points.add(500)
							remove_list.append((pos, missile))
							new_list.append((pos, explode1))
							new_list.append(((x+1,y), explode2))
							new_list.append(((x-1,y), explode2))
							new_list.append(((x,y-1), explode3))
							missile_exploded = True
							enemy_destroyed = True
						else:
							if random.random() > 0.95:  # Fire megalaser
								new_list.append(((x,y), enemy_missile))
								new_list.append(((x,y-1), enemy_missile))
								new_list.append(((x,y-2), enemy_missile))
								new_list.append(((x,y-3), enemy_missile))
								
							if x == 0:
								remove_list.append((pos, enemy_base1))
								new_list.append(((x+1,y), enemy_base1))
							elif x == play_size-1:
								remove_list.append((pos, enemy_base1))
								new_list.append(((x-1,y), enemy_base1))
							else:
								remove_list.append((pos, enemy_base1))
								new_list.append(((x+random.randint(-1,1),y), enemy_base1))

					if enemy_left in cell: # Move randomly left and right, move down when at the edges
						# Check if hit by a player missile
						if missile in cell:
							remove_list.append((pos, enemy_left))
							score_points.add(100)
							remove_list.append((pos, missile))
							new_list.append((pos, explode1))
							missile_exploded = True
							enemy_destroyed = True
						else:
							if y > 1: # Move left
								if random.random() < 0.01:
									new_list.append((pos, enemy_missile))

								remove_list.append((pos, enemy_left))
								if 0 < x:
									new_list.append(((x-1,y), enemy_left))
								elif x == 0:
									new_list.append(((x,y-1), enemy_right))  # Move down one row
							elif y == 1:  # Chance of landing
								if 0 < x:
									if random.random() < 0.9 or enemy_lander in cell:
										remove_list.append((pos, enemy_left))
										new_list.append(((x-1,y), enemy_left))
									else:
										remove_list.append((pos, enemy_left))
										new_list.append(((x,y), enemy_lander))
								else:
									remove_list.append((pos, enemy_left))
									new_list.append(((x+1,y), enemy_right))
									
					if enemy_right in cell: # Move randomly left and right, move down when at the edges
						# Check if hit by a player missile						
						if missile in cell:
							remove_list.append((pos, enemy_right))
							score_points.add(100)
							remove_list.append((pos, missile))
							new_list.append((pos, explode1))
							missile_exploded = True
							enemy_destroyed = True
						else:
							if y > 1: # Move right
								if random.random() < 0.01:
									new_list.append((pos, enemy_missile))
								remove_list.append((pos, enemy_right))
								if x < play_size-1:
									new_list.append(((x+1,y), enemy_right))
								elif x == play_size-1:
									new_list.append(((x,y-1), enemy_left))  # Move down one row
							elif y == 1:  # Chance of landing
								if x < play_size-1:
									if random.random() < 0.9 or enemy_lander in cell:
										remove_list.append((pos, enemy_right))
										new_list.append(((x+1,y), enemy_right))
									else:
										remove_list.append((pos, enemy_right))
										new_list.append((pos, enemy_lander))
								else:
									remove_list.append((pos, enemy_right))
									new_list.append(((x-1,y), enemy_left))
					
					if enemy_missile in cell: # Move down the screen
						if missile in cell or missile in r.view.get_at((x,y-1)):
							remove_list.append((pos, enemy_missile))
							remove_list.append((pos, missile))
							score_points.add(20)
							new_list.append((pos, explode1))
							missile_exploded = True
						else:
							if ship in cell: # Boom!
								remove_list.append((pos, enemy_missile))
								new_list.append((pos, explode1))
								r.view.erase_at((len(lbl_pilots.text)+score_pilots.value+3-1, play_size-1))
								new_list.append(((len(lbl_pilots.text)+score_pilots.value+3-1, play_size-1), explode1))
								if score_pilots.value < 1:
									game_over_flag = True
								else:
									score_pilots.add(-1)
								for px in xrange(0, play_size):
									r.view.erase_at((px, 1))
									new_list.append(((px, 1), random.choice([explode1, explode2, explode3])))
									
							if y > 1:
								remove_list.append((pos, enemy_missile))
								new_list.append(((x,y-1), enemy_missile))
							else:
								remove_list.append((pos, enemy_missile))
								new_list.append((pos, explode1))

					if missile in cell and missile_exploded == False:
						# Move up the screen
						if y < play_size-3:
							remove_list.append((pos, missile))
							new_list.append(((x,y+1), missile))
						else:
							remove_list.append((pos, missile))
					if missile in cell and enemy_destroyed == True:
						tick_rate -= 1
						if tick_rate < tick_rate_min:
							tick_rate = tick_rate_min
						if random.random() > 0.5:
							r.view.set_at((0, play_size-3), enemy_right)
						else:
							r.view.set_at((play_size-1, play_size-3), enemy_left)
				# Process play zone updates
				for (pos,thing) in remove_list:
					r.view.remove(pos, thing)
				for (pos,thing) in new_list:
					r.view.set_at(pos, thing)
			
			iterations += 1
			
			if game_over_flag:
				r.view.draw_label(lbl_game_over, [(play_size>>1)-4, play_size>>1])
			
			r.draw([0,0],[width, height])
			
			
		pygame.display.update()

		for event in pygame.event.get():
			if event.type == pygame.QUIT:
				keepGoing = False
			elif event.type == pygame.MOUSEBUTTONUP:
				if event.button == 1: # 1 == Left
					if not game_over_flag:
						if iterations - last_shot > tick_rate<<1:
							x, y = ship_pos
							if y < play_size-3:
								r.view.set_at((x,y), missile)
								r.view.set_at((x,y+1), explode1)
								last_shot = iterations
								score_points.value -= 1
								if score_points.value < 0:
									score_points.value = 0

			elif event.type == pygame.MOUSEMOTION:
				if not game_over_flag:
					(px,py) = event.pos
					cell_x = int(px/r.view.cell_width)
					# cell_y = int(py/r.view.cell_height)
					x,y = ship_pos
					if cell_x < x and 0 < x:  # Move left
						if r.view.get_at((x-1, y)) == []:
							r.view.remove(ship_pos, ship)
							ship_pos = x-1, y
							r.view.set_at(ship_pos, ship)
					if cell_x > x and x < play_size-1:  # Move right
						if r.view.get_at((x+1, y)) == []:
							r.view.remove(ship_pos, ship)
							ship_pos = x+1, y
							r.view.set_at(ship_pos, ship)
		
		level = int(score_points.value / 10000)
		if level_handled < level:
			r.view.set_at((play_size-1, play_size-random.randint(4,play_size>>1)), enemy_base1)
			score_pilots.add(1)
			level_handled = level

saucer_attack()

def random_tiles():  #  Messing about space-themed salvage
	size = width,height = 800,800  # Pygame
	r = RendererLens(pygame.display.set_mode(size, pygame.SRCALPHA))
	r.set_view(View2DLens())
	play_size = 50
	r.view.set_size( (play_size, play_size, 1, 1), (width/play_size, height/play_size))
	
	# Set up tiles
	tiles = Tiles()
	font_cells = "0123456789abcdefghijklmnopqrstuvwxyz"

	for c in font_cells:
		t = CharacterCellLens("font/"+str(c))
		tiles.add(str(c),t)

	game_cells = glob.glob(os.path.join("space_junk", "*.png"))
	for fn in game_cells:
		name = fn.replace(".png","")
		t = CharacterCellLens(name)
		tiles.add(name, t)

	for col in xrange(0, play_size):
		for row in xrange(0, play_size):
			if random.random() > 0.7:
				r.view.set_at((row, col), tiles.get(random.choice(tiles.list())))

	keepGoing = True
	iterations = 0
	pause = False
	while keepGoing:
		if pause == False:
			iterations += 1
			
			r.draw([0,0],[width, height])
			
			
		pygame.display.update()

		for event in pygame.event.get():
			if event.type == pygame.QUIT:
				keepGoing = False
			elif event.type == pygame.MOUSEBUTTONUP:
				if event.button == 1: # 1 == Left
					pause = not pause
					(px,py) = event.pos
	
def game_of_life(): # Conway game of Life
	size = width,height = 800,800  # Pygame
	r = RendererLens(pygame.display.set_mode(size, pygame.SRCALPHA))
	r.set_view(View2DLens())
	play_size = 50
	r.view.set_size( (play_size, play_size, 1, 1), (width/play_size, height/play_size))
	alive = CharacterCellLens("alive")
	alive.paper.add_frame(pygame.image.load("alive_frame2.png"))
	dead = CharacterCellLens("dead")
	
	# Initialise the playzone
	for col in xrange(0, play_size):
		for row in xrange(0, play_size):
			if random.random() > 0.8:
				r.view.set_at((row, col), alive)

	keepGoing = True
	iterations = 0
	pause = False
	while keepGoing:
		if pause == False:
			alive.tick()
			iterations += 1
			
			r.draw([0,0],[width>>3,height>>3])
			r.draw([width>>3,height>>3],[width>>2,height>>2])
			r.draw([(width>>3)+(width>>2),(height>>3)+(height>>2)],[width>>1,height>>1])
			r.draw([width-(width>>3),height-(height>>3)],[width>>3,height>>3])
			
			#  Game logic
			cells_new = {}
			cells_die = {}
			
			for col in xrange(0, play_size):
				for row in xrange(0, play_size):
					num_neighbors = 0
					for dx in xrange(-1,2):
						for dy in xrange(-1,2):
							if alive in r.view.get_at((row+dy,col+dx)) and not (dx == 0 and dy ==0):
								num_neighbors += 1
					if (num_neighbors < 2 or num_neighbors > 3) and (alive in r.view.get_at((row, col))):
						cells_die[(row,col)] = False
					elif num_neighbors == 3 and not (alive in r.view.get_at((row, col))):
						cells_new[(row,col)] = True

			for pos in cells_new:
				r.view.erase_at(pos)
				r.view.set_at(pos, alive)

			for pos in cells_die:
				r.view.erase_at(pos)
				r.view.set_at(pos, dead)
			
		pygame.display.update()

		for event in pygame.event.get():
			if event.type == pygame.QUIT:
				keepGoing = False
			elif event.type == pygame.MOUSEBUTTONUP:
				if event.button == 1: # 1 == Left
					pause = not pause
					(px,py) = event.pos

				
game_of_life()

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

