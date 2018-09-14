# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/meta/FlagNotificationMeta.py
from gui.Scaleform.framework.entities.BaseDAAPIComponent import BaseDAAPIComponent

class FlagNotificationMeta(BaseDAAPIComponent):
    """
    DO NOT MODIFY!
    Generated with yaml.
    __author__ = 'yaml_processor'
    @extends BaseDAAPIComponent
    null
    """

    def as_setStateS(self, state):
        """
        :param state:
        :return :
        """
        return self.flashObject.as_setState(state) if self._isDAAPIInited() else None

    def as_setActiveS(self, value):
        """
        :param value:
        :return :
        """
        return self.flashObject.as_setActive(value) if self._isDAAPIInited() else None

    def as_setupS(self, states):
        """
        :param states:
        :return :
        """
        return self.flashObject.as_setup(states) if self._isDAAPIInited() else None

    def as_hideS(self):
        """
        :return :
        """
        return self.flashObject.as_hide() if self._isDAAPIInited() else None

    def as_updateFieldsS(self, state, titleStr, body):
        """
        :param state:
        :param titleStr:
        :param body:
        :return :
        """
        return self.flashObject.as_updateFields(state, titleStr, body) if self._isDAAPIInited() else None
