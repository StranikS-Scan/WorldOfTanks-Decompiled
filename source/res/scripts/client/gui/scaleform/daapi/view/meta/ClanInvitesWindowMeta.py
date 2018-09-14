# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/meta/ClanInvitesWindowMeta.py
from gui.Scaleform.framework.entities.abstract.AbstractWindowView import AbstractWindowView

class ClanInvitesWindowMeta(AbstractWindowView):

    def onInvitesButtonClick(self):
        self._printOverrideError('onInvitesButtonClick')

    def as_setDataS(self, data):
        """
        :param data: Represented by ClanInvitesWindowVO (AS)
        """
        return self.flashObject.as_setData(data) if self._isDAAPIInited() else None

    def as_setClanInfoS(self, data):
        """
        :param data: Represented by ClanBaseInfoVO (AS)
        """
        return self.flashObject.as_setClanInfo(data) if self._isDAAPIInited() else None

    def as_setHeaderStateS(self, data):
        """
        :param data: Represented by ClanInvitesWindowHeaderStateVO (AS)
        """
        return self.flashObject.as_setHeaderState(data) if self._isDAAPIInited() else None

    def as_setClanEmblemS(self, source):
        return self.flashObject.as_setClanEmblem(source) if self._isDAAPIInited() else None

    def as_setControlsEnabledS(self, enabled):
        return self.flashObject.as_setControlsEnabled(enabled) if self._isDAAPIInited() else None
