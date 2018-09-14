# Embedded file name: scripts/client/gui/Scaleform/daapi/view/meta/FortRoomMeta.py
from gui.Scaleform.daapi.view.lobby.rally.BaseRallyRoomView import BaseRallyRoomView

class FortRoomMeta(BaseRallyRoomView):

    def showChangeDivisionWindow(self):
        self._printOverrideError('showChangeDivisionWindow')

    def as_showLegionariesCountS(self, isShow, msg):
        if self._isDAAPIInited():
            return self.flashObject.as_showLegionariesCount(isShow, msg)

    def as_showLegionariesToolTipS(self, isShow):
        if self._isDAAPIInited():
            return self.flashObject.as_showLegionariesToolTip(isShow)

    def as_showOrdersBgS(self, isShow):
        if self._isDAAPIInited():
            return self.flashObject.as_showOrdersBg(isShow)
