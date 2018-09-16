# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/meta/FalloutBattlePageMeta.py
"""
This file was generated using the wgpygen.
Please, don't edit this file manually.
"""
from gui.Scaleform.daapi.view.battle.classic.page import ClassicPage

class FalloutBattlePageMeta(ClassicPage):

    def as_setPostmortemGasAtackInfoS(self, infoStr, respawnStr, showDeadIcon):
        return self.flashObject.as_setPostmortemGasAtackInfo(infoStr, respawnStr, showDeadIcon) if self._isDAAPIInited() else None

    def as_hidePostmortemGasAtackInfoS(self):
        return self.flashObject.as_hidePostmortemGasAtackInfo() if self._isDAAPIInited() else None
