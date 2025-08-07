import pygame

import modules.visualization.ui_config as config


class Selector(pygame.Surface):
    """A UI component for cycling through a list of selectable items.

    This component displays a label with the current selection and arrow buttons
    on either side to navigate through the list of items. The selector supports
    hover effects and click interactions.

    Attributes:
        position (tuple[int, int]): The (x, y) position of this component on the parent surface.
        size (tuple[int, int]): The (width, height) dimensions of this component.
        items (list[str]): The list of selectable items.
        index (int): The index of the currently selected item.
        on_change (callable, optional): Function to call when selection changes.
    """

    def __init__(
        self,
        position: tuple[int, int],
        size: tuple[int, int],
        items: list[str],
        initial_index: int = 0,
        on_change=None,
    ):
        """Initialize a new Selector component.

        Args:
            position (tuple[int, int]): The (x, y) position on the parent surface.
            size (tuple[int, int]): The (width, height) dimensions.
            items (list[str]): The list of selectable items.
            initial_index (int, optional): The starting index. Defaults to 0.
            on_change (callable, optional): Function to call when selection changes.
                The function should accept the new selected value and environment state.
        """
        super().__init__(config.selector["size"], pygame.SRCALPHA)

        self.position = position
        self.size = size
        self.items = items
        self.index = min(initial_index, len(items) - 1) if items else 0
        self.on_change = on_change

        # Initialize rects for interactive elements
        self.__label_rect = pygame.Rect(0, 0, 0, 0)
        self.__left_arrow_rect = pygame.Rect(0, 0, *config.selector["arrow_size"])
        self.__right_arrow_rect = pygame.Rect(0, 0, *config.selector["arrow_size"])

        # Track hover state
        self.__hover_left = False
        self.__hover_right = False

        # Position the elements
        self.__update_layout()

        # Initial render
        self.render()

    def render(self):
        """Render the selector with its current state."""
        # Clear the surface
        self.fill((0, 0, 0, 0))

        # Draw the label background
        pygame.draw.rect(self, config.selector["label_bg_color"], self.__label_rect)

        # Draw the label text
        if self.items:
            self.__render_text()

        # Draw the arrows
        self.__draw_arrow(self.__left_arrow_rect, False, self.__hover_left)
        self.__draw_arrow(self.__right_arrow_rect, True, self.__hover_right)

    def handle_event(self, surface, event, env):
        """Process events for the selector component.

        Handles mouse movement for hover effects and clicks for changing selection.

        Args:
            surface (pygame.Surface): The surface to draw on.
            event (pygame.event.Event): The event to process.
            env (dict): The environment state to update.

        Returns:
            dict: The updated environment state.
        """
        new_env = {**env}  # Create a copy of the environment

        if event.type == pygame.MOUSEMOTION:
            local_pos = self.__get_local_mouse_pos(surface, event.pos)
            self.__handle_hover(*local_pos)

        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            local_pos = self.__get_local_mouse_pos(surface, event.pos)

            if self.__left_arrow_rect.collidepoint(*local_pos):
                new_env = self.__select_previous(new_env)
            elif self.__right_arrow_rect.collidepoint(*local_pos):
                new_env = self.__select_next(new_env)

        return new_env

    def __update_layout(self):
        """Update the layout of the selector components."""
        # Calculate center coordinates
        center_x = self.get_width() // 2
        center_y = self.get_height() // 2
        center = (center_x, center_y)

        # Calculate label dimensions
        if self.items:
            self.__label_rect.size = config.selector["label_size"]
            self.__label_rect.center = center

            # Position arrows
            padding = config.selector["arrow_padding"]
            self.__left_arrow_rect.midright = (
                self.__label_rect.left - padding,
                center_y,
            )
            self.__right_arrow_rect.midleft = (
                self.__label_rect.right + padding,
                center_y,
            )

    def __get_font(self):
        """Get the font object for the selector text.

        Returns:
            pygame.font.Font: The font object with the configured properties.
        """
        return pygame.font.Font(
            f"./assets/fonts/{config.selector['font_name']}.ttf",
            config.selector["font_size"],
        )

    def __render_text(self):
        """Render the label text."""
        font = self.__get_font()
        text_surf = font.render(
            self.items[self.index], True, config.selector["label_text_color"]
        )

        text_rect = text_surf.get_rect(center=self.__label_rect.center)
        self.blit(text_surf, text_rect)

    def __draw_arrow(self, rect, pointing_right, hover):
        """Draw an arrow pointing left or right.

        Args:
            rect (pygame.Rect): The rectangle containing the arrow.
            pointing_right (bool): True if arrow points right, False for left.
            hover (bool): Whether the arrow is being hovered.
        """
        color = (
            config.selector["arrow_hover_color"]
            if hover
            else config.selector["arrow_color"]
        )

        cx, cy = rect.center
        w, h = rect.size

        if pointing_right:
            points = [
                (cx + w // 2, cy),
                (cx - w // 2, cy - h // 2),
                (cx - w // 2, cy + h // 2),
            ]
        else:
            points = [
                (cx - w // 2, cy),
                (cx + w // 2, cy - h // 2),
                (cx + w // 2, cy + h // 2),
            ]

        pygame.draw.polygon(self, color, points)

    def __handle_hover(self, mx, my):
        """Handle hover state updates.

        Args:
            mx (int): Mouse x coordinate relative to selector.
            my (int): Mouse y coordinate relative to selector.

        Returns:
            bool: True if hover state changed, False otherwise.
        """
        # Update hover states
        prev_left = self.__hover_left
        prev_right = self.__hover_right

        self.__hover_left = self.__left_arrow_rect.collidepoint(mx, my)
        self.__hover_right = self.__right_arrow_rect.collidepoint(mx, my)

        # Re-render if hover state changed
        if prev_left != self.__hover_left or prev_right != self.__hover_right:
            self.render()
            return True

        return False

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

        # Combine parent position with this component's position
        abs_position = (
            surface_position[0] + self.position[0],
            surface_position[1] + self.position[1],
        )

        # Return mouse position relative to this component
        return (
            event_pos[0] - abs_position[0],
            event_pos[1] - abs_position[1],
        )

    def __select_previous(self, env):
        """Select the previous item in the list.

        Args:
            env (dict): The current environment state.

        Returns:
            dict: The updated environment state.
        """
        if not self.items:
            return env

        new_env = {**env}

        prev_index = self.index
        self.index = (self.index - 1) % len(self.items)

        if prev_index != self.index:
            self.__update_layout()
            self.render()

            if self.on_change:
                new_env = self.on_change(self.value, new_env)

        return new_env

    def __select_next(self, env):
        """Select the next item in the list.

        Args:
            env (dict): The current environment state.

        Returns:
            dict: The updated environment state.
        """
        if not self.items:
            return env

        new_env = {**env}

        prev_index = self.index
        self.index = (self.index + 1) % len(self.items)

        if prev_index != self.index:
            self.__update_layout()
            self.render()

            if self.on_change:
                new_env = self.on_change(self.value, new_env)

        return new_env

    @property
    def value(self):
        """Get the currently selected item.

        Returns:
            str: The selected item, or None if the list is empty.
        """
        return self.items[self.index] if self.items else None
