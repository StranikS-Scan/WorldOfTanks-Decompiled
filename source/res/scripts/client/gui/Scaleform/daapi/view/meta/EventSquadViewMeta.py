# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/meta/EventSquadViewMeta.py
from gui.Scaleform.daapi.view.lobby.prb_windows.squad_view import SquadView

class EventSquadViewMeta(SquadView):

    def selectDifficulty(self, value):
        self._printOverrideError('selectDifficulty')

    def as_updateDifficultyS(self, data):
        return self.flashObject.as_updateDifficulty(data) if self._isDAAPIInited() else None

    def as_enableDifficultyDropdownS(self, value):
        return self.flashObject.as_enableDifficultyDropdown(value) if self._isDAAPIInited() else None
