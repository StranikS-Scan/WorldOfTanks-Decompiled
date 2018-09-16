# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/meta/ClanSearchInfoMeta.py
"""
This file was generated using the wgpygen.
Please, don't edit this file manually.
"""
from gui.Scaleform.framework.entities.BaseDAAPIComponent import BaseDAAPIComponent

class ClanSearchInfoMeta(BaseDAAPIComponent):

    def sendRequest(self):
        self._printOverrideError('sendRequest')

    def openClanProfile(self):
        self._printOverrideError('openClanProfile')

    def requestData(self, clanId):
        self._printOverrideError('requestData')

    def as_setInitDataS(self, data):
        """
        :param data: Represented by ClanSearchInfoInitDataVO (AS)
        """
        return self.flashObject.as_setInitData(data) if self._isDAAPIInited() else None

    def as_setDataS(self, data):
        """
        :param data: Represented by ClanSearchInfoDataVO (AS)
        """
        return self.flashObject.as_setData(data) if self._isDAAPIInited() else None

    def as_setStateDataS(self, data):
        """
        :param data: Represented by ClanSearchInfoStateDataVO (AS)
        """
        return self.flashObject.as_setStateData(data) if self._isDAAPIInited() else None

    def as_setEmblemS(self, emblem):
        return self.flashObject.as_setEmblem(emblem) if self._isDAAPIInited() else None

    def as_setWaitingVisibleS(self, visible):
        return self.flashObject.as_setWaitingVisible(visible) if self._isDAAPIInited() else None

    def as_setDummyS(self, data):
        """
        :param data: Represented by DummyVO (AS)
        """
        return self.flashObject.as_setDummy(data) if self._isDAAPIInited() else None

    def as_setDummyVisibleS(self, visible):
        return self.flashObject.as_setDummyVisible(visible) if self._isDAAPIInited() else None
