# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/meta/EventNotificationPanelMeta.py
from gui.Scaleform.framework.entities.BaseDAAPIComponent import BaseDAAPIComponent

class EventNotificationPanelMeta(BaseDAAPIComponent):
    """
    DO NOT MODIFY!
    Generated with yaml.
    __author__ = 'yaml_processor'
    @extends BaseDAAPIComponent
    null
    """

    def onHideAnimationComplete(self, state):
        """
        :param state:
        :return :
        """
        self._printOverrideError('onHideAnimationComplete')

    def as_initS(self, states):
        """
        :param states:
        :return :
        """
        return self.flashObject.as_init(states) if self._isDAAPIInited() else None

    def as_showS(self, state):
        """
        :param state:
        :return :
        """
        return self.flashObject.as_show(state) if self._isDAAPIInited() else None

    def as_hideS(self):
        """
        :return :
        """
        return self.flashObject.as_hide() if self._isDAAPIInited() else None
