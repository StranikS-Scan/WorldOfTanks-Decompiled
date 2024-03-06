# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/prb_control/entities/comp7/pre_queue/actions_validator.py
from CurrentVehicle import g_currentVehicle
from gui.impl.gen import R
from gui.impl.gen.view_models.views.lobby.comp7.meta_view.tab_model import MetaRootViews
from gui.periodic_battles.models import PrimeTimeStatus
from gui.prb_control.entities.base.actions_validator import BaseActionsValidator, ActionsValidatorComposite
from gui.prb_control.entities.base.pre_queue.actions_validator import PreQueueActionsValidator
from gui.prb_control.items import ValidationResult
from gui.prb_control.settings import PRE_QUEUE_RESTRICTION
from helpers import dependency
from skeletons.gui.game_control import IComp7Controller
from skeletons.gui.impl import IGuiLoader

class Comp7Validator(BaseActionsValidator):
    __comp7Ctrl = dependency.descriptor(IComp7Controller)

    def _validate(self):
        status, _, isInPrimeTime = self.__comp7Ctrl.getPrimeTimeStatus()
        if status == PrimeTimeStatus.NOT_SET:
            return ValidationResult(False, PRE_QUEUE_RESTRICTION.MODE_NOT_SET)
        return ValidationResult(False, PRE_QUEUE_RESTRICTION.MODE_NOT_AVAILABLE) if not self.__comp7Ctrl.isAvailable() or not isInPrimeTime else super(Comp7Validator, self)._validate()


class Comp7PlayerValidator(BaseActionsValidator):
    __comp7Ctrl = dependency.descriptor(IComp7Controller)

    def _validate(self):
        if self.__comp7Ctrl.isOffline:
            return ValidationResult(False, PRE_QUEUE_RESTRICTION.MODE_OFFLINE)
        if self.__comp7Ctrl.isBanned:
            return ValidationResult(False, PRE_QUEUE_RESTRICTION.BAN_IS_SET)
        if self.__comp7Ctrl.isQualificationResultsProcessing():
            return ValidationResult(False, PRE_QUEUE_RESTRICTION.QUALIFICATION_RESULTS_PROCESSING)
        return ValidationResult(False, PRE_QUEUE_RESTRICTION.QUALIFICATION_CALCULATION_RATING) if self.__comp7Ctrl.isQualificationCalculationRating() else super(Comp7PlayerValidator, self)._validate()


class Comp7VehicleValidator(BaseActionsValidator):
    __comp7Ctrl = dependency.descriptor(IComp7Controller)

    def _validate(self):
        if g_currentVehicle.isPresent():
            restriction = self.__comp7Ctrl.isSuitableVehicle(g_currentVehicle.item)
            if restriction is not None:
                return restriction
        return ValidationResult(False, PRE_QUEUE_RESTRICTION.LIMIT_NO_SUITABLE_VEHICLES, ctx={'levels': self.__comp7Ctrl.getModeSettings().levels}) if not self.__comp7Ctrl.hasSuitableVehicles() else None


class Comp7ShopValidator(BaseActionsValidator):
    __uiLoader = dependency.descriptor(IGuiLoader)

    def _validate(self):
        uiLoader = dependency.instance(IGuiLoader)
        contentResId = R.views.lobby.comp7.MetaRootView()
        metaView = uiLoader.windowsManager.getViewByLayoutID(contentResId)
        if not metaView:
            return
        isComp7ShopTab = metaView.tabId == MetaRootViews.SHOP
        return None if not isComp7ShopTab else ValidationResult(False, PRE_QUEUE_RESTRICTION.SHOP_PAGE_OPENED)


class Comp7ActionsValidator(PreQueueActionsValidator):

    def _createStateValidator(self, entity):
        baseValidator = super(Comp7ActionsValidator, self)._createStateValidator(entity)
        validators = [baseValidator,
         Comp7Validator(entity),
         Comp7PlayerValidator(entity),
         Comp7ShopValidator(entity)]
        return ActionsValidatorComposite(entity, validators=validators)

    def _createVehiclesValidator(self, entity):
        baseValidator = super(Comp7ActionsValidator, self)._createVehiclesValidator(entity)
        return ActionsValidatorComposite(entity, [Comp7VehicleValidator(entity), baseValidator])
