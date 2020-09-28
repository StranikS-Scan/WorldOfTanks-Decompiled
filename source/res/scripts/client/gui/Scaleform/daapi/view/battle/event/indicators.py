# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/battle/event/indicators.py
from account_helpers.settings_core.settings_constants import GRAPHICS
from gui.Scaleform.daapi.view.battle.shared.indicators import DamageIndicator, DAMAGE_INDICATOR_TYPE, StandardMarkerVOBuilder, AbstractMarkerVOBuilderFactory
from gui.battle_control import avatar_getter
from gui.battle_control.battle_constants import HIT_INDICATOR_MAX_ON_SCREEN
from gui.wt_event.wt_event_helpers import getHunterDescr, LOWER_LIMIT_OF_MEDIUM_LVL, LOWER_LIMIT_OF_HIGH_LVL
from helpers import dependency
from skeletons.gui.battle_session import IBattleSessionProvider
_LOW_LEVEL_POSTFIX = ':low'
_MEDIUM_LEVEL_POSTFIX = ':medium'
_HIGH_LEVEL_POSTFIX = ':high'

def _getMarkerTypePostfix(powerPoints):
    if powerPoints < LOWER_LIMIT_OF_MEDIUM_LVL:
        return _LOW_LEVEL_POSTFIX
    return _MEDIUM_LEVEL_POSTFIX if powerPoints < LOWER_LIMIT_OF_HIGH_LVL else _HIGH_LEVEL_POSTFIX


class _WTStandardMarkerVOBuilder(StandardMarkerVOBuilder):
    sessionProvider = dependency.descriptor(IBattleSessionProvider)

    def _getBackground(self, markerData):
        bgStr = super(_WTStandardMarkerVOBuilder, self)._getBackground(markerData)
        if self.sessionProvider.dynamic.arenaInfo is not None:
            powerPoints = self.sessionProvider.dynamic.arenaInfo.powerPoints
            return bgStr + _getMarkerTypePostfix(powerPoints)
        else:
            return bgStr


class _WTStandardMarkerVOBuilderFactory(AbstractMarkerVOBuilderFactory):

    def getVOBuilder(self, markerData):
        return _WTStandardMarkerVOBuilder()


def createDamageIndicator():
    return WTDamageIndicator(HIT_INDICATOR_MAX_ON_SCREEN)


class WTDamageIndicator(DamageIndicator):

    def invalidateSettings(self):
        getter = self.settingsCore.getSetting
        self._isBlind = bool(getter(GRAPHICS.COLOR_BLIND))
        info = self.sessionProvider.getCtx().getVehicleInfo(avatar_getter.getPlayerVehicleID())
        isHunter = getHunterDescr() == info.vehicleType.compactDescr
        if isHunter:
            self.__setHunterSettings()
        else:
            self.__setBossSettings()

    def _setUpVOBuilderFactoryAndUpdateMethod(self, indicatorType):
        if indicatorType == DAMAGE_INDICATOR_TYPE.STANDARD:
            self._voBuilderFactory = _WTStandardMarkerVOBuilderFactory()
            self._updateMethod = self.as_showStandardS
        else:
            super(WTDamageIndicator, self)._setUpVOBuilderFactoryAndUpdateMethod(indicatorType)

    def __setHunterSettings(self):
        self._setUpVOBuilderFactoryAndUpdateMethod(DAMAGE_INDICATOR_TYPE.EXTENDED)
        self.as_updateSettingsS(isStandard=False, isWithTankInfo=True, isWithAnimation=True, isWithValue=True)

    def __setBossSettings(self):
        self._setUpVOBuilderFactoryAndUpdateMethod(DAMAGE_INDICATOR_TYPE.STANDARD)
        self.as_updateSettingsS(isStandard=True, isWithTankInfo=False, isWithAnimation=False, isWithValue=False)
