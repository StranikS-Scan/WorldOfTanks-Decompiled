# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/meta/EpicSpectatorViewMeta.py
from gui.Scaleform.daapi.view.battle.shared.postmortem_panel import PostmortemPanel

class EpicSpectatorViewMeta(PostmortemPanel):

    def as_setFollowInfoTextS(self, folowText):
        return self.flashObject.as_setFollowInfoText(folowText) if self._isDAAPIInited() else None

    def as_changeModeS(self, mode):
        return self.flashObject.as_changeMode(mode) if self._isDAAPIInited() else None

    def as_focusOnVehicleS(self, focused):
        return self.flashObject.as_focusOnVehicle(focused) if self._isDAAPIInited() else None

    def as_setTimerS(self, time):
        return self.flashObject.as_setTimer(time) if self._isDAAPIInited() else None
