# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/meta/ReferralManagementWindowMeta.py
from gui.Scaleform.framework.entities.abstract.AbstractWindowView import AbstractWindowView

class ReferralManagementWindowMeta(AbstractWindowView):

    def onInvitesManagementLinkClick(self):
        self._printOverrideError('onInvitesManagementLinkClick')

    def inviteIntoSquad(self, referralID):
        self._printOverrideError('inviteIntoSquad')

    def as_setDataS(self, data):
        return self.flashObject.as_setData(data) if self._isDAAPIInited() else None

    def as_setTableDataS(self, referrals):
        return self.flashObject.as_setTableData(referrals) if self._isDAAPIInited() else None

    def as_setAwardDataDataS(self, data):
        return self.flashObject.as_setAwardDataData(data) if self._isDAAPIInited() else None

    def as_setProgressDataS(self, data):
        return self.flashObject.as_setProgressData(data) if self._isDAAPIInited() else None

    def as_showAlertS(self, alertStr):
        return self.flashObject.as_showAlert(alertStr) if self._isDAAPIInited() else None
