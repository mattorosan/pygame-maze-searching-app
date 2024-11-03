import os
import sys
import time
import heapq
import copy

from enum import Enum
from typing import Optional
from collections import deque

Tuple2Int = tuple[int, int]


class Tile(Enum):
	NONE = None
	BLANK = ' '
	BRICK = '#'


class Movement(Enum):
	LEFT = ((-1, 0), 'l')
	RIGHT = ((1, 0), 'r')
	UP = ((0, -1), 'u')
	DOWN = ((0, 1), 'd')


class Algorithm(Enum):
	DFS = "Depth First Search"
	BFS = "Breadth First Search"
	UFC = "Uniform Cost Search"
	A_STAR = "A Star Search"


class State:
	def __init__(self):
		self.agent_position: Tuple2Int = tuple()
		self.stones_weights: dict[Tuple2Int, int] = {}
		self.switches_states: dict[Tuple2Int, bool] = {}

	def __lt__(self, other):
		return self.heuristic() < other.heuristic()

	def is_finished(self) -> bool:
		return all(switch_state for switch_state in self.switches_states.values())

	def get_agent_movements(self) -> list[tuple[Tuple2Int, str, Optional[Tuple2Int]]]:
		"""
		Get all the movements that agent can make from his position

		:return: List of movements, which are tuples of new coordinates, action and new stone coordinates (if there is a valid stone push, else None)
		"""
		movements = []
		row, col = self.agent_position
		for movement in Movement:
			(horizontal, vertical), action = movement.value
			new_row = row + vertical
			new_col = col + horizontal
			# Stone in the way
			if (new_row, new_col) in self.stones_weights.keys():
				new_stone_row = new_row + vertical
				new_stone_col = new_col + horizontal
				# Check for push against other stones or walls
				if (new_stone_row, new_stone_col) in self.stones_weights.keys():
					continue
				new_stone_position = (new_stone_row, new_stone_col)
			else:
				new_stone_position = None
			movements.append(((new_row, new_col), action.upper() if new_stone_position else action, new_stone_position))
		return movements

	def heuristic(self) -> int:
		distance_cost: [[Tuple2Int, Tuple2Int], int] = lambda begin, end: abs(begin[0] - end[0]) + abs(begin[1] - end[1])
		total_cost = 0
		for switch_position in self.switches_states.keys():
			push_stone_cost = []
			move_to_stone_cost = []
			for stone_position, stone_weight in self.stones_weights.items():
				# The cost of pushing the stone to the switch
				push_stone_cost.append(distance_cost(stone_position, switch_position) * stone_weight)
				# Being nearer to the more "positionally advantageous" stone is better
				move_to_stone_cost.append(distance_cost(self.agent_position, stone_position) + push_stone_cost[-1])
			total_cost += sum(push_stone_cost) + min(move_to_stone_cost)
		return total_cost


class Maze:
	def __init__(self):
		self._state = State()
		self._tiles: list[list[Tile]] = []
		self._size: Tuple2Int = (0, 0)
		# Results
		self._path = ""
		self._time = 0
		self._memory = 0
		self._nodes_count = 0

	@property
	def state(self) -> State:
		return self._state

	@property
	def tiles(self) -> list[list[Tile]]:
		return self._tiles

	@property
	def size(self) -> Tuple2Int:
		return self._size

	@property
	def path(self) -> str:
		return self._path

	@property
	def time(self) -> int:
		return self._time

	@property
	def memory(self) -> int:
		return self._memory

	@property
	def nodes_count(self) -> int:
		return self._nodes_count

	@property
	def rows(self) -> int:
		return self._size[0]

	@property
	def cols(self) -> int:
		return self._size[1]

	def read_input(self, filename: str) -> bool:
		"""
		Read the maze data from the input file

		:param filename: Input file name (absolute path)
		:return: Whether the read process was successful
		"""
		if not os.path.exists(filename):
			print(f"File \"{filename}\" not found!")
			return False

		with open(filename, 'r') as file:
			stone_weights_list = [int(val) for val in file.readline().split(' ')[::-1]]
			maze_strings_list = file.read().split('\n')

		maze_cols = max(len(line) for line in maze_strings_list)
		for row, line in enumerate(maze_strings_list):
			self._tiles.append([])
			maze_cols = max(maze_cols, len(line))

			line_length = len(line)
			if line_length < maze_cols:
				maze_strings_list[row] = f"{line}{(maze_cols - line_length) * ' '}"
			else:
				maze_cols = line_length

			for col, char in enumerate(maze_strings_list[row]):
				tile = Tile.NONE
				match char:
					case '@' | '+':  # Agent/Agent on switch
						self._state.agent_position = (row, col)
					case '$':  # Stone
						self._state.stones_weights[(row, col)] = stone_weights_list.pop()
					case '.':  # Switch
						self._state.switches_states[(row, col)] = False
					case '*':  # Stone on switch
						self._state.stones_weights[(row, col)] = stone_weights_list.pop()
						self._state.switches_states[(row, col)] = True
					case ' ':  # Blank space
						pass
					case '#':  # Brick
						tile = Tile.BRICK
					case _:
						print(f"Invalid input file character: \'{char}\'!")
						return False
				self._tiles[row].append(tile)
		self._size = (len(self._tiles), maze_cols)

		self._calculate_blank_tiles(maze_strings_list)
		return True

	def write_output(self, filename: str, algorithm: Algorithm) -> bool:
		"""
		Write the current state to the output file

		:param algorithm: The algorithm used for searching
		:param filename: Output file name (absolute path)
		:return: Whether the write process was successful
		"""
		if not os.path.exists(filename):
			print(f"Output file \"{filename}\" not found!")
			return False

		with open(filename, "w") as file:
			file.write(f"{algorithm.value}\n")
			file.write(f"Steps: {len(self._path)}, Weight: ?, Node: {self._nodes_count}, Time (ms): {self._time}, Memory (MB): {self._memory}\n")
			file.write(f"{self._path}\n")
		return True

	def _calculate_blank_tiles(self, maze_strings: list[str]) -> None:
		"""
		Calculate tiles that are inside the maze boundaries

		:param maze_strings: List of maze strings split from the input file
		:return: None
		"""
		maze_rows, maze_cols = self._size
		# Calculate the horizontal parts
		horizontal_parts: list[list[Tuple2Int]] = []
		for row, line in enumerate(maze_strings):
			begin = end = 0
			is_valid_part = False
			horizontal_parts.append([])
			for col, char in enumerate(line):
				if char == '#':
					if is_valid_part:  # End of a valid part
						horizontal_parts[row].append((begin, end))
						is_valid_part = False
					if col + 1 < len(line) and line[col + 1] != '#':  # Beginning of a valid part
						begin = end = col + 1
						is_valid_part = True
					continue
				if is_valid_part:
					end += 1
		# Calculate the vertical parts
		vertical_parts: list[list[Tuple2Int]] = []
		for col in range(maze_cols):
			begin = end = 0
			is_valid_part = False
			vertical_parts.append([])
			for row, line in enumerate(maze_strings):
				if line[col] == '#':
					if is_valid_part:  # End of a valid part
						vertical_parts[col].append((begin, end))
						is_valid_part = False
					if row + 1 < maze_rows and maze_strings[row + 1][col] != '#':  # Beginning of a valid part
						begin = end = row + 1
						is_valid_part = True
					continue
				if is_valid_part:
					end += 1
		# The intersections of the horizontal and vertical parts are valid ones
		for i, row in enumerate(self._tiles):
			for left, right in horizontal_parts[i]:
				mid = left + (right - left) // 2  # Any position works, since the whole part must be valid, we only need to check one
				for top, bottom in vertical_parts[mid]:
					if i not in range(top, bottom):
						continue
					# Is valid part
					for j in range(left, right):  # Set all valid tiles to Tile.BLANK
						row[j] = Tile.BLANK
					break
		return None

	# ----------------------------------------------------------------
	# Algorithms
	# ----------------------------------------------------------------
	def depth_first_search(self) -> bool:
		"""
		Search for path using DFS

		:return: Whether a path was found
		"""
		visited = {self._compress_state(self._state)}
		stack = [(self._state, "")]
		self._time = time.time()
		self._memory = 0
		self._nodes_count = 0
		while stack:
			self._nodes_count += 1
			current_state, current_path = stack.pop()
			if current_state.is_finished():
				self._path = current_path
				self._time = (time.time() - self._time) * 1000
				self._memory /= 1000000
				return True

			for new_state, new_path in self._generate_new_states(current_state, current_path):
				if len(visited) != (visited.add(self._compress_state(new_state)) or len(visited)):  # New state added
					stack.append((new_state, new_path))
		return False

	def breadth_first_search(self) -> bool:
		"""
		Search for path using BFS

		:return: Whether a path was found
		"""
		visited = {self._compress_state(self._state)}
		dequeue = deque([(self._state, "")])
		self._time = time.time()
		self._memory = 0
		self._nodes_count = 0
		while dequeue:
			self._nodes_count += 1
			current_state, current_path = dequeue.popleft()
			if current_state.is_finished():
				self._path = current_path
				self._time = (time.time() - self._time) * 1000
				self._memory /= 1000000
				return True

			for new_state, new_path in self._generate_new_states(current_state, current_path):
				if len(visited) != (visited.add(self._compress_state(new_state)) or len(visited)):  # New state added
					dequeue.append((new_state, new_path))
		return False

	def uniform_cost_search(self) -> bool:
		"""
		Search for path using UFC

		:return: Whether a path was found
		"""
		visited = {self._compress_state(self._state)}
		states_heapq = [(0, self._state, "")]
		self._time = time.time()
		self._memory = 0
		self._nodes_count = 0
		while states_heapq:
			self._nodes_count += 1
			current_cost, current_state, current_path = heapq.heappop(states_heapq)
			if current_state.is_finished():
				self._path = current_path
				self._time = (time.time() - self._time) * 1000
				self._memory /= 1000000
				return True

			for new_state, new_path in self._generate_new_states(current_state, current_path):
				if len(visited) != (visited.add(self._compress_state(new_state)) or len(visited)):  # New state added
					heapq.heappush(states_heapq, (current_cost + 1, new_state, new_path))
		return False

	def a_star_search(self) -> bool:
		"""
		Search for path using A*

		:return: Whether a path was found
		"""
		visited = {self._compress_state(self._state)}
		states_heapq = [(0, self._state, "")]
		self._time = time.time()
		self._memory = 0
		self._nodes_count = 0
		while states_heapq:
			self._nodes_count += 1
			current_cost, current_state, current_path = heapq.heappop(states_heapq)
			if current_state.is_finished():
				self._path = current_path
				self._time = (time.time() - self._time) * 1000
				self._memory /= 1000000
				return True

			for new_state, new_path in self._generate_new_states(current_state, current_path):
				if len(visited) != (visited.add(self._compress_state(new_state)) or len(visited)):  # New state added
					heapq.heappush(states_heapq, (current_cost + current_state.heuristic(), new_state, new_path))
		return False

	def _generate_new_states(self, current_state: State, current_path: str) -> list[tuple[State, str]]:
		"""
		Generates new states from agent movement of the given state

		:param current_state: Current state to generate
		:param current_path: Path generated so far
		:return: List of valid states and paths
		"""

		new_states = []
		for new_agent_position, action, new_stone_position in current_state.get_agent_movements():
			new_agent_row, new_agent_col = new_agent_position
			if self._tiles[new_agent_row][new_agent_col] == Tile.BRICK:
				continue

			new_state = copy.deepcopy(current_state)
			new_state.agent_position = new_agent_position
			if new_stone_position is not None:  # Push stone
				new_stone_row, new_stone_col = new_stone_position
				if self._tiles[new_stone_row][new_stone_col] == Tile.BRICK:
					continue
				new_state.stones_weights.update({new_stone_position: new_state.stones_weights.pop(new_agent_position)})

				if new_agent_position in new_state.switches_states.keys():  # Push stone out of switch
					new_state.switches_states[new_agent_position] = False

				if new_stone_position in new_state.switches_states.keys():  # Push stone into switch
					new_state.switches_states[new_stone_position] = True
			new_states.append((new_state, f"{current_path}{action}"))
			self._memory += sys.getsizeof(new_state)
		return new_states

	def _compress_state(self, state: State) -> str:
		"""
		Compress the current state into a string for look up

		:state: State to compress
		:return: State string
		"""
		lines = [[tile.value or ' ' for tile in row] for row in self._tiles]
		for switch_row, switch_col in state.switches_states.keys():
			lines[switch_row][switch_col] = '.'

		for stone_row, stone_col in state.stones_weights.keys():
			lines[stone_row][stone_col] = '$' if lines[stone_row][stone_col] == ' ' else '*'

		agent_row, agent_col = state.agent_position
		lines[agent_row][agent_col] = '@' if lines[agent_row][agent_col] == ' ' else '+'
		return '\n'.join("".join(line) for line in lines)
