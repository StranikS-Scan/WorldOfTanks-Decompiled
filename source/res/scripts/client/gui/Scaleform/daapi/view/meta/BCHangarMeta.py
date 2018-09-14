# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/meta/BCHangarMeta.py
from gui.Scaleform.daapi.view.lobby.hangar.Hangar import Hangar

class BCHangarMeta(Hangar):

    def as_setBootcampDataS(self, data):
        """
        :param data: Represented by BCLobbySettingsVO (AS)
        """
        return self.flashObject.as_setBootcampData(data) if self._isDAAPIInited() else None

    def as_showAnimatedS(self, data):
        return self.flashObject.as_showAnimated(data) if self._isDAAPIInited() else None
