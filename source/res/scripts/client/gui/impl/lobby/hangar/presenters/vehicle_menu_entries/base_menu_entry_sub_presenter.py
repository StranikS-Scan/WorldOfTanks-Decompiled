# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/hangar/presenters/vehicle_menu_entries/base_menu_entry_sub_presenter.py
from __future__ import absolute_import
import json
from CurrentVehicle import g_currentVehicle
from frameworks.wulf.view.submodel_presenter import SubModelPresenter
from gui.impl.gen.view_models.views.lobby.hangar.vehicle_menu_model import VehicleMenuModel
from gui.shared.utils.HangarSpace import HangarVideoCameraController
from helpers import dependency
from skeletons.gui.shared.utils import IHangarSpace

class EntryStateWithReason(object):

    def __init__(self, state, reason, params=None):
        self.state = state
        self.reason = reason
        self.params = params


class BaseMenuEntrySubPresenter(SubModelPresenter):
    __hangarSpace = dependency.descriptor(IHangarSpace)

    def __init__(self, entryId, viewModel, parentView):
        super(BaseMenuEntrySubPresenter, self).__init__(viewModel, parentView)
        self._entryId = entryId

    @property
    def _cameraController(self):
        return self.__hangarSpace.videoCameraController

    def packEntry(self):
        data = {'state': self._getMenuEntryState(),
         'counter': 0}
        if g_currentVehicle.isPresent():
            menuEntryStateValue = self._getState()
            if isinstance(menuEntryStateValue, EntryStateWithReason):
                data['stateReason'] = menuEntryStateValue.reason
                if menuEntryStateValue.params is not None:
                    data['params'] = menuEntryStateValue.params
        self.getViewModel().getMenuEntries().set(self._entryId, json.dumps(data))
        return

    def onNavigate(self):
        return NotImplementedError

    def _getState(self):
        return NotImplementedError

    def _getMenuEntryState(self):
        if self._cameraController.isEnabled:
            return VehicleMenuModel.DISABLED
        if not g_currentVehicle.isPresent():
            return VehicleMenuModel.DISABLED
        menuEntryStateValue = self._getState()
        return menuEntryStateValue.state if isinstance(menuEntryStateValue, EntryStateWithReason) else menuEntryStateValue
