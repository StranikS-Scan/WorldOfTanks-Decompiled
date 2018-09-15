# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/meta/EventBoardsAwardsOverlayMeta.py
from gui.Scaleform.framework.entities.BaseDAAPIComponent import BaseDAAPIComponent

class EventBoardsAwardsOverlayMeta(BaseDAAPIComponent):

    def changeFilter(self, id):
        self._printOverrideError('changeFilter')

    def as_setHeaderS(self, data):
        """
        :param data: Represented by EventBoardTableFilterVO (AS)
        """
        return self.flashObject.as_setHeader(data) if self._isDAAPIInited() else None

    def as_setDataS(self, data):
        """
        :param data: Represented by EventBoardsAwardsOverlayVO (AS)
        """
        return self.flashObject.as_setData(data) if self._isDAAPIInited() else None
