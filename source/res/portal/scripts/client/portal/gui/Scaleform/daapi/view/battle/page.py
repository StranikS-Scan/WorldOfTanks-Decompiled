# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: portal/scripts/client/portal/gui/Scaleform/daapi/view/battle/page.py
import BigWorld
from debug_utils import LOG_DEBUG
from aih_constants import CTRL_MODE_NAME
from gui.battle_control.battle_constants import BATTLE_CTRL_ID
from gui.Scaleform.daapi.view.battle.classic.page import ClassicPage, COMMON_CLASSIC_CONFIG, EXTENDED_CLASSIC_CONFIG
from gui.Scaleform.daapi.view.battle.shared.crosshair import CrosshairPanelContainer
from gui.Scaleform.daapi.view.battle.shared.indicators import createPredictionIndicator
from gui.Scaleform.daapi.view.battle.shared.page import ComponentsConfig
from gui.Scaleform.genConsts.BATTLE_VIEW_ALIASES import BATTLE_VIEW_ALIASES
from PortalBattleStateComponent import PortalBattleStateComponent
from portal_common.portal_constants import BattleState
from portal.gui.Scaleform.daapi.view.battle.indicators import createPortalBattlesDamageIndicator
from portal.gui.Scaleform.daapi.view.battle.portal_markers_manager import PortalMarkersManager
from portal.gui.Scaleform.genConsts.PORTAL_BATTLE_VIEW_ALIASES import PORTAL_BATTLE_VIEW_ALIASES
from portal.sounds.sound_constants import PortalMusicState, PortalBattleUISound
from portal.sounds.sound_helpers import play2DSound
_PORTAL_COMPONENTS_CONFIG = ComponentsConfig(config=((BATTLE_CTRL_ID.HIT_DIRECTION, (BATTLE_VIEW_ALIASES.PREDICTION_INDICATOR, BATTLE_VIEW_ALIASES.HIT_DIRECTION)), (BATTLE_CTRL_ID.BATTLE_FIELD_CTRL, (PORTAL_BATTLE_VIEW_ALIASES.PLAYERS_DATA_PANEL,)), (BATTLE_CTRL_ID.BATTLE_HINTS, (BATTLE_VIEW_ALIASES.BATTLE_HINT,))), viewsConfig=((BATTLE_VIEW_ALIASES.PREDICTION_INDICATOR, createPredictionIndicator), (BATTLE_VIEW_ALIASES.HIT_DIRECTION, createPortalBattlesDamageIndicator)))
_EXTERNAL_COMPONENTS = (CrosshairPanelContainer, PortalMarkersManager)

class PortalBattlePage(ClassicPage):
    __POSTMORTEM_TOGGLEABLE_COMPONENTS = {'ribbonsPanel',
     'statusNotificationsPanel',
     'battleVehicleErrorMessages',
     'battleVehicleMessages'}

    def __init__(self, components=None, external=_EXTERNAL_COMPONENTS, fullStatsAlias=BATTLE_VIEW_ALIASES.FULL_STATS):
        if components is None:
            components = COMMON_CLASSIC_CONFIG if self.sessionProvider.isReplayPlaying else EXTENDED_CLASSIC_CONFIG
        components = self.__filterComponents(components + _PORTAL_COMPONENTS_CONFIG)
        super(PortalBattlePage, self).__init__(components=components, external=external, fullStatsAlias=fullStatsAlias)
        return

    @property
    def battleState(self):
        arenaInfo = BigWorld.player().arena.arenaInfo
        return arenaInfo.portalBattleStateComponent

    def _populate(self):
        super(PortalBattlePage, self)._populate()
        LOG_DEBUG('Portal battle page is created.')

    def _dispose(self):
        super(PortalBattlePage, self)._dispose()
        play2DSound(PortalBattleUISound.GAMEPLAY_EXIT)
        LOG_DEBUG('Portal battle page is destroyed.')

    def _onBattleLoadingStart(self):
        LOG_DEBUG('PortalBattlePage._onBattleLoadingStart')
        if not self.sessionProvider.isReplayPlaying:
            self._blToggling = set(self.as_getComponentsVisibilityS())
            self._blToggling.difference_update([BATTLE_VIEW_ALIASES.BATTLE_LOADING])
            self._setComponentsVisibility(visible={BATTLE_VIEW_ALIASES.BATTLE_LOADING}, hidden=self._blToggling)
            PortalMusicState.setState(PortalMusicState.LOADING)
        super(PortalBattlePage, self)._onBattleLoadingStart()

    def _onBattleLoadingFinish(self):
        if not self.sessionProvider.isReplayPlaying:
            play2DSound(PortalBattleUISound.GAMEPLAY_ENTER)
            self._blToggling.remove(BATTLE_VIEW_ALIASES.FULL_STATS)
        super(PortalBattlePage, self)._onBattleLoadingFinish()

    def _startBattleSession(self):
        super(PortalBattlePage, self)._startBattleSession()
        vehicleChangeComponent = getattr(BigWorld.player(), 'DynamicVehicleChangeComponent', None)
        if vehicleChangeComponent:
            vehicleChangeComponent.onStartVehicleControl += self.__onStartVehicleControl
            vehicleChangeComponent.onStopVehicleControl += self.__onStopVehicleControl
        PortalBattleStateComponent.onBattleStateChanged += self.__onBattleStateChanged
        PortalBattleStateComponent.onWaveStarted += self.__onWaveStarted
        return

    def _stopBattleSession(self):
        PortalBattleStateComponent.onLaneInfoChanged -= self.__onLastWaveLaneInfoChanged
        PortalBattleStateComponent.onWaveStarted -= self.__onWaveStarted
        PortalBattleStateComponent.onBattleStateChanged -= self.__onBattleStateChanged
        vehicleChangeComponent = getattr(BigWorld.player(), 'DynamicVehicleChangeComponent', None)
        if vehicleChangeComponent:
            vehicleChangeComponent.onStartVehicleControl -= self.__onStartVehicleControl
            vehicleChangeComponent.onStopVehicleControl -= self.__onStopVehicleControl
        super(PortalBattlePage, self)._stopBattleSession()
        return

    def _changeCtrlMode(self, ctrlMode):
        super(PortalBattlePage, self)._changeCtrlMode(ctrlMode)
        atgmToggleableComponents = {'playersDataPanel',
         'damagePanel',
         'minimap',
         'battleHint',
         'gameMessagesPanel',
         'battleMessenger',
         'consumablesPanel',
         'battleTimer',
         'battleEndWarningPanel',
         'perksPanel',
         'battleDamageLogPanel',
         'battleVehicleMessages',
         'statusNotificationsPanel',
         'battleVehicleErrorMessages',
         'ribbonsPanel',
         'portalHudWidgetView',
         'damageInfoPanel',
         'battlePlayerMessages',
         'prebattleTimer',
         'debugPanel'}
        if self.battleState.battleState != BattleState.SUPER_BOSS_FIGHT:
            atgmToggleableComponents.add(PORTAL_BATTLE_VIEW_ALIASES.ENEMIES_DATA_PANEL)
        if ctrlMode == CTRL_MODE_NAME.ATGM:
            self._setComponentsVisibility(visible={PORTAL_BATTLE_VIEW_ALIASES.GUIDED_MISSILE_WIDGET}, hidden=atgmToggleableComponents)
        elif self.as_isComponentVisibleS(PORTAL_BATTLE_VIEW_ALIASES.GUIDED_MISSILE_WIDGET):
            self._setComponentsVisibility(visible=atgmToggleableComponents, hidden={PORTAL_BATTLE_VIEW_ALIASES.GUIDED_MISSILE_WIDGET})
        if ctrlMode == CTRL_MODE_NAME.POSTMORTEM:
            self._setComponentsVisibility(hidden=self.__POSTMORTEM_TOGGLEABLE_COMPONENTS)
        else:
            self._setComponentsVisibility(visible=self.__POSTMORTEM_TOGGLEABLE_COMPONENTS)

    def __onStartVehicleControl(self, vehicleID):
        self._setComponentsVisibility(hidden={BATTLE_VIEW_ALIASES.CONSUMABLES_PANEL}, visible={PORTAL_BATTLE_VIEW_ALIASES.INTERCEPTION_WIDGET})

    def __onStopVehicleControl(self, isInterrupted):
        self._setComponentsVisibility(hidden={PORTAL_BATTLE_VIEW_ALIASES.INTERCEPTION_WIDGET}, visible={BATTLE_VIEW_ALIASES.CONSUMABLES_PANEL})

    def __onBattleStateChanged(self, battleState):
        if battleState == BattleState.NORMAL or battleState == BattleState.BOSS_FIGHT:
            shouldShow = not self.battleState.areWavesEnded()
            if shouldShow and not self.as_isComponentVisibleS(PORTAL_BATTLE_VIEW_ALIASES.ENEMIES_DATA_PANEL):
                self._setComponentsVisibility(visible={PORTAL_BATTLE_VIEW_ALIASES.ENEMIES_DATA_PANEL})
        elif battleState == BattleState.SUPER_BOSS_FIGHT:
            self._setComponentsVisibility(hidden={PORTAL_BATTLE_VIEW_ALIASES.ENEMIES_DATA_PANEL})

    def __onWaveStarted(self, currentWave, wavesCount):
        if currentWave == wavesCount:
            PortalBattleStateComponent.onLaneInfoChanged += self.__onLastWaveLaneInfoChanged

    def __onLastWaveLaneInfoChanged(self, laneID, laneInfo):
        areWavesEnded = self.battleState.areWavesEnded()
        isEnemiesPanelVisible = self.as_isComponentVisibleS(PORTAL_BATTLE_VIEW_ALIASES.ENEMIES_DATA_PANEL)
        if areWavesEnded and isEnemiesPanelVisible:
            self._setComponentsVisibility(hidden={PORTAL_BATTLE_VIEW_ALIASES.ENEMIES_DATA_PANEL})
        elif not areWavesEnded and not isEnemiesPanelVisible:
            self._setComponentsVisibility(visible={PORTAL_BATTLE_VIEW_ALIASES.ENEMIES_DATA_PANEL})

    @staticmethod
    def __filterComponents(components):
        disabledViewsByCtrlID = {BATTLE_CTRL_ID.BATTLE_FIELD_CTRL: [BATTLE_VIEW_ALIASES.PLAYERS_PANEL, BATTLE_VIEW_ALIASES.FRAG_CORRELATION_BAR],
         BATTLE_CTRL_ID.ARENA_PERIOD: [BATTLE_VIEW_ALIASES.PLAYERS_PANEL]}
        newConfig = []
        for ctrlID, views in components.getConfig():
            filteredViews = views
            disabledViews = disabledViewsByCtrlID.get(ctrlID)
            if disabledViews:
                filteredViews = tuple([ view for view in views if view not in disabledViews ])
            newConfig.append((ctrlID, filteredViews))

        return ComponentsConfig(tuple(newConfig), components.getViewsConfig())

    def _onPostMortemSwitched(self, noRespawnPossible, respawnAvailable):
        super(PortalBattlePage, self)._onPostMortemSwitched(noRespawnPossible, respawnAvailable)
        self.as_setPostmortemTipsVisibleS(True)

    def _onRespawnBaseMoving(self):
        super(PortalBattlePage, self)._onRespawnBaseMoving()
        self.as_setPostmortemTipsVisibleS(False)
