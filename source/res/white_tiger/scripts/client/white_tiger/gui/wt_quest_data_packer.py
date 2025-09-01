# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: white_tiger/scripts/client/white_tiger/gui/wt_quest_data_packer.py
import logging
from gui.shared.missions.packers.events import DailyQuestUIDataPacker, packQuestBonusModelAndTooltipData
from white_tiger.gui.wt_bonus_packers import getWTEventBonusPacker
from white_tiger.gui.impl.gen.view_models.views.lobby.widgets.quest_view_model import QuestViewModel
_logger = logging.getLogger(__name__)

class WTQuestUIDataPacker(DailyQuestUIDataPacker):

    def __init__(self, event):
        super(WTQuestUIDataPacker, self).__init__(event)
        self.__tooltipData = {}

    def pack(self, model=None):
        if model is not None and not isinstance(model, QuestViewModel):
            _logger.error('Provided model type is not matching quest type. Expected QuestViewModel')
            return
        else:
            model = model if model is not None else QuestViewModel()
            self._packModel(model)
            self._resolveQuestIcon(model)
            return model

    def _packModel(self, model):
        super(WTQuestUIDataPacker, self)._packModel(model)
        completedMissions = self._event.getBonusCount()
        maxMissions = self._event.bonusCond.getBonusLimit()
        model.setCompletedMissions(completedMissions)
        model.setMaxMissions(maxMissions)

    def _packBonuses(self, model):
        packer = getWTEventBonusPacker()
        self.__tooltipData = {}
        packQuestBonusModelAndTooltipData(packer, model.getBonuses(), self._event, tooltipData=self.__tooltipData)

    def getTooltipData(self):
        return self.__tooltipData
