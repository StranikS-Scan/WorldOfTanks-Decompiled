# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/meta/QuestsCurrentTabMeta.py
from gui.Scaleform.daapi.view.lobby.server_events.QuestsTab import QuestsTab

class QuestsCurrentTabMeta(QuestsTab):
    """
    DO NOT MODIFY!
    Generated with yaml.
    __author__ = 'yaml_processor'
    @extends QuestsTab
    """

    def sort(self, type, hideDone):
        self._printOverrideError('sort')

    def getSortedTableData(self, tableData):
        self._printOverrideError('getSortedTableData')

    def getQuestInfo(self, questID):
        self._printOverrideError('getQuestInfo')

    def collapse(self, id):
        self._printOverrideError('collapse')

    def as_showNoDataS(self):
        return self.flashObject.as_showNoData() if self._isDAAPIInited() else None

    def as_showWaitingS(self, value):
        return self.flashObject.as_showWaiting(value) if self._isDAAPIInited() else None

    def as_showNoSelectS(self):
        return self.flashObject.as_showNoSelect() if self._isDAAPIInited() else None

    def as_updateQuestInfoS(self, data):
        return self.flashObject.as_updateQuestInfo(data) if self._isDAAPIInited() else None

    def as_setSelectedQuestS(self, questID):
        return self.flashObject.as_setSelectedQuest(questID) if self._isDAAPIInited() else None
