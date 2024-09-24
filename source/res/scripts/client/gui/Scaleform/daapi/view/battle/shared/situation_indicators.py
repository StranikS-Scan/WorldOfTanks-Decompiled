# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/battle/shared/situation_indicators.py
import BigWorld
import WWISE
from gui.Scaleform.daapi.view.meta.SituationIndicatorsMeta import SituationIndicatorsMeta
from gui.battle_control.battle_constants import VEHICLE_VIEW_STATE, VEHICLE_VIEW_STATE_ID_TO_WEATHER_ZONE_NAME
from gui.impl import backport
from gui.impl.gen import R
from gui.shared.utils.functions import makeTooltip
from helpers import dependency
from items import tankmen
from items.components.perks_constants import PerkState
from shared_utils import CONST_CONTAINER
from skeletons.gui.battle_session import IBattleSessionProvider
from ReplayEvents import g_replayEvents

class PerksSounds(CONST_CONTAINER):
    PERK = 'detachment_perk'
    PERK_STOP = 'detachment_perk_stop'


class WeatherState(object):
    INACTIVE = 0
    ACTIVE = 1


def _getTooltip(weatherName):
    toolTipRes = R.strings.tooltips.weather.dyn(weatherName)
    toolTipStr = makeTooltip(header=backport.text(toolTipRes.header()), body=backport.text(toolTipRes.body()))
    return toolTipStr


class SituationIndicators(SituationIndicatorsMeta):
    sessionProvider = dependency.descriptor(IBattleSessionProvider)

    def setPerks(self, perks):
        self.clearHUD()
        perksData = []
        for perkData in sorted(perks, key=lambda k: k['perkID']):
            perkID = perkData['perkID']
            skillName = tankmen.getSkillsConfig().vsePerkToSkill.get(perkID)
            perk = {'perkName': skillName,
             'state': perkData['state'],
             'duration': perkData['coolDown'],
             'lifeTime': self._getLifeTime(perkData)}
            perksData.append(perk)

        self.as_setPerksS(perksData)

    def updatePerks(self, changedPerks, prevPerks):
        for perkID, perkData in changedPerks.iteritems():
            lifeTime = self._getLifeTime(perkData)
            state = perkData['state']
            skillName = tankmen.getSkillsConfig().vsePerkToSkill.get(perkID)
            self.as_updatePerkS(skillName, state, perkData['coolDown'], lifeTime)
            if state == PerkState.ACTIVE:
                if perkID not in prevPerks or prevPerks[perkID]['state'] != PerkState.ACTIVE:
                    WWISE.WW_eventGlobal(PerksSounds.PERK)
            if perkID in prevPerks and prevPerks[perkID]['state'] == PerkState.ACTIVE:
                WWISE.WW_eventGlobal(PerksSounds.PERK_STOP)

    def clearHUD(self):
        self.as_clearPanelS()

    def _populate(self):
        super(SituationIndicators, self)._populate()
        vStateCtrl = self.sessionProvider.shared.vehicleState
        if vStateCtrl is not None:
            vStateCtrl.onVehicleStateUpdated += self.__onVehicleStateUpdated
            vStateCtrl.onVehicleControlling += self.__onVehicleControlling
        g_replayEvents.onPause += self._onReplayPaused
        return

    def _dispose(self):
        g_replayEvents.onPause -= self._onReplayPaused
        super(SituationIndicators, self)._dispose()

    def _destroy(self):
        vStateCtrl = self.sessionProvider.shared.vehicleState
        if vStateCtrl is not None:
            vStateCtrl.onVehicleStateUpdated -= self.__onVehicleStateUpdated
            vStateCtrl.onVehicleControlling -= self.__onVehicleControlling
        super(SituationIndicators, self)._destroy()
        return

    def _getLifeTime(self, perkData):
        lifeTimeServer = perkData['lifeTime']
        return lifeTimeServer - BigWorld.serverTime() if BigWorld.serverTime() < lifeTimeServer else -1

    def __onVehicleStateUpdated(self, state, value):
        if state in VEHICLE_VIEW_STATE.WEATHER_ZONES:
            weatherName = VEHICLE_VIEW_STATE_ID_TO_WEATHER_ZONE_NAME[state]
            self.as_updateWeatherS(weatherName, WeatherState.ACTIVE if not value.needToCloseTimer() else WeatherState.INACTIVE, _getTooltip(weatherName))

    def __onVehicleControlling(self, _):
        ctrl = self.sessionProvider.shared.vehicleState
        if ctrl is None:
            return
        else:
            weatherItemsToSet = []
            for state in VEHICLE_VIEW_STATE.WEATHER_ZONES:
                value = ctrl.getStateValue(state)
                weatherName = VEHICLE_VIEW_STATE_ID_TO_WEATHER_ZONE_NAME[state]
                weatherItemsToSet.append({'weatherName': weatherName,
                 'state': WeatherState.ACTIVE if value is not None and not value.needToCloseTimer() else WeatherState.INACTIVE,
                 'toolTip': _getTooltip(weatherName)})

            self.as_setWeatherS(weatherItemsToSet)
            return

    def _onReplayPaused(self, isPaused):
        self.as_replayPauseS(isPaused)
