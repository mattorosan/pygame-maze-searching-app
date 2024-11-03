import os
import pygame
from abc import abstractmethod
from enum import Enum
from typing import Any, Callable, Optional, Union

from .element import Element
from .constants import Tuple2Int, Tuple4Int, \
    CENTER_ALIGN, AUTO_VALUE


class _ButtonMode(Enum):
    """
    Class for representing button modes
    """
    IDLE = "idle"
    HOVERED = "hovered"
    PENDING = "pending"
    PRESSED = "pressed"
    DISABLED = "disabled"


BUTTON_IDLE = _ButtonMode.IDLE
BUTTON_HOVERED = _ButtonMode.HOVERED
BUTTON_PENDING = _ButtonMode.PENDING
BUTTON_PRESSED = _ButtonMode.PRESSED
BUTTON_DISABLED = _ButtonMode.DISABLED


class Button(Element):
    """
    Button class provides abstract base class button widget

    :param position: Button position
    :param size: Button square_dimensions
    :param button_id: Button id
    :param text: Button text
    :param is_disabled: Whether button is disabled
    :param callback: Button invoke action
    """

    # Keyword arguments
    keyword_arguments = [
        "theme",
        "idle_bg", "hovered_bg", "pending_bg", "pressed_bg", "disabled_bg",
        "idle_fg", "hovered_fg", "pending_fg", "pressed_fg", "disabled_fg",
        "txt_font", "txt_size", "txt_bold", "txt_italic", "txt_align", "txt_pad", "txt_limit",
        "idle_img", "hovered_img", "pending_img", "pressed_img", "disabled_img",
        "img_scale", "img_align", "img_pad",
        "idle_border", "hovered_border", "pending_border", "pressed_border", "disabled_border",
        "border_width", "border_radius",
    ]

    def __init__(self,
                 position: Tuple2Int,
                 size: Tuple2Int,
                 button_id: str,
                 text: str = "",
                 is_disabled: bool = False,
                 callback: Callable = None,
                 **kwargs):
        self._x, self._y = position
        self.width, self.height = size

        self.rect = pygame.Rect(position, size)
        self.button_id = button_id
        self.text = text

        self._callback = callback

        self._bg_dict = {}
        self._fg_dict = {}

        self._font = None
        self._text_align = (CENTER_ALIGN, CENTER_ALIGN)
        self._text_pad = (0, 0)
        self._text_pos = [self._x, self._y]
        self.text_size_limit = ()

        self._img_dict = {}
        self._img_scale = size
        self._img_align = (CENTER_ALIGN, CENTER_ALIGN)
        self._img_pad = (0, 0)
        self._img_pos = [self._x, self._y]

        self._border_color_dict = {}
        self._border_radius = ()
        self._border_width = None

        self._mode = BUTTON_IDLE if not is_disabled else BUTTON_DISABLED
        self._is_invoked = False
        self._load_theme(kwargs)

    @property
    def x(self) -> int:
        return self._x

    @property
    def y(self) -> int:
        return self._y

    @property
    def position(self) -> Tuple2Int:
        return self._x, self._y

    @property
    def size(self) -> Tuple2Int:
        return self.width, self.height

    @property
    def is_idle(self):
        return self._mode == BUTTON_IDLE

    @property
    def is_hovered(self) -> bool:
        return self._mode == BUTTON_HOVERED

    @property
    def is_pending(self) -> bool:
        return self._mode == BUTTON_PENDING

    @property
    def is_pressed(self) -> bool:
        return self._mode == BUTTON_PRESSED

    @property
    def is_disabled(self) -> bool:
        return self._mode == BUTTON_DISABLED

    @property
    def is_invoked(self) -> bool:
        return self._is_invoked

    def _load_theme(self, kwargs: dict[str]) -> None:
        """
        Load button appearance theme
        """
        super().validate_theme(kwargs, Button.keyword_arguments)
        # Backgrounds
        self.set_backgrounds(kwargs)
        # Text labels
        if self.text:
            text_align = kwargs.get("txt_align", (CENTER_ALIGN, CENTER_ALIGN))
            text_pad = kwargs.get("txt_pad", (0, 0))
            self.set_label_font(kwargs)
            self.set_label_foregrounds(kwargs)
            self.set_labels_position(alignments=text_align, paddings=text_pad)
            self.text_size_limit = kwargs.get("txt_limit", (self.width - self._text_pad[0], self.height - self._text_pad[1]))
        # Images
        image_scale = kwargs.get("img_scale", self.size)
        image_align = kwargs.get("img_align", (CENTER_ALIGN, CENTER_ALIGN))
        image_pad = kwargs.get("img_pad", (0, 0))
        self.set_images(image_dict=kwargs, size=image_scale)
        self.set_images_position(alignments=image_align, paddings=image_pad)
        # Borders
        border_width = kwargs.get("border_width", 1)
        border_radius = kwargs.get("border_radius", (0, 0, 0, 0))
        self.set_borders(border_dict=kwargs, border_width=border_width, border_radius=border_radius)
        return None

    def set_position(self, x: int = None, y: int = None) -> None:
        """
        Set button position
        """
        if x is not None:
            x_diff = x - self._x
            self._img_pos[0] += x_diff
            self._text_pos[0] += x_diff
            self._x = x
        if y is not None:
            y_diff = y - self._y
            self._img_pos[1] += y_diff
            self._text_pos[1] += y_diff
            self._y = y
        return None

    def set_backgrounds(self, bg_dict: dict[str]) -> None:
        """
        Set background colors
        """
        idle_bg = bg_dict.get("idle_bg")
        hovered_bg = bg_dict.get("hovered_bg", idle_bg)
        pending_bg = bg_dict.get("pending_bg", hovered_bg)
        pressed_bg = bg_dict.get("pressed_bg", hovered_bg)
        disabled_bg = bg_dict.get("disabled_bg", idle_bg)
        self._bg_dict.update({
            BUTTON_IDLE:     idle_bg,
            BUTTON_HOVERED:  hovered_bg,
            BUTTON_PENDING:  pending_bg,
            BUTTON_PRESSED:  pressed_bg,
            BUTTON_DISABLED: disabled_bg,
        })
        return None

    def set_label_font(self, font_dict: dict[str]) -> None:
        """
        Set label font
        """
        font = font_dict.get("txt_font", "consolas")
        size = font_dict.get("txt_size", self.height // 2)
        bold = font_dict.get("txt_bold", False)
        italic = font_dict.get("txt_italic", False)
        self._font = pygame.font.SysFont(font, size, bold=bold, italic=italic)
        return None

    def set_label_foregrounds(self, fg_dict: dict[str]) -> None:
        """
        Set label foreground colors
        """
        idle_fg = fg_dict.get("idle_fg")
        hovered_fg = fg_dict.get("hovered_fg", idle_fg)
        pending_fg = fg_dict.get("pending_fg", hovered_fg)
        pressed_fg = fg_dict.get("pressed_fg", hovered_fg)
        disabled_fg = fg_dict.get("disabled_fg", idle_fg)
        self._fg_dict.update({
            BUTTON_IDLE:     idle_fg,
            BUTTON_HOVERED:  hovered_fg,
            BUTTON_PENDING:  pending_fg,
            BUTTON_PRESSED:  pressed_fg,
            BUTTON_DISABLED: disabled_fg,
        })
        return None

    def set_labels_position(self, alignments: tuple[Enum, Enum] = (CENTER_ALIGN, CENTER_ALIGN),
                            paddings: tuple[Union[Enum, int], Union[Enum, int]] = (0, 0)):
        """
        Set label position
        """
        text_size = self._font.size(self.text)
        self._text_align = alignments
        self._text_pad = paddings
        self._text_pos = [self._x + paddings[0], self._y + paddings[1]]
        for i in range(len(self._text_pos)):
            self._text_pos[i] += (self.size[i] - text_size[i]) // 2 if alignments[i] == CENTER_ALIGN else \
                (self.size[i] - text_size[i]) if alignments[i].value > CENTER_ALIGN.value else 0
        return None

    def set_images(self, image_dict: dict[str] = None, size: tuple[Union[Enum, int], Union[Enum, int]] = (AUTO_VALUE, AUTO_VALUE)) -> None:
        """
        Set images and image square_dimensions
        """
        idle_img = image_dict.get("idle_img")
        hovered_img = image_dict.get("hovered_img", idle_img)
        pending_img = image_dict.get("pending_img", hovered_img)
        pressed_img = image_dict.get("pressed_img", hovered_img)
        disabled_img = image_dict.get("disabled_img", idle_img)
        self._img_dict.update({
            BUTTON_IDLE:     idle_img,
            BUTTON_HOVERED:  hovered_img,
            BUTTON_PENDING:  pending_img,
            BUTTON_PRESSED:  pressed_img,
            BUTTON_DISABLED: disabled_img,
        })
        for key, value in self._img_dict.items():
            if isinstance(value, (bytes, str)):
                if os.path.exists(value):
                    self._img_dict[key] = pygame.image.load(value).convert_alpha()
                else:
                    print(f"Image path not found: {value}!")
                    self._img_dict[key] = None
            if isinstance(self._img_dict[key], pygame.Surface):
                self._img_scale = self._img_dict[key].get_size()

        if size != (AUTO_VALUE, AUTO_VALUE):
            image_w, image_h = size
            if image_h != image_w == AUTO_VALUE:
                image_w = int(image_h * self._img_scale[0] / self._img_scale[1])
            if image_w != image_h == AUTO_VALUE:
                image_h = int(image_w * self._img_scale[1] / self._img_scale[0])
            self._img_scale = (image_w, image_h)

            for key, value in self._img_dict.items():
                if value is None:
                    continue
                self._img_dict[key] = pygame.transform.smoothscale(value, self._img_scale).convert_alpha()
        return None

    def set_images_position(self, alignments: tuple[Enum, Enum] = (CENTER_ALIGN, CENTER_ALIGN),
                            paddings: tuple[Union[Enum, int], Union[Enum, int]] = (0, 0)):
        """
        Set image position
        """
        self._img_align = alignments
        self._img_pad = paddings
        self._img_pos = [self._x + paddings[0], self._y + paddings[1]]
        for i in range(len(self._img_pos)):
            self._img_pos[i] += (self.size[i] - self._img_scale[i]) // 2 if alignments[i] == CENTER_ALIGN else \
                (self.size[i] - self._img_scale[i]) if alignments[i].value > CENTER_ALIGN.value else 0
        return None

    def set_borders(self, border_dict: dict[str], border_width: int = 1, border_radius: Tuple4Int = (0, 0, 0, 0)) -> None:
        """
        Set borders
        """
        idle_border = border_dict.get("idle_border")
        hovered_border = border_dict.get("hovered_border", idle_border)
        pending_border = border_dict.get("pending_border", hovered_border)
        pressed_border = border_dict.get("pressed_border", hovered_border)
        disabled_border = border_dict.get("disabled_border", idle_border)
        self._border_color_dict.update({
            BUTTON_IDLE:     idle_border,
            BUTTON_HOVERED:  hovered_border,
            BUTTON_PENDING:  pending_border,
            BUTTON_PRESSED:  pressed_border,
            BUTTON_DISABLED: disabled_border,
        })
        self._border_width = border_width
        self._border_radius = border_radius
        return None

    def set_mode(self, is_enabled: bool = None) -> None:
        """
        Set button interaction permission
        """
        if is_enabled is None:
            self._mode = BUTTON_IDLE if not self.is_disabled else BUTTON_DISABLED
        else:
            self._mode = BUTTON_IDLE if is_enabled else BUTTON_DISABLED
        return None

    def invoke(self) -> Optional[Any]:
        """
        Invoke the callback whenever button is interacted
        """
        self._is_invoked = True
        if self._callback is not None:
            return self._callback()
        return None

    @abstractmethod
    def update(self, time_delta: float) -> None:
        """
        Update button, handle timing and mouse collision
        """
        if self.is_disabled:
            return None

        if self.rect.collidepoint(pygame.mouse.get_pos()):
            if self.is_idle:
                self._mode = BUTTON_HOVERED
        else:
            if self.is_hovered:
                self._mode = BUTTON_IDLE
        return None

    def draw(self, surface: pygame.Surface) -> None:
        """
        Draw button
        """
        # Background
        background = self._bg_dict.get(self._mode)
        if background is not None:
            pygame.draw.rect(surface, background, rect=(self.position, self.size),
                             border_top_left_radius=self._border_radius[0], border_top_right_radius=self._border_radius[1],
                             border_bottom_right_radius=self._border_radius[2], border_bottom_left_radius=self._border_radius[3])
        # Image
        image = self._img_dict.get(self._mode)
        if image is not None:
            surface.blit(image, self._img_pos)
        # Text
        if self.text:
            foreground = self._fg_dict.get(self._mode)
            if foreground is not None:
                label = self._font.render(self.text, True, foreground)
                surface.blit(label, self._text_pos, ((0, 0), self.text_size_limit))
        # Border
        border_color = self._border_color_dict[self._mode]
        if border_color is not None:
            pygame.draw.rect(surface, border_color, rect=(self.position, self.size), width=self._border_width,
                             border_top_left_radius=self._border_radius[0], border_top_right_radius=self._border_radius[1],
                             border_bottom_right_radius=self._border_radius[2], border_bottom_left_radius=self._border_radius[3])
        return None


class PushButton(Button):
    """
    PushButton class provides classic button widget

    :param state: Button boolean state
    :param is_instant: Whether button invokes on the moment it is pushed or released, is False by default
    :param is_latching: Whether button stays in pressed state and requires a second push to release it, is False by default
    """
    
    def __init__(self,
                 position: Tuple2Int,
                 size: Tuple2Int,
                 button_id: str,
                 text: str = "",
                 callback: Callable = None,
                 state: bool = False,
                 is_instant: bool = False,
                 is_latching: bool = False,
                 **kwargs):
        super().__init__(position=position, size=size, button_id=button_id, text=text, callback=callback, **kwargs)

        self._state = state

        self.is_instant = is_instant
        self.is_latching = is_latching

    @property
    def state(self) -> bool:
        return self._state

    def toggle(self, state: bool = None) -> None:
        """
        Set button state
        """
        self._state = not self._state if state is None else state
        self._mode = BUTTON_PRESSED if self._state else BUTTON_IDLE
        return None

    def update(self, time_delta: float) -> None:
        """
        Update button, handle timing and mouse collision
        """
        return super().update(time_delta)

    def process_event(self, event: pygame.event.Event) -> bool:
        """
        Process button interaction
        """
        if self.is_disabled:
            return False

        consumed_event = False
        self._is_invoked = False
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == pygame.BUTTON_LEFT:
            if self.rect.collidepoint(event.pos):
                if self.is_instant:
                    self.invoke()
                    self._state = not self._state
                    self._mode = BUTTON_IDLE if (self.is_latching and not self._state) else BUTTON_PRESSED
                else:
                    self._mode = BUTTON_PENDING
                    return False
                consumed_event = True
        if event.type == pygame.MOUSEBUTTONUP and event.button == pygame.BUTTON_LEFT:
            if self.is_pending:
                if self.rect.collidepoint(event.pos):
                    self.invoke()
                    self._state = not self._state
                    consumed_event = True
            self._mode = BUTTON_PRESSED if (self.is_latching and self._state) else BUTTON_IDLE
        return consumed_event


class RepeatButton(Button):
    """
    RepeatButton class provides repeat button widget

    :param repeat_limit: Time between the first and second invokes
    :param repeat_interval: Time between every repeated invoke after the second one
    """

    def __init__(self,
                 position: Tuple2Int,
                 size: Tuple2Int,
                 button_id: str,
                 text: str = "",
                 callback: Callable = None,
                 repeat_limit: float = 0.5,
                 repeat_interval: float = 0.1,
                 **kwargs):
        super().__init__(position=position, size=size, button_id=button_id, text=text, callback=callback, **kwargs)

        self.repeat_limit = repeat_limit
        self.repeat_interval = repeat_interval
        self.repeat_time = 0.0

    def update(self, time_delta: float) -> bool:
        """
        Update button, handle timing and mouse collision
        """
        super().update(time_delta)
        if self.is_pressed:
            if self.repeat_time < self.repeat_limit:
                self.repeat_time += time_delta
            else:
                self.invoke()
                self.repeat_time = self.repeat_limit - self.repeat_interval
                return True
        return False

    def process_event(self, event: pygame.event.Event) -> bool:
        """
        Process button interaction
        """
        if self.is_disabled:
            return False

        consumed_event = False
        self._is_invoked = False
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == pygame.BUTTON_LEFT:
            if self.rect.collidepoint(event.pos):
                self.invoke()
                self.repeat_time = 0.0
                self._mode = BUTTON_PRESSED
                consumed_event = True
        if event.type == pygame.MOUSEBUTTONUP and event.button == pygame.BUTTON_LEFT:
            if self.is_pressed:
                self._mode = BUTTON_IDLE
        return consumed_event
