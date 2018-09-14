# Embedded file name: scripts/client/gui/Scaleform/daapi/view/meta/FortBattleDirectionPopoverMeta.py
from gui.Scaleform.daapi.view.lobby.popover.SmartPopOverView import SmartPopOverView

class FortBattleDirectionPopoverMeta(SmartPopOverView):

    def requestToJoin(self, fortBattleID):
        self._printOverrideError('requestToJoin')

    def as_setDataS(self, data):
        if self._isDAAPIInited():
            return self.flashObject.as_setData(data)
