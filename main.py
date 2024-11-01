import pygame

import core

pygame.init()


def main() -> None:
	screen = pygame.display.set_mode((1200, 650), pygame.SRCALPHA)
	game = core.Game(position=(50, 50), size=(800, 500), input_file="input/input-3.txt")  # 5, 7, 8, 9, 10

	run = True
	while run:
		for event in pygame.event.get():
			if event.type == pygame.QUIT:
				run = False

		screen.fill("#bdbdbd")
		game.draw(screen)

		pygame.display.update()
	return None


if __name__ == '__main__':
	main()
