# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/meta/ReceivedInviteWindowMeta.py
from gui.Scaleform.framework.entities.abstract.AbstractWindowView import AbstractWindowView

class ReceivedInviteWindowMeta(AbstractWindowView):
    """
    DO NOT MODIFY!
    Generated with yaml.
    __author__ = 'yaml_processor'
    @extends AbstractWindowView
    null
    """

    def acceptInvite(self):
        """
        :return :
        """
        self._printOverrideError('acceptInvite')

    def declineInvite(self):
        """
        :return :
        """
        self._printOverrideError('declineInvite')

    def cancelInvite(self):
        """
        :return :
        """
        self._printOverrideError('cancelInvite')

    def as_setTitleS(self, value):
        """
        :param value:
        :return :
        """
        return self.flashObject.as_setTitle(value) if self._isDAAPIInited() else None

    def as_setReceivedInviteInfoS(self, value):
        """
        :param value:
        :return :
        """
        return self.flashObject.as_setReceivedInviteInfo(value) if self._isDAAPIInited() else None
