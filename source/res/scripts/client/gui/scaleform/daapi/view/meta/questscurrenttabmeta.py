# Embedded file name: scripts/client/gui/Scaleform/daapi/view/meta/QuestsCurrentTabMeta.py
from gui.Scaleform.framework.entities.DAAPIModule import DAAPIModule

class QuestsCurrentTabMeta(DAAPIModule):

    def sort(self, type, hideDone):
        self._printOverrideError('sort')

    def getQuestInfo(self, questID):
        self._printOverrideError('getQuestInfo')

    def getSortedTableData(self, tableData):
        self._printOverrideError('getSortedTableData')

    def as_setQuestsDataS(self, data, totalTasks):
        if self._isDAAPIInited():
            return self.flashObject.as_setQuestsData(data, totalTasks)

    def as_setSelectedQuestS(self, questID):
        if self._isDAAPIInited():
            return self.flashObject.as_setSelectedQuest(questID)
