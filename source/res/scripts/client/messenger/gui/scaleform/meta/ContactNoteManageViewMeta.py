# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/messenger/gui/Scaleform/meta/ContactNoteManageViewMeta.py
from messenger.gui.Scaleform.meta.BaseManageContactViewMeta import BaseManageContactViewMeta

class ContactNoteManageViewMeta(BaseManageContactViewMeta):
    """
    DO NOT MODIFY!
    Generated with yaml.
    __author__ = 'yaml_processor'
    @extends BaseManageContactViewMeta
    null
    """

    def sendData(self, data):
        """
        :param data:
        :return :
        """
        self._printOverrideError('sendData')

    def as_setUserPropsS(self, value):
        """
        :param value:
        :return :
        """
        return self.flashObject.as_setUserProps(value) if self._isDAAPIInited() else None
