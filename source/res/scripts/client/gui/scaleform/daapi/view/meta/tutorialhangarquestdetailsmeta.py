# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/meta/TutorialHangarQuestDetailsMeta.py
from gui.Scaleform.framework.entities.BaseDAAPIComponent import BaseDAAPIComponent

class TutorialHangarQuestDetailsMeta(BaseDAAPIComponent):
    """
    DO NOT MODIFY!
    Generated with yaml.
    __author__ = 'yaml_processor'
    @extends BaseDAAPIComponent
    """

    def requestQuestInfo(self, questID):
        self._printOverrideError('requestQuestInfo')

    def showTip(self, id, type):
        self._printOverrideError('showTip')

    def getSortedTableData(self, data):
        self._printOverrideError('getSortedTableData')

    def as_updateQuestInfoS(self, data):
        """
        :param data: Represented by TutorialHangarQuestDetailsVO (AS)
        """
        return self.flashObject.as_updateQuestInfo(data) if self._isDAAPIInited() else None
