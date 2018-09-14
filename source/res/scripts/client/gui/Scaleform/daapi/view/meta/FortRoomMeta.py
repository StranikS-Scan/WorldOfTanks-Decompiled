# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/meta/FortRoomMeta.py
from gui.Scaleform.daapi.view.lobby.rally.BaseRallyRoomView import BaseRallyRoomView

class FortRoomMeta(BaseRallyRoomView):
    """
    DO NOT MODIFY!
    Generated with yaml.
    __author__ = 'yaml_processor'
    @extends BaseRallyRoomView
    null
    """

    def showChangeDivisionWindow(self):
        """
        :return :
        """
        self._printOverrideError('showChangeDivisionWindow')

    def as_showLegionariesCountS(self, isShow, msg, tooltip):
        """
        :param isShow:
        :param msg:
        :param tooltip:
        :return :
        """
        return self.flashObject.as_showLegionariesCount(isShow, msg, tooltip) if self._isDAAPIInited() else None

    def as_showLegionariesToolTipS(self, isShow):
        """
        :param isShow:
        :return :
        """
        return self.flashObject.as_showLegionariesToolTip(isShow) if self._isDAAPIInited() else None

    def as_showOrdersBgS(self, isShow):
        """
        :param isShow:
        :return :
        """
        return self.flashObject.as_showOrdersBg(isShow) if self._isDAAPIInited() else None

    def as_setChangeDivisionButtonEnabledS(self, value):
        """
        :param value:
        :return :
        """
        return self.flashObject.as_setChangeDivisionButtonEnabled(value) if self._isDAAPIInited() else None
