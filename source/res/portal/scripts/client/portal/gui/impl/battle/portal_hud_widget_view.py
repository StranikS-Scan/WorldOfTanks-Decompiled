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
        vm = self.viewModel
        if vm is None or not vm.isBound():
            return
        else:
            with vm.transaction() as model:
                self.__fillState(model)
                self.__fillCamps(model)
                self.__fillBosses(model)
            return

    def __fillState(self, model):
        period = BigWorld.player().arena.period
        widgetState = WidgetState.DEFAULT
        if period in (ARENA_PERIOD.PREBATTLE, ARENA_PERIOD.WAITING, ARENA_PERIOD.IDLE):
            widgetState = WidgetState.PREBATTLE
        if self.battleState.battleState == BattleState.SUPER_BOSS_FIGHT and self.__isSuperBossPresent():
            widgetState = WidgetState.SUPERBOSSFIGHT
        if period == ARENA_PERIOD.AFTERBATTLE:
            widgetState = WidgetState.AFTERBATTLE
        model.setState(widgetState)

    def __isSuperBossPresent(self):
        return any((info.bossID == PortalBossesID.SUPER_BOSS_ID for info in self.battleState.bossInfo))

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

    def __fillVehicleNameAndTag(self, model, bossInfo):
        arenaDP = self.__sessionProvider.getArenaDP()
        if arenaDP is None:
            model.setVehicleName('')
            model.setVehicleClassTag('')
            return
        else:
            boss = bossInfo[PortalBossesID.BOSS_ID]
            vInfo = arenaDP.getVehicleInfo(boss.vehicleID)
            vType = vInfo.vehicleType
            if vType.classTag is None:
                return
            model.setVehicleName(vType.shortName)
            model.setVehicleClassTag(vType.classTag)
            return

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
        self.__fillVehicleNameAndTag(model, bossInfo)

    def __updateSingleBoss(self, model, bossInfo):
        prevHealth = model.getBossCurrentHealth()
        boss = bossInfo[PortalBossesID.BOSS_ID]
        model.setBossCurrentHealth(boss.currentHealth)
        model.setBossMaxHealth(boss.maxHealth)
        model.setBossLastDamage(max(prevHealth - boss.currentHealth, 0))
        self.__fillVehicleNameAndTag(model, bossInfo)

    def __onAllCampsInited(self, *args, **kwargs):
        vm = self.viewModel
        if vm is None or not vm.isBound():
            return
        else:
            with vm.transaction() as model:
                self.__fillCamps(model)
                self.__fillState(model)
            return

    def __onCampUpdated(self, *args, **kwargs):
        vm = self.viewModel
        if vm is None or not vm.isBound():
            return
        else:
            with vm.transaction() as model:
                self.__fillCamps(model)
            return

    def __onBattleStateChanged(self, *args, **kwargs):
        vm = self.viewModel
        if vm is None or not vm.isBound():
            return
        else:
            with vm.transaction() as model:
                self.__fillState(model)
            return

    def __onBossInfoUpdated(self, *args, **kwargs):
        vm = self.viewModel
        if vm is None or not vm.isBound():
            return
        else:
            with vm.transaction() as model:
                self.__fillBosses(model)
                self.__fillState(model)
            return

    def __onVehicleAdded(self, vehicleID):
        bossInfo = self.battleState.bossInfo
        if not bossInfo:
            return
        else:
            boss = bossInfo[PortalBossesID.BOSS_ID]
            if vehicleID != boss.vehicleID:
                return
            vm = self.viewModel
            if vm is None or not vm.isBound():
                return
            with vm.transaction() as model:
                self.__fillVehicleNameAndTag(model, bossInfo)
            return

    def __onArenaPeriodChange(self, period, periodEndTime, periodLength, periodAdditionalInfo):
        vm = self.viewModel
        if vm is None or not vm.isBound():
            return
        else:
            with vm.transaction() as model:
                if not self.__sessionProvider.isReplayPlaying:
                    self.__fillState(model)
            return

    def _getEvents(self):
        events = [(PortalBattleStateComponent.onAllCampsInited, self.__onAllCampsInited),
         (PortalBattleStateComponent.onCampInfoUpdated, self.__onCampUpdated),
         (PortalBattleStateComponent.onAllBossesInited, self.__onBossInfoUpdated),
         (PortalBattleStateComponent.onBossInfoUpdated, self.__onBossInfoUpdated),
         (PortalBattleStateComponent.onBattleStateChanged, self.__onBattleStateChanged),
         (PlayerEvents.g_playerEvents.onArenaPeriodChange, self.__onArenaPeriodChange)]
        player = BigWorld.player()
        if player is not None and player.arena is not None:
            events.append((player.arena.onVehicleAdded, self.__onVehicleAdded))
        return tuple(events)
