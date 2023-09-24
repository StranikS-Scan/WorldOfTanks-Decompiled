# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/meta/InjectComponentMeta.py
from gui.Scaleform.framework.entities.BaseDAAPIComponent import BaseDAAPIComponent

class InjectComponentMeta(BaseDAAPIComponent):

    def as_setPlaceIdS(self, placeId):
        return self.flashObject.as_setPlaceId(placeId) if self._isDAAPIInited() else None
