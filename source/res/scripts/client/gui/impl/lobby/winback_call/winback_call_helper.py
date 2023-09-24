# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/winback_call/winback_call_helper.py
import typing
from gui.impl import backport
from gui.impl.gen import R
from gui.impl.gen.view_models.views.lobby.winback_call.winback_call_friend_status import WinBackCallFriendState
from gui.server_events.bonuses import getNonQuestBonuses
from gui.shared.missions.packers.bonus import getDefaultBonusPackersMap, BonusUIPacker
from helpers import dependency
from helpers import time_utils
from shared_utils import first
from skeletons.gui.server_events import IEventsCache
from skeletons.gui.game_control import IWinBackCallController
if typing.TYPE_CHECKING:
    from typing import Optional, List, Dict
    from gui.server_events.event_items import TokenQuest
    from gui.impl.gen.view_models.views.lobby.winback_call.winback_call_friend_base import WinbackCallFriendBase
    from gui.impl.gen.view_models.views.lobby.winback_call.winback_call_friend_status import WinbackCallFriendStatus
    from gui.game_control.winback_call_controller import _Friend
_BONUSES_ORDER = ('premium_plus', 'goodies', 'items')

def getWinBackBonusPacker():
    mapping = getDefaultBonusPackersMap()
    return BonusUIPacker(mapping)


def _keyBonusesOrder(bonus):
    return _BONUSES_ORDER.index(bonus.getName()) if bonus.getName() in _BONUSES_ORDER else len(_BONUSES_ORDER)


@dependency.replace_none_kwargs(eventsCache=IEventsCache, winBackCallCtrl=IWinBackCallController)
def getWinBackCallQuest(eventsCache=None, winBackCallCtrl=None):
    filterFunc = lambda quest: quest.getID() == winBackCallCtrl.inviteTokenQuestID
    quests = eventsCache.getHiddenQuests(filterFunc)
    return None if not quests else first(quests.values())


def getWinBackCallBonuses(rewards=None):
    if rewards:
        bonuses = _createWinbackCallBonuses(rewards)
    else:
        bonuses = _makeWinBackCallBonuses()
    return sorted(bonuses, key=_keyBonusesOrder)


def _createWinbackCallBonuses(rewards):
    bonuses = []
    for key, value in rewards.items():
        bonus = getNonQuestBonuses(key, value)
        if bonus:
            bonuses.extend(bonus)

    return bonuses


def _makeWinBackCallBonuses():
    winBackQuest = getWinBackCallQuest()
    return [] if winBackQuest is None else winBackQuest.getBonuses()


def _getFriendUIState(friend):
    inviteStatus = friend.inviteStatus
    states = [ state.value for state in WinBackCallFriendState ]
    return WinBackCallFriendState(inviteStatus) if inviteStatus in states else WinBackCallFriendState.UNDEFINED


def _fillFriendStatus(model, friend):
    state = _getFriendUIState(friend)
    if state == WinBackCallFriendState.NOT_SENT:
        period = time_utils.getServerUTCTime() - friend.lastLogin
        logOffPeriod = max(int(round(float(period) / time_utils.ONE_YEAR)), 1)
        status = backport.ntext(R.strings.winback_call.winbackCallMainView.friend.status.NOT_SENT(), logOffPeriod, years=logOffPeriod)
    else:
        status = backport.text(R.strings.winback_call.winbackCallMainView.friend.status.dyn(state.value)())
    model.setState(state)
    model.setStatus(status)


def fillFriendBaseData(model, friend):
    model.setDatabaseID(friend.spaID)
    model.setName(friend.userName)
    model.setClan(friend.userClan)
    _fillFriendStatus(model.status, friend)
    return model
