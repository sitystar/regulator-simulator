"""Player controller for the interactive simulation loop."""

try:
    import pygame
except ImportError as exc:
    raise ImportError(
        "pygame-ce is required, not classic pygame.\n"
        "Install it with: pip install pygame-ce."
    ) from exc

from collections.abc import Sequence

from .graphics_renderer import GraphicsRenderer
from .simulation_renderer import SimulationRenderer
from .simulator import Simulator
from .texts import Language
from .tunables import Tunable
from .window_manager import WindowManager

SCALE_ADJUSTMENT_SPEED: float = 2.0
SPEED_ADJUSTMENT_SPEED: float = 2.0
MAX_FRAME_DT: float = 0.1
KEY_REPEAT_DELAY_MS: int = 400
KEY_REPEAT_INTERVAL_MS: int = 80

#: Maps the scancodes of the digit keys (main row and keypad) to their
#: zero-based index, used to select a tunable.
TUNABLE_SELECT_KEYS: dict[int, int] = {
    scan: index
    for keys in (
        tuple(getattr(pygame, f"KSCAN_{digit}") for digit in range(1, 10)),
        tuple(getattr(pygame, f"KSCAN_KP{digit}") for digit in range(1, 10)),
    )
    for index, scan in enumerate(keys)
}

#: Scancodes that respond to auto-repeated key presses.
REPEATABLE_SCANCODES: tuple[int, ...] = (pygame.KSCAN_UP, pygame.KSCAN_DOWN)


class PlayerController:
    """Coordinates the interactive simulation loop.

    Attributes:
        speed: Simulation speed multiplier.
        paused: Whether the simulation is paused.
    """

    paused: bool

    _window_manager: WindowManager
    _graphics_renderer: GraphicsRenderer
    _simulation_renderer: SimulationRenderer
    _simulator: Simulator
    _tunables: tuple[Tunable, ...]
    _selected_tunable: int
    _language: Language
    _speed: float
    _running: bool

    def __init__(
        self,
        window_manager: WindowManager,
        graphics_renderer: GraphicsRenderer,
        simulation_renderer: SimulationRenderer,
        simulator: Simulator,
        speed: float = 1.0,
        paused: bool = False,
        tunables: Sequence[Tunable] = (),
        language: Language | None = None,
    ) -> None:
        """Initialize the player controller.

        Args:
            window_manager: The ``WindowManager`` instance
                for managing the simulation window.
            graphics_renderer: The ``GraphicsRenderer`` instance
                for managing the graphics rendering.
            simulation_renderer: The ``SimulationRenderer`` instance
                for managing the simulation rendering.
            simulator: The ``Simulator`` instance
                for managing the simulation.
            speed: The initial simulation speed multiplier.
                Must be positive. Defaults to ``1.0``.
            paused: Whether the simulation should start paused.
                Defaults to ``False``.
            tunables: Parameters adjustable at runtime from the keyboard.
                Keys ``1``-``9`` select one of them and ``Up``/``Down``
                change its value. Defaults to ``()``.
            language: UI language holder; the ``L`` key switches
                the language at runtime. A new ``Language`` in English
                is created if ``None``. Defaults to ``None``.

        Raises:
            ValueError: If ``speed`` is not positive.
        """
        self._window_manager = window_manager
        self._graphics_renderer = graphics_renderer
        self._simulation_renderer = simulation_renderer
        self._simulator = simulator
        self._tunables = tuple(tunables)
        self._selected_tunable = 0
        self._language = language if language is not None else Language()
        self.speed = speed

        pygame.init()

        self.paused = paused
        self._running = False

    @property
    def speed(self) -> float:
        """Simulation speed multiplier."""
        return self._speed

    @speed.setter
    def speed(self, speed: float) -> None:
        """Set the simulation speed multiplier. Must be positive.

        Raises:
            ValueError: If ``speed`` is not positive.
        """
        if speed <= 0.0:
            raise ValueError("Speed must be positive.")
        self._speed = speed

    def stop(self) -> None:
        """Stop the interactive simulation loop."""
        self._running = False

    def _process_events(self) -> None:
        """Handle window events and keyboard shortcuts."""
        for event in pygame.event.get():
            if event.type in (pygame.QUIT, pygame.WINDOWCLOSE):
                self.stop()
            elif event.type == pygame.WINDOWRESIZED:
                self._graphics_renderer.update_size()
            elif event.type == pygame.KEYDOWN:
                mode = pygame.key.get_mods()
                if getattr(event, "repeat", 0) and (
                    event.scancode not in REPEATABLE_SCANCODES
                ):
                    continue
                if event.scancode == pygame.KSCAN_R and not (mode & pygame.KMOD_SHIFT):
                    self._simulator.reset()
                elif event.scancode == pygame.KSCAN_SPACE:
                    self.paused = not self.paused
                elif event.scancode == pygame.KSCAN_Q or (
                    event.scancode == pygame.KSCAN_W and mode & pygame.KMOD_CTRL
                ):
                    self.stop()
                elif event.scancode == pygame.KSCAN_L:
                    self._language.toggle()
                elif event.scancode in TUNABLE_SELECT_KEYS and self._tunables:
                    index = TUNABLE_SELECT_KEYS[event.scancode]
                    if index < len(self._tunables):
                        self._selected_tunable = index
                elif event.scancode == pygame.KSCAN_UP and self._tunables:
                    self._tunables[self._selected_tunable].adjust(
                        1, big=bool(mode & pygame.KMOD_SHIFT)
                    )
                elif event.scancode == pygame.KSCAN_DOWN and self._tunables:
                    self._tunables[self._selected_tunable].adjust(
                        -1, big=bool(mode & pygame.KMOD_SHIFT)
                    )

    def _process_adjustment_keys(self, dt: float) -> None:
        """Handle continuous input for scale and speed adjustments.

        Args:
            dt: Delta time for smooth transitions.
        """
        keys = pygame.key.get_pressed()
        if keys[pygame.K_LCTRL] or keys[pygame.K_RCTRL]:
            if keys[pygame.K_EQUALS] or keys[pygame.K_KP_PLUS]:
                self._simulation_renderer.scale *= 1.0 + SCALE_ADJUSTMENT_SPEED * dt
            if keys[pygame.K_MINUS] or keys[pygame.K_KP_MINUS]:
                self._simulation_renderer.scale *= 1.0 - SCALE_ADJUSTMENT_SPEED * dt
        if keys[pygame.K_LSHIFT] or keys[pygame.K_RSHIFT]:
            if keys[pygame.K_EQUALS] or keys[pygame.K_KP_PLUS]:
                self.speed *= 1.0 + SPEED_ADJUSTMENT_SPEED * dt
            if keys[pygame.K_MINUS] or keys[pygame.K_KP_MINUS]:
                self.speed *= 1.0 - SPEED_ADJUSTMENT_SPEED * dt
            if keys[pygame.K_r]:
                self.speed = 1.0

    def run(self, fps: int = 0) -> None:
        """Start the interactive simulation loop.

        Args:
            fps: Maximum frames per second. If ``0``, the simulation will run at
                maximum speed. Must be a non-negative integer. Defaults to ``0``.

        Raises:
            ValueError: If ``fps`` is negative or not an integer.
        """
        if not isinstance(fps, int) or isinstance(fps, bool) or fps < 0:
            raise ValueError("FPS must be a non-negative integer.")

        first_frame = True
        self._running = True
        self._window_manager.show()
        pygame.key.set_repeat(KEY_REPEAT_DELAY_MS, KEY_REPEAT_INTERVAL_MS)
        clock = pygame.time.Clock()
        try:
            while self._running:
                self._process_events()
                dt = min(clock.tick(fps) / 1000.0, MAX_FRAME_DT)
                self._process_adjustment_keys(dt)

                if not self.paused:
                    self._simulator.simulate_dt(dt * self.speed)

                texts = self._language.texts
                self._simulation_renderer.render(
                    (
                        texts.paused if self.paused else texts.running,
                        f"{texts.speed}: {self.speed:.2f}",
                        f"{texts.scale}: {self._simulation_renderer.scale:.2f}",
                    ),
                    tunables=self._tunables,
                    selected_tunable=(
                        self._selected_tunable if self._tunables else None
                    ),
                )
                self._graphics_renderer.present()

                if first_frame:
                    first_frame = False
                    self._window_manager.reset_position()
        finally:
            self._window_manager.hide()
