# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/meta/HangarHeaderMeta.py
from gui.Scaleform.framework.entities.BaseDAAPIComponent import BaseDAAPIComponent

class HangarHeaderMeta(BaseDAAPIComponent):
    """
    DO NOT MODIFY!
    Generated with yaml.
    __author__ = 'yaml_processor'
    @extends BaseDAAPIComponent
    """

    def showCommonQuests(self):
        self._printOverrideError('showCommonQuests')

    def showPersonalQuests(self):
        self._printOverrideError('showPersonalQuests')

    def showBeginnerQuests(self):
        self._printOverrideError('showBeginnerQuests')

    def as_setDataS(self, data):
        """
        :param data: Represented by HangarHeaderVO (AS)
        """
        return self.flashObject.as_setData(data) if self._isDAAPIInited() else None
