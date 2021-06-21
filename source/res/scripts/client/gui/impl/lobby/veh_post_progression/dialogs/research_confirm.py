# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/veh_post_progression/dialogs/research_confirm.py
import logging
from frameworks.wulf import ViewSettings
from gui.impl.common.base_sub_model_view import BaseSubModelView
from gui.impl.gen import R
from gui.impl.gen.view_models.common.bonus_model import BonusModel
from gui.impl.gen.view_models.common.bonus_value_model import BonusValueModel
from gui.impl.gen.view_models.views.lobby.post_progression.dialogs.research_steps_dialog import ResearchStepsDialog
from gui.impl.gen.view_models.views.lobby.post_progression.dialogs.short_modification_model import ShortModificationModel, ModificationType
from gui.impl.gen.view_models.views.lobby.post_progression.dialogs.short_step_model import ShortStepModel
from gui.impl.lobby.dialogs.full_screen_dialog_view import FullScreenDialogView
from gui.impl.wrappers.user_compound_price_model import BuyPriceModelBuilder
from gui.shared.gui_items import GUI_ITEM_TYPE
from gui.shared.items_parameters.functions import aggregateKpi
from gui.veh_post_porgression.models.ext_money import EXT_MONEY_ZERO, getFullXPFromXPPrice, ExtendedCurrency
from gui.veh_post_porgression.models.purchase import PurchaseProvider
from post_progression_common import ACTION_TYPES
from uilogging.veh_post_progression.constants import LogAdditionalInfo
from uilogging.veh_post_progression.loggers import VehPostProgressionDialogLogger
_logger = logging.getLogger(__name__)
_ACTION_TYPE_TO_MODIFICATION_TYPE = {ACTION_TYPES.MODIFICATION: ModificationType.MODIFICATION,
 ACTION_TYPES.PAIR_MODIFICATION: ModificationType.PAIRMODIFICATION,
 ACTION_TYPES.FEATURE: ModificationType.MODIFICATIONWITHFEATURE}

class PostProgressionResearchConfirm(FullScreenDialogView[ResearchStepsDialog]):
    __slots__ = ('_buyContent', '_mainContent', '__stepIDs', '__vehicle', '__price', '__steps', '__xpBalance', '__postProgression')

    def __init__(self, *args, **kwargs):
        settings = ViewSettings(layoutID=R.views.lobby.veh_post_progression.PostProgressionResearchSteps(), model=ResearchStepsDialog())
        settings.args = args
        settings.kwargs = kwargs
        super(PostProgressionResearchConfirm, self).__init__(settings)
        self.__vehicle = kwargs.get('vehicle', None)
        self.__stepIDs = kwargs.get('stepIDs', ())
        self.__updateData(self.__vehicle)
        return

    def _onLoading(self, *args, **kwargs):
        super(PostProgressionResearchConfirm, self)._onLoading(*args, **kwargs)
        self._buyContent = PostProgressionResearchBottomContent(viewModel=self.viewModel.dealPanel)
        self._buyContent.onLoading(self.__price, self.__xpBalance)
        self._mainContent = PostProgressionResearchMainContent(viewModel=self.viewModel.mainContent)
        self._mainContent.onLoading(self.__steps, self.__postProgression)

    def _initialize(self, *args, **kwargs):
        super(PostProgressionResearchConfirm, self)._initialize()
        if self._buyContent is not None:
            self._buyContent.initialize()
        if self._mainContent is not None:
            self._mainContent.initialize()
        return

    def _finalize(self):
        if self._mainContent is not None:
            self._mainContent.finalize()
        if self._buyContent is not None:
            self._buyContent.finalize()
        super(PostProgressionResearchConfirm, self)._finalize()
        return

    def _onCancelClicked(self):
        super(PostProgressionResearchConfirm, self)._onCancelClicked()
        VehPostProgressionDialogLogger().logClick(LogAdditionalInfo.MODIFICATION_LEVEL)

    def _onInventoryResync(self, reason, diff):
        super(PostProgressionResearchConfirm, self)._onInventoryResync(reason, diff)
        changedVehicles = diff.get(GUI_ITEM_TYPE.VEHICLE, {})
        if self.__vehicle.intCD in changedVehicles:
            self.__vehicle = self._itemsCache.items.getItemByCD(self.__vehicle.intCD)
        if self.__vehicle is not None and self.__updateData(self.__vehicle):
            if self._buyContent is not None:
                self._buyContent.update(self.__price, self.__xpBalance)
            if self._mainContent is not None:
                self._mainContent.update(self.__steps, self.__postProgression)
        else:
            self._onCancel()
        return

    def __updateData(self, vehicle):
        self.__price = EXT_MONEY_ZERO
        self.__steps = []
        if vehicle is not None and vehicle.postProgressionAvailability:
            for stepID in self.__stepIDs:
                step = vehicle.postProgression.getStep(stepID)
                if step.isRestricted() or step.isReceived():
                    _logger.error('restricted or already unlocked step in chain %s', stepID)
                    return False
                self.__steps.append(step)
                self.__price += step.getPrice()

            self.__postProgression = vehicle.postProgression
            self.__xpBalance = self._stats.getMoneyExt(self.__vehicle.intCD)
            return True
        else:
            return False


class PostProgressionResearchBottomContent(BaseSubModelView):

    def onLoading(self, price, balance):
        super(PostProgressionResearchBottomContent, self).onLoading()
        self.update(price, balance)

    def update(self, price, balance):
        super(PostProgressionResearchBottomContent, self).update()
        mayConsume = PurchaseProvider.mayConsume(balance, price).result
        with self._viewModel.transaction() as viewModel:
            viewModel.getPrice().clear()
            BuyPriceModelBuilder.fillPriceModel(viewModel, convertPrice(mayConsume, balance, price), balance=balance)
            viewModel.getPrice().invalidate()
            viewModel.setIsDisabled(not mayConsume)


class PostProgressionResearchMainContent(BaseSubModelView):

    def onLoading(self, steps, postProgression):
        super(PostProgressionResearchMainContent, self).onLoading()
        self.update(steps, postProgression)

    def update(self, steps, postProgression):
        super(PostProgressionResearchMainContent, self).update()
        unlockedSteps = []
        kpiList = []
        with self._viewModel.transaction() as viewModel:
            stepsResearch = viewModel.getStepsResearch()
            features = viewModel.getUnlockFeatures()
            stepsResearch.clear()
            features.clear()
            for step in steps:
                stepModel = self.__fillStepModel(step)
                if step.action.actionType == ACTION_TYPES.FEATURE:
                    feature = self.__fillModificationModel(step)
                    features.addViewModel(feature)
                unlockedSteps.extend((postProgression.getStep(unlockStepID) for unlockStepID in step.getNextStepIDs()))
                kpiList.extend(step.action.getKpi())
                stepsResearch.addViewModel(stepModel)

            stepsResearch.invalidate()
            features.invalidate()
            unlockedSteps.sort(key=lambda s: s.getLevel())
            unlockModifications = viewModel.getUnlockModifications()
            unlockModifications.clear()
            for unlockStep in unlockedSteps:
                if not unlockStep.isRestricted() and unlockStep.action.isMultiAction():
                    shortModModel = self.__fillModificationModel(unlockStep)
                    unlockModifications.addViewModel(shortModModel)

            unlockModifications.invalidate()
            self.__fillBonusesArray(viewModel.modificationsBonuses.getItems(), kpiList)

    def __fillStepModel(self, step):
        stepModel = ShortStepModel()
        stepModel.setLevel(step.getLevel())
        return stepModel

    def __fillBonusesArray(self, bonusesArray, kpiList):
        bonusesArray.clear()
        for kpi in aggregateKpi(kpiList).getKpiIterator():
            value = BonusValueModel()
            value.setValue(kpi.value)
            value.setValueKey(kpi.name)
            value.setValueType(kpi.type)
            bonusModel = BonusModel()
            bonusModel.setLocaleName(kpi.name)
            bonusModel.getValues().addViewModel(value)
            bonusesArray.addViewModel(bonusModel)

        bonusesArray.invalidate()

    def __fillModificationModel(self, step):
        shortModModel = ShortModificationModel()
        shortModModel.setModificationName(step.action.getLocName())
        shortModModel.setModificationType(str(_ACTION_TYPE_TO_MODIFICATION_TYPE.get(step.action.actionType, '')))
        shortModModel.setLevel(step.getLevel())
        return shortModModel


def convertPrice(mayConsume, balance, price):
    if mayConsume:
        price = getFullXPFromXPPrice(balance, price)
        price = price.replaceAll({ExtendedCurrency.XP: price.vehXP,
         ExtendedCurrency.VEH_XP: 0})
    return price
