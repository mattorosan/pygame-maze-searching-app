import elements

FPS = 30

WINDOW_SIZE = (1200, 650)

GAME_POSITION = (50, 50)
GAME_SIZE = (800, 550)

DEFAULT_OUTPUT_FILE = "output/output.txt"

BUTTON_THEME = {
	"idle_bg": "#30312F", "hovered_bg": "#454442", "pressed_bg": "#41403E",
	"idle_fg": "#adadad", "hovered_fg": "#fefefe", "disabled_fg": "#6a6a6a",
	"txt_font": "consolas", "txt_size": 22, "txt_bold": True, "txt_align": (elements.CENTER_ALIGN, elements.CENTER_ALIGN),
	"img_scale": (25, 25), "img_align": (elements.LEFT_ALIGN, elements.CENTER_ALIGN), "img_pad": (15, 0),
	"border_radius": (5, 5, 5, 5), "border_width": 1, "hovered_border": "#efefef"
}
"""
	"idle_bg": "#30312F", "hovered_bg": "#658720", "pressed_bg": "#86AF3F",
	"idle_fg": "#adadad", "hovered_fg": "#fefefe", "disabled_fg": "#6a6a6a",
	"txt_font": "consolas", "txt_size": 22, "txt_bold": True, "txt_align": (elements.CENTER_ALIGN, elements.CENTER_ALIGN),"""
BUTTON_THEME_2 = {
	"img_scale": (160, 80), "img_align": (elements.CENTER_ALIGN, elements.CENTER_ALIGN),
}

ANIMATION_SPEED_OPTIONS = [
	"Slow", "Medium", "Fast"
]

ALGORITHM_OPTIONS = [
	"Depth First Search", "Breadth First Search", "Uniform Cost Search", "A Star Search"
]

DROPDOWN_THEME = {
	"idle_bg":  "#3C3A38", "idle_fg": "#DEDEDE",
	"txt_font": "", "txt_size": 27, "txt_bold": False,
	"hovered_border": "#C0C2C5", "border_width": 1, "border_radius": (3, 3, 3, 3),
	"main_txt_pad": 12,
	"option_txt_font": "roboto", "option_txt_size": 18, "option_txt_align": (elements.LEFT_ALIGN, elements.CENTER_ALIGN), "option_txt_pad": (20, 0),
	"idle_option_bg": "#FFFFFF", "selected_option_bg": "#1E90FF",
	"idle_option_fg": "#222222", "selected_option_fg": "#FFFFFF"
}