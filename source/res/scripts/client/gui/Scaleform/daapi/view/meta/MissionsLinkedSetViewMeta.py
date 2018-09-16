# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/meta/MissionsLinkedSetViewMeta.py
from gui.Scaleform.daapi.view.lobby.missions.regular.missions_page import LinkedSetMissionView

class MissionsLinkedSetViewMeta(LinkedSetMissionView):

    def useTokenClick(self, eventID):
        self._printOverrideError('useTokenClick')

    def expand(self, id, value):
        self._printOverrideError('expand')

    def as_setMaintenanceS(self, visible, message1, message2, buttonLabel):
        return self.flashObject.as_setMaintenance(visible, message1, message2, buttonLabel) if self._isDAAPIInited() else None

    def as_setPlayFadeInTweenEnabledS(self, value):
        return self.flashObject.as_setPlayFadeInTweenEnabled(value) if self._isDAAPIInited() else None
