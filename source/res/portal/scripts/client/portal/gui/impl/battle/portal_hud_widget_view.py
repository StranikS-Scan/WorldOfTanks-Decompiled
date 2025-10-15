# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: portal/scripts/client/portal/gui/impl/battle/portal_hud_widget_view.py
from PortalBattleStateComponent import PortalBattleStateComponent
from constants import ARENA_PERIOD
from gui.impl.gen import R
from frameworks.wulf import ViewFlags, ViewSettings
from portal.gui.impl.gen.view_models.views.battle.portal_hud_widget_view_model import PortalHudWidgetViewModel, WidgetState
from portal.gui.impl.gen.view_models.views.battle.portal_widget_camp import PortalWidgetCamp, CampState
from portal_common.portal_constants import BattleState, PortalBossesID, PORTAL_GAME_PARAMS_KEY
from portal.gui.portal_gui_constants import CAMP_ORDER_INDEX
from gui.impl.pub import ViewImpl
import BigWorld
from helpers import dependency
import PlayerEvents
from skeletons.gui.lobby_context import ILobbyContext
from skeletons.gui.battle_session import IBattleSessionProvider

class PortalHudWidgetView(ViewImpl):
    __slots__ = ()
    __lobbyContext = dependency.descriptor(ILobbyContext)
    __sessionProvider = dependency.descriptor(IBattleSessionProvider)

    def __init__(self):
        settings = ViewSettings(R.views.portal.battle.PortalHudWidgetView())
        settings.flags = ViewFlags.VIEW
        settings.model = PortalHudWidgetViewModel()
        super(PortalHudWidgetView, self).__init__(settings)

    @property
    def viewModel(self):
        return super(PortalHudWidgetView, self).getViewModel()

    @property
    def battleState(self):
        return BigWorld.player().arena.arenaInfo.portalBattleStateComponent

    def _onLoading(self, *args, **kwargs):
        super(PortalHudWidgetView, self)._onLoading(*args, **kwargs)
        self._updateModel()

    def _updateModel(self):
        with self.viewModel.transaction() as model:
            self.__fillState(model)
            self.__fillCamps(model)
            self.__fillBosses(model)

    def __fillState(self, model, period=None):
        widgetState = WidgetState.DEFAULT
        if not period:
            period = ARENA_PERIOD.BATTLE
        if period in (ARENA_PERIOD.PREBATTLE, ARENA_PERIOD.WAITING, ARENA_PERIOD.IDLE):
            widgetState = WidgetState.PREBATTLE
        if self.battleState.battleState == BattleState.SUPER_BOSS_FIGHT:
            widgetState = WidgetState.SUPERBOSSFIGHT
        if period == ARENA_PERIOD.AFTERBATTLE:
            widgetState = WidgetState.AFTERBATTLE
        model.setState(widgetState)

    def __getPortalConfig(self):
        return self.__lobbyContext.getServerSettings().getSettings()[PORTAL_GAME_PARAMS_KEY]

    def __fillCamps(self, model):
        array = model.camps
        array.clearItems()
        frontierInfos = self.__getPortalConfig()['scenario']['campsSettings']['frontiers']
        campsWithFrontiers = []
        for camp in self.battleState.campInfo:
            campFrontier = None
            for frontier, frontierInfo in frontierInfos.iteritems():
                if camp.campName in frontierInfo['camps']:
                    campFrontier = frontier
                    break

            campsWithFrontiers.append((campFrontier, camp))

        sortedData = sorted(campsWithFrontiers, key=lambda x: CAMP_ORDER_INDEX[x[0]])
        canBeCapturedCamps = 0
        capturedCamps = 0
        for _, camp in sortedData:
            campModel = PortalWidgetCamp()
            allDefenders = camp.allDefenders
            aliveDefenders = camp.aliveDefenders
            campModel.setAllDefenders(allDefenders)
            campModel.setKilledDefenders(aliveDefenders)
            campState = CampState.DEFAULT
            if aliveDefenders == 0:
                campState = CampState.CANBECAPTURED
                canBeCapturedCamps += 1
            if camp.status:
                campState = CampState.CAPTURED
                capturedCamps += 1
            campModel.setState(campState)
            array.addViewModel(campModel)

        array.invalidate()
        model.setCampsCount(len(self.battleState.campInfo))
        model.setCapturedCamps(capturedCamps)
        model.setCanBeCapturedCamps(canBeCapturedCamps)
        return

    def __fillBosses(self, model):
        bossesCount = len(self.battleState.bossInfo)
        if bossesCount == 2:
            self.__updateTwoBosses(model, self.battleState.bossInfo)
        elif bossesCount == 1:
            self.__updateSingleBoss(model, self.battleState.bossInfo)

    def __updateTwoBosses(self, model, bossInfo):
        prevSuperBossHealth = model.getSuperBossCurrentHealth()
        prevBossHealth = model.getBossCurrentHealth()
        superBoss = bossInfo[PortalBossesID.SUPER_BOSS_ID]
        boss = bossInfo[PortalBossesID.BOSS_ID]
        model.setSuperBossCurrentHealth(superBoss.currentHealth)
        model.setSuperBossMaxHealth(superBoss.maxHealth)
        model.setBossCurrentHealth(boss.currentHealth)
        model.setBossMaxHealth(boss.maxHealth)
        model.setSuperBossLastDamage(max(prevSuperBossHealth - superBoss.currentHealth, 0))
        model.setBossLastDamage(max(prevBossHealth - boss.currentHealth, 0))

    def __updateSingleBoss(self, model, bossInfo):
        prevHealth = model.getBossCurrentHealth()
        boss = bossInfo[PortalBossesID.BOSS_ID]
        model.setBossCurrentHealth(boss.currentHealth)
        model.setBossMaxHealth(boss.maxHealth)
        model.setBossLastDamage(max(prevHealth - boss.currentHealth, 0))

    def __onAllCampsInited(self, *args, **kwargs):
        with self.viewModel.transaction() as model:
            self.__fillCamps(model)
            self.__fillState(model)

    def __onCampUpdated(self, *args, **kwargs):
        with self.viewModel.transaction() as model:
            self.__fillCamps(model)

    def __onBattleStateChanged(self, *args, **kwargs):
        with self.viewModel.transaction() as model:
            self.__fillState(model)

    def __onBossInfoUpdated(self, *args, **kwargs):
        with self.viewModel.transaction() as model:
            self.__fillBosses(model)

    def __onArenaPeriodChange(self, period, periodEndTime, periodLength, periodAdditionalInfo):
        with self.viewModel.transaction() as model:
            if not self.__sessionProvider.isReplayPlaying:
                self.__fillState(model, period)

    def _getEvents(self):
        return ((PortalBattleStateComponent.onAllCampsInited, self.__onAllCampsInited),
         (PortalBattleStateComponent.onCampInfoUpdated, self.__onCampUpdated),
         (PortalBattleStateComponent.onAllBossesInited, self.__onBossInfoUpdated),
         (PortalBattleStateComponent.onBossInfoUpdated, self.__onBossInfoUpdated),
         (PortalBattleStateComponent.onBattleStateChanged, self.__onBattleStateChanged),
         (PlayerEvents.g_playerEvents.onArenaPeriodChange, self.__onArenaPeriodChange))
