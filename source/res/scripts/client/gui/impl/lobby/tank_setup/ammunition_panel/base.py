# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/tank_setup/ammunition_panel/base.py
import logging
from gui.impl.lobby.tank_setup.base_sub_model_view import BaseSubModelView
_logger = logging.getLogger(__name__)

class BaseAmmunitionPanel(BaseSubModelView):
    __slots__ = ('_vehicle', '_controller')

    def __init__(self, viewModel, vehicle):
        super(BaseAmmunitionPanel, self).__init__(viewModel)
        self._controller = self._createAmmunitionBlockController(vehicle)

    @property
    def viewModel(self):
        return self._viewModel

    def onLoading(self, *args, **kwargs):
        super(BaseAmmunitionPanel, self).onLoading(*args, **kwargs)
        with self.viewModel.transaction() as model:
            if kwargs:
                self.changeSelectedSection(**kwargs)
            self._controller.createTabModels(model.getSections())

    def finalize(self):
        super(BaseAmmunitionPanel, self).finalize()
        self._controller = None
        return

    def update(self, vehicle, fullUpdate=False):
        self._controller.updateVehicle(vehicle)
        with self.viewModel.transaction():
            if fullUpdate or vehicle is None:
                self._controller.createTabModels(self.viewModel.getSections())
            else:
                self._controller.updateTabModels(self.viewModel.getSections())
            self.viewModel.setSyncInitiator((self.viewModel.getSyncInitiator() + 1) % 1000)
        return

    def updateSection(self, sectionName):
        with self.viewModel.transaction():
            self._controller.updateTabModel(sectionName, self.viewModel.getSections())
            self.viewModel.setSyncInitiator((self.viewModel.getSyncInitiator() + 1) % 1000)

    def changeSelectedSection(self, selectedSection, selectedSlot):
        if selectedSection or selectedSection == '':
            self.viewModel.setSelectedSection(selectedSection)
            self.viewModel.setSelectedSlot(selectedSlot)
            self._controller.updateCurrentSection(selectedSection)

    def _createAmmunitionBlockController(self, vehicle):
        raise NotImplementedError
