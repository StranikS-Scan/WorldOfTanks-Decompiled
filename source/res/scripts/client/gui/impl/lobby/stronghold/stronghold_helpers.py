# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/stronghold/stronghold_helpers.py
import logging
import typing
from helpers import dependency
from skeletons.gui.shared import IItemsCache
from skeletons.gui.server_events import IEventsCache
if typing.TYPE_CHECKING:
    from gui.prb_control.entities.base.unit.listener import IStrongholdListener
_logger = logging.getLogger(__name__)
STYLE_PROGRESS_PREFIX = 'style_progress_'
CLAN_SEASON_PROGRESS_PREFIX = 'clan_season_progress_26_2'
CLAN_SEASON_PROGRESS_POSTFIX = ''
CLAN_SEASON_QUEST_PREFIX = 'clan_season_quest'

def isClanSeasonProgressQuest(qID):
    return qID.startswith(CLAN_SEASON_PROGRESS_PREFIX)


def isClanSeasonQuest(qID):
    return qID.startswith(CLAN_SEASON_QUEST_PREFIX)


@dependency.replace_none_kwargs(itemsCache=IItemsCache, eventsCache=IEventsCache)
def getClanSeasonProgressLevel(itemsCache=None, eventsCache=None):
    quests = eventsCache.getAllQuests(lambda q: isClanSeasonProgressQuest(q.getID()))
    tokens = itemsCache.items.tokens.getTokenCount(CLAN_SEASON_PROGRESS_PREFIX + CLAN_SEASON_PROGRESS_POSTFIX)
    return min(len(quests), tokens)


def isStrongholdEntity(prbEntity):
    from gui.prb_control.entities.stronghold.unit.entity import StrongholdBrowserEntity
    from gui.prb_control.entities.stronghold.unit.entity import StrongholdEntity
    return isinstance(prbEntity, (StrongholdBrowserEntity, StrongholdEntity))
