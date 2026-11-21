"""Localized UI strings for the interactive player."""

from dataclasses import dataclass


@dataclass(frozen=True)
class UiStrings:
    """UI strings of a single language.

    Attributes:
        running: Status text while the simulation is running.
        paused: Status text while the simulation is paused.
        speed: Label of the simulation speed multiplier.
        scale: Label of the visual zoom level.
        position: Label of the current position.
        velocity: Label of the current velocity.
        force: Label of the current control force.
        mass: Label of the system mass.
        damping: Label of the damping coefficient.
        external_force: Label of the constant external force.
        frequency: Label of the regulator sampling rate.
        target: Label of the target position.
        initial_position: Label of the initial position.
        initial_velocity: Label of the initial velocity.
        initial_force: Label of the initial control force.
        unit_mass: Unit of mass.
        unit_damping: Unit of the damping coefficient.
        unit_force: Unit of force.
        unit_position: Unit of position.
        unit_velocity: Unit of velocity.
        unit_frequency: Unit of frequency.
        help_scale: Help line for the zoom shortcut.
        help_speed: Help line for the speed shortcut.
        help_speed_reset: Help line for the speed reset shortcut.
        help_param: Help line for the parameter selection keys.
        help_tune: Help line for the parameter adjustment keys.
        help_restart: Help line for the restart key.
        help_pause: Help line for the pause key.
        help_exit: Help line for the exit keys.
        help_language: Help line for the language key.
        parameter_names: Translation of tunable display names;
            unknown names fall back to the name itself.
        parameter_units: Translation of tunable unit suffixes;
            unknown units fall back to the unit itself.
    """

    running: str
    paused: str
    speed: str
    scale: str
    position: str
    velocity: str
    force: str
    mass: str
    damping: str
    external_force: str
    frequency: str
    target: str
    initial_position: str
    initial_velocity: str
    initial_force: str
    unit_mass: str
    unit_damping: str
    unit_force: str
    unit_position: str
    unit_velocity: str
    unit_frequency: str
    help_scale: str
    help_speed: str
    help_speed_reset: str
    help_param: str
    help_tune: str
    help_restart: str
    help_pause: str
    help_exit: str
    help_language: str
    parameter_names: dict[str, str]
    parameter_units: dict[str, str]


EN = UiStrings(
    running="RUNNING",
    paused="PAUSED",
    speed="Speed",
    scale="Scale",
    position="X",
    velocity="V",
    force="F",
    mass="M",
    damping="Damping",
    external_force="External F",
    frequency="Freq",
    target="Target",
    initial_position="X0",
    initial_velocity="V0",
    initial_force="F0",
    unit_mass="kg",
    unit_damping="N·s/m",
    unit_force="N",
    unit_position="m",
    unit_velocity="m/s",
    unit_frequency="Hz",
    help_scale="Scale: Ctrl +/-",
    help_speed="Speed: Shift +/-",
    help_speed_reset="Speed=1: Shift+R",
    help_param="Param: 1..9",
    help_tune="Tune: Up/Down (Shift = x10)",
    help_restart="Restart: R",
    help_pause="Pause: Space",
    help_exit="Exit: Q / Ctrl+W",
    help_language="Lang: L",
    parameter_names={},
    parameter_units={},
)

RU = UiStrings(
    running="РАБОТАЕТ",
    paused="ПАУЗА",
    speed="Скорость",
    scale="Масштаб",
    position="X",
    velocity="V",
    force="F",
    mass="Масса",
    damping="Трение",
    external_force="Внешняя сила",
    frequency="Частота",
    target="Цель",
    initial_position="X0",
    initial_velocity="V0",
    initial_force="F0",
    unit_mass="кг",
    unit_damping="Н·с/м",
    unit_force="Н",
    unit_position="м",
    unit_velocity="м/с",
    unit_frequency="Гц",
    help_scale="Масштаб: Ctrl +/-",
    help_speed="Скорость: Shift +/-",
    help_speed_reset="Скорость=1: Shift+R",
    help_param="Параметр: 1..9",
    help_tune="Настроить: Up/Down (Shift = x10)",
    help_restart="Рестарт: R",
    help_pause="Пауза: Пробел",
    help_exit="Выход: Q / Ctrl+W",
    help_language="Язык: L",
    parameter_names={
        "Mass": "Масса",
        "Damping": "Трение",
        "Ext force": "Внешняя сила",
        "Target": "Цель",
    },
    parameter_units={
        "kg": "кг",
        "N·s/m": "Н·с/м",
        "N": "Н",
        "m": "м",
    },
)

#: Available languages keyed by their code.
LANGUAGES: dict[str, UiStrings] = {"en": EN, "ru": RU}


class Language:
    """Mutable holder of the current UI language.

    Shared by the player controller and the renderers so that the
    language can be switched at runtime and stays in sync everywhere.

    Attributes:
        code: The language code, a key of ``LANGUAGES``.
    """

    _code: str

    def __init__(self, code: str = "en") -> None:
        """Initialize the language.

        Args:
            code: The language code, a key of ``LANGUAGES``.
                Defaults to ``"en"``.

        Raises:
            ValueError: If ``code`` is not a key of ``LANGUAGES``.
        """
        self.code = code

    @property
    def code(self) -> str:
        """The language code."""
        return self._code

    @code.setter
    def code(self, code: str) -> None:
        """Set the language code.

        Args:
            code: The language code, a key of ``LANGUAGES``.

        Raises:
            ValueError: If ``code`` is not a key of ``LANGUAGES``.
        """
        if code not in LANGUAGES:
            raise ValueError(
                f"Unknown language code: {code!r}. "
                f"Expected one of {sorted(LANGUAGES)}."
            )
        self._code = code

    @property
    def texts(self) -> UiStrings:
        """UI strings of the current language."""
        return LANGUAGES[self._code]

    def toggle(self) -> None:
        """Switch to the next language in ``LANGUAGES``."""
        codes = tuple(LANGUAGES)
        self.code = codes[(codes.index(self._code) + 1) % len(codes)]
