# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/meta/ClanProfileBaseViewMeta.py
from gui.Scaleform.framework.entities.BaseDAAPIComponent import BaseDAAPIComponent

class ClanProfileBaseViewMeta(BaseDAAPIComponent):
    """
    DO NOT MODIFY!
    Generated with yaml.
    __author__ = 'yaml_processor'
    @extends BaseDAAPIComponent
    null
    """

    def onHeaderButtonClick(self, actionId):
        """
        :param actionId:
        :return :
        """
        self._printOverrideError('onHeaderButtonClick')

    def as_setClanInfoS(self, data):
        """
        :param data:
        :return :
        """
        return self.flashObject.as_setClanInfo(data) if self._isDAAPIInited() else None

    def as_setHeaderStateS(self, data):
        """
        :param data:
        :return :
        """
        return self.flashObject.as_setHeaderState(data) if self._isDAAPIInited() else None

    def as_setClanEmblemS(self, source):
        """
        :param source:
        :return :
        """
        return self.flashObject.as_setClanEmblem(source) if self._isDAAPIInited() else None

    def as_setDataS(self, value):
        """
        :param value:
        :return :
        """
        return self.flashObject.as_setData(value) if self._isDAAPIInited() else None

    def as_showWaitingS(self, value):
        """
        :param value:
        :return :
        """
        return self.flashObject.as_showWaiting(value) if self._isDAAPIInited() else None

    def as_showDummyS(self, data):
        """
        :param data:
        :return :
        """
        return self.flashObject.as_showDummy(data) if self._isDAAPIInited() else None

    def as_hideDummyS(self):
        """
        :return :
        """
        return self.flashObject.as_hideDummy() if self._isDAAPIInited() else None
