import pygame
from enum import Enum

from algorithms import Tuple2Int, Tile, Movement, Algorithm, Maze


class AnimationSpeed(Enum):
	SLOW = 1.2
	MEDIUM = 0.8
	FAST = 0.4


class Game:
	def __init__(self,
				 position: Tuple2Int,
				 size: Tuple2Int,
				 input_file: str):
		self._position = position
		self._size = size

		self._maze = Maze()
		self._maze.read_input(input_file)

		self._tile_size = 0
		# Graphics
		self._surface = pygame.Surface(size=size)
		self._rect = None

		self._agent_image = None
		self._agent_image_position = None

		self._stone_image = None
		self._stones_weights_labels: dict[Tuple2Int, pygame.Surface] = {}
		self._stones_images_positions: dict[Tuple2Int, tuple[float, float]] = {}

		self._switch_image = None
		self._brick_image = None
		self._blank_space_surface = None
		# Controls
		self._is_animating = False
		self._finished_animating = False
		self._animation_time = 0.0
		self._animation_speed = AnimationSpeed.MEDIUM.value
		self._movement_index = 0
		self._movement = (0, 0)
		self._action = None
		self._agent_position = None

		self._calculate_tiles_resolution()

		# self._maze.search_and_write_output(DEFAULT_OUTPUT_FILE, Algorithm.DFS)
		# self._maze.search_and_write_output(DEFAULT_OUTPUT_FILE, Algorithm.BFS)
		# self._maze.search_and_write_output(DEFAULT_OUTPUT_FILE, Algorithm.UFC)
		# self._maze.search_and_write_output(DEFAULT_OUTPUT_FILE, Algorithm.A_STAR)

	@property
	def position(self) -> Tuple2Int:
		return self._position

	@property
	def size(self) -> Tuple2Int:
		return self._size

	@property
	def tile_size(self) -> int:
		return self._tile_size

	@property
	def is_animating(self) -> bool:
		return self._is_animating

	@property
	def finished_animating(self) -> bool:
		return self._finished_animating

	@property
	def animation_speed(self) -> AnimationSpeed:
		return AnimationSpeed(self._animation_speed)

	@animation_speed.setter
	def animation_speed(self, new_speed: AnimationSpeed):
		old_progress = self._animation_time / self._animation_speed
		self._animation_speed = new_speed.value
		self._animation_time = old_progress * self._animation_speed

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
		width_padding = (width - self._tile_size * maze_cols) // 2
		height_padding = (height - self._tile_size * maze_rows) // 2
		self._rect = pygame.Rect(
			width_padding, height_padding, maze_cols * self._tile_size, maze_rows * self._tile_size)
		# Resize images
		self._agent_image = pygame.transform.smoothscale(
			pygame.image.load("assets/images/agent.png"), (self._tile_size, self._tile_size)).convert_alpha()
		self._stone_image = pygame.transform.smoothscale(
			pygame.image.load("assets/images/stone.png"), (self._tile_size, self._tile_size)).convert_alpha()
		self._switch_image = pygame.transform.smoothscale(
			pygame.image.load("assets/images/switch.png"), (self._tile_size, self._tile_size)).convert_alpha()
		self._brick_image = pygame.transform.smoothscale(
			pygame.image.load("assets/images/brick.png"), (self._tile_size, self._tile_size)).convert_alpha()

		self._blank_space_surface = pygame.Surface((self._tile_size, self._tile_size))
		self._blank_space_surface.fill("#bfbfbf")

		self._initialize_objects()
		return None

	def _initialize_objects(self) -> None:
		self._stones_weights_labels.clear()
		self._stones_images_positions.clear()

		label_size = self._tile_size / 1.6
		label_radius = self._tile_size / 3.2
		label_font = pygame.font.SysFont(name="monospace", size=int(label_radius), bold=True)  # Initial font size
		for stone_position, stone_weight in self._maze.state.stones_weights.items():
			label = label_font.render(f"{stone_weight}", True, "#010101")

			for scaling_factor in range(10, 1, -1):  # Scale down font size
				new_font = pygame.font.SysFont(name="monospace", size=int(label_radius * (scaling_factor - 1) / 10), bold=True)
				label = new_font.render(f"{stone_weight}", True, "#010101")
				if label.get_width() <= label_radius * 1.5:
					break

			label_surface = pygame.Surface((label_size, label_size), pygame.SRCALPHA)
			pygame.draw.circle(label_surface, color="#efefef", center=(label_radius, label_radius), radius=label_radius, width=0)
			pygame.draw.circle(label_surface, color="#010101", center=(label_radius, label_radius), radius=label_radius, width=2)
			label_surface.blit(label, ((label_surface.get_width() - label.get_width()) / 2, (label_surface.get_height() - label.get_height()) / 2))
			self._stones_weights_labels[stone_position] = label_surface

		agent_row, agent_col = self._maze.state.agent_position
		agent_x = self._rect.left + agent_col * self._tile_size
		agent_y = self._rect.top + agent_row * self._tile_size
		self._agent_image_position = (agent_x, agent_y)

		for stone_row, stone_col in self._maze.state.stones_weights.keys():
			stone_x = self._rect.left + stone_col * self._tile_size
			stone_y = self._rect.top + stone_row * self._tile_size
			self._stones_images_positions[(stone_row, stone_col)] = (stone_x, stone_y)
		return None

	def _calculate_movement(self) -> tuple[Tuple2Int, str]:
		match (action := self._maze.path[self._movement_index]):
			case 'l' | 'L':
				movement, _ = Movement.LEFT.value
			case 'r' | 'R':
				movement, _ = Movement.RIGHT.value
			case 'u' | 'U':
				movement, _ = Movement.UP.value
			case _:
				movement, _ = Movement.DOWN.value
		return movement, action

	def start_animation(self) -> None:
		self._is_animating = True
		self._animation_time = 0.0
		self._movement_index = 0
		self._movement, self._action = self._calculate_movement()

		horizontal, vertical = self._movement
		agent_row, agent_col = self._maze.state.agent_position
		self._agent_position = (agent_row + vertical, agent_col + horizontal)
		return None

	def pause_resume_animation(self) -> None:
		self._is_animating = not self._is_animating
		return None

	def reset_animation(self) -> None:
		self._is_animating = False
		self._finished_animating = False
		self._initialize_objects()
		return None

	def start_search(self, algorithm: Algorithm) -> bool:
		match algorithm:
			case Algorithm.DFS:
				result = self._maze.depth_first_search()
			case Algorithm.BFS:
				result = self._maze.breadth_first_search()
			case Algorithm.UFC:
				result = self._maze.uniform_cost_search()
			case _:
				result = self._maze.a_star_search()
		return result

	def update(self, time_delta: float) -> None:
		if not self._is_animating:
			return None

		self._animation_time += time_delta
		if self._animation_time >= self._animation_speed:  # Reach new tile
			self._animation_time = 0.0
			self._movement_index += 1
			if self._movement_index >= len(self._maze.path):
				self._is_animating = False
				self._finished_animating = True
				return None
			self._movement, self._action = self._calculate_movement()

			horizontal, vertical = self._movement
			agent_row, agent_col = self._agent_position
			self._agent_position = (agent_row + vertical, agent_col + horizontal)

			agent_x = self._rect.left + agent_col * self._tile_size
			agent_y = self._rect.top + agent_row * self._tile_size
			self._agent_image_position = (agent_x, agent_y)

			stone_position = (agent_row + vertical * 2, agent_col + horizontal * 2)
			if self._action.isupper():
				stone_x = self._rect.left + (agent_col + horizontal) * self._tile_size
				stone_y = self._rect.top + (agent_row + vertical) * self._tile_size
				self._stones_images_positions.pop(self._agent_position)
				self._stones_images_positions.update({stone_position: (stone_x, stone_y)})
				self._stones_weights_labels.update({stone_position: self._stones_weights_labels.pop(self._agent_position)})
		# Update images positions
		distance = time_delta / self._animation_speed * self._tile_size
		horizontal, vertical = self._movement
		agent_image_x, agent_image_y = self._agent_image_position
		self._agent_image_position = (agent_image_x + horizontal * distance, agent_image_y + vertical * distance)

		if self._action.isupper():
			agent_row, agent_col = self._agent_position
			stone_position = (agent_row + vertical, agent_col + horizontal)
			stone_x, stone_y = self._stones_images_positions[stone_position]
			self._stones_images_positions[stone_position] = (stone_x + horizontal * distance, stone_y + vertical * distance)
		return None

	def process_event(self, event: pygame.event.Event) -> bool:
		return True

	def draw(self, surface: pygame.Surface) -> None:
		"""
		Draw the game on the given background

		:param surface: Surface to draw
		:return: None
		"""
		self._surface.fill("#4d4d4d")
		# Tiles
		for row in range(self._maze.rows):
			for col in range(self._maze.cols):
				tile = self._maze.tiles[row][col]
				if tile == Tile.NONE:
					continue

				if self._maze.state.switches_states.get((row, col)) is not None:
					tile_surface = self._blank_space_surface
				else:
					tile_surface = self._blank_space_surface if tile == Tile.BLANK else self._brick_image

				tile_x = self._rect.left + col * self._tile_size
				tile_y = self._rect.top + row * self._tile_size
				self._surface.blit(tile_surface, (tile_x, tile_y))
		# Border
		pygame.draw.rect(self._surface, "#000000", (0, 0, *self._size), width=1)
		# Grid
		grid_x = self._rect.left
		while grid_x <= self._rect.right + 1:
			pygame.draw.line(self._surface, "#c9c9c9", (grid_x, self._rect.top), (grid_x, self._rect.bottom))
			grid_x += self._tile_size

		grid_y = self._rect.top
		while grid_y <= self._rect.bottom + 1:
			pygame.draw.line(self._surface, "#c9c9c9", (self._rect.left, grid_y), (self._rect.right, grid_y))
			grid_y += self._tile_size
		# Agent
		self._surface.blit(self._agent_image, self._agent_image_position)
		# Switch
		for switch_row, switch_col in self._maze.state.switches_states.keys():
			switch_x = self._rect.left + switch_col * self._tile_size
			switch_y = self._rect.top + switch_row * self._tile_size
			self._surface.blit(self._switch_image, (switch_x, switch_y))
		# Stone
		for (stone_image_x, stone_image_y), stone_weight_label in zip(self._stones_images_positions.values(), self._stones_weights_labels.values()):
			self._surface.blit(self._stone_image, (stone_image_x, stone_image_y))
			# Stone weight label
			stone_label_x = stone_image_x + (self._tile_size - stone_weight_label.get_width()) // 2
			stone_label_y = stone_image_y + (self._tile_size - stone_weight_label.get_height()) // 2
			self._surface.blit(stone_weight_label, (stone_label_x, stone_label_y))

		pygame.draw.rect(self._surface, "#efefef", self._surface.get_rect(topleft=(0, 0)), width=1)

		surface.blit(self._surface, self._position)
		return None
