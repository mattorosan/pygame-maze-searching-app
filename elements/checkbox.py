import os
import pygame
from enum import Enum

from .element import Element
from .constants import Tuple2Int


class _CheckboxMode(Enum):
    """
    Class for representing checkbox modes
    """
    IDLE = "idle"
    HOVERED = "hovered"
    PRESSED = "pressed"
    DISABLED = "disabled"
    

CHECKBOX_IDLE = _CheckboxMode.IDLE
CHECKBOX_HOVERED = _CheckboxMode.HOVERED
CHECKBOX_PRESSED = _CheckboxMode.PRESSED
CHECKBOX_DISABLED = _CheckboxMode.DISABLED


class Checkbox(Element):
    """
    Checkbox class provides checkbox widget. In essence, the checkbox functions similarly to a push button, one can say that a checkbox is just a
    special variant (but lighter and less complex since the checkbox does not contain any text or images) of a button. Therefore, instead of using
    push button to represent a checkbox, it is better to create a whole Checkbox class to get the job done. It is a trade-off between more code and
    less redundancy

    :param position: Widget position
    :param size: Widget square_dimensions
    :param widget_id: Widget id
    :param state: Checkbox state
    """
    
    # Keyword arguments
    keyword_arguments = [
        "theme",
        "idle_img", "hovered_img", "pressed_img", "disabled_img",
        "idle_border", "hovered_border", "pressed_border", "disabled_border", "border_radius", "border_width"
    ]

    def __init__(self,
                 position: Tuple2Int,
                 size: Tuple2Int,
                 widget_id: str,
                 state: bool = False,
                 **kwargs):
        self.x, self.y = position
        self._width, self._height = size

        self.rect = pygame.Rect(position, size)
        self.widget_id = widget_id

        self._state = state

        self._img_dict = {}

        self._border_dict = {}
        self._border_radius = 0
        self._border_width = None

        self._mode = CHECKBOX_IDLE
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
    def is_idle(self):
        return self._mode == CHECKBOX_IDLE

    @property
    def is_hovered(self) -> bool:
        return self._mode == CHECKBOX_HOVERED

    @property
    def is_pressed(self) -> bool:
        return self._mode == CHECKBOX_PRESSED

    @property
    def is_disabled(self) -> bool:
        return self._mode == CHECKBOX_DISABLED

    @property
    def state(self) -> bool:
        return self._state

    def _load_theme(self, kwargs: dict[str]) -> None:
        """
        Load checkbox appearance theme
        """
        super().validate_theme(kwargs, Checkbox.keyword_arguments)
        # Images
        idle_img = kwargs.get("idle_img")
        if idle_img is None:
            idle_img = "elements/assets/checkbox_default/idle_checkbox.png"
            hovered_img = kwargs.get("hovered_img", "elements/assets/checkbox_default/hovered_checkbox.png")
            pressed_img = kwargs.get("pressed_img", "elements/assets/checkbox_default/pressed_checkbox.png")
        else:
            hovered_img = kwargs.get("hovered_img", idle_img)
            pressed_img = kwargs.get("pressed_img", idle_img)
        disabled_img = kwargs.get("disabled_img", idle_img)
        self._img_dict.update({
            CHECKBOX_IDLE:     idle_img,
            CHECKBOX_HOVERED:  hovered_img,
            CHECKBOX_PRESSED:  pressed_img,
            CHECKBOX_DISABLED: disabled_img,
        })
        for key, value in self._img_dict.items():
            if isinstance(value, (bytes, str)):
                if os.path.exists(value):
                    self._img_dict[key] = pygame.transform.smoothscale(pygame.image.load(value), self.rect.size).convert_alpha()
                else:
                    print(f"Image path not found: {value}!")
                    self._img_dict[key] = None
        # Borders
        idle_border = kwargs.get("idle_border")
        hovered_border = kwargs.get("hovered_border", idle_border)
        pressed_border = kwargs.get("pressed_border", idle_border)
        disabled_border = kwargs.get("disabled_border", idle_border)
        self._border_dict.update({
            CHECKBOX_IDLE:     idle_border,
            CHECKBOX_HOVERED:  hovered_border,
            CHECKBOX_PRESSED:  pressed_border,
            CHECKBOX_DISABLED: disabled_border,
        })
        self._border_radius = kwargs.get("border_radius", 0)
        self._border_width = kwargs.get("border_width", 1)
        return None

    def set_mode(self, is_enabled: bool = None) -> None:
        """
        Set checkbox interaction permission
        """
        if is_enabled is None:
            self._mode = CHECKBOX_IDLE if not self.is_disabled else CHECKBOX_DISABLED
        else:
            self._mode = CHECKBOX_IDLE if is_enabled else CHECKBOX_DISABLED
        return None

    def toggle(self, state: bool = None) -> None:
        """
        Set checkbox state
        """
        self._state = not self._state if state is None else state
        return None
    
    def update(self, time_delta: float) -> None:
        """
        Update checkbox, handle timing and mouse collision
        """
        if self.is_disabled:
            return None

        if self.rect.collidepoint(pygame.mouse.get_pos()):
            if self.is_idle:
                self._mode = CHECKBOX_HOVERED
        else:
            if self.is_hovered:
                self._mode = CHECKBOX_IDLE
        return None

    def process_event(self, event: pygame.event.Event) -> bool:
        """
        Process checkbox interaction
        """
        if self.is_disabled:
            return False

        consumed_event = False
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == pygame.BUTTON_LEFT:
            if self.rect.collidepoint(event.pos):
                self._mode = CHECKBOX_PRESSED
        if event.type == pygame.MOUSEBUTTONUP and event.button == pygame.BUTTON_LEFT:
            if self.is_pressed:
                if self.rect.collidepoint(event.pos):
                    self.toggle()
                    consumed_event = True
                self._mode = CHECKBOX_IDLE
        return consumed_event

    def draw(self, surface: pygame.Surface) -> None:
        """
        Draw checkbox on given surface
        """
        if self._state:
            # Image
            image = self._img_dict.get(self._mode)
            if image is not None:
                surface.blit(image, (self.x, self.y))
        else:
            # Border
            border_color = self._border_dict.get(self._mode)
            if border_color is not None:
                pygame.draw.rect(surface, border_color, rect=(self.position, self.size), width=self._border_width, border_radius=self._border_radius)
        return None
