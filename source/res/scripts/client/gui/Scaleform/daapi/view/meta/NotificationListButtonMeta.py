# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/meta/NotificationListButtonMeta.py
from gui.Scaleform.framework.entities.BaseDAAPIComponent import BaseDAAPIComponent

class NotificationListButtonMeta(BaseDAAPIComponent):
    """
    DO NOT MODIFY!
    Generated with yaml.
    __author__ = 'yaml_processor'
    @extends BaseDAAPIComponent
    null
    """

    def handleClick(self):
        """
        :return :
        """
        self._printOverrideError('handleClick')

    def as_setStateS(self, isBlinking):
        """
        :param isBlinking:
        :return :
        """
        return self.flashObject.as_setState(isBlinking) if self._isDAAPIInited() else None
