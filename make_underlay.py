import pygame

img = pygame.Surface((880,800), pygame.SRCALPHA)

sq1 = pygame.Surface((10,10), pygame.SRCALPHA)
sq1.fill([0x80,0x80,0x80,0xff])
sq2 = pygame.Surface((10,10), pygame.SRCALPHA)
sq2.fill([0x10,0x10,0x10,0xff])

for y in xrange(0, 80):
	for x in xrange(0, 88):
		if (y+x)%2 == 0:
			img.blit(sq1, [x*10, y*10])
		else:
			img.blit(sq2, [x*10, y*10])
			
pygame.image.save(img,"underlay.png")