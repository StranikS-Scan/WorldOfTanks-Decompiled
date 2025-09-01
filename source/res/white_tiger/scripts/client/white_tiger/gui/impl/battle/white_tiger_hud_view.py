# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: white_tiger/scripts/client/white_tiger/gui/impl/battle/white_tiger_hud_view.py
import logging
from frameworks.wulf import ViewFlags, ViewSettings
from frameworks.wulf import Array
from gui.impl.gen import R
from gui.impl.pub import ViewImpl
from helpers import i18n, dependency
from gui.impl import backport
from gui.battle_control import avatar_getter
from gui.battle_control.arena_info import player_format
from skeletons.gui.battle_session import IBattleSessionProvider
from skeletons.account_helpers.settings_core import ISettingsCore
from gui.battle_control.arena_info.interfaces import IArenaVehiclesController
from skeletons.gui.game_control import IAnonymizerController
from white_tiger.gui.impl.gen.view_models.views.battle.white_tiger_hud_view_model import WhiteTigerHudViewModel
from white_tiger_common.wt_constants import WT_VEHICLE_TAGS
from account_helpers.settings_core.settings_constants import GRAPHICS
from white_tiger.gui.impl.gen.view_models.views.battle.generator_status_model import GeneratorStatusModel, GeneratorStatusEnum
from white_tiger.cgf_components.wt_helpers import getBattleStateComponent
_logger = logging.getLogger(__name__)
_GENERATOR_ID_LABEL_MAP = {1: 'A',
 2: 'B',
 3: 'C'}

class WhiteTigerHudView(ViewImpl, IArenaVehiclesController):
    __slots__ = ('_generatorModels',)
    __sessionProvider = dependency.descriptor(IBattleSessionProvider)
    __settingsCore = dependency.descriptor(ISettingsCore)
    __anonymizerController = dependency.descriptor(IAnonymizerController)

    def __init__(self):
        settings = ViewSettings(R.views.white_tiger.battle.WhiteTigerHudView(), ViewFlags.VIEW, WhiteTigerHudViewModel())
        super(WhiteTigerHudView, self).__init__(settings)
        self._generatorModels = {}
        with self.viewModel.transaction() as model:
            _modelsArray = Array()
            for k in _GENERATOR_ID_LABEL_MAP:
                generator = GeneratorStatusModel()
                generator.setName(_GENERATOR_ID_LABEL_MAP[k])
                generator.setGeneratorStatus(GeneratorStatusEnum.ACTIVE)
                generator.setProgress(0.0)
                self._generatorModels[k] = generator
                _modelsArray.addViewModel(generator)

            model.setGenerators(_modelsArray)

    @property
    def viewModel(self):
        return super(WhiteTigerHudView, self).getViewModel()

    def addVehicleInfo(self, vInfo, _):
        if WT_VEHICLE_TAGS.MINIBOSS in vInfo.vehicleType.tags:
            self.__setupMiniBossInfo(vInfo)
        if WT_VEHICLE_TAGS.BOSS in vInfo.vehicleType.tags:
            self.__setupBoss(vInfo)

    def updateVehiclesStats(self, updated, arenaDP):
        for _, vStatsVO in updated:
            vInfo = arenaDP.getVehicleInfo(vStatsVO.vehicleID)
            if WT_VEHICLE_TAGS.BOSS in vInfo.vehicleType.tags:
                self.__updateBossKills(vInfo)

    def _initialize(self, *args, **kwargs):
        super(WhiteTigerHudView, self)._initialize(*args, **kwargs)
        self.__sessionProvider.addArenaCtrl(self)

    def _onLoaded(self, *args, **kwargs):
        super(WhiteTigerHudView, self)._onLoaded(*args, **kwargs)
        arenaDP = self.__sessionProvider.getArenaDP()
        for vInfo in arenaDP.getVehiclesInfoIterator():
            if WT_VEHICLE_TAGS.BOSS in vInfo.vehicleType.tags:
                self.__setupBoss(vInfo)
            if WT_VEHICLE_TAGS.MINIBOSS in vInfo.vehicleType.tags:
                self.__setupMiniBossInfo(vInfo)

        with self.viewModel.transaction() as model:
            model.setIsColorblind(self.__settingsCore.getSetting(GRAPHICS.COLOR_BLIND))
            model.setIsEndgame(False)

    def _subscribe(self):
        super(WhiteTigerHudView, self)._subscribe()
        battleStateComponent = getBattleStateComponent()
        if battleStateComponent:
            battleStateComponent.onPublicHealthChange += self.__onPublicHealthChange
            battleStateComponent.onHyperionCharge += self.__onHyperionCharge
            battleStateComponent.onShieldStatusChange += self.__onShieldStatusChange
            battleStateComponent.onGeneratorsLeftInitialize += self.__onGeneratorDestroyed
            battleStateComponent.onGeneratorDestroyed += self.__onGeneratorDestroyed
            battleStateComponent.onShieldDowntime += self.__onShieldDowntime
            battleStateComponent.onGeneratorCapture += self.__onGeneratorCapture
            battleStateComponent.onGeneratorStopCapture += self.__onGeneratorStopCapture
            battleStateComponent.onGeneratorLocked += self.__onGeneratorLocked
        self.__settingsCore.onSettingsChanged += self.__onSettingsChanged

    def _unsubscribe(self):
        super(WhiteTigerHudView, self)._unsubscribe()
        self.__settingsCore.onSettingsChanged -= self.__onSettingsChanged

    def __setupBoss(self, vInfo):
        with self.viewModel.transaction() as model:
            playerData = player_format.PlayerFullNameFormatter().format(vInfo)
            model.boss.setName(playerData.playerName)
            model.boss.setClan(playerData.clanAbbrev)
            model.setIsSpecialBoss(WT_VEHICLE_TAGS.PRIORITY_BOSS in vInfo.vehicleType.tags)
            model.setIsAlly(avatar_getter.getPlayerVehicleID() == vInfo.vehicleID)
            model.boss.setKills(self.__getKills(vInfo))
            model.boss.setCurrentHP(vInfo.vehicleType.maxHealth)
            model.boss.setMaxHP(vInfo.vehicleType.maxHealth)
            model.boss.setIsAnonymized(self.__anonymizerController.isAnonymized)

    def __setupMiniBossInfo(self, vInfo):
        with self.viewModel.transaction() as model:
            botName = i18n.makeString(backport.text(R.strings.white_tiger_battle.botNames.Ermelinda()))
            model.miniboss.setName(botName)
            model.setIsMinibossActive(True)
            model.miniboss.setMaxHP(vInfo.vehicleType.maxHealth)
            model.miniboss.setCurrentHP(vInfo.vehicleType.maxHealth)

    def __onPublicHealthChange(self, vehicleID, newHealth):
        arenaDP = self.__sessionProvider.getArenaDP()
        vInfoVO = arenaDP.getVehicleInfo(vehicleID)
        with self.viewModel.transaction() as model:
            if WT_VEHICLE_TAGS.BOSS in vInfoVO.vehicleType.tags:
                model.boss.setCurrentHP(newHealth)
            elif WT_VEHICLE_TAGS.MINIBOSS in vInfoVO.vehicleType.tags:
                model.miniboss.setCurrentHP(newHealth)

    def __updateBossKills(self, vInfo):
        with self.viewModel.transaction() as model:
            model.boss.setKills(self.__getKills(vInfo))

    def __getKills(self, vInfo):
        arenaDP = self.__sessionProvider.getArenaDP()
        vStats = arenaDP.getVehicleStats(vInfo.vehicleID)
        frags = vStats.frags if vStats is not None else 0
        return frags

    def __onHyperionCharge(self, charge):
        with self.viewModel.transaction() as model:
            model.setHyperionCharge(charge)

    def __onSettingsChanged(self, diff):
        if GRAPHICS.COLOR_BLIND in diff:
            with self.viewModel.transaction() as model:
                model.setIsColorblind(diff[GRAPHICS.COLOR_BLIND])

    def __onShieldStatusChange(self, isShieldDown):
        with self.viewModel.transaction() as model:
            model.setIsShieldDown(isShieldDown)

    def __onGeneratorDestroyed(self, generatorsLeft):
        if generatorsLeft == 0:
            with self.viewModel.transaction() as model:
                model.setIsEndgame(True)

    def __onShieldDowntime(self, totalTime, remainingTime):
        with self.viewModel.transaction() as model:
            model.setShieldCooldownSeconds(remainingTime)

    def __onGeneratorCapture(self, generatorID, progress, timeLeft, numInvaders, isLocked):
        if generatorID not in self._generatorModels:
            _logger.error('ID does not exist')
            return
        self._generatorModels[generatorID].setProgress(progress)

    def __onGeneratorStopCapture(self, generatorID, wasCaptured):
        if generatorID not in self._generatorModels:
            _logger.error('ID does not exist')
            return
        self._generatorModels[generatorID].setProgress(0.0)

    def __onGeneratorLocked(self, generatorID, locked, _, __, ___):
        if generatorID not in self._generatorModels:
            _logger.error('ID does not exist')
            return
        if locked:
            self._generatorModels[generatorID].setGeneratorStatus(GeneratorStatusEnum.LOCKED)
        else:
            self._generatorModels[generatorID].setGeneratorStatus(GeneratorStatusEnum.ACTIVE)
