# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/tank_setup/tank_setup_helper.py
import logging
import typing
from BWUtil import AsyncReturn
from frameworks.wulf.view.array import fillViewModelsArray
from gui.impl.lobby.tank_setup.tank_setup_sounds import playSlotActionSound
from gui.impl.gen.view_models.common.vehicle_mechanic_model import MechanicsEnum, VehicleMechanicModel
from gui.impl.gen.view_models.views.lobby.tank_setup.sub_views.shell_mechanic_subtypes_model import ShellMechanicSubtypesModel
from gui.impl.gen.view_models.views.lobby.tank_setup.sub_views.shell_mechanic_column_config_model import ShellMechanicColumnConfigModel
from gui.impl.gen.view_models.views.lobby.tank_setup.sub_views.shell_specification_model import ShellSpecificationModel
from gui.impl.gen.view_models.views.lobby.tank_setup.sub_views.param_value_model import ParamValueModel, MechanicState
from gui.impl.lobby.common.vehicle_model_helpers import fillVehicleMechanicModel
from gui.shared.gui_items.vehicle_mechanics.constants import VEHICLE_MECHANICS_GUI_MAP
from gui.shared.items_parameters.formatters import formatParameter, MEASURE_UNITS
from gui.shared.items_parameters.shell_mechanics_helper import ShellMechanicState
from helpers import i18n
from items.components.supply_slot_categories import SlotCategories
from wg_async import wg_async, wg_await, await_callback
if typing.TYPE_CHECKING:
    from vehicles.mechanics.mechanic_constants import VehicleMechanic
    from gui.shared.gui_items.vehicle_mechanics.shell_mechanic_item import ShellMechanicItem
_logger = logging.getLogger(__name__)
NONE_ID = -1
_CATEGORY_MASK = {category:1 << idx for idx, category in enumerate(SlotCategories.ORDER)}
_MECHANIC_STATES = {ShellMechanicState.ON: MechanicState.ON,
 ShellMechanicState.OFF: MechanicState.OFF}
_MECHANIC_SUBTYPE_TO_STATE = {'basic': MechanicState.OFF,
 'modified': MechanicState.ON}

def createShellSpecificationModel(paramName, parameters, mechanic):
    specificationModel = ShellSpecificationModel()
    specificationModel.setParamName(paramName)
    specificationModel.setMetricValue(i18n.makeString(MEASURE_UNITS.get(paramName, '')))
    paramsModels = []
    for state, shellParam in parameters:
        valueModel = ParamValueModel()
        valueModel.setValue(formatParameter(paramName, shellParam.get(paramName)) or '')
        valueModel.setMechanic(VEHICLE_MECHANICS_GUI_MAP.get(mechanic, MechanicsEnum.UNKNOWN).value)
        valueModel.setState(_MECHANIC_STATES.get(state, MechanicState.DEFAULT))
        paramsModels.append(valueModel)

    fillViewModelsArray(paramsModels, specificationModel.getValues())
    return specificationModel


def createShellMechanicsModels(shellMechanicItems, minPriority=0):
    mechanicsArray = []
    for mechanic in shellMechanicItems:
        if mechanic.isHidden or mechanic.priority < minPriority:
            continue
        mechanicModel = VehicleMechanicModel()
        fillVehicleMechanicModel(mechanicModel, mechanic)
        mechanicsArray.append(mechanicModel)

    return mechanicsArray


def createShellMechanicsSubtypesModel(shellMechanicItems, minPriority=0):
    mechanicsArray = []
    for mechanic in shellMechanicItems:
        if mechanic.isHidden or mechanic.priority < minPriority:
            continue
        subtypeDict = mechanic.mechanicSubtype
        if not subtypeDict:
            continue
        model = ShellMechanicSubtypesModel()
        model.setMechanic(VEHICLE_MECHANICS_GUI_MAP.get(mechanic.mechanic, MechanicsEnum.UNKNOWN).value)
        columnConfigsArray = model.getColumnConfigs()
        for subtype, subtypeName in subtypeDict.items():
            state = _MECHANIC_SUBTYPE_TO_STATE.get(subtype)
            if state is not None:
                stateModel = ShellMechanicColumnConfigModel()
                stateModel.setState(state.value)
                stateModel.setSubtype(subtypeName)
                stateModel.setWithTextLabel(subtypeDict.get(subtype + 'WithTextLabel', False))
                stateModel.setWithRichTooltip(subtypeDict.get(subtype + 'WithRichTooltip', True))
                columnConfigsArray.addViewModel(stateModel)

        mechanicsArray.append(model)

    return mechanicsArray


def getCategoriesMask(categories):
    return sum((_CATEGORY_MASK[category] for category in categories))


def setLastSlotAction(viewModel, vehicle, setupName, actionType, intCD=NONE_ID, slotID=NONE_ID, leftID=NONE_ID, rightID=NONE_ID, leftIntCD=NONE_ID, rightIntCD=NONE_ID):
    with viewModel.lastSlotAction.transaction() as tx:
        tx.setActionType(actionType)
        tx.setIntCD(intCD)
        tx.setInstalledSlotId(slotID)
        tx.setLeftID(leftID)
        tx.setRightID(rightID)
        tx.setLeftIntCD(leftIntCD)
        tx.setRightIntCD(rightIntCD)
    playSlotActionSound(setupName, actionType, vehicle, int(intCD), leftIntCD, rightIntCD)


def clearLastSlotAction(viewModel):
    with viewModel.lastSlotAction.transaction() as tx:
        tx.setActionType('')
        tx.setIntCD(NONE_ID)
        tx.setInstalledSlotId(NONE_ID)
        tx.setLeftID(NONE_ID)
        tx.setRightID(NONE_ID)
        tx.setLeftIntCD(NONE_ID)
        tx.setRightIntCD(NONE_ID)


class TankSetupAsyncCommandLock(object):
    __slots__ = ('__inProcess',)

    def __init__(self):
        self.__inProcess = False

    @property
    def isLocked(self):
        return self.__inProcess

    @wg_async
    def tryAsyncCommand(self, func, *args, **kwargs):
        if not self.__inProcess:
            try:
                self._lock()
                result = yield wg_await(func(*args, **kwargs))
                raise AsyncReturn(result)
            finally:
                self._unlock()

        else:
            _logger.warning('Action in process')
            raise AsyncReturn(None)
        return

    @wg_async
    def tryAsyncCommandWithCallback(self, func, *args, **kwargs):
        if not self.__inProcess:
            try:
                self._lock()
                result = yield await_callback(func)(*args, **kwargs)
                raise AsyncReturn(result)
            finally:
                self._unlock()

        else:
            _logger.debug('Action in process')
            raise AsyncReturn(None)
        return

    def _lock(self):
        self.__inProcess = True

    def _unlock(self):
        self.__inProcess = False
