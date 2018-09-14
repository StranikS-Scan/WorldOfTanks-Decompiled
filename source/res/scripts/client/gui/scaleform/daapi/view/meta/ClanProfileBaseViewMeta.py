# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/meta/ClanProfileBaseViewMeta.py
from gui.Scaleform.framework.entities.BaseDAAPIComponent import BaseDAAPIComponent

class ClanProfileBaseViewMeta(BaseDAAPIComponent):
    """
    DO NOT MODIFY!
    Generated with yaml.
    __author__ = 'yaml_processor'
    @extends BaseDAAPIComponent
    """

    def onHeaderButtonClick(self, actionId):
        self._printOverrideError('onHeaderButtonClick')

    def as_setClanInfoS(self, data):
        """
        :param data: Represented by ClanBaseInfoVO (AS)
        """
        return self.flashObject.as_setClanInfo(data) if self._isDAAPIInited() else None

    def as_setHeaderStateS(self, data):
        """
        :param data: Represented by ClanProfileHeaderStateVO (AS)
        """
        return self.flashObject.as_setHeaderState(data) if self._isDAAPIInited() else None

    def as_setClanEmblemS(self, source):
        return self.flashObject.as_setClanEmblem(source) if self._isDAAPIInited() else None

    def as_setDataS(self, value):
        return self.flashObject.as_setData(value) if self._isDAAPIInited() else None

    def as_showWaitingS(self, value):
        return self.flashObject.as_showWaiting(value) if self._isDAAPIInited() else None

    def as_showDummyS(self, data):
        """
        :param data: Represented by DummyVO (AS)
        """
        return self.flashObject.as_showDummy(data) if self._isDAAPIInited() else None

    def as_hideDummyS(self):
        return self.flashObject.as_hideDummy() if self._isDAAPIInited() else None
