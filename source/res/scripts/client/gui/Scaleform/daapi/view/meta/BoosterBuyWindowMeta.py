# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/meta/BoosterBuyWindowMeta.py
from gui.Scaleform.framework.entities.abstract.AbstractWindowView import AbstractWindowView

class BoosterBuyWindowMeta(AbstractWindowView):

    def buy(self, count):
        self._printOverrideError('buy')

    def setAutoRearm(self, autoRearm):
        self._printOverrideError('setAutoRearm')

    def as_setInitDataS(self, data):
        """
        :param data: Represented by BoosterBuyWindowVO (AS)
        """
        return self.flashObject.as_setInitData(data) if self._isDAAPIInited() else None

    def as_updateDataS(self, data):
        """
        :param data: Represented by BoosterBuyWindowUpdateVO (AS)
        """
        return self.flashObject.as_updateData(data) if self._isDAAPIInited() else None
