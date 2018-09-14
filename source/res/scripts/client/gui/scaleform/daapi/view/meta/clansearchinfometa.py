# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/meta/ClanSearchInfoMeta.py
from gui.Scaleform.framework.entities.BaseDAAPIComponent import BaseDAAPIComponent

class ClanSearchInfoMeta(BaseDAAPIComponent):
    """
    DO NOT MODIFY!
    Generated with yaml.
    __author__ = 'yaml_processor'
    @extends BaseDAAPIComponent
    null
    """

    def sendRequest(self):
        """
        :return :
        """
        self._printOverrideError('sendRequest')

    def openClanProfile(self):
        """
        :return :
        """
        self._printOverrideError('openClanProfile')

    def requestData(self, clanId):
        """
        :param clanId:
        :return :
        """
        self._printOverrideError('requestData')

    def as_setInitDataS(self, data):
        """
        :param data:
        :return :
        """
        return self.flashObject.as_setInitData(data) if self._isDAAPIInited() else None

    def as_setDataS(self, data):
        """
        :param data:
        :return :
        """
        return self.flashObject.as_setData(data) if self._isDAAPIInited() else None

    def as_setStateDataS(self, data):
        """
        :param data:
        :return :
        """
        return self.flashObject.as_setStateData(data) if self._isDAAPIInited() else None

    def as_setEmblemS(self, emblem):
        """
        :param emblem:
        :return :
        """
        return self.flashObject.as_setEmblem(emblem) if self._isDAAPIInited() else None

    def as_setWaitingVisibleS(self, visible):
        """
        :param visible:
        :return :
        """
        return self.flashObject.as_setWaitingVisible(visible) if self._isDAAPIInited() else None

    def as_setDummyS(self, data):
        """
        :param data:
        :return :
        """
        return self.flashObject.as_setDummy(data) if self._isDAAPIInited() else None

    def as_setDummyVisibleS(self, visible):
        """
        :param visible:
        :return :
        """
        return self.flashObject.as_setDummyVisible(visible) if self._isDAAPIInited() else None
