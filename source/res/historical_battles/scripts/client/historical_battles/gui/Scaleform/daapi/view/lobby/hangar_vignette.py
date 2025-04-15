# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: historical_battles/scripts/client/historical_battles/gui/Scaleform/daapi/view/lobby/hangar_vignette.py
import logging
from gui.impl.pub import ViewImpl
from gui.impl.gen import R
from frameworks.wulf import ViewFlags, ViewSettings
from gui.Scaleform.framework.entities.inject_component_adaptor import InjectComponentAdaptor
from helpers import dependency
from historical_battles.skeletons.gui.game_event_controller import IGameEventController
from historical_battles.gui.impl.gen.view_models.views.lobby.hangar_vignette_model import HangarVignetteModel
_logger = logging.getLogger(__name__)

class HangarVignette(InjectComponentAdaptor):

    def _makeInjectView(self):
        return HangarVignetteView(R.views.historical_battles.lobby.HangarVignette())


class HangarVignetteView(ViewImpl):
    __gameEventController = dependency.descriptor(IGameEventController)

    def __init__(self, layoutID):
        settings = ViewSettings(layoutID)
        settings.flags = ViewFlags.VIEW
        settings.model = HangarVignetteModel()
        super(HangarVignetteView, self).__init__(settings)

    @property
    def viewModel(self):
        return super(HangarVignetteView, self).getViewModel()

    def _getEvents(self):
        return ((self.__gameEventController.frontDataUpdated, self.__onFrontDataUpdated),)

    def _onLoading(self, *args, **kwargs):
        super(HangarVignetteView, self)._onLoading(*args, **kwargs)
        self.__setFrontType()

    def __setFrontType(self):
        currentFront = self.__gameEventController.frontController.getSelectedFront()
        with self.viewModel.transaction() as model:
            model.setFrontType(currentFront.getName())

    def __onFrontDataUpdated(self, *_):
        self.__setFrontType()
