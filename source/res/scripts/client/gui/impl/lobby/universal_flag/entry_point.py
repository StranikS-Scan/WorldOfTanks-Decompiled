# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/universal_flag/entry_point.py
import logging
from frameworks.wulf import ViewFlags, ViewSettings
from gui.Scaleform.framework.entities.inject_component_adaptor import InjectComponentAdaptor
from gui.impl.gen import R
from gui.impl.gen.view_models.views.lobby.universal_flag.universal_flag_entry_point_model import UniversalFlagEntryPointModel, VisibilityState
from gui.impl.lobby.universal_flag.tooltips.entry_point_tooltip import EntryPointTooltip
from gui.impl.pub import ViewImpl
from helpers import dependency
from shared_utils import nextTick
from skeletons.gui.game_control import IUniversalFlagEntryPointController
_logger = logging.getLogger(__name__)

class _LastEntryPointState(object):

    def __init__(self):
        self.visibilityState = IUniversalFlagEntryPointController.VisibilityState.HIDDEN


_g_lastEntryPointState = _LastEntryPointState()

class UniversalFlagEntryPointComponent(InjectComponentAdaptor):

    def _onPopulate(self):
        self.__createInject()

    def _makeInjectView(self, *args):
        return EntryPoint()

    @nextTick
    def __createInject(self):
        self._createInjectView()


class EntryPoint(ViewImpl):
    __slots__ = ()
    __universalFlagEntryPointController = dependency.descriptor(IUniversalFlagEntryPointController)

    def __init__(self):
        settings = ViewSettings(R.views.lobby.universal_flag.UniversalFlagEntryPointView())
        settings.flags = ViewFlags.VIEW
        settings.model = UniversalFlagEntryPointModel()
        super(EntryPoint, self).__init__(settings)

    @property
    def viewModel(self):
        return super(EntryPoint, self).getViewModel()

    def _onLoading(self, *args, **kwargs):
        super(EntryPoint, self)._onLoading(*args, **kwargs)
        self.__updateModel()

    def _getEvents(self):
        return ((self.viewModel.openEvent, self.__universalFlagEntryPointController.openEvent), (self.__universalFlagEntryPointController.onDataUpdated, self.__updateModel))

    def createToolTipContent(self, event, contentID):
        return EntryPointTooltip() if contentID == R.views.lobby.universal_flag.tooltips.EntryPointTooltip() else super(EntryPoint, self).createToolTipContent(event, contentID)

    def __updateModel(self, *_):
        controller = self.__universalFlagEntryPointController
        with self.viewModel.transaction() as model:
            model.setVisibilityState(VisibilityState(controller.visibilityState.value))
            model.background.setActive(controller.flagBackground.active)
            model.background.setActiveHover(controller.flagBackground.activeHover)
            model.background.setDisabled(controller.flagBackground.disabled)
            model.background.setDisabledHover(controller.flagBackground.disabledHover)
            model.setPrevState(VisibilityState(_g_lastEntryPointState.visibilityState.value or 0))
        _g_lastEntryPointState.visibilityState = controller.visibilityState
