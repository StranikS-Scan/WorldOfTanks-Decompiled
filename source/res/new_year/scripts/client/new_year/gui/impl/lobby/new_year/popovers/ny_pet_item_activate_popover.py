# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: new_year/scripts/client/new_year/gui/impl/lobby/new_year/popovers/ny_pet_item_activate_popover.py
import math
import typing
from helpers import dependency
from new_year.gui.impl.gen.view_models.views.lobby.new_year.popovers.ny_pet_item_activate_popover_model import NyPetItemActivatePopoverModel
from new_year.gui.impl.gen.view_models.views.lobby.new_year.views.pet.ny_indicator_type import IndicatorType
from frameworks.wulf import ViewSettings
from gui.impl.pub import PopOverViewImpl
from gui.impl.gen import R
from new_year.gui.impl.lobby.new_year.tooltips.ny_pet_token_stepper_tooltip import NyPetTokenStepperTooltip
from new_year.skeletons.new_year import ITamagotchiWebRequester, ITamagotchiDataProvider
if typing.TYPE_CHECKING:
    from new_year.gui.impl.gen.view_models.views.lobby.new_year.views.pet.ny_pet_model import NyPetModel
    from new_year.gui.impl.gen.view_models.views.lobby.new_year.views.pet.ny_pet_indicator_model import NyPetIndicatorModel

class NyPetItemActivatePopover(PopOverViewImpl):
    _dataProvider = dependency.descriptor(ITamagotchiDataProvider)
    _webRequester = dependency.descriptor(ITamagotchiWebRequester)
    __slots__ = ('__petModel', '__indicatorModel', '__indicatorType', '__amount')

    def __init__(self, mainModel, indicatorModel, indicatorType):
        settings = ViewSettings(layoutID=R.views.new_year.lobby.new_year.popovers.NyPetItemActivatePopover(), model=NyPetItemActivatePopoverModel())
        self.__petModel = mainModel
        self.__indicatorModel = indicatorModel
        self.__indicatorType = indicatorType
        self.__amount = 0
        super(NyPetItemActivatePopover, self).__init__(settings)

    @property
    def viewModel(self):
        return super(NyPetItemActivatePopover, self).getViewModel()

    def _getEvents(self):
        return ((self.viewModel.onItemAmountChange, self.__onItemAmountChange),
         (self.viewModel.onItemActivate, self.__onItemActivate),
         (self._dataProvider.onOnboardingChanged, self.__onOnboardingChanged),
         (self._dataProvider.onSeasonEnded, self.__onSeasonEnded))

    def createToolTipContent(self, event, contentID):
        return NyPetTokenStepperTooltip(self.__indicatorType) if contentID == R.views.new_year.lobby.new_year.tooltips.NyPetTokenStepperTooltip() else super(NyPetItemActivatePopover, self).createToolTipContent(event, contentID)

    def _onLoading(self, *args, **kwargs):
        self._dataProvider.onUpdateTipsRequested(False)
        name = self.__indicatorType.value.lower()
        config = self._dataProvider.config.indicators[name]
        maxValue = itemsCount = self._dataProvider.getIndicatorCurrency(name)
        initAmount = 1 if itemsCount > 0 else 0
        isLeaderboardFinished = self._dataProvider.isLeaderboardFinished
        if self._dataProvider.config.currentSeason is None:
            maxValue = max(0, config.maxPoints - self._dataProvider.playerInfo.indicators[name])
            maxValue = math.ceil(maxValue / float(config.item.scalePoint))
        self.__petModel.setIsPopoverOpened(True)
        with self.viewModel.transaction() as tx:
            tx.setIsOnboarding(self._dataProvider.isOnboarding)
            tx.setType(self.__indicatorType)
            tx.setItemsInInventory(itemsCount)
            tx.setVitalityPoints(config.item.scalePoint)
            tx.setMaxValue(maxValue)
            tx.setWasLeaderboardFinished(isLeaderboardFinished)
            if not isLeaderboardFinished:
                tx.setLoyaltyPoints(config.item.leaderboardPoint)
            self.__applyPreview(tx, initAmount)
        super(NyPetItemActivatePopover, self)._onLoading(*args, **kwargs)
        return

    def _onLoaded(self, *args, **kwargs):
        self.__indicatorModel.setPotentialCurPoint(self.viewModel.getPotentialVitalityPoints())
        super(NyPetItemActivatePopover, self)._onLoaded(*args, **kwargs)

    def _finalize(self):
        super(NyPetItemActivatePopover, self)._finalize()
        self.__petModel.setIsPopoverOpened(False)
        self.__indicatorModel.setPotentialCurPoint(0)
        self._dataProvider.onUpdateTipsRequested(True)

    def __applyPreview(self, tx, amount):
        self.__amount = amount
        name = self.__indicatorType.value.lower()
        config = self._dataProvider.config.indicators[name]
        extraScalePoints = int(config.item.scalePoint * self.__amount)
        tx.setPotentialLoyaltyPoints(int(config.item.leaderboardPoint * self.__amount))
        tx.setPotentialVitalityPoints(extraScalePoints)
        self.__indicatorModel.setPotentialCurPoint(self.__indicatorModel.getCurPoint() + extraScalePoints)

    def __onItemAmountChange(self, args):
        amount = args.get('amount', 0)
        with self.viewModel.transaction() as tx:
            self.__applyPreview(tx, amount)

    def __onItemActivate(self):
        item = self._dataProvider.config.indicators[self.__indicatorType.value.lower()].item
        self._webRequester.activateItem(item.id, self.__amount)

    def __onOnboardingChanged(self, state):
        self.viewModel.setIsOnboarding(state)

    def __onSeasonEnded(self, _):
        if self._dataProvider.isLeaderboardFinished:
            self.viewModel.setWasLeaderboardFinished(True)
