# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: battle_royale_progression/scripts/client/battle_royale_progression/gui/impl/lobby/views/quests_packer.py
import logging
from battle_royale_progression.gui.impl.lobby.views.bonus_packer import getBonusPacker
import constants
from gui.shared.missions.packers.bonus import BonusUIPacker
from gui.shared.missions.packers.events import DailyQuestUIDataPacker, packQuestBonusModelAndTooltipData
_logger = logging.getLogger(__name__)

class BRDailyQuestUIDataPacker(DailyQuestUIDataPacker):

    def _packBonuses(self, model):
        packer = getBonusPacker()
        self._tooltipData = {}
        packQuestBonusModelAndTooltipData(packer, model.getBonuses(), self._event, tooltipData=self._tooltipData)


def getEventUIDataPacker(event):
    if event.getType() in constants.EVENT_TYPE.LIKE_BATTLE_QUESTS:
        return BRDailyQuestUIDataPacker(event)
    else:
        _logger.warning('Only LIKE_BATTLE_QUESTS allowed')
        return None
