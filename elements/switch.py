import os
import pygame
from typing import Callable

from .element import Element
from .constants import Tuple2Int


class Switch(Element):
    """
    Switch class provides toggle switch widget

    :param position: Switch position
    :param size: Switch square_dimensions
    :param widget_id: Widget id
    :param state: Switch state
    """

    # Keyword arguments
    keyword_arguments = [
        "theme",
        "on_img", "off_img"
    ]

    def __init__(self,
                 position: Tuple2Int,
                 size: Tuple2Int,
                 widget_id: str,
                 callback: Callable = None,
                 state: bool = False,
                 **kwargs):
        self.x, self.y = position
        self._width, self._height = size

        self.rect = pygame.Rect(position, size)
        self.widget_id = widget_id
        self._state = state

        self._callback = callback

        self._img_dict = {}
        self._load_theme(kwargs)

    @property
    def position(self) -> Tuple2Int:
        return self.x, self.y

    @property
    def size(self) -> Tuple2Int:
        return self._width, self._height

    @property
    def width(self) -> int:
        return self._width

    @property
    def height(self) -> int:
        return self._height

    @property
    def state(self) -> bool:
        return self._state

    def _load_theme(self, kwargs: dict[str]) -> None:
        """
        Load switch appearance theme
        """
        super().validate_theme(kwargs, Switch.keyword_arguments)
        self._img_dict.update({
            True: kwargs.get("on_img", "elements/assets/switch_default/on_switch.png"),
            False: kwargs.get("off_img", "elements/assets/switch_default/off_switch.png")
        })
        for key, value in self._img_dict.items():
            if isinstance(value, (bytes, str)):
                if os.path.exists(value):
                    self._img_dict[key] = pygame.transform.smoothscale(pygame.image.load(value), self.rect.size).convert_alpha()
                else:
                    print(f"Image path not found: {value}!")
                    self._img_dict[key] = None
        return None

    def toggle(self, state: bool = None) -> None:
        """
        Set switch state
        """
        self._state = not self._state if state is None else state
        return None

    def update(self, time_delta: float) -> None:
        """
        Update switch, handle timing and mouse collision
        """
        return super().update(time_delta)  # This method does nothing, Switch does not update

    def process_event(self, event: pygame.event.Event) -> bool:
        """
        Process switch interaction
        """
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == pygame.BUTTON_LEFT:
            if self.rect.collidepoint(event.pos):
                self.toggle()
                return True
        return False

    def draw(self, surface: pygame.Surface) -> None:
        """
        Draw switch on given surface
        """
        image = self._img_dict[self._state]
        if image is not None:
            surface.blit(image, (self.x, self.y))
        return None
