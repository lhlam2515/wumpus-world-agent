import pygame

import modules.visualization.ui_config as config


class Panel(pygame.Surface):
    """A UI component that displays information in a structured panel format.

    This panel includes a title header and a list of key-value pairs displayed as items.

    Attributes:
        position: The (x, y) position of this panel on the parent surface.
        size: The (width, height) dimensions of this panel.
        title: The title text displayed in the panel header.
        items: Dictionary of items displayed in the panel.
    """

    def __init__(
        self,
        position: tuple[int, int],
        size: tuple[int, int],
        title: str,
        items: dict | None = None,
    ):
        """Initialize a new Panel instance.

        Args:
            position (tuple[int, int]): The (x, y) position on the parent surface.
            size (tuple[int, int]): The (width, height) dimensions.
            title (str): The title text to display in the panel header.
            items (dict | None): Dictionary of items to display, where keys are labels and values are the displayed values.
        """
        super().__init__(size, pygame.SRCALPHA)

        self.position = position
        self.size = size
        self.title = title
        self.items = items

        self.render()  # Initial render to set up the panel display

    def render(self, items: dict | None = None) -> None:
        """Render the panel with its background, headline, and items.

        Draws the panel background, header, and all items with their values.

        Args:
            items (dict | None): A dictionary of items to display in the panel.
                If None, the existing items will be used.
        """
        self.items = items if items is not None else self.items

        self.fill((0, 0, 0, 0))

        # Draw panel background
        rect = pygame.Rect((0, 0), self.size)
        pygame.draw.rect(
            self,
            config.panel["bg_color"],
            rect,
            border_radius=config.panel["border_radius"],
        )

        # Draw panel headline
        self.__render_headline()

        # Draw items
        self.__render_items()

    def __render_headline(self) -> None:
        """Render the panel headline/title section.

        Draws the headline background rectangle and renders the title text.
        """
        rect = pygame.Rect((0, 0), (self.size[0], 44))
        pygame.draw.rect(
            self,
            config.panel["headline_color"],
            rect,
            border_top_left_radius=config.panel["border_radius"],
            border_top_right_radius=config.panel["border_radius"],
        )
        self.__render_text(self.title, rect.center, "headline_font", "headline_size")

    def __render_items(self) -> None:
        """Render the items in the panel.

        Draws each key-value pair from the items dictionary with appropriate styling.
        """
        if not self.items:
            return

        start_y = 50
        for tag, value in self.items.items():
            # Render tag text
            rect = pygame.Rect((0, start_y), (self.size[0] // 2, 32))
            self.__render_text(
                f"{tag}:",
                rect.center,
                "tag_font",
                "tag_size",
            )

            # Render value text
            rect.topleft = (self.size[0] // 2, start_y)
            self.__render_text(
                str(value),
                rect.center,
                "value_font",
                "value_size",
            )

            start_y += config.panel["item_height"] + config.panel["item_spacing"]

    def __get_font(self, font_name_key: str, font_size_key: str) -> pygame.font.Font:
        """Get the font object for rendering text.

        Args:
            font_name_key: The config key for the font name.
            font_size_key: The config key for the font size.

        Returns:
            Font: The font object with the configured properties.
        """
        return pygame.font.Font(
            f"./assets/fonts/{config.panel[font_name_key]}.ttf",
            config.panel[font_size_key],
        )

    def __render_text(
        self,
        text: str,
        position: tuple[int, int],
        font_name_key: str,
        font_size_key: str,
    ) -> None:
        """Render text on the panel surface.

        Args:
            text: The text to render.
            position: The (x, y) position for the center of the text.
            font_name_key: The config key for the font name.
            font_size_key: The config key for the font size.
        """
        font = self.__get_font(font_name_key, font_size_key)
        text_surf = font.render(text, True, config.panel["text_color"])

        text_rect = text_surf.get_rect(center=position)
        self.blit(text_surf, text_rect)
