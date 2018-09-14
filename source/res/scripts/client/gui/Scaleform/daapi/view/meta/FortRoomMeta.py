# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/meta/FortRoomMeta.py
from gui.Scaleform.daapi.view.lobby.rally.BaseRallyRoomView import BaseRallyRoomView

class FortRoomMeta(BaseRallyRoomView):
    """
    DO NOT MODIFY!
    Generated with yaml.
    __author__ = 'yaml_processor'
    @extends BaseRallyRoomView
    """

    def showChangeDivisionWindow(self):
        self._printOverrideError('showChangeDivisionWindow')

    def as_showLegionariesCountS(self, isShow, msg, tooltip):
        return self.flashObject.as_showLegionariesCount(isShow, msg, tooltip) if self._isDAAPIInited() else None

    def as_showLegionariesToolTipS(self, isShow):
        return self.flashObject.as_showLegionariesToolTip(isShow) if self._isDAAPIInited() else None

    def as_showOrdersBgS(self, isShow):
        return self.flashObject.as_showOrdersBg(isShow) if self._isDAAPIInited() else None

    def as_setChangeDivisionButtonEnabledS(self, value):
        return self.flashObject.as_setChangeDivisionButtonEnabled(value) if self._isDAAPIInited() else None
