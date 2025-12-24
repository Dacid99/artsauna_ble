from .models import ArtsaunaState


class ArtsaunaStateMixin:
    @property
    def state(self) -> ArtsaunaState:
        return self._state

    @property
    def rgb_mode(self) -> int:
        return (self._state.rgb + 2) % 9

    @property
    def volume(self) -> int:
        return self._state.volume

    @property
    def target_temp(self) -> int:
        return self._state.target_temp

    @property
    def current_temp(self) -> int:
        return self._state.current_temp

    @property
    def external_lighting_on(self) -> bool:
        return self._state.lighting % 2 == 1

    @property
    def internal_lighting_on(self) -> bool:
        return self._state.lighting % 2 == 0 and self._state.lighting != 0

    @property
    def rgb_on(self) -> bool:
        return self._state.rgb != 6

    @property
    def lighting_on(self) -> bool:
        return self.external_lighting_on or self.internal_lighting_on or self.rgb_on

    @property
    def fm_frequency(self) -> float:
        return self._state.fm_frequency / 100.0

    @property
    def power_on(self) -> bool:
        return self._state.power_on

    @property
    def heating_on(self) -> bool:
        return self._state.heating_on == 1

    @property
    def remaining_time(self) -> int:
        return self._state.remaining_time

    @property
    def unit_is_celsius(self) -> bool:
        return self._state.unit_is_celsius
