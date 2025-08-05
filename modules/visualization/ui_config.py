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
    "green": (144, 238, 144),  # Light green for safe cells
    "red": (255, 0, 0),  # Tomato red for danger/wumpus
    "yellow": (255, 215, 0),  # Gold for treasure
    "gray": (169, 169, 169),  # Dark gray for unknown cells
    "white": (255, 255, 255),  # White for visited cells
    "black": (0, 0, 0),  # Black for text and borders
    "light_gray": (200, 200, 200),  # Light gray for secondary buttons
    "disabled_gray": (180, 180, 180),  # Medium gray for disabled elements
    "disabled_blue": (180, 222, 254),  # Light blue, used for disabled primary
    "hover_blue": (120, 180, 255),  # Lighter blue for hover states
}

# =============================================================================
# TYPOGRAPHY
# =============================================================================
fonts = {
    "family": "Arial",  # Default font family
    "sizes": {
        "large": 24,
        "medium": 18,
        "small": 14,
        "tiny": 12,
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
    "title_size": fonts["sizes"]["large"],
    "title_color": colors["dark_blue"],
    "font_family": fonts["family"],
}

info_section = {"position": (10, 70)}

# =============================================================================
# COMPONENT CONFIGURATION
# =============================================================================

# Button configuration
button = {
    # Typography settings
    "text_normal": fonts["sizes"]["medium"],
    "text_small": fonts["sizes"]["small"],
    "font_family": fonts["family"],
    # Visual settings
    "border_radius": 8,
    "hover_offset": 2,
    "border_width": 2,
    # Button variants
    "primary": {
        "bg_color": colors["primary_blue"],
        "text_color": colors["white"],
        "border_color": colors["dark_blue"],
        "hover_bg_color": colors["hover_blue"],
        "disabled_bg_color": colors["disabled_gray"],
        "disabled_text_color": colors["white"],
    },
    "secondary": {
        "bg_color": colors["light_gray"],
        "text_color": colors["black"],
        "border_color": colors["gray"],
        "hover_bg_color": colors["white"],
        "disabled_bg_color": colors["disabled_gray"],
        "disabled_text_color": colors["gray"],
    },
    "danger": {
        "bg_color": colors["red"],
        "text_color": colors["white"],
        "border_color": colors["red"],
        "hover_bg_color": (255, 69, 41),  # Darker red
        "disabled_bg_color": colors["disabled_gray"],
        "disabled_text_color": colors["white"],
    },
}

# Panel configuration
panel = {
    "bg_color": colors["dark_blue"],
    "width": 300,
    "border_radius": 8,
    "headline_color": colors["primary_blue"],
    "headline_font": fonts["family"],
    "headline_size": fonts["sizes"]["large"],
    "tag_font": fonts["family"],
    "tag_size": fonts["sizes"]["medium"],
    "value_font": fonts["family"],
    "value_size": fonts["sizes"]["medium"],
    "item_spacing": 10,
    "item_height": 20,
    "text_color": colors["white"],
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
