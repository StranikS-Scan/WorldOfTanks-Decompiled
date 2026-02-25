# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/hangar/presenters/vehicle_menu_presenter.py
from __future__ import absolute_import
import logging
from CurrentVehicle import g_currentVehicle
from gui.impl.gen.view_models.views.lobby.hangar.vehicle_menu_model import VehicleMenuModel
from gui.impl.pub.view_component import ViewComponent
from gui.prb_control.entities.base.listener import IPrbListener
from gui.shared.utils.HangarSpace import HangarVideoCameraController
from helpers import dependency
from skeletons.gui.game_control import IHangarGuiController
from skeletons.gui.shared.utils import IHangarSpace
_logger = logging.getLogger(__name__)

class VehicleMenuPresenter(ViewComponent[VehicleMenuModel], IPrbListener):
    __hangarGuiCtrl = dependency.descriptor(IHangarGuiController)
    __hangarSpace = dependency.descriptor(IHangarSpace)

    def __init__(self):
        super(VehicleMenuPresenter, self).__init__(model=VehicleMenuModel)
        self.__menuEntries = {}
        self.__isVehicleChanging = False

    @property
    def viewModel(self):
        return super(VehicleMenuPresenter, self).getViewModel()

    @property
    def cameraController(self):
        return self.__hangarSpace.videoCameraController

    def _getEvents(self):
        return ((g_currentVehicle.onChanged, self.__onVehicleChanged), (g_currentVehicle.onChangeStarted, self.__onVehicleChanging), (self.viewModel.onNavigate, self.__onNavigate))

    def _finalize(self):
        for menuEntry in self.__menuEntries.values():
            menuEntry.finalize()

        self.__menuEntries = {}
        self.__isVehicleChanging = False
        super(VehicleMenuPresenter, self)._finalize()

    def _onLoading(self, *args, **kwargs):
        super(VehicleMenuPresenter, self)._onLoading()
        self.__initMenuEntries()
        if self.__menuEntries:
            self.__updateModel()

    def __initMenuEntries(self):
        menuHelper = self.__hangarGuiCtrl.currentGuiProvider.getVehicleMenuHelper()
        if menuHelper is None:
            return
        else:
            entries = menuHelper.getMenuEntries()
            for entryId, entryPresenter in entries.items():
                self.__menuEntries[entryId] = entryPresenter(entryId, self.viewModel, self)
                self.__menuEntries[entryId].initialize()

            return

    def __updateModel(self):
        entriesModel = self.viewModel.getMenuEntries()
        entriesModel.clear()
        for entry in self.__menuEntries.values():
            entry.packEntry()

    def __onNavigate(self, args):
        entry = args.get('entry')
        _logger.debug('Navigate to %s', entry)
        if self.__isVehicleChanging:
            _logger.debug('Vehicle is changing, canceling the navigation')
            return
        if self.cameraController.isEnabled:
            _logger.debug('Navigate to %s disabled by free camera', entry)
            return
        self.__menuEntries[entry].onNavigate()

    def __onVehicleChanging(self):
        self.__isVehicleChanging = True

    def __onVehicleChanged(self):
        self.__isVehicleChanging = False
        self.__updateModel()
