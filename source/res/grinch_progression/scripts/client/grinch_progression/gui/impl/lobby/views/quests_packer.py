# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: grinch_progression/scripts/client/grinch_progression/gui/impl/lobby/views/quests_packer.py
import logging
import typing
from grinch_progression.gui.impl.gen.view_models.views.lobby.views.mission_model import MissionModel
from grinch_progression.gui.impl.lobby.views.quests_helper import isGrinchWeekendQuestID, getRoleStr, getChupterNum, vehicleRoleStrToModel
from grinch_progression.skeletons.game_controller import IGrinchProgressionController
from grinch.gui.impl.gen.view_models.views.lobby.post_battle.post_battle_mission_model import PostBattleMissionModel
from gui.server_events.bonuses import BattleTokensBonus
from gui.shared.missions.packers.events import findFirstConditionModel, getEventUIDataPacker
import constants
from helpers import dependency
if typing.TYPE_CHECKING:
    from typing import Optional
    from gui.server_events.event_items import ServerEventAbstract
    from gui.impl.gen.view_models.common.missions.daily_quest_model import DailyQuestModel
    from gui.impl.gen.view_models.common.missions.conditions.preformatted_condition_model import PreformattedConditionModel
_logger = logging.getLogger(__name__)

@dependency.replace_none_kwargs(grinchProgressionCtrl=IGrinchProgressionController)
def calculatePrize(quest, grinchProgressionCtrl=None):
    bonusTokenCount = 0
    for bonus in quest.getBonuses():
        if not isinstance(bonus, BattleTokensBonus):
            continue
        bonusTokens = bonus.getTokens()
        for tokenID, token in bonusTokens.iteritems():
            if tokenID == grinchProgressionCtrl.token:
                bonusTokenCount += token.count
                break

    return bonusTokenCount


class GrinchDailyQuestUIDataPacker(object):

    def __init__(self, event):
        self._event = event

    def pack(self):
        model = MissionModel()
        self._packModel(model)
        self._packPrize(model)
        return model

    @classmethod
    def _getFirstConditionModelFromQuestModel(cls, dailyQuestModel):
        postBattleModel = findFirstConditionModel(dailyQuestModel.postBattleCondition)
        bonusConditionModel = findFirstConditionModel(dailyQuestModel.bonusCondition)
        return postBattleModel if postBattleModel and (postBattleModel.getConditionType() != 'win' or not bonusConditionModel) else bonusConditionModel

    def _packModel(self, cardModel):
        questUIPacker = getEventUIDataPacker(self._event)
        fullQuestModel = questUIPacker.pack()
        preFormattedConditionModel = self._getFirstConditionModelFromQuestModel(fullQuestModel)
        if preFormattedConditionModel is not None:
            self._feedModel(cardModel, preFormattedConditionModel)
        return

    def _packPrize(self, cardModel):
        bonusTokenCount = calculatePrize(self._event)
        if bonusTokenCount:
            cardModel.setPrize(bonusTokenCount)
        else:
            _logger.warning("Can't find token bonus")

    def _feedModel(self, model, formattedModel):
        model.setDescription(formattedModel.getDescrData())
        currentProgress = formattedModel.getCurrent()
        if currentProgress == 0 and self._event.isCompleted():
            currentProgress = 1
        model.setCurrent(currentProgress)
        model.setTarget(formattedModel.getTotal() or 1)
        model.setQuestId(self._event.getID())
        isWeekly = isGrinchWeekendQuestID(self._event.getID())
        model.setIsWeekly(isWeekly)
        if isWeekly:
            model.setRole(vehicleRoleStrToModel(getRoleStr(self._event)))
            model.setChapter(getChupterNum(self._event))


class GrinchPostBattleQuestUIDataPacker(GrinchDailyQuestUIDataPacker):

    def pack(self):
        model = PostBattleMissionModel()
        self._packModel(model)
        self._packPrize(model)
        return model

    def _feedModel(self, model, formattedModel):
        model.setDescription(formattedModel.getDescrData())
        model.setCurrentProgress(formattedModel.getCurrent())
        model.setTotalProgress(formattedModel.getTotal())


def getGrinchUIDataPacker(event):
    if event.getType() in constants.EVENT_TYPE.LIKE_BATTLE_QUESTS:
        return GrinchDailyQuestUIDataPacker(event)
    else:
        _logger.warning('Only LIKE_BATTLE_QUESTS allowed')
        return None


def getGrinchPostBattleUIDataPacker(event):
    if event.getType() in constants.EVENT_TYPE.LIKE_BATTLE_QUESTS:
        return GrinchPostBattleQuestUIDataPacker(event)
    else:
        _logger.warning('Only LIKE_BATTLE_QUESTS allowed')
        return None
