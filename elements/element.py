import pygame
from abc import ABC, abstractmethod


class Element(ABC):
	"""
	Abstract base class for all pygame UI elements
	"""

	@staticmethod
	def validate_theme(kwargs: dict, valid_kwargs: list[str]) -> None:
		"""
		Validate theme keyword arguments
		"""
		try:
			theme = kwargs.pop("theme")
		except KeyError:
			pass
		else:
			if theme is not None and isinstance(theme, dict):
				kwargs.update(theme)

		for key in kwargs.keys():
			if key not in valid_kwargs:
				error_msg = f"Unexpected keyword argument: {key}!"
				raise KeyError(error_msg)
		return None

	@abstractmethod
	def update(self, time_delta: float) -> None:
		pass

	@abstractmethod
	def process_event(self, event: pygame.event.Event) -> bool:
		pass

	@abstractmethod
	def draw(self, background: pygame.Surface) -> None:
		pass
