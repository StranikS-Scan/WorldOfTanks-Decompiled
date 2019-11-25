# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/meta/StatsBaseMeta.py
from gui.Scaleform.framework.entities.BaseDAAPIComponent import BaseDAAPIComponent

class StatsBaseMeta(BaseDAAPIComponent):

    def acceptSquad(self, sessionID):
        self._printOverrideError('acceptSquad')

    def addToSquad(self, sessionID):
        self._printOverrideError('addToSquad')

    def as_setIsInteractiveS(self, value):
        return self.flashObject.as_setIsInteractive(value) if self._isDAAPIInited() else None
