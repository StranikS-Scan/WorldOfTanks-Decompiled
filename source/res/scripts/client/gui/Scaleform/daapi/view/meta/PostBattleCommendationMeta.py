# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/meta/PostBattleCommendationMeta.py
from gui.Scaleform.framework.entities.BaseDAAPIComponent import BaseDAAPIComponent

class PostBattleCommendationMeta(BaseDAAPIComponent):

    def selectedChoice(self, choice):
        self._printOverrideError('selectedChoice')

    def as_setInitDataS(self, choices, selectedChoice):
        return self.flashObject.as_setInitData(choices, selectedChoice) if self._isDAAPIInited() else None
