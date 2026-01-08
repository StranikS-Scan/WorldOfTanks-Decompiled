# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: battle_royale_progression/scripts/client/battle_royale_progression/gui/impl/lobby/views/quests_packer.py
import logging
from battle_royale_progression.gui.impl.lobby.views.bonus_packer import getBonusPacker
import constants
from gui.impl.gen.view_models.common.missions.daily_quest_model import DailyQuestModel
from gui.shared.missions.packers.bonus import BonusUIPacker
from gui.shared.missions.packers.events import BattleQuestUIDataPacker, packQuestBonusModelAndTooltipData, findFirstConditionModel
from gui.server_events.formatters import DECORATION_SIZES
from skeletons.gui.server_events import IEventsCache
from helpers import dependency
from gui.impl.gen.view_models.common.missions.conditions.preformatted_condition_model import PreformattedConditionModel
_logger = logging.getLogger(__name__)

class BRDailyQuestUIDataPacker(BattleQuestUIDataPacker):
    eventsCache = dependency.descriptor(IEventsCache)

    def _packBonuses(self, model):
        packer = getBonusPacker()
        self._tooltipData = {}
        packQuestBonusModelAndTooltipData(packer, model.getBonuses(), self._event, tooltipData=self._tooltipData)

    def pack(self, model=None):
        if model is not None:
            not isinstance(model, DailyQuestModel) and _logger.error('Provided model type is not matching quest type. Expected DailyQuestModel')
            return
        else:
            model = model if model is not None else DailyQuestModel()
            self._packModel(model)
            self.__resolveQuestIcon(model)
            return model

    def __resolveQuestIcon(self, model):
        iconId = self._event.getIconID()
        if iconId is not None and iconId > 0:
            prefetcher = self.eventsCache.prefetcher
            questIcon = prefetcher.getMissionDecoration(iconId, DECORATION_SIZES.DAILY)
            if not questIcon:
                _logger.error('Failed to prefetch daily quest icon from uiDecorator %s', str(iconId))
        else:
            condition = findFirstConditionModel(model.postBattleCondition) or findFirstConditionModel(model.bonusCondition)
            if condition is None:
                _logger.warning('No condition found. Unable to define quest icon.')
                return
            model.setIcon(condition.getIconKey())
        return


def getEventUIDataPacker(event):
    if event.getType() in constants.EVENT_TYPE.LIKE_BATTLE_QUESTS:
        return BRDailyQuestUIDataPacker(event)
    else:
        _logger.warning('Only LIKE_BATTLE_QUESTS allowed')
        return None
