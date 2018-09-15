# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/meta/BCLobbyHeaderObserverMeta.py
from gui.Scaleform.framework.entities.BaseDAAPIComponent import BaseDAAPIComponent

class BCLobbyHeaderObserverMeta(BaseDAAPIComponent):

    def as_doEnableNavigationS(self):
        return self.flashObject.as_doEnableNavigation() if self._isDAAPIInited() else None

    def as_showAnimatedS(self, data):
        """
        :param data: Represented by Vector.<String> (AS)
        """
        return self.flashObject.as_showAnimated(data) if self._isDAAPIInited() else None

    def as_setBootcampDataS(self, data):
        """
        :param data: Represented by BCLobbySettingsVO (AS)
        """
        return self.flashObject.as_setBootcampData(data) if self._isDAAPIInited() else None

    def as_setHeaderButtonsS(self, data):
        """
        :param data: Represented by Array (AS)
        """
        return self.flashObject.as_setHeaderButtons(data) if self._isDAAPIInited() else None

    def as_setHeaderKeysMapS(self, data):
        return self.flashObject.as_setHeaderKeysMap(data) if self._isDAAPIInited() else None

    def as_setMainMenuKeysMapS(self, data):
        return self.flashObject.as_setMainMenuKeysMap(data) if self._isDAAPIInited() else None
