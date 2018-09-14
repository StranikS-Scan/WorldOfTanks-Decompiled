# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/meta/QuestsTabMeta.py
from gui.Scaleform.framework.entities.BaseDAAPIComponent import BaseDAAPIComponent

class QuestsTabMeta(BaseDAAPIComponent):

    def as_setQuestsDataS(self, data):
        return self.flashObject.as_setQuestsData(data) if self._isDAAPIInited() else None

    def as_setSelectedQuestS(self, questID):
        return self.flashObject.as_setSelectedQuest(questID) if self._isDAAPIInited() else None
