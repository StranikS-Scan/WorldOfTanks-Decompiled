# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/LobbySelectableView.py
from gui.Scaleform.daapi import LobbySubView
from hangar_selectable_objects import ISelectableLogicCallback, HangarSelectableLogic

class LobbySelectableView(LobbySubView, ISelectableLogicCallback):

    def __init__(self, ctx=None):
        super(LobbySelectableView, self).__init__(ctx)
        self.__selectableLogic = None
        return

    def _autoCreateSelectableLogic(self):
        return True

    def onHighlight3DEntity(self, entity):
        self._highlight3DEntityAndShowTT(entity)

    def onFade3DEntity(self, entity):
        self._fade3DEntityAndHideTT(entity)

    def _populate(self):
        super(LobbySelectableView, self)._populate()
        self._activateSelectableLogic()

    def _dispose(self):
        self._deactivateSelectableLogic()
        super(LobbySelectableView, self)._dispose()

    def _highlight3DEntityAndShowTT(self, entity):
        pass

    def _fade3DEntityAndHideTT(self, entity):
        pass

    def _activateSelectableLogic(self):
        if self.__selectableLogic is not None or not self._autoCreateSelectableLogic():
            return
        else:
            self.__selectableLogic = self._createSelectableLogic()
            self.__selectableLogic.init(self)
            return

    def _deactivateSelectableLogic(self):
        if self.__selectableLogic is not None:
            self.__selectableLogic.fini()
            self.__selectableLogic = None
        return

    def _createSelectableLogic(self):
        return HangarSelectableLogic()
