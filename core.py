import pygame

from algorithms import Tuple2Int, Tile, State, Maze, \
	depth_first_search, breadth_first_search, uniform_cost_search, a_star_search


class Game:
	def __init__(self,
				 position: Tuple2Int,
				 size: Tuple2Int,
				 input_file: str):
		self._position = position
		self._size = size

		self._maze = Maze(input_file=input_file)
		self._tile_size = 0
		# Graphics
		self._surface = pygame.Surface(size=size)

		self._agent_image = None
		self._stone_small_image = None
		self._stone_image = None
		self._switch_normal_image = None
		self._switch_image = None
		self._brick_image = None
		self._blank_space_surface = None
		self._pushed_switch_surface = None

		self._stones_weights_labels = {}
		self._maze_rect = None

		self._calculate_tiles_resolution()
		# depth_first_search(self._maze.get_state())
		# breadth_first_search(self._maze.get_state())
		# uniform_cost_search(self._maze.get_state())
		a_star_search(self._maze.get_state())

	@property
	def position(self) -> Tuple2Int:
		return self._position

	@property
	def size(self) -> Tuple2Int:
		return self._size

	@property
	def tile_size(self) -> int:
		return self._tile_size

	def _calculate_tiles_resolution(self) -> None:
		"""
		Calculate tiles' resolution based on game size and maze size

		:return: None
		"""
		width, height = self._size
		maze_rows, maze_cols = self._maze.size
		# Calculate tile size
		self._tile_size = width // maze_cols  # Try matching the width first
		if self._tile_size * maze_rows > height:  # If height is exceeded, match the height instead
			self._tile_size = height // maze_rows
		# Calculate maze rect
		width_padding = (width - self._tile_size * maze_cols) / 2
		height_padding = (height - self._tile_size * maze_rows) / 2
		self._maze_rect = pygame.Rect(
			width_padding, height_padding, maze_cols * self._tile_size, maze_rows * self._tile_size)
		# Resize images
		self._agent_image = pygame.transform.smoothscale(
			pygame.image.load("assets/agent.png"), (self._tile_size, self._tile_size)).convert_alpha()
		self._stone_image = pygame.transform.smoothscale(
			pygame.image.load("assets/stone.png"), (self._tile_size, self._tile_size)).convert_alpha()
		self._switch_image = pygame.transform.smoothscale(
			pygame.image.load("assets/switch.png"), (self._tile_size, self._tile_size)).convert_alpha()
		self._brick_image = pygame.transform.smoothscale(
			pygame.image.load("assets/brick.png"), (self._tile_size, self._tile_size)).convert_alpha()

		self._blank_space_surface = pygame.Surface((self._tile_size, self._tile_size))
		self._blank_space_surface.fill("#bfbfbf")

		self._pushed_switch_surface = pygame.Surface((self._tile_size, self._tile_size))
		self._pushed_switch_surface.fill("#24e357")

		label_size = self._tile_size / 1.6
		label_radius = self._tile_size / 3.2
		label_font = pygame.font.SysFont(name="monospace", size=int(label_radius), bold=True)  # Initial font size
		for stone_position in self._maze.get_stones_positions():
			label = label_font.render(f"{self._maze.get_stone_weight(stone_position)}", True, "#010101")

			for scaling_factor in range(10, 1, -1):  # Scale down font size
				new_font = pygame.font.SysFont(name="monospace", size=int(label_radius * (scaling_factor - 1) / 10), bold=True)
				label = new_font.render(f"{self._maze.get_stone_weight(stone_position)}", True, "#010101")
				if label.get_width() <= label_radius * 1.5:
					break

			label_surface = pygame.Surface((label_size, label_size), pygame.SRCALPHA)
			pygame.draw.circle(label_surface, color="#efefef", center=(label_radius, label_radius), radius=label_radius, width=0)
			pygame.draw.circle(label_surface, color="#010101", center=(label_radius, label_radius), radius=label_radius, width=2)
			label_surface.blit(label, ((label_surface.get_width() - label.get_width()) / 2, (label_surface.get_height() - label.get_height()) / 2))
			self._stones_weights_labels[stone_position] = label_surface
		return None

	# def update(self, time_delta: float) -> None:
	# 	return None
	#
	# def process_event(self, , event: pygame.event.Event) -> bool:
	# 	return True

	def draw(self, background: pygame.Surface) -> None:
		"""
		Draw the game on the given background

		:param background: Surface to draw
		:return: None
		"""
		self._surface.fill("#4d4d4d")
		# Tiles
		for row in range(self._maze.rows):
			for col in range(self._maze.cols):
				tile = self._maze.get_tile((row, col))
				if tile == Tile.NONE:
					continue

				if (switch_state := self._maze.get_switch_state((row, col))) is not None:
					surface = self._pushed_switch_surface if switch_state else self._blank_space_surface
				else:
					surface = self._blank_space_surface if tile == Tile.BLANK else self._brick_image

				tile_x = self._maze_rect.left + col * self._tile_size
				tile_y = self._maze_rect.top + row * self._tile_size
				self._surface.blit(surface, (tile_x, tile_y))
		# Border
		pygame.draw.rect(self._surface, "#000000", (0, 0, *self._size), width=1)
		# Grid
		grid_x = self._maze_rect.left
		while grid_x <= self._maze_rect.right + 1:
			pygame.draw.line(self._surface, "#c9c9c9", (grid_x, self._maze_rect.top), (grid_x, self._maze_rect.bottom))
			grid_x += self._tile_size

		grid_y = self._maze_rect.top
		while grid_y <= self._maze_rect.bottom + 1:
			pygame.draw.line(self._surface, "#c9c9c9", (self._maze_rect.left, grid_y), (self._maze_rect.right, grid_y))
			grid_y += self._tile_size
		# Agent
		agent_row, agent_col = self._maze.agent_position
		agent_x = self._maze_rect.left + agent_col * self._tile_size
		agent_y = self._maze_rect.top + agent_row * self._tile_size
		self._surface.blit(self._agent_image, (agent_x, agent_y))
		# Switch
		for switch_row, switch_col in self._maze.get_switches_positions():
			switch_x = self._maze_rect.left + switch_col * self._tile_size
			switch_y = self._maze_rect.top + switch_row * self._tile_size
			self._surface.blit(self._switch_image, (switch_x, switch_y))
		# Stone
		for (stone_row, stone_col), weight_label in self._stones_weights_labels.items():
			stone_x = self._maze_rect.left + stone_col * self._tile_size
			stone_y = self._maze_rect.top + stone_row * self._tile_size
			self._surface.blit(self._stone_image, (stone_x, stone_y))
			# Stone weight
			self._surface.blit(weight_label, (
				stone_x + (self._tile_size - weight_label.get_width()) / 2, stone_y + (self._tile_size - weight_label.get_height()) / 2))

		background.blit(self._surface, self._position)
		return None
