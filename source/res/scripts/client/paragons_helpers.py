# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/paragons_helpers.py
from gui.paragons.paragons_constants import ParagonsSystemMessages
from messenger import MessengerEntry
from messenger.m_constants import SCH_CLIENT_MSG_TYPE

def _pushParagonsClientMessage(messageType, parameters=None):
    return MessengerEntry.g_instance.protos.BW.serviceChannel.pushClientMessage({'type': messageType,
     'parameters': parameters}, SCH_CLIENT_MSG_TYPE.PARAGONS_SM_TYPE)


def pushParagonsEnableMessage():
    _pushParagonsClientMessage(ParagonsSystemMessages.PROJECT_IS_AVAILABLE)


def pushParagonsBranchResetAvailableMessage():
    _pushParagonsClientMessage(ParagonsSystemMessages.BRANCH_RESET_IS_AVAILABLE)


def pushParagonsContinuingMessage():
    _pushParagonsClientMessage(ParagonsSystemMessages.PROJECT_IS_CONTINUING)


def pushParagonsNewStageAvailableMessage():
    _pushParagonsClientMessage(ParagonsSystemMessages.NEW_CHAPTER_IS_AVAILABLE)


def pushParagonsDisableMessage():
    _pushParagonsClientMessage(ParagonsSystemMessages.PROJECT_IS_UNAVAILABLE)


def pushParagonsBranchResetErrorNotification():
    _pushParagonsClientMessage(ParagonsSystemMessages.BRANCH_RESET_ERROR)


def pushParagonsBattleRewardMessage(coins):
    _pushParagonsClientMessage(ParagonsSystemMessages.BATTLE_REWARD, parameters={'coins': coins})


def pushParagonsLevelRewardMessage(chapter, level, coins, showSelector, rewards):
    if showSelector:
        messageType = ParagonsSystemMessages.LEVEL_SELECTABLE_REWARDS
    else:
        messageType = ParagonsSystemMessages.LEVEL_REWARDS
    _pushParagonsClientMessage(messageType, parameters={'coins': coins,
     'rewards': rewards,
     'chapter': chapter,
     'level': level})


def pushParagonsBranchResetedNotification(credits, equipments, instructions, ammunitions, appearances, kits, crews):
    _pushParagonsClientMessage(ParagonsSystemMessages.BRANCH_RESETED, parameters={'credits': credits,
     'equipments': equipments,
     'instructions': instructions,
     'ammunitions': ammunitions,
     'appearances': appearances,
     'kits': kits,
     'crews': crews})


def pushParagonsBranchIsUnavalableMessage():
    _pushParagonsClientMessage(ParagonsSystemMessages.BRANCH_IS_UNAVAILABLE)


def pushParagonsBranchIsAvalableMessage():
    _pushParagonsClientMessage(ParagonsSystemMessages.BRANCH_IS_AVAILABLE)
