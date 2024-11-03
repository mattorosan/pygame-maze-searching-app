import itertools
import pygame
import pygame_menu
from enum import Enum
from typing import Any, Optional, Union

from .element import Element
from .button import PushButton
from .constants import Tuple2Int, \
    LEFT_ALIGN, CENTER_ALIGN, AUTO_VALUE


class DropdownEvent(Enum):
    OPEN_SELECTION_BOX = 0
    CLOSE_SELECTION_BOX = 1
    SELECT_NEW_OPTION = 2
    SELECT_OLD_OPTION = 3


class Dropdown(Element):
    """
    Dropdown class provides dropdown selection widget

    :param position: Dropdown main button position
    :param size: Dropdown main button square_dimensions
    :param widget_id: Widget id
    :param options: List of options
    :param cycle_options: Whether to cycle option order when using arrow keys
    """

    main_button_keyword_arguments = [
        "button_theme",
        "idle_bg", "hovered_bg", "pressed_bg", "disabled_bg",
        "idle_fg", "hovered_fg", "pressed_fg", "disabled_fg",
        "txt_font", "txt_size", "txt_bold", "txt_italic",
        "idle_border", "hovered_border", "pressed_border", "disabled_border", "border_width", "border_radius",
    ]
    keyword_arguments = [
        "theme",
        "options_display", "default_option", "option_size", "titles",
        "idle_option_bg", "selected_option_bg", "title_bg",
        "idle_option_fg", "selected_option_fg", "title_fg",
        "main_txt_pad",
        "option_txt_font", "option_txt_size", "idle_option_txt_bold", "selected_option_txt_italic", "option_txt_align", "option_txt_pad",
        "default_option_txt_align", "default_option_txt_pad",
        "title_txt_font", "title_txt_size", "title_txt_bold", "title_txt_italic", "title_txt_align", "title_txt_pad",
        "down_arrow_img",
        "selection_border", "selection_border_width",
        "slider_pad", "idle_slider_color", "hovered_slider_color", "page_control_color", "page_control_thick"
    ] + main_button_keyword_arguments

    event = DropdownEvent

    def __init__(self,
                 position: Tuple2Int,
                 size: Tuple2Int,
                 widget_id: str,
                 options: Union[list, tuple],
                 cycle_options: bool = False,
                 **kwargs):
        self._x, self._y = position
        self._width, self._height = size
        self._options = options

        self.event = None
        self.widget_id = widget_id
        self.cycle_options = cycle_options

        self._main_button = None
        self._is_active = False

        self._option_rects = []
        self._option_positions = []
        self._option_text_positions = []

        self._title_texts = []
        self._title_indexes = []
        self._title_rects = []
        self._title_positions = []
        self._title_text_positions = []

        self._option_size = ()
        self._selection_position = (self._x, self._y + self._height)
        self._selection_origin = [0, 0]
        self._selection_size = ()
        self._selection_rect = None
        self._selection_surface = None
        self._background_rect = None

        self._scroll_bar = None

        self._idle_option_bg = None
        self._selected_option_bg = None
        self._title_bg = None
        self._idle_option_fg = None
        self._selected_option_fg = None
        self._title_fg = None
        self._selection_border_color = None
        self._selection_border_width = 0

        self._title_font = None
        self._idle_option_font = None
        self._selected_option_font = None

        self._down_arrow_img = None
        self._down_arrow_position = ()

        self._options_display = 0
        self._default_option_index = -1
        self._hover_option = 0
        self._selected_option_index = 0
        self._selected_box_index = 0

        self._is_waiting_mouse_release = False
        self._is_repeating_key = False
        self._key_holding = None
        self._key_repeat_time = 0.0
        self._key_repeat_limit = 0.4
        self._key_repeat_interval = 0.025

        self._load_theme(kwargs)

    @property
    def x(self) -> int:
        return self._x

    @property
    def y(self) -> int:
        return self._y

    @property
    def selected_option_index(self) -> int:
        return self._selected_option_index

    @property
    def default_option_index(self) -> int:
        return self._default_option_index

    @property
    def selected_option(self) -> Any:
        return self._options[self._selected_option_index]

    @property
    def is_active(self) -> bool:
        return self._is_active

    def _load_theme(self, kwargs: dict) -> None:
        """
        Load dropdown appearance theme
        """
        super().validate_theme(kwargs, Dropdown.keyword_arguments)
        # Down arrow image
        main_text_pad = kwargs.get("main_text_pad", 12)
        down_arrow_img = kwargs.get("down_arrow_img", "elements/assets/dropdown_default/down_arrow.png")
        if down_arrow_img is not None:
            img_width = img_height = self._height * 0.32
            self._down_arrow_img = pygame.transform.smoothscale(pygame.image.load(down_arrow_img), (img_width, img_height)).convert_alpha()
            self._down_arrow_position = (self._x + self._width - img_width - main_text_pad, self._y + (self._height - img_height) // 2)
        # Main button
        main_button_theme = {}
        for key in Dropdown.main_button_keyword_arguments:
            try:
                arg = kwargs[key]
            except KeyError:
                continue
            else:
                main_button_theme[key] = arg
        self._main_button = PushButton(
            position=(self._x, self._y), size=(self._width, self._height), button_id=f"{self.widget_id}_main_button",
            text=self._options[self._selected_option_index], is_instant=True, is_latching=True,
            txt_align=(LEFT_ALIGN, CENTER_ALIGN), txt_pad=(main_text_pad, 0),
            theme=main_button_theme)
        self._main_button.text_size_limit = (
            self._main_button.text_size_limit[0] - main_text_pad - self._down_arrow_img.get_width(),
            self._main_button.text_size_limit[1])
        # Color themes
        self._idle_option_bg = kwargs.get("idle_option_bg")
        self._selected_option_bg = kwargs.get("selected_option_bg", self._idle_option_bg)
        self._title_bg = kwargs.get("title_bg", self._idle_option_bg)
        self._idle_option_fg = kwargs.get("idle_option_fg")
        self._selected_option_fg = kwargs.get("selected_option_fg", self._idle_option_fg)
        self._title_fg = kwargs.get("title_fg", self._idle_option_fg)
        self._selection_border_color = kwargs.get("selection_border")
        self._selection_border_width = kwargs.get("selection_border_width", 1)
        # Options
        self._default_option_index = kwargs.get("default_option", -1)
        self._options_display = kwargs.get("options_display", len(self._options))
        option_width, option_height = kwargs.get("option_size", (AUTO_VALUE, AUTO_VALUE))
        self._option_size = (self._width if option_width == AUTO_VALUE else option_width,
                             int(self._height * 0.75) if option_height == AUTO_VALUE else option_height)
        self._selection_size = (self._option_size[0], self._options_display * self._option_size[1])
        # Text labels
        option_text_font = kwargs.get("option_txt_font", "roboto")
        text_size = kwargs.get("option_txt_size", int(self._option_size[1] // 1.5))
        bold_idle_option = kwargs.get("idle_option_txt_bold", False)
        italic_selected_option = kwargs.get("selected_option_txt_italic", False)
        self._idle_option_font = pygame.font.SysFont(option_text_font, text_size, bold=bold_idle_option)
        self._selected_option_font = pygame.font.SysFont(option_text_font, text_size, bold=True, italic=italic_selected_option)

        titles = kwargs.get("titles", [])
        if titles:
            for title_text, title_index in titles:
                self._title_texts.append(title_text)
                self._title_indexes.append(title_index)
            title_text_font = kwargs.get("title_txt_font", "arial")
            bold_title = kwargs.get("title_txt_bold", True)
            italic_title = kwargs.get("title_txt_italic", True)
            self._title_font = pygame.font.SysFont(title_text_font, text_size, bold=bold_title, italic=italic_title)
        # Scroll bar
        slider_pad = kwargs.get("slider_pad", 2)
        idle_slider_color = kwargs.get("idle_slider_color", "#7C7C7C")
        hovered_slider_color = kwargs.get("hovered_slider_color", "#8C8C8C")
        page_control_color = kwargs.get("page_control_color", "#FFFFFF")
        page_control_thick = kwargs.get("page_control_thick", 20)
        if self._options_display < len(self._options) + len(titles):
            self._scroll_bar = pygame_menu.widgets.ScrollBar(
                length=self._selection_size[1], values_range=[0, (len(self._options) + len(titles)) * self._option_size[1] - self._selection_size[1]],
                orientation=pygame_menu.locals.ORIENTATION_VERTICAL,
                slider_pad=slider_pad, slider_color=idle_slider_color, slider_hover_color=hovered_slider_color,
                page_ctrl_color=page_control_color, page_ctrl_thick=page_control_thick)
            self._scroll_bar.set_position(self._x + self._selection_size[0] - page_control_thick - 1, self._y + self._height)
            self._option_size = (self._option_size[0] - page_control_thick, self._option_size[1])
        self._selection_rect = pygame.Rect((self._x, self._y + self._height), (self._option_size[0], self._selection_size[1]))
        self._background_rect = pygame.Rect((self._x, self._y + self._height), self._selection_size)
        self._selection_surface = pygame.Surface((self._option_size[0], (len(self._options) + len(titles)) * self._option_size[1]))
        # Fonts and text positions
        option_text_align = kwargs.get("option_txt_align", (LEFT_ALIGN, CENTER_ALIGN))
        option_text_pad = kwargs.get("option_txt_pad", (5, 0))
        title_text_align = kwargs.get("title_txt_align", option_text_align)
        title_text_pad = kwargs.get("title_txt_pad", option_text_pad)
        default_option_text_align = kwargs.get("default_option_align", title_text_align)
        default_option_text_pad = kwargs.get("default_option_pad", title_text_pad)

        rect_index = option_count = title_count = 0
        title_index = self._title_indexes[title_count] if title_count < len(self._title_indexes) else -1
        while rect_index < len(self._options) + len(titles):
            rect_y = self._selection_position[1] + rect_index * self._option_size[1]
            rect = pygame.Rect((self._x, rect_y), self._option_size)
            is_title = rect_index == title_index
            self._title_rects.append(rect) if is_title else self._option_rects.append(rect)
            self._title_positions.append(rect_y) if is_title else self._option_positions.append(rect_y)

            text_size = self._title_font.size(self._title_texts[title_count - 1]) if is_title else \
                self._idle_option_font.size(self._options[option_count])
            text_align = title_text_align if is_title else \
                default_option_text_align if option_count == self._default_option_index else option_text_align
            text_pad = title_text_pad if is_title else \
                default_option_text_pad if option_count == self._default_option_index else option_text_pad
            text_pos = [text_pad[0], rect_index * self._option_size[1] + text_pad[1]]

            for j in range(len(text_pos)):
                text_pos[j] += (self._option_size[j] - text_size[j]) // 2 if text_align[j] == CENTER_ALIGN else \
                    (self._option_size[j] - text_size[j]) if text_align[j].value > CENTER_ALIGN.value else 0
            self._title_text_positions.append(text_pos) if is_title else self._option_text_positions.append(text_pos)

            rect_index += 1
            if is_title:
                title_count += 1
                title_index = self._title_indexes[title_count] if title_count < len(self._title_indexes) else -1
            else:
                option_count += 1
        return None

    def set_default_option(self, option: int = None) -> None:
        """
        Set dropdown default option
        """
        if option is not None and 0 <= option < len(self._options):
            self._default_option_index = option
        else:
            self._default_option_index = None
        return None

    def _adjust_scroll_bar(self, is_centered: bool) -> None:
        """
        Adjust dropdown scroll bar position so that active option is in the middle (if possible)

        :param is_centered: If 'True', selected option is positioned in the middle of the selection box. Otherwise, it is adjusted to be on top or
        bottom, based on the option index.
        :return: None
        """
        if self._scroll_bar is None:
            return None

        old_scroll_bar_value = self._selection_origin[1]
        if is_centered:
            lower_bound = self._selected_box_index - (self._options_display - 1) // 2
            new_scroll_bar_value = min(max(lower_bound * self._option_size[1], 0), self._selection_surface.get_height() - self._selection_size[1])
        else:
            position_difference = (self._options_display - 1) * self._option_size[1]
            hover_option_position = self._option_positions[self._hover_option] - self._selection_position[1]
            if hover_option_position < old_scroll_bar_value:
                new_scroll_bar_value = hover_option_position
            elif hover_option_position > old_scroll_bar_value + position_difference:
                new_scroll_bar_value = hover_option_position - position_difference
            else:
                new_scroll_bar_value = old_scroll_bar_value

        if new_scroll_bar_value != old_scroll_bar_value:
            self._scroll_bar.set_value(new_scroll_bar_value)
            for rect, position in zip(itertools.chain(self._option_rects, self._title_rects),
                                      itertools.chain(self._option_positions, self._title_positions)):
                rect.y = position - new_scroll_bar_value
            self._selection_origin[1] = new_scroll_bar_value
        return

    def select(self, option: Optional[Union[int, str]] = None) -> bool:
        """
        Select the option at the given index

        :param option: Option index/text
        :return: whether a new option is selected
        """
        if isinstance(option, str):
            try:
                option_index = self._options.index(option)
            except ValueError:
                option_index = 0
                print("Invalid option!")
        elif isinstance(option, int):
            if option == self._selected_option_index or not 0 <= option < len(self._options):
                return False
            option_index = option
        else:
            option_index = self._default_option_index
        return self._select_unchecked(option_index)

    def _select_unchecked(self, option_index: Optional[int]) -> bool:
        if option_index is None:
            option_index = 0

        if option_index == self._selected_option_index:
            self.event = Dropdown.event.SELECT_OLD_OPTION
            self.close()
            return False

        self._hover_option = self._selected_box_index = self._selected_option_index = option_index
        for title_index in self._title_indexes:
            if option_index < title_index:
                break
            self._selected_box_index += 1
        self._main_button.text = self._options[self._selected_option_index]
        self.close()
        self.event = Dropdown.event.SELECT_NEW_OPTION
        return True

    def open(self) -> None:
        """
        Open the option selection panel
        """
        if not self._is_active:
            self._is_active = True
            self._main_button.toggle(state=True)
            self._hover_option = self._selected_option_index
            self.event = Dropdown.event.OPEN_SELECTION_BOX
            self._adjust_scroll_bar(is_centered=True)
        return None

    def close(self) -> None:
        """
        Close the option selection panel
        """
        if self._is_active:
            self._is_active = False
            self._main_button.toggle(state=False)
            self._is_waiting_mouse_release = False
            if self._key_holding is not None:
                self._key_holding = None
                self._key_repeat_time = 0.0
            self.event = Dropdown.event.CLOSE_SELECTION_BOX
        return None

    def update(self, time_delta) -> None:
        """
        Update dropdown widget, handle the key pressed timing
        """
        if self.is_active:
            if self._key_holding is not None:
                if self._key_repeat_time < self._key_repeat_limit:
                    self._key_repeat_time += time_delta
                else:
                    self._process_key_down_event(self._key_holding)
                    self._key_repeat_time = self._key_repeat_limit - self._key_repeat_interval
        return self._main_button.update(time_delta)

    def process_event(self, event: pygame.event.Event) -> bool:
        """
        Process dropdown interaction
        """
        consumed_event = False
        self.event = None
        if self._process_keyboard_event(event):
            consumed_event = True
        elif self._process_scroll_bar_event(event):
            consumed_event = True
        elif self._process_mouse_event(event):
            consumed_event = True
        return consumed_event

    def _process_mouse_event(self, event: pygame.event.Event) -> bool:
        """
        Process dropdown interaction with mouse
        """
        consumed_event = False
        if self._main_button.process_event(event):
            if self._main_button.is_invoked:
                self.open() if self._main_button.state else self.close()
                return True
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == pygame.BUTTON_LEFT:
            if self.is_active:
                if self._selection_rect.collidepoint(event.pos):
                    self._is_waiting_mouse_release = True
                    consumed_event = True
                elif not self._background_rect.collidepoint(event.pos):
                    self.close()
                    consumed_event = True
        elif event.type == pygame.MOUSEBUTTONUP and event.button == pygame.BUTTON_LEFT:
            if self.is_active:
                if self._is_waiting_mouse_release:
                    if self._selection_rect.collidepoint(event.pos):
                        for rect in self._title_rects:
                            if rect.collidepoint(event.pos):
                                self._is_waiting_mouse_release = False
                                return False
                        self._select_unchecked(self._hover_option)
                        consumed_event = True
                    self._is_waiting_mouse_release = False
        elif event.type == pygame.MOUSEMOTION:
            if self._selection_rect.collidepoint(event.pos):
                for i, rect in enumerate(self._option_rects):
                    if rect.collidepoint(pygame.mouse.get_pos()):
                        self._hover_option = i
                        break
        return consumed_event
    
    def _process_keyboard_event(self, event: pygame.event.Event) -> bool:
        """
        Process dropdown interaction with keyboard
        """
        if not self.is_active:
            return False

        consumed_event = False
        if event.type == pygame.KEYDOWN:
            if event.key != self._key_holding:
                self._key_repeat_time = 0.0
                self._key_holding = event.key
            if self._process_key_down_event(event.key):
                consumed_event = True
        elif event.type == pygame.KEYUP:
            self._key_holding = None
            consumed_event = True
        return consumed_event
        
    def _process_key_down_event(self, key: pygame.key) -> bool:
        """
        Process single keyboard input
        """
        consumed_event = True
        match key:
            case pygame.K_UP:  # Highlight the option above
                if self._hover_option > 0:
                    self._hover_option -= 1
                elif self.cycle_options:
                    self._hover_option = len(self._options) - 1
                else:
                    return False
            case pygame.K_DOWN:  # Highlight the option below
                if self._hover_option < len(self._options) - 1:
                    self._hover_option += 1
                elif self.cycle_options:
                    self._hover_option = 0
                else:
                    return False
            case pygame.K_PAGEUP:  # Highlight the top option in the dropdown
                if self._hover_option == 0:
                    return False
                self._hover_option = max(self._hover_option - self._options_display + 1, 0)
            case pygame.K_PAGEDOWN:  # Highlight the bottom option in the dropdown
                if self._hover_option == len(self._options) - 1:
                    return False
                self._hover_option = min(self._hover_option + self._options_display - 1, len(self._options) - 1)
            case pygame.K_HOME:  # Highlight the first option in the selection box
                if self._hover_option == 0:
                    return False
                self._hover_option = 0
            case pygame.K_END:  # Highlight the last option in the selection box
                if self._hover_option == len(self._options) - 1:
                    return False
                self._hover_option = len(self._options) - 1
            case pygame.K_RETURN:  # Select the highlighted option
                if self._hover_option != self.selected_option_index:
                    self._select_unchecked(self._hover_option)
                    return True
            case pygame.K_ESCAPE:  # Close the dropdown
                self.close()
                return True
            case _:
                return False
        self._adjust_scroll_bar(is_centered=False)
        return consumed_event
    
    def _process_scroll_bar_event(self, event: pygame.event.Event) -> bool:
        """
        Process scroll bar interaction
        """
        consumed_event = False
        if self.is_active:
            if self._scroll_bar is not None:
                consumed_event = self._scroll_bar.update([event])
                old_scroll_bar_value = self._selection_origin[1]
                new_scroll_bar_value = self._scroll_bar.get_value()
                if new_scroll_bar_value != old_scroll_bar_value:
                    for rect, position in zip(itertools.chain(self._option_rects, self._title_rects),
                                              itertools.chain(self._option_positions, self._title_positions)):
                        rect.y = position - new_scroll_bar_value
                    self._selection_origin[1] = new_scroll_bar_value
        return consumed_event

    def draw(self, surface: pygame.Surface) -> None:
        """
        Draw dropdown on given surface
        """
        self._main_button.draw(surface)
        surface.blit(self._down_arrow_img, self._down_arrow_position)
        # Option selection box
        if self.is_active:
            if self._idle_option_bg is not None:
                self._selection_surface.fill(self._idle_option_bg)
            for i, option_rect in enumerate(self._option_rects):
                if i == self._hover_option:
                    if self._selected_option_bg is not None:
                        rect = ((0, self._option_positions[i] - self._selection_position[1]), option_rect.size)
                        pygame.draw.rect(self._selection_surface, self._selected_option_bg, rect)
                    text_color = self._selected_option_fg
                else:
                    text_color = self._idle_option_fg
                if text_color is not None:
                    font = self._selected_option_font if i == self._selected_option_index else self._idle_option_font
                    label = font.render(self._options[i], True, text_color)
                    self._selection_surface.blit(label, self._option_text_positions[i])
            for i, title_rect in enumerate(self._title_rects):
                if self._title_bg is not None:
                    rect = ((0, self._title_positions[i] - self._selection_position[1]), title_rect.size)
                    pygame.draw.rect(self._selection_surface, self._title_bg, rect)
                if self._title_fg is not None:
                    label = self._title_font.render(self._title_texts[i], True, self._title_fg)
                    self._selection_surface.blit(label, self._title_text_positions[i])

            surface.blit(self._selection_surface, self._selection_position, (self._selection_origin, self._selection_size))
            if self._scroll_bar is not None:
                self._scroll_bar.draw(surface)
            if self._selection_border_color is not None:
                pygame.draw.rect(surface, self._selection_border_color, self._background_rect, width=self._selection_border_width)
        return None
