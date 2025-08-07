import pygame
import modules.visualization.ui_config as config


class Button:
    """A UI button component for interactive interfaces.

    This class represents a clickable button that can be drawn on a pygame surface.
    It supports hover effects, different visual variants, and custom actions when clicked.

    Attributes:
        position (tuple[int, int]): The (x, y) position of the button's top-left corner.
        size (tuple[int, int]): The (width, height) dimensions of the button.
        label (str): The text displayed on the button.
        variant (str): The visual style of the button (e.g., "primary", "secondary").
        text_style (list[str]): Style properties for the button text as [size_key, font_key].
        action (callable, optional): Function to call when the button is clicked.
        disabled (bool): Whether the button is currently disabled and should not respond to clicks.
    """

    def __init__(
        self,
        position: tuple[int, int],
        size: tuple[int, int],
        label: str,
        variant: str,
        text_style: list[str],
        action=None,
        disabled: bool = False,
    ):
        """Initialize a new Button instance.

        Args:
            position (tuple[int, int]): The (x, y) position of the button's top-left corner.
            size (tuple[int, int]): The (width, height) dimensions of the button.
            label (str): The text displayed on the button.
            variant (str): The visual style of the button (e.g., "primary", "secondary").
            text_style (list[str]): Style properties for the button text as [size_key, font_key].
            action (callable, optional): Function to call when the button is clicked.
            disabled (bool): Whether the button is currently disabled and should not respond to clicks.
        """
        self.position = position
        self.size = size
        self.label = label
        self.variant = variant
        self.text_style = text_style
        self.action = action
        self.disabled = disabled

        self.rect = pygame.Rect(position, size)
        self.font = self.__get_font(text_style[0], text_style[1])

    def draw(self, surface: pygame.Surface):
        """Draw the button on the given surface.

        Renders the button with the appropriate styling. If the mouse is hovering
        over the button, applies a hover effect by increasing the button size and
        font size slightly.

        Args:
            surface (pygame.Surface): The surface to draw the button on.
        """
        rect, font = self.rect, self.font
        color = config.button[self.variant]["bg_color"]

        if self.disabled:
            color = config.button[self.variant].get("disabled_color", color)
        elif self.is_hovered(surface, pygame.mouse.get_pos()):
            rect, font = self.__get_hover_styles()

        pygame.draw.rect(
            surface,
            color,
            rect,
            border_radius=config.button["border_radius"],
        )

        # Render the label text
        self.__render_text(surface, font, rect)

    def is_hovered(self, surface: pygame.Surface, mouse_pos: tuple[int, int]) -> bool:
        """Check if the button is hovered by the mouse.

        Args:
            mouse_pos (tuple[int, int]): The current mouse position as (x, y).

        Returns:
            bool: True if the mouse is over the button, False otherwise.
        """
        rel_pos = self.__get_local_mouse_pos(surface, mouse_pos)
        return self.rect.collidepoint(rel_pos)

    def is_clicked(self, surface: pygame.Surface, event: pygame.event.Event) -> bool:
        """Check if the button was clicked.

        Args:
            surface (pygame.Surface): The surface where the button is drawn.
            event (pygame.event.Event): The mouse event to check.
        """
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            rel_pos = self.__get_local_mouse_pos(surface, event.pos)
            return self.rect.collidepoint(rel_pos)
        return False

    def __get_font(self, size_key, font_key, hover=False):
        """Get the pygame font object based on style keys.

        Args:
            size_key (str): The key for font size in the config.
            font_key (str): The key for font family in the config.

        Returns:
            pygame.font.Font: The font object with the requested properties.
        """
        return pygame.font.Font(
            f"./assets/fonts/{config.button[font_key]}.ttf",
            config.button[size_key]
            + (config.button["hover_offset"] // 2 if hover else 0),
        )

    def __get_hover_styles(self):
        """Apply hover effect styles to the button.

        Returns:
            tuple: (pygame.Rect, pygame.font.Font) The hover-modified rectangle and font.
        """
        offset = config.button["hover_offset"]
        position = (self.position[0] - offset, self.position[1] - offset)
        size = (self.size[0] + offset * 2, self.size[1] + offset * 2)

        # Create the enlarged rectangle
        hover_rect = pygame.Rect(position, size)

        # Get the enlarged font
        hover_font = self.__get_font(self.text_style[0], self.text_style[1], hover=True)

        return hover_rect, hover_font

    def __render_text(self, surface, font, rect):
        """Render the button's text label.

        Args:
            surface (pygame.Surface): The surface to draw on.
            font (pygame.font.Font): The font to use for rendering.
            rect (pygame.Rect): The button rectangle for positioning.
        """
        color = config.button[self.variant]["text_color"]
        if self.disabled:
            color = config.button[self.variant].get("disabled_text", color)

        text_surface = font.render(self.label, True, color)
        text_rect = text_surface.get_rect(center=rect.center)
        surface.blit(text_surface, text_rect)

    def __get_local_mouse_pos(self, surface, event_pos):
        """Convert global mouse position to local coordinates.

        Args:
            surface (pygame.Surface): The parent surface.
            event_pos (tuple): The global mouse position.

        Returns:
            tuple: The mouse position relative to this selector.
        """
        # Get the parent surface position
        surface_position = (
            surface.get_rect().topleft
            if not hasattr(surface, "position")
            else surface.position
        )

        # Return mouse position relative to this component
        return (
            event_pos[0] - surface_position[0],
            event_pos[1] - surface_position[1],
        )
