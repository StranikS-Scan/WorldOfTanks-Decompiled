# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/battle_control/controllers/hit_direction_ctrl/components.py
import weakref
import typing
from account_helpers.settings_core.settings_constants import DAMAGE_INDICATOR, GRAPHICS
if typing.TYPE_CHECKING:
    from gui.battle_control.controllers.hit_direction_ctrl.base import IHitIndicator
    from gui.battle_control.controllers.hit_direction_ctrl.pulls import BaseHitPull
_VISUAL_DAMAGE_INDICATOR_SETTINGS = (DAMAGE_INDICATOR.TYPE,
 DAMAGE_INDICATOR.VEHICLE_INFO,
 DAMAGE_INDICATOR.DAMAGE_VALUE,
 DAMAGE_INDICATOR.ANIMATION,
 GRAPHICS.COLOR_BLIND,
 DAMAGE_INDICATOR.DYNAMIC_INDICATOR,
 DAMAGE_INDICATOR.PRESET_CRITS,
 DAMAGE_INDICATOR.PRESET_ALLIES)

class BaseHitComponent(object):

    def __init__(self, pull):
        self._pull = pull
        self._ui = None
        return

    @property
    def ui(self):
        return self._ui

    @property
    def pull(self):
        return self._pull

    def setVisible(self, isVisible):
        if self._ui:
            self._ui.setVisible(isVisible)

    def setUI(self, ui, isVisible):
        self._ui = ui
        self._ui.invalidateSettings()
        self._ui.setVisible(isVisible)
        proxy = weakref.proxy(self._ui)
        self._pull.setIndicator(proxy)

    def clear(self):
        self._pull.clear()
        if self._ui:
            self._ui.destroy()
        self._ui = None
        return

    def invalidateSettings(self, diff):
        self._pull.invalidateSettings(diff)


class HitDamageComponent(BaseHitComponent):

    def invalidateSettings(self, diff):
        super(HitDamageComponent, self).invalidateSettings(diff)
        if not self._ui:
            return
        for key in _VISUAL_DAMAGE_INDICATOR_SETTINGS:
            if key in diff:
                self._ui.invalidateSettings()
                self._pull.redraw()
                break
