# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: new_year/scripts/client/new_year/gui/impl/lobby/new_year/pet/ny_pet_indicators_block.py
import typing
import SoundGroups
from debug_utils import LOG_ERROR
from gui.impl.gui_decorators import args2params
from helpers import dependency
from helpers.time_utils import getCurrentTimestamp
from new_year.gui.impl.gen.view_models.views.lobby.new_year.views.pet.ny_indicator_type import IndicatorType
from new_year.gui.impl.gen.view_models.views.lobby.new_year.views.pet.ny_pet_item_leaderboard_point import NyPetItemLeaderboardPoint
from new_year.gui.impl.gen.view_models.views.lobby.new_year.views.pet.ny_pet_model import NyPetModel
from new_year.gui.impl.gen.view_models.views.lobby.new_year.views.pet.ny_pet_model import State
from new_year.gui.impl.lobby.new_year.ny_leaderboard_recount_view import NyLeaderboardRecountViewWindow
from new_year.gui.impl.lobby.new_year.sub_model_presenter import SubModelPresenter
from new_year.ny_constants import PERCENT
from new_year.skeletons.new_year import ITamagotchiDataProvider, INewYearController, IRaccoonAnimationController
from new_year.gui.impl.new_year.sounds import RaccoonMood
from skeletons.gui.shared import IItemsCache
if typing.TYPE_CHECKING:
    from new_year.tamagotchi.dto.player_info import PlayerInfo
    from new_year.gui.impl.gen.view_models.views.lobby.new_year.views.pet.ny_pet_indicator_model import NyPetIndicatorModel

class NyPetIndicatorsBlock(SubModelPresenter):
    __slots__ = ()
    _INTERNAL_VIEW_STATE = None
    _dataProvider = dependency.descriptor(ITamagotchiDataProvider)
    _itemsCache = dependency.descriptor(IItemsCache)
    _nyController = dependency.descriptor(INewYearController)
    _raccoonCtrl = dependency.descriptor(IRaccoonAnimationController)
    _MOOD_TO_SOUND = {State.FUN: RaccoonMood.FUN,
     State.NORMAL: RaccoonMood.NORMAL,
     State.SAD: RaccoonMood.SAD}

    @property
    def viewModel(self):
        return self.getViewModel()

    def initialize(self, *args, **kwargs):
        self.__buildCards()
        self.updateViewModel()
        super(NyPetIndicatorsBlock, self).initialize(*args, **kwargs)

    def finalize(self):
        super(NyPetIndicatorsBlock, self).finalize()
        self.__resetIndicators()
        self.clear()

    def updateViewModel(self):
        pInfo = self._dataProvider.playerInfo
        with self.viewModel.transaction() as model:
            self.__fillHeader(model, pInfo)
            self.__fillNeeds(model)
            for indicatorName, points in pInfo.indicators.iteritems():
                indicatorType = IndicatorType(indicatorName)
                vm = self.getIndicator(indicatorType, model)
                self.applyIndicatorData(indicatorName, vm, points)

    @staticmethod
    def getIndicator(indType, tx):
        if indType == IndicatorType.FOOD:
            return tx.foodIndicator
        elif indType == IndicatorType.FUN:
            return tx.funIndicator
        elif indType == IndicatorType.ACTIVITY:
            return tx.activityIndicator
        else:
            LOG_ERROR('invalid indicator type - ', indType.value)
            return None

    @classmethod
    def applyIndicatorData(cls, name, vm, points):
        pInfo = cls._dataProvider.playerInfo
        config = cls._dataProvider.config.indicators[name]
        giftsLeft = config.giftCountUnlock - pInfo.giftCollected
        vm.setMaxPoint(config.maxPoints)
        vm.setItemScalePoint(config.item.scalePoint)
        vm.setLettersToUnlock(max(0, giftsLeft))
        vm.setCurPoint(min(points, config.maxPoints))
        vm.setItemCount(cls._dataProvider.getIndicatorCurrency(name))
        vm.setBonus(cls._dataProvider.getIndicatorDeb(name))
        vm.setScaleDowngradeTime(cls._dataProvider.getIndicatorStateDecayTime(name))
        vm.setScaleEmptyTime(cls._dataProvider.getIndicatorDecayTime(name))
        vm.setIsLocked(giftsLeft > 0)
        levels = vm.getScaleLevels()
        levels.clear()
        for lvl in config.levels[1::]:
            levels.addNumber(lvl.points)

        levels.invalidate()
        return

    def _getEvents(self):
        return ((self.viewModel.onResetWasOverflowed, self.__onResetWasOverflowed),
         (self._itemsCache.onSyncCompleted, self.__onSyncCompleted),
         (self._dataProvider.onSimulationEnd, self.__onSimulationEnd),
         (self._dataProvider.onItemsActivateRequested, self.__onItemsActivateRequested),
         (self._dataProvider.onItemsActivated, self.__onItemsActivated),
         (self._dataProvider.onGiftCountUpdated, self.__onGiftCountUpdated))

    def __buildCards(self):
        with self.viewModel.transaction() as model:
            model.foodIndicator.setType(IndicatorType.FOOD)
            model.funIndicator.setType(IndicatorType.FUN)
            model.activityIndicator.setType(IndicatorType.ACTIVITY)

    def __fillHeader(self, model, player):
        maxBonus = self._nyController.getMaxBonusValue() * PERCENT
        currBonus = self._nyController.getActiveSettingBonusValue() * PERCENT + self._dataProvider.getDeb()
        model.setGiftTime(self._dataProvider.getGiftDelay())
        model.setGiftCount(player.giftCount)
        model.setCurBonus(min(currBonus, maxBonus))
        model.setMaxBonus(maxBonus)
        mood = State(player.state.lower())
        if model.getState() != mood:
            self._applyRaccoonSoundMood(mood)
        model.setState(mood)
        self._raccoonCtrl.updateMoodState(mood)

    def __fillNeeds(self, model):
        needs = model.getPetNeeds()
        needs.clear()
        for name in self._dataProvider.getNeeds():
            needs.addString(name)

        needs.invalidate()

    def __onSyncCompleted(self, *_, **__):
        with self.viewModel.transaction() as tx:
            for indicatorName, _ in self._dataProvider.playerInfo.indicators.iteritems():
                indicatorType = IndicatorType(indicatorName)
                vm = self.getIndicator(indicatorType, tx)
                vm.setItemCount(self._dataProvider.getIndicatorCurrency(indicatorName))

    def __onSimulationEnd(self):
        self.updateViewModel()

    @args2params(IndicatorType)
    def __onResetWasOverflowed(self, type):
        self.getIndicator(type, self.viewModel).setWasOverflowed(False)

    def __onItemsActivateRequested(self, *_, **__):
        self.__toggleIndicatorsWaiting(True)

    def __onItemsActivated(self, isSuccess, itemId, count, isRecalculation):
        self.__toggleIndicatorsWaiting(False)
        if not isSuccess and isRecalculation:
            NyLeaderboardRecountViewWindow(parent=self.getParentWindow()).load()
            return
        with self.viewModel.transaction() as tx:
            for name, indicator in self._dataProvider.config.indicators.iteritems():
                if indicator.item.id != itemId:
                    continue
                self._raccoonCtrl.activateItem(name)
                indicatorType = IndicatorType(name)
                model = self.getIndicator(indicatorType, tx)
                model.setWasOverflowed(self._dataProvider.playerInfo.indicators[name] >= indicator.maxPoints)
                if not self._dataProvider.isLeaderboardFinished:
                    points = model.getItemLeaderboardPoint()
                    item = NyPetItemLeaderboardPoint()
                    item.setId(getCurrentTimestamp())
                    item.setValue(count * indicator.item.leaderboardPoint)
                    item.setType(indicatorType)
                    points.addViewModel(item)
                    points.invalidate()

    def __onGiftCountUpdated(self):
        with self.viewModel.transaction() as tx:
            tx.setGiftCount(self._dataProvider.playerInfo.giftCount)
            tx.setGiftTime(self._dataProvider.getGiftDelay())

    def __toggleIndicatorsWaiting(self, state):
        with self.viewModel.transaction() as tx:
            tx.foodIndicator.setIsLoading(state)
            tx.funIndicator.setIsLoading(state)
            tx.activityIndicator.setIsLoading(state)

    def __resetIndicators(self):
        with self.viewModel.transaction() as tx:
            for indicatorName, _ in self._dataProvider.playerInfo.indicators.iteritems():
                array = self.getIndicator(IndicatorType(indicatorName), tx).getItemLeaderboardPoint()
                array.clear()
                array.invalidate()

    def _applyRaccoonSoundMood(self, mood):
        nextState = self._MOOD_TO_SOUND.get(mood)
        SoundGroups.g_instance.setState(RaccoonMood.GROUP, nextState)
