# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: fall_tanks/scripts/client/fall_tanks/gui/Scaleform/daapi/view/battle/page/view.py
import typing
from gui.battle_control.battle_constants import BATTLE_CTRL_ID
from gui.Scaleform.daapi.view.battle.shared import SharedPage
from gui.Scaleform.daapi.view.battle.shared.indicators import createPredictionIndicator
from gui.Scaleform.daapi.view.battle.shared.page import ComponentsConfig
from gui.Scaleform.daapi.view.battle.shared.start_countdown_sound_player import StartCountdownSoundPlayer
from gui.Scaleform.genConsts.BATTLE_VIEW_ALIASES import BATTLE_VIEW_ALIASES
from shared_utils import CONST_CONTAINER
from fall_tanks.gui.battle_control.mixins import FallTanksBattleMixin
from fall_tanks.gui.Scaleform.daapi.view.battle import crosshair
from fall_tanks.gui.Scaleform.daapi.view.battle import indicators
from fall_tanks.gui.Scaleform.daapi.view.battle import markers2d
from fall_tanks.gui.Scaleform.daapi.view.battle.page.manager import FallTanksComponentsManager
if typing.TYPE_CHECKING:
    from fall_tanks.gui.battle_control.arena_info.interfaces import IFallTanksVehicleInfo

class DynamicAliases(CONST_CONTAINER):
    PREBATTLE_TIMER_SOUND_PLAYER = 'prebattleTimerSoundPlayer'


class _FallTanksComponentsConfig(ComponentsConfig):

    def __init__(self):
        super(_FallTanksComponentsConfig, self).__init__(((BATTLE_CTRL_ID.ARENA_PERIOD, (BATTLE_VIEW_ALIASES.BATTLE_TIMER,
           BATTLE_VIEW_ALIASES.PREBATTLE_TIMER,
           DynamicAliases.PREBATTLE_TIMER_SOUND_PLAYER,
           BATTLE_VIEW_ALIASES.BATTLE_END_WARNING_PANEL,
           BATTLE_VIEW_ALIASES.HINT_PANEL)),
         (BATTLE_CTRL_ID.PERKS, (BATTLE_VIEW_ALIASES.SITUATION_INDICATORS,)),
         (BATTLE_CTRL_ID.MAPS, (BATTLE_VIEW_ALIASES.MINIMAP,)),
         (BATTLE_CTRL_ID.DEBUG, (BATTLE_VIEW_ALIASES.DEBUG_PANEL,)),
         (BATTLE_CTRL_ID.PREBATTLE_SETUPS_CTRL, (BATTLE_VIEW_ALIASES.DAMAGE_PANEL,)),
         (BATTLE_CTRL_ID.AMMO, (BATTLE_VIEW_ALIASES.CONSUMABLES_PANEL,)),
         (BATTLE_CTRL_ID.HIT_DIRECTION, (BATTLE_VIEW_ALIASES.HIT_DIRECTION, BATTLE_VIEW_ALIASES.PREDICTION_INDICATOR))), viewsConfig=((BATTLE_VIEW_ALIASES.HIT_DIRECTION, indicators.createFallTanksDamageIndicator), (BATTLE_VIEW_ALIASES.PREDICTION_INDICATOR, createPredictionIndicator), (DynamicAliases.PREBATTLE_TIMER_SOUND_PLAYER, StartCountdownSoundPlayer)))


_FALL_TANKS_COMPONENTS_CONFIG = _FallTanksComponentsConfig()

class FallTanksPage(SharedPage, FallTanksBattleMixin):

    def __init__(self):
        super(FallTanksPage, self).__init__(components=_FALL_TANKS_COMPONENTS_CONFIG, external=(crosshair.FallTanksCrosshairPanelContainer, markers2d.FallTanksMarkersManager))
        self.__visibilityManager = FallTanksComponentsManager(self)

    def setComponentsVisibility(self, visible=None, hidden=None):
        self._setComponentsVisibility(visible=visible, hidden=hidden)

    def _dispose(self):
        self.__visibilityManager.destroy()
        super(FallTanksPage, self)._dispose()

    def _startBattleSession(self):
        super(FallTanksPage, self)._startBattleSession()
        self.startFallTanksAttachedListening(self.__onFallTanksAttachedInfoUpdate)
        self.__onFallTanksAttachedInfoUpdate()

    def _stopBattleSession(self):
        self.__visibilityManager.clear()
        self.stopFallTanksAttachedListening(self.__onFallTanksAttachedInfoUpdate)
        super(FallTanksPage, self)._stopBattleSession()

    def _onAvatarCtrlModeChanged(self, ctrlMode):
        pass

    def _onBattleLoadingFinish(self):
        super(FallTanksPage, self)._onBattleLoadingFinish()
        self.__visibilityManager.onBattleLoaded()

    def _onPostMortemReload(self):
        self.__setIsInPostmortem(False)

    def _onPostMortemSwitched(self, noRespawnPossible, respawnAvailable):
        self.__setIsInPostmortem(True)
        self.as_onPostmortemActiveS(True)

    def _onRespawnBaseMoving(self):
        self.as_onPostmortemActiveS(False)
        self.__setIsInPostmortem(False)

    def _handleGUIToggled(self, event):
        self._toggleGuiVisible()

    def _handleHelpEvent(self, event):
        pass

    def _handleRadialMenuCmd(self, event):
        pass

    def _handleToggleFullStats(self, event):
        pass

    def _handleToggleFullStatsQuestProgress(self, event):
        pass

    def _handleToggleFullStatsPersonalReserves(self, event):
        pass

    def _processCallout(self, needShow):
        pass

    def __setIsInPostmortem(self, isInPostmortem):
        self._isInPostmortem = isInPostmortem
        self.__visibilityManager.setIsInPostmortem(isInPostmortem)

    def __onFallTanksAttachedInfoUpdate(self, attachedInfo=None):
        attachedInfo = attachedInfo or self.getFallTanksAttachedVehicleInfo()
        self.__visibilityManager.onFallTanksAttachedInfoUpdate(attachedInfo)
