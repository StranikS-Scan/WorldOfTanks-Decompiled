# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/wt_event/wt_event_quest_data_packer.py
from gui.shared.missions.packers.events import BattleQuestUIDataPacker, packQuestBonusModelAndTooltipData
from gui.wt_event.wt_event_bonuses_packers import getWtEventBonusPacker

class WTEventBattleQuestUIDataPacker(BattleQuestUIDataPacker):

    def __init__(self, event):
        super(WTEventBattleQuestUIDataPacker, self).__init__(event)
        self.__tooltipData = {}

    def _packBonuses(self, model):
        packer = getWtEventBonusPacker()
        self.__tooltipData = {}
        packQuestBonusModelAndTooltipData(packer, model.getBonuses(), self._event, tooltipData=self.__tooltipData)

    def getTooltipData(self):
        return self.__tooltipData
