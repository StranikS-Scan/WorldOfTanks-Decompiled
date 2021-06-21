# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/veh_post_progression/tooltip/pair_modification_tooltip_view.py
import typing
from frameworks.wulf import ViewSettings
from gui.Scaleform.daapi.view.lobby.veh_post_progression.veh_post_progression_vehicle import g_postProgressionVehicle
from gui.impl.gen import R
from gui.impl.gen.view_models.common.bonus_model import BonusModel
from gui.impl.gen.view_models.common.bonus_value_model import BonusValueModel
from gui.impl.gen.view_models.views.lobby.post_progression.tooltip.modification_model import ModificationModel
from gui.impl.gen.view_models.views.lobby.post_progression.tooltip.pair_modification_tooltip_view_model import PairModificationTooltipViewModel, PairModificationState
from gui.impl.pub import ViewImpl
from gui.impl.wrappers.user_compound_price_model import BuyPriceModelBuilder
from uilogging.veh_post_progression.constants import LogGroups
from uilogging.veh_post_progression.loggers import VehPostProgressionModificationTooltipLogger
if typing.TYPE_CHECKING:
    from frameworks.wulf import Array
    from gui.veh_post_porgression.models.modifications import MultiModsItem, SimpleModItem
    from gui.veh_post_porgression.models.progression_step import PostProgressionStepItem

class PairModificationTooltipView(ViewImpl):
    __uiLogger = VehPostProgressionModificationTooltipLogger(LogGroups.PAIR_MODIFICATION)
    __slots__ = ()

    def __init__(self, *args, **kwargs):
        settings = ViewSettings(R.views.lobby.veh_post_progression.tooltip.PairModificationTooltipView())
        settings.model = PairModificationTooltipViewModel()
        settings.args = args
        settings.kwargs = kwargs
        super(PairModificationTooltipView, self).__init__(settings)

    @property
    def viewModel(self):
        return super(PairModificationTooltipView, self).getViewModel()

    def _onLoading(self, step, modificationId, *args, **kwargs):
        super(PairModificationTooltipView, self)._onLoading(*args, **kwargs)
        if not g_postProgressionVehicle.isPresent():
            return
        pairModification = step.action
        currentModification = pairModification.getModificationByID(modificationId)
        with self.viewModel.transaction() as model:
            model.setNameRes(currentModification.getLocNameRes()())
            model.setState(self.__getState(step, modificationId))
            model.setLevel(step.getLevel())
            BuyPriceModelBuilder.fillPriceModel(model.price, currentModification.getPrice())
            self.__fillModifications(model.getModifications(), pairModification, modificationId)
            self.__fillModifiers(model.modifiers.getItems(), currentModification)

    def _onLoaded(self, *args, **kwargs):
        super(PairModificationTooltipView, self)._onLoaded(*args, **kwargs)
        self.__uiLogger.onTooltipOpened()

    def _finalize(self):
        super(PairModificationTooltipView, self)._finalize()
        self.__uiLogger.onTooltipClosed()

    def __getState(self, step, modificationId):
        if step.isLocked():
            return PairModificationState.LOCKED
        else:
            purchasedId = step.action.getPurchasedID()
            if purchasedId == modificationId:
                return PairModificationState.BOUGHT
            return PairModificationState.UNLOCKED if purchasedId is None else PairModificationState.ANOTHERISINSTALLED

    def __fillModifications(self, modifications, pairModification, modificationId):
        modifications.clear()
        for modification in pairModification.modifications:
            modificationModel = ModificationModel()
            modificationModel.setIconResName(modification.getImageName())
            modificationModel.setIsCurrent(modification.actionID == modificationId)
            modificationModel.setIsInstalled(pairModification.getPurchasedID() == modification.actionID)
            modifications.addViewModel(modificationModel)

        modifications.invalidate()

    def __fillModifiers(self, modifiers, modification):
        modifiers.clear()
        for kpi in modification.getKpi(g_postProgressionVehicle.defaultItem):
            value = BonusValueModel()
            value.setValue(kpi.value)
            value.setValueKey(kpi.name)
            value.setValueType(kpi.type)
            value.setIsDebuff(kpi.isDebuff)
            bonusModel = BonusModel()
            bonusModel.setLocaleName(kpi.name)
            bonusModel.getValues().addViewModel(value)
            modifiers.addViewModel(bonusModel)

        modifiers.invalidate()
