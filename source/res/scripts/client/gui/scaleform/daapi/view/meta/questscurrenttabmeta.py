# Embedded file name: scripts/client/gui/Scaleform/daapi/view/meta/QuestsCurrentTabMeta.py
from gui.Scaleform.daapi.view.lobby.server_events.QuestsTab import QuestsTab

class QuestsCurrentTabMeta(QuestsTab):

    def sort(self, type, hideDone):
        self._printOverrideError('sort')

    def getSortedTableData(self, tableData):
        self._printOverrideError('getSortedTableData')

    def getQuestInfo(self, questID):
        self._printOverrideError('getQuestInfo')

    def as_updateQuestInfoS(self, data):
        if self._isDAAPIInited():
            return self.flashObject.as_updateQuestInfo(data)
