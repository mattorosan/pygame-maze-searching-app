import pygame

import elements
from core import AnimationSpeed, Algorithm, Game
from elements.button import PushButton
from elements.dropdown import Dropdown
from constants import FPS, WINDOW_SIZE, GAME_POSITION, GAME_SIZE, BUTTON_THEME, BUTTON_THEME_2, ANIMATION_SPEED_OPTIONS, ALGORITHM_OPTIONS, \
	DROPDOWN_THEME


class MainGui:
	def __init__(self,
				 input_file: str):
		self._size = WINDOW_SIZE
		self._fps = FPS

		self._clock = pygame.time.Clock()

		self._screen = pygame.display.set_mode(self._size, pygame.SRCALPHA)
		pygame.display.set_caption("Ares's Adventure")
		pygame.display.set_icon(pygame.image.load("assets/icon/icon_1.png").convert())

		self._start_button = PushButton(
			position=(925, 50), size=(200, 40), button_id="start", text="Start",
			is_instant=True, is_disabled=True,
			idle_img="assets/widgets/start.png",
			theme=BUTTON_THEME
		)
		self._pause_resume_button = PushButton(
			position=(925, 125), size=(200, 40), button_id="pause_resume", text="Pause",
			is_latching=True, is_disabled=True,
			idle_img="assets/widgets/pause.png",
			pressed_img="assets/widgets/resume.png",
			theme=BUTTON_THEME
		)
		self._reset_button = PushButton(
			position=(925, 200), size=(200, 40), button_id="reset", text="Reset",
			is_instant=False, is_disabled=True,
			idle_img="assets/widgets/reset.png",
			theme=BUTTON_THEME
		)
		self._execute_search_button = PushButton(
			position=(945, 500), size=(160, 80), button_id="search",
			is_instant=False,
			idle_img="assets/widgets/search.png",
			disabled_img="assets/widgets/disabled_search.png",
			theme=BUTTON_THEME_2
		)
		self._buttons = [
			self._start_button,
			self._pause_resume_button,
			self._reset_button,
			self._execute_search_button,
		]

		self._animation_speed_dropdown = Dropdown(
			position=(900, 320), size=(250, 40), widget_id="select_animation_speed",
			options=ANIMATION_SPEED_OPTIONS, options_display=3, option_size=(elements.AUTO_VALUE, 28),
			theme=DROPDOWN_THEME
		)
		self._animation_speed_dropdown.select("Medium")

		self._algorithm_dropdown = Dropdown(
			position=(900, 440), size=(250, 40), widget_id="select_algorithm",
			options=ALGORITHM_OPTIONS, options_display=4, option_size=(elements.AUTO_VALUE, 28),
			theme=DROPDOWN_THEME
		)
		self._algorithm_dropdown.select(3)

		self._dropdowns = [
			self._animation_speed_dropdown,
			self._algorithm_dropdown,
		]
		self._previous_dropdown = None

		self._labels = {}
		font = pygame.font.SysFont("Arial", 20, bold=True)
		for i, text in enumerate(("Animation speed", "Algorithm")):
			label = font.render(text, True, "#efefef")
			label_position = (900 + (250 - label.get_width()) / 2, 320 + i * 120 - label.get_height() * 1.5)
			self._labels.update({label: label_position})

		self._pending_tasks = []

		self._game = Game(position=GAME_POSITION, size=GAME_SIZE, input_file=input_file)

	def main_loop(self) -> None:
		"""
		Gui main loop

		:return: None
		"""
		run = True
		while run:
			ui_refresh_rate = self._clock.tick(self._fps) / 1000
			self.update(ui_refresh_rate)
			for event in pygame.event.get():
				if event.type == pygame.QUIT:
					run = False
				self.process_event(event)
			self.draw(self._screen)
		return None

	def update(self, time_delta: float) -> None:
		"""
		Update gui after given time delta

		:param time_delta: Time elapsed between each update
		:return: None
		"""
		if self._game.finished_animating:
			self._pause_resume_button.set_mode(False)

		for button in self._buttons:
			button.update(time_delta)

		for dropdown in self._dropdowns:
			dropdown.update(time_delta)

		self._game.update(time_delta)
		pygame.display.flip()

		while self._pending_tasks:
			task = self._pending_tasks.pop()
			task()
		return None

	def process_event(self, event: pygame.event.Event) -> bool:
		"""
		Process gui event

		:param event: Gui event
		:return: Whether gui event is consumed
		"""
		for dropdown in self._dropdowns:
			if dropdown.process_event(event):
				if dropdown.is_active:
					if dropdown.event == Dropdown.event.OPEN_SELECTION_BOX:
						if self._previous_dropdown is not None:
							self._previous_dropdown.close()
						self._previous_dropdown = dropdown
				else:
					self._previous_dropdown = None
					if dropdown.event == Dropdown.event.SELECT_NEW_OPTION:
						match dropdown:
							case self._animation_speed_dropdown:
								self._game.animation_speed = list(AnimationSpeed)[dropdown.selected_option_index]
							case self._algorithm_dropdown:
								if self._execute_search_button.is_disabled:
									self._execute_search_button.set_mode(True)
					else:
						continue
				return True

		for button in self._buttons:
			if button.process_event(event):
				match button:
					case self._start_button:
						self._pause_resume_button.set_mode(True)
						self._reset_button.set_mode(True)
						self._start_button.set_mode(False)
						self._game.start_animation()
					case self._pause_resume_button:
						self._pause_resume_button.text = "Pause" if not self._pause_resume_button.state else "Resume"
						self._game.pause_resume_animation()
					case self._reset_button:
						self._start_button.set_mode(True)
						self._pause_resume_button.set_mode(False)
						self._pause_resume_button.text = "Pause"
						self._reset_button.set_mode(False)
						self._game.reset_animation()
					case self._execute_search_button:
						button.set_mode(False)
						# Delay the execution to allow the button to redraw its new state

						def _task():
							self._game.start_search(list(Algorithm)[self._algorithm_dropdown.selected_option_index])
							self._start_button.set_mode(True)
							self._pause_resume_button.set_mode(False)
							self._pause_resume_button.text = "Pause"
							self._reset_button.set_mode(False)
							self._execute_search_button.set_mode(True)
							self._game.reset_animation()
						self._pending_tasks.append(_task)
					case _:
						pass
				return True
		return False

	def draw(self, surface: pygame.Surface) -> None:
		"""
		Draw the gui to the given surface

		:param surface: Surface to draw
		:return: None
		"""
		self._screen.fill("#0d0e2e")

		for label, label_position in self._labels.items():
			surface.blit(label, label_position)

		for button in self._buttons:
			button.draw(surface)

		active_dropdown = None
		for dropdown in self._dropdowns:
			if dropdown.is_active:
				active_dropdown = dropdown
				continue
			dropdown.draw(surface)
		if active_dropdown is not None:
			active_dropdown.draw(surface)

		self._game.draw(surface)
		return None


if __name__ == '__main__':
	pygame.init()

	gui = MainGui(input_file="input/input_3.txt")
	gui.main_loop()

	pygame.quit()
