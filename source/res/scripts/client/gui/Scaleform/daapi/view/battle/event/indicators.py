# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/battle/event/indicators.py
from gui.Scaleform.daapi.view.battle.shared.indicators import _DamageIndicator, DAMAGE_INDICATOR_TYPE, DAMAGE_INDICATOR, GRAPHICS

class PveDamageIndicator(_DamageIndicator):

    def invalidateSettings(self):
        getter = self.settingsCore.getSetting
        self._isBlind = bool(getter(GRAPHICS.COLOR_BLIND))
        self._setUpVOBuilderFactoryAndUpdateMethod(indicatorType=DAMAGE_INDICATOR_TYPE.STANDARD)
        self.as_updateSettingsS(isStandard=True, isWithTankInfo=bool(getter(DAMAGE_INDICATOR.VEHICLE_INFO)), isWithAnimation=bool(getter(DAMAGE_INDICATOR.ANIMATION)), isWithValue=bool(getter(DAMAGE_INDICATOR.DAMAGE_VALUE)))
