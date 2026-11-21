"""Runtime-tunable parameters for the interactive player."""

from collections.abc import Callable


class Tunable:
    """A parameter that can be adjusted from the keyboard at runtime.

    Attributes:
        name: Short display name, e.g. ``P``.
        getter: Callable returning the current value.
        setter: Callable receiving the new value.
        step: Value change of a single small adjustment. Must be positive.
        big_step: Value change of a single large adjustment
            (with ``Shift`` held). Must be positive.
            Defaults to ``step * 10``.
        minimum: Lower bound of the value, or ``None`` for unbounded.
        maximum: Upper bound of the value, or ``None`` for unbounded.
        unit: Unit suffix for display, e.g. ``kg``. May be empty.
        precision: Number of decimal places used to display the value.
    """

    def __init__(
        self,
        name: str,
        getter: Callable[[], float],
        setter: Callable[[float], None],
        step: float = 0.1,
        big_step: float | None = None,
        minimum: float | None = None,
        maximum: float | None = None,
        unit: str = "",
        precision: int = 2,
    ) -> None:
        """Initialize the tunable.

        Args:
            name: Short display name, e.g. ``P``.
            getter: Callable returning the current value.
            setter: Callable receiving the new value. It may raise
                ``ValueError`` if the value is not acceptable.
            step: Value change of a single small adjustment.
                Must be positive. Defaults to ``0.1``.
            big_step: Value change of a single large adjustment
                (with ``Shift`` held). Must be positive.
                Defaults to ``step * 10``.
            minimum: Lower bound of the value, or ``None`` for unbounded.
                Defaults to ``None``.
            maximum: Upper bound of the value, or ``None`` for unbounded.
                Defaults to ``None``.
            unit: Unit suffix for display, e.g. ``kg``. May be empty.
                Defaults to ``""``.
            precision: Number of decimal places used to display the value.
                Defaults to ``2``.

        Raises:
            ValueError: If ``step`` or ``big_step`` is not positive,
                ``minimum`` is greater than ``maximum``, or
                ``precision`` is not a non-negative integer.
        """
        if step <= 0.0:
            raise ValueError("Step must be positive.")
        if big_step is not None and big_step <= 0.0:
            raise ValueError("Big step must be positive.")
        if minimum is not None and maximum is not None and minimum > maximum:
            raise ValueError("Minimum must not be greater than maximum.")
        if (
            not isinstance(precision, int)
            or isinstance(precision, bool)
            or precision < 0
        ):
            raise ValueError("Precision must be a non-negative integer.")

        self.name = name
        self.getter = getter
        self.setter = setter
        self.step = step
        self.big_step = step * 10.0 if big_step is None else big_step
        self.minimum = minimum
        self.maximum = maximum
        self.unit = unit
        self.precision = precision

    def adjust(self, direction: int, big: bool = False) -> None:
        """Change the value by one step and clamp it to the bounds.

        Args:
            direction: ``1`` to increase, ``-1`` to decrease.
            big: Whether to use ``big_step`` instead of ``step``.
                Defaults to ``False``.

        Raises:
            ValueError: If ``direction`` is not ``-1`` or ``1``.
        """
        if direction not in (-1, 1):
            raise ValueError("Direction must be -1 or 1.")
        delta = self.big_step if big else self.step
        value = round(self.getter() + direction * delta, 9)
        if self.minimum is not None:
            value = max(self.minimum, value)
        if self.maximum is not None:
            value = min(self.maximum, value)
        self.setter(value)

    def format(self, unit: str | None = None) -> str:
        """Format the current value for display.

        Args:
            unit: Unit override for display, e.g. a localized unit.
                Defaults to the tunable's own unit.

        Returns:
            The value with ``precision`` decimal places
            and the unit suffix, if any.
        """
        unit = self.unit if unit is None else unit
        value = f"{self.getter():.{self.precision}f}"
        return f"{value} {unit}" if unit else value
