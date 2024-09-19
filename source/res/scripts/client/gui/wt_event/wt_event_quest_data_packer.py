# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/wt_event/wt_event_quest_data_packer.py
import logging
from gui.impl.gen.view_models.views.lobby.postbattle.events.wt_event_quest_model import WtEventQuestModel
from gui.shared.missions.packers.events import BattleQuestUIDataPacker, DailyQuestUIDataPacker, packQuestBonusModelAndTooltipData
from gui.wt_event.wt_event_bonuses_packers import getWtEventBonusPacker
from gui.impl.gen.view_models.views.lobby.wt_event.wt_quest_model import WtQuestModel
_logger = logging.getLogger(__name__)

class WTEventBattleQuestUIDataPacker(BattleQuestUIDataPacker):

    def __init__(self, event):
        super(WTEventBattleQuestUIDataPacker, self).__init__(event)
        self.__tooltipData = {}

    def _packBonuses(self, model):
        packer = getWtEventBonusPacker()
        self.__tooltipData = {}
        packQuestBonusModelAndTooltipData(packer, model.getBonuses(), self._event, tooltipData=self.__tooltipData)

    def _packModel(self, model):
        super(WTEventBattleQuestUIDataPacker, self)._packModel(model)
        model.setCompletedMissions(self._event.getBonusCount())
        model.setMaxMissions(self._event.bonusCond.getBonusLimit())

    def _packPostBattleConds(self, model):
        pass

    def getTooltipData(self):
        return self.__tooltipData


class WTQuestUIDataPacker(DailyQuestUIDataPacker):

    def __init__(self, event):
        super(WTQuestUIDataPacker, self).__init__(event)
        self.__tooltipData = {}

    def pack(self, model=None):
        if model is not None and not isinstance(model, WtQuestModel):
            _logger.error('Provided model type is not matching quest type. Expected WtQuestModel')
            return
        else:
            model = model if model is not None else WtQuestModel()
            self._packModel(model)
            return model

    def _packModel(self, model):
        super(WTQuestUIDataPacker, self)._packModel(model)
        completedMissions = self._event.getBonusCount()
        maxMissions = self._event.bonusCond.getBonusLimit()
        model.setCompletedMissions(completedMissions)
        model.setMaxMissions(maxMissions)

    def _packBonuses(self, model):
        packer = getWtEventBonusPacker()
        self.__tooltipData = {}
        packQuestBonusModelAndTooltipData(packer, model.getBonuses(), self._event, tooltipData=self.__tooltipData)

    def getTooltipData(self):
        return self.__tooltipData
