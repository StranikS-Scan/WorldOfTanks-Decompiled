# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/hangar_selectable_view.py
import logging
from helpers import dependency
from gui.impl.pub import ViewImpl
from hangar_selectable_objects import ISelectableLogicCallback, HangarSelectableLogic
from gui.shared import g_eventBus, EVENT_BUS_SCOPE, events
from skeletons.gui.app_loader import IAppLoader
from SelectableObjectTooltipController import SelectableObjectTooltipController
_logger = logging.getLogger(__name__)

class HangarSelectableView(ViewImpl, ISelectableLogicCallback, SelectableObjectTooltipController):
    _appLoader = dependency.descriptor(IAppLoader)

    def __init__(self, settings):
        super(HangarSelectableView, self).__init__(settings)
        self.__selectableLogic = None
        return

    @staticmethod
    def notifyCursorOver3DScene(isOver3dScene):
        g_eventBus.handleEvent(events.LobbySimpleEvent(events.LobbySimpleEvent.NOTIFY_CURSOR_OVER_3DSCENE, ctx={'isOver3dScene': isOver3dScene}), EVENT_BUS_SCOPE.DEFAULT)

    def onHighlight3DEntity(self, entity):
        self._highlight3DEntityAndShowTT(entity)

    def onFade3DEntity(self, entity):
        self._fade3DEntityAndHideTT(entity)

    def _onLoading(self):
        self._activateSelectableLogic()
        super(HangarSelectableView, self)._onLoading()

    def _finalize(self):
        self._deactivateSelectableLogic()
        super(HangarSelectableView, self)._finalize()

    def _highlight3DEntityAndShowTT(self, entity):
        pass

    def _fade3DEntityAndHideTT(self, entity):
        pass

    def _activateSelectableLogic(self):
        if self.__selectableLogic is not None:
            return
        else:
            self.__selectableLogic = self._createSelectableLogic()
            self.__selectableLogic.init(self)
            self.notifyCursorOver3DScene(True)
            return

    def _deactivateSelectableLogic(self):
        if self.__selectableLogic is not None:
            self.__selectableLogic.fini()
            self.__selectableLogic = None
            self.notifyCursorOver3DScene(False)
        return

    def _createSelectableLogic(self):
        return HangarSelectableLogic()
