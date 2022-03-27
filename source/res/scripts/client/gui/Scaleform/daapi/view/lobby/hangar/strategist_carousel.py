# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/hangar/strategist_carousel.py
import logging
from gui.Scaleform.framework.entities.inject_component_adaptor import InjectComponentAdaptor
from gui.impl.gen.view_models.views.lobby.rts.carousel_view_model import StateEnum
from gui.impl.lobby.rts.carousel_view import CarouselView
_logger = logging.getLogger(__name__)

class StrategistCarousel(InjectComponentAdaptor):

    def __init__(self):
        _logger.debug('[StrategistCarousel] Init')
        super(StrategistCarousel, self).__init__()

    def _onPopulate(self):
        _logger.debug('[StrategistCarousel] OnPopulate')
        self._updateInjectedViewState()

    def _makeInjectView(self):
        return CarouselView()

    def _updateInjectedViewState(self):
        if self.getInjectView() is None:
            self._createInjectView()
        return

    def getOnSlotSelected(self):
        return self.getInjectView().onSlotSelected

    def restoreFromRoster(self):
        if self.getInjectView() is not None:
            self.getInjectView().viewModel.setState(StateEnum.NORMAL)
        return
