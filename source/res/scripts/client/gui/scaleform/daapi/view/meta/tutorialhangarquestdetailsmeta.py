# Embedded file name: scripts/client/gui/Scaleform/daapi/view/meta/TutorialHangarQuestDetailsMeta.py
from gui.Scaleform.framework.entities.BaseDAAPIComponent import BaseDAAPIComponent

class TutorialHangarQuestDetailsMeta(BaseDAAPIComponent):

    def requestQuestInfo(self, questID):
        self._printOverrideError('requestQuestInfo')

    def showTip(self, id, type):
        self._printOverrideError('showTip')

    def as_updateQuestInfoS(self, data):
        if self._isDAAPIInited():
            return self.flashObject.as_updateQuestInfo(data)
