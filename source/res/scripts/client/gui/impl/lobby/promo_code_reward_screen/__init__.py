# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/promo_code_reward_screen/__init__.py
from collections import namedtuple
from gui.impl.gen import R
from helpers import dependency
from skeletons.gui.lobby_context import ILobbyContext
REWARD_SCREEN_TOKEN_PREFIX = 'rwscr'
REWARD_SCREEN_TOKEN_DELIMITER = ':'
WAITING_MESSAGE = 'draw_research_items'
WAITING_DATA_TIMEOUT = 10
REWARDS_SOURCE_INVOICE = 0
REWARDS_SOURCE_BATTLE_RESULTS = 1
REWARDS_SOURCE_TOKEN_QUESTS = 2
RewardScreenDescr = namedtuple('RewardScreenDescr', 'id, description, title, subtitle,  background, quests, questsDescription, tags')
RewardScreenTokenDescr = namedtuple('RewardScreenTokenDescr', 'tag, codeId, uniqIdInChain')

def isPromoCodeToken(token):
    return token.startswith(REWARD_SCREEN_TOKEN_PREFIX + REWARD_SCREEN_TOKEN_DELIMITER)


def parseToken(token):
    if not isPromoCodeToken(token):
        return None
    else:
        tag, codeId, uniqIdInChain = token.split(REWARD_SCREEN_TOKEN_DELIMITER)
        return RewardScreenTokenDescr(tag, codeId, uniqIdInChain)


@dependency.replace_none_kwargs(lobbyCtx=ILobbyContext)
def isPromoCodeRewardScreenEnabled(lobbyCtx=None):
    return lobbyCtx.getServerSettings().isPromoCodeRewardScreenEnabled()


def isLootboxesExtensionAvailable():
    lootBoxRes = R.views.dyn('gui_lootboxes').dyn('lobby').dyn('gui_lootboxes')
    return lootBoxRes.isValid()
