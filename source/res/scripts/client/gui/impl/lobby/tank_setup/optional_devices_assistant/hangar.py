# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/tank_setup/optional_devices_assistant/hangar.py
import typing
from gui.impl.common.base_sub_model_view import BaseSubModelView
from account_helpers.AccountSettings import AccountSettings, SHOWN_OPTIONAL_DEVICES_ASSISTANT_HINT
from helpers import dependency
from skeletons.gui.game_control import IOptionalDevicesAssistantController
if typing.TYPE_CHECKING:
    from gui.impl.gen.view_models.views.lobby.tank_setup.sub_views.optional_devices_assistant_model import OptionalDevicesAssistantModel

class OptionalDevicesAssistantView(BaseSubModelView):
    __slots__ = ('_vehicle',)
    _optionalDevicesAssistantCtrl = dependency.descriptor(IOptionalDevicesAssistantController)

    def __init__(self, viewModel, vehicle):
        super(OptionalDevicesAssistantView, self).__init__(viewModel)
        self._vehicle = vehicle
        self.viewModel.setIsHintShown(AccountSettings.getSettings(SHOWN_OPTIONAL_DEVICES_ASSISTANT_HINT))

    @property
    def viewModel(self):
        return self._viewModel

    def onLoading(self, *args, **kwargs):
        super(OptionalDevicesAssistantView, self).onLoading(*args, **kwargs)
        self._fillModel()

    def updateVehicle(self, vehicle):
        self._vehicle = vehicle
        self._fillModel()

    def __onHintShown(self, _):
        if not AccountSettings.getSettings(SHOWN_OPTIONAL_DEVICES_ASSISTANT_HINT):
            AccountSettings.setSettings(SHOWN_OPTIONAL_DEVICES_ASSISTANT_HINT, True)
            self.viewModel.setIsHintShown(True)

    def _fillModel(self):
        resultType, resultVehicle, resultItems = self._optionalDevicesAssistantCtrl.getPopularOptDevicesList(self._vehicle)
        with self.viewModel.transaction() as tx:
            tx.setOptionalDevicesResultType(resultType)
            tx.setSourceVehicleCompDescr(resultVehicle)
            items = tx.getOptionalDevicesAssistantItems()
            items.clear()
            items.reserve(len(resultItems))
            for item in resultItems:
                items.addViewModel(item)

            items.invalidate()

    def _addListeners(self):
        super(OptionalDevicesAssistantView, self)._addListeners()
        self._optionalDevicesAssistantCtrl.onConfigChanged += self.__onDataChanged
        self.viewModel.onHintShown += self.__onHintShown

    def _removeListeners(self):
        super(OptionalDevicesAssistantView, self)._removeListeners()
        self._optionalDevicesAssistantCtrl.onConfigChanged -= self.__onDataChanged
        self.viewModel.onHintShown -= self.__onHintShown

    def __onDataChanged(self):
        self._fillModel()
