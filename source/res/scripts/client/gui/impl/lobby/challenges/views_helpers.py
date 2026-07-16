# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/challenges/views_helpers.py
from __future__ import absolute_import
import typing
import constants
from challenges_common import CHALLENGE_MIN_VEHICLE_LEVEL
from gui.shared.missions.packers.events import ChallengeMissionUIDataPacker
from helpers import dependency
from shared_utils import first
from skeletons.gui.challenges import IChallengesController
from skeletons.gui.shared import IItemsCache
from gui.impl.gen.view_models.views.lobby.user_missions.hub.tabs.challenge_missions.challenge_quest_model import ChallengeState, ChallengeQuestModel
from gui.shared.utils.requesters.ItemsRequester import REQ_CRITERIA

@dependency.replace_none_kwargs(challenges=IChallengesController)
def updateChallengeModel(challengeItem, tooltipData, challenges=None):
    model = ChallengeQuestModel()
    challengeProgress = challenges.getChallengeProgress(challengeItem.challengeID)
    state = getChallengeState(challengeItem, challengeProgress, challenges=challenges)
    rest = challengeProgress['attempts']
    model.setChallengeID(challengeItem.challengeID)
    model.setChallengeName(challengeItem.name)
    model.setType(challengeItem.challengeType.value)
    model.setPriority(challengeItem.priority)
    model.setAttempts(challengeItem.attempts)
    model.setRemainingAttempts(challengeItem.attempts if not rest and state == ChallengeState.INACTIVE else rest)
    model.setExpireTime(challengeItem.expireTime)
    model.setTotalMissions(len(challengeItem.questsIDs))
    missions = challengeProgress['quests']
    model.setCompletedMissions(missions - 1 if missions else missions)
    model.setIsNew(not challengeItem.isVisited)
    model.setState(state)
    model.setRemainingFreeRestarts(max(challengeItem.freeRestartsPerCompletion - challengeItem.usedFreeRestarts, 0))
    currency, cost = first(challengeItem.restartPrice.items())
    model.setCurrencyType(currency)
    model.setRestartCost(cost)
    model.setIsEnoughMoney(challenges.isEnoughMoneyForRestart(challengeItem))
    missionsModel = model.getMissions()
    for quest in challengeItem.iterQuests():
        packer = ChallengeMissionUIDataPacker(quest)
        missionsModel.addViewModel(packer.pack())
        tooltipData[quest.getID()] = packer.getTooltipData()

    model.setMainRewardType(challengeItem.mainRewardType.value)
    model.setCompletions(challengeProgress['wins'])
    model.setAllowedCompletions(challengeItem.allowedCompletions)
    return model


@dependency.replace_none_kwargs(itemsCache=IItemsCache)
def getSuitableVehicles(itemsCache=None):
    suitableVehicles = itemsCache.items.getVehicles(REQ_CRITERIA.INVENTORY | REQ_CRITERIA.VEHICLE.LEVELS(list(range(CHALLENGE_MIN_VEHICLE_LEVEL, constants.MAX_VEHICLE_LEVEL + 1))) | ~REQ_CRITERIA.VEHICLE.EVENT_BATTLE)
    return suitableVehicles


@dependency.replace_none_kwargs(challenges=IChallengesController)
def getChallengeState(challenge, progress, challenges=None):
    if challenges.activeChallengeID == challenge.challengeID:
        return ChallengeState.ACTIVE
    if progress['attempts'] == 0 and progress['quests'] > 0:
        return ChallengeState.FAILED
    return ChallengeState.COMPLETED if challenges.isChallengeCompleted(challenge) else ChallengeState.INACTIVE


def parseChallengeQuestId(questID):
    if questID is None:
        return (0, 0)
    else:
        try:
            challengeInfo = questID.split(':')
            return (int(challengeInfo[1]), int(challengeInfo[2]))
        except (IndexError, ValueError, TypeError):
            return (0, 0)

        return
