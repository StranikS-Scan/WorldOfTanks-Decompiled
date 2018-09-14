# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/meta/QuestsCurrentTabMeta.py
from gui.Scaleform.daapi.view.lobby.server_events.QuestsTab import QuestsTab

class QuestsCurrentTabMeta(QuestsTab):
    """
    DO NOT MODIFY!
    Generated with yaml.
    __author__ = 'yaml_processor'
    @extends QuestsTab
    null
    """

    def sort(self, type, hideDone):
        """
        :param type:
        :param hideDone:
        :return :
        """
        self._printOverrideError('sort')

    def getSortedTableData(self, tableData):
        """
        :param tableData:
        :return Array:
        """
        self._printOverrideError('getSortedTableData')

    def getQuestInfo(self, questID):
        """
        :param questID:
        :return :
        """
        self._printOverrideError('getQuestInfo')

    def as_updateQuestInfoS(self, data):
        """
        :param data:
        :return :
        """
        return self.flashObject.as_updateQuestInfo(data) if self._isDAAPIInited() else None
