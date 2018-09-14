# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/meta/AccountPopoverMeta.py
from gui.Scaleform.daapi.view.lobby.popover.SmartPopOverView import SmartPopOverView

class AccountPopoverMeta(SmartPopOverView):

    def openBoostersWindow(self, slotId):
        self._printOverrideError('openBoostersWindow')

    def openClanResearch(self):
        self._printOverrideError('openClanResearch')

    def openRequestWindow(self):
        self._printOverrideError('openRequestWindow')

    def openInviteWindow(self):
        self._printOverrideError('openInviteWindow')

    def openClanStatistic(self):
        self._printOverrideError('openClanStatistic')

    def openCrewStatistic(self):
        self._printOverrideError('openCrewStatistic')

    def openReferralManagement(self):
        self._printOverrideError('openReferralManagement')

    def as_setDataS(self, data):
        return self.flashObject.as_setData(data) if self._isDAAPIInited() else None

    def as_setClanDataS(self, data):
        return self.flashObject.as_setClanData(data) if self._isDAAPIInited() else None

    def as_setCrewDataS(self, data):
        return self.flashObject.as_setCrewData(data) if self._isDAAPIInited() else None

    def as_setClanEmblemS(self, emblemId):
        return self.flashObject.as_setClanEmblem(emblemId) if self._isDAAPIInited() else None

    def as_setCrewEmblemS(self, emblemId):
        return self.flashObject.as_setCrewEmblem(emblemId) if self._isDAAPIInited() else None

    def as_setReferralDataS(self, data):
        return self.flashObject.as_setReferralData(data) if self._isDAAPIInited() else None
