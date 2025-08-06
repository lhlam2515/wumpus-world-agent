"""
Configuration file for the Wumpus World visualization UI.

This file contains all the configuration parameters for the UI components,
organized into logical sections:
1. Application-wide settings
2. Layout configurations
3. Component configurations
"""

# =============================================================================
# COLOR PALETTE
# =============================================================================
# Common colors used throughout the application
colors = {
    "primary_blue": (61, 169, 252),  # Cornflower blue for primary actions
    "dark_blue": (9, 64, 103),  # Steel blue for backgrounds and borders
    "light_blue": (216, 238, 254),  # Light blue for app background
    "subtle_blue": (2, 86, 151),
    "green": (144, 238, 144),  # Light green for safe cells
    "red": (255, 0, 0),
    "primary_red": (239, 69, 101),
    "yellow": (255, 215, 0),  # Gold for treasure
    "gray": (169, 169, 169),  # Dark gray for unknown cells
    "white": (255, 255, 255),  # White for visited cells
    "black": (0, 0, 0),  # Black for text and borders
    "light_gray": (200, 200, 200),  # Light gray for secondary buttons
    "disabled_gray": (180, 180, 180),  # Medium gray for disabled elements
    "disabled_blue": (180, 222, 254),  # Light blue, used for disabled primary
    "hover_blue": (120, 180, 255),  # Lighter blue for hover states
    "text_dark": (48, 48, 48),
}

# =============================================================================
# TYPOGRAPHY
# =============================================================================
fonts = {
    "medium": "Roboto-Medium",
    "regular": "Roboto-Regular",
    "sizes": {
        "large": 28,
        "medium": 24,
        "small": 20,
        "tiny": 18,
    },
}

# =============================================================================
# LAYOUT CONFIGURATION
# =============================================================================
# Main application screen
screen = {
    "size": (1400, 720),
    "bg_color": colors["light_blue"],
}

map_section = {
    "position": (340, 0),
    "button_size": (184, 56),
    "button_spacing": 25,
    "board_spacing": 25,
    "animation_delay": 1000,
    "text_size": fonts["sizes"]["medium"],
    "text_color": colors["red"],
    "text_font": fonts["regular"],
    "title_size": fonts["sizes"]["large"],
    "title_color": colors["dark_blue"],
    "title_font": fonts["medium"],
}

info_section = {"position": (10, 50)}

# =============================================================================
# COMPONENT CONFIGURATION
# =============================================================================

# Button configuration
button = {
    # Typography settings
    "text_medium": fonts["sizes"]["medium"],
    "text_small": fonts["sizes"]["small"],
    "font_medium": fonts["medium"],
    "font_regular": fonts["regular"],
    # Visual settings
    "border_radius": 8,
    "hover_offset": 5,
    # Button variants
    "primary": {
        "bg_color": colors["primary_blue"],
        "disabled_color": colors["disabled_blue"],
        "disabled_text": colors["white"],
        "text_color": colors["white"],
    },
    "secondary": {
        "bg_color": colors["light_gray"],
        "disabled_color": colors["light_gray"],
        "disabled_text": colors["disabled_gray"],
        "text_color": colors["text_dark"],
    },
    "tertiary": {
        "bg_color": colors["primary_red"],
        "text_color": colors["white"],
    },
    "subtle": {
        "bg_color": colors["subtle_blue"],
        "text_color": colors["white"],
    },
}

# Panel configuration
panel = {
    "bg_color": colors["dark_blue"],
    "width": 300,
    "border_radius": 8,
    "headline_color": colors["primary_blue"],
    "headline_font": fonts["medium"],
    "headline_size": fonts["sizes"]["medium"],
    "tag_font": fonts["medium"],
    "tag_size": fonts["sizes"]["small"],
    "value_font": fonts["regular"],
    "value_size": fonts["sizes"]["tiny"],
    "item_spacing": 10,
    "item_height": 20,
    "text_color": colors["white"],
}

selector = {
    "size": (270, 44),
    "arrow_color": colors["primary_blue"],
    "arrow_hover_color": colors["hover_blue"],
    "arrow_size": (34, 44),
    "arrow_padding": 10,
    "label_size": (169, 44),
    "label_bg_color": colors["dark_blue"],
    "label_text_color": colors["white"],
    "label_padding": 32,
    "font_name": fonts["medium"],
    "font_size": fonts["sizes"]["small"],
}

world_view = {"board_size": 512}

cell = {
    "safe": colors["green"],
    "unknown": colors["gray"],
    "default": colors["white"],
    "visited": colors["white"],
    "border": colors["dark_blue"],
}

# Entity colors
entity = {
    "gold": colors["yellow"],
    "wumpus": (139, 69, 19),  # Saddle brown
    "pit": (105, 105, 105),  # Dim gray
    "agent": (86, 86, 253),  # blue
    "breeze": colors["primary_blue"],
    "stench": colors["red"],
    "scream": colors["red"],
    "arrow_head": colors["white"],
    "arrow_body": (255, 165, 0),
}
