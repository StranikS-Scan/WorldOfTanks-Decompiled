# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/meta/GetPremiumPopoverMeta.py
from gui.Scaleform.daapi.view.lobby.popover.SmartPopOverView import SmartPopOverView

class GetPremiumPopoverMeta(SmartPopOverView):
    """
    DO NOT MODIFY!
    Generated with yaml.
    __author__ = 'yaml_processor'
    @extends SmartPopOverView
    null
    """

    def onActionBtnClick(self, arenaUniqueID):
        """
        :param arenaUniqueID:
        :return :
        """
        self._printOverrideError('onActionBtnClick')

    def as_setDataS(self, data):
        """
        :param data:
        :return :
        """
        return self.flashObject.as_setData(data) if self._isDAAPIInited() else None
