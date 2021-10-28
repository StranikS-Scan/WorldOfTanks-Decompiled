# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/halloween/hangar_selectable_view.py
import logging
from gui.impl.lobby.halloween.event_helpers import notifyCursorOver3DScene
from helpers import dependency
from gui.impl.pub import ViewImpl
from skeletons.gui.shared.utils import IHangarSpace
from hangar_selectable_objects import ISelectableLogicCallback, HangarSelectableLogic
_logger = logging.getLogger(__name__)

class HangarSelectableView(ViewImpl, ISelectableLogicCallback):
    _hangarSpace = dependency.descriptor(IHangarSpace)

    def __init__(self, settings):
        super(HangarSelectableView, self).__init__(settings)
        self.__selectableLogic = None
        return

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
            notifyCursorOver3DScene(True)
            return

    def _deactivateSelectableLogic(self):
        if self.__selectableLogic is not None:
            self.__selectableLogic.fini()
            self.__selectableLogic = None
            notifyCursorOver3DScene(False)
        return

    def _createSelectableLogic(self):
        return HangarSelectableLogic()
