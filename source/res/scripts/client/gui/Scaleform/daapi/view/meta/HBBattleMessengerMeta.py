# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/meta/HBBattleMessengerMeta.py
from messenger.gui.Scaleform.view.battle.messenger_view import BattleMessengerView

class HBBattleMessengerMeta(BattleMessengerView):

    def as_toggleReadingModerS(self, value):
        return self.flashObject.as_toggleReadingModer(value) if self._isDAAPIInited() else None
