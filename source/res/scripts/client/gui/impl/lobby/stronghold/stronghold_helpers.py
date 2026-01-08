# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/stronghold/stronghold_helpers.py
import logging
import typing
from constants import QUEUE_TYPE, ARENA_BONUS_TYPE
from gui.impl import backport
from gui.impl.gen import R
from helpers import dependency, int2roman
from skeletons.gui.lobby_context import ILobbyContext
from skeletons.gui.shared import IItemsCache
from skeletons.gui.server_events import IEventsCache
if typing.TYPE_CHECKING:
    from gui.prb_control.entities.base.unit.listener import IStrongholdListener
_logger = logging.getLogger(__name__)
STYLE_PROGRESS_PREFIX = 'style_progress_'
CLAN_SEASON_PROGRESS_PREFIX = 'clan_season_progress'
CLAN_SEASON_PROGRESS_POSTFIX = ''
CLAN_SEASON_QUEST_PREFIX = 'clan_season_quest'
BATTLE_MODIFIERS_DOMAIN = 'battleSeasonModifiers'
BATTLE_MODIFIERS_DOMAIN_GM = 'battleSeasonModifiersGM'
QUEUE_STRONGHOLD = 'stronghold'
QUEUE_SORTIE_10 = 'sortie_10'
QUEUE_SORTIE_8 = 'sortie_8'
QUEUE_SORTIE_6 = 'sortie_6'
QUEUE_FORT_BATTLE_10 = 'fortBattle_10'
GLOBAL_MAP = 'global_map'
ALL_STRONGHOLD_QUEUE = (QUEUE_SORTIE_10,
 QUEUE_SORTIE_8,
 QUEUE_SORTIE_6,
 QUEUE_FORT_BATTLE_10)
SORTIE_QUEUES = (QUEUE_SORTIE_10, QUEUE_SORTIE_8, QUEUE_SORTIE_6)
FORT_BATTLES = (QUEUE_FORT_BATTLE_10,)
QUEUE_SORTIE_PREFIX = 'sortie_'

def isClanSeasonProgressQuest(qID):
    return qID.startswith(CLAN_SEASON_PROGRESS_PREFIX)


def isClanSeasonQuest(qID):
    return qID.startswith(CLAN_SEASON_QUEST_PREFIX)


def getQueue(prbEntity):
    from gui.prb_control.entities.stronghold.unit.entity import StrongholdBrowserEntity
    from gui.prb_control.entities.stronghold.unit.entity import StrongholdEntity
    if isinstance(prbEntity, StrongholdBrowserEntity):
        return QUEUE_STRONGHOLD
    if isinstance(prbEntity, StrongholdEntity):
        if prbEntity.isSortie():
            return QUEUE_SORTIE_PREFIX + str(prbEntity.getMinLevel())
        return QUEUE_FORT_BATTLE_10
    return QUEUE_STRONGHOLD


def canHaveBattleModifiers():
    from gui.prb_control.dispatcher import g_prbLoader
    from gui.prb_control.entities.stronghold.unit.entity import StrongholdBrowserEntity
    from gui.prb_control.entities.stronghold.unit.entity import StrongholdEntity
    dispatcher = g_prbLoader.getDispatcher()
    if dispatcher is None:
        return False
    else:
        prbEntity = dispatcher.getEntity()
        isStronghold = isinstance(prbEntity, (StrongholdBrowserEntity, StrongholdEntity))
        isGlobalMap = prbEntity.getQueueType() == QUEUE_TYPE.SPEC_BATTLE and prbEntity.getBonusType() == ARENA_BONUS_TYPE.GLOBAL_MAP
        return isStronghold or isGlobalMap


@dependency.replace_none_kwargs(lobbyContext=ILobbyContext)
def isBattleModifierAvailableInQueue(prbEntity, lobbyContext=None):
    from gui.prb_control.entities.stronghold.unit.entity import StrongholdBrowserEntity
    from gui.prb_control.entities.stronghold.unit.entity import StrongholdEntity
    battleModifiersConfig = lobbyContext.getServerSettings().battleModifiersConfig
    if not battleModifiersConfig.isEnabled:
        return False
    elif isinstance(prbEntity, StrongholdBrowserEntity):
        return any((bool(getattr(battleModifiersConfig, queue)) for queue in ALL_STRONGHOLD_QUEUE))
    elif isinstance(prbEntity, StrongholdEntity):
        if prbEntity.getHeaderType() is None:
            return False
        if prbEntity.isSortie():
            return bool(getattr(battleModifiersConfig, QUEUE_SORTIE_PREFIX + str(prbEntity.getMinLevel())))
        return bool(getattr(battleModifiersConfig, QUEUE_FORT_BATTLE_10))
    else:
        return bool(getattr(battleModifiersConfig, GLOBAL_MAP)) if prbEntity.getQueueType() == QUEUE_TYPE.SPEC_BATTLE and prbEntity.getBonusType() == ARENA_BONUS_TYPE.GLOBAL_MAP else False


@dependency.replace_none_kwargs(lobbyContext=ILobbyContext)
def getBattleModifiersByPrbEntity(prbEntity, lobbyContext=None):
    from gui.prb_control.entities.stronghold.unit.entity import StrongholdEntity
    battleModifiersConfig = lobbyContext.getServerSettings().battleModifiersConfig
    if not battleModifiersConfig.isEnabled:
        return ()
    elif isinstance(prbEntity, StrongholdEntity):
        if prbEntity.getHeaderType() is None:
            return ()
        if prbEntity.isSortie():
            return getattr(battleModifiersConfig, QUEUE_SORTIE_PREFIX + str(prbEntity.getMinLevel()))
        return getattr(battleModifiersConfig, QUEUE_FORT_BATTLE_10)
    else:
        return getattr(battleModifiersConfig, GLOBAL_MAP) if prbEntity.getQueueType() == QUEUE_TYPE.SPEC_BATTLE and prbEntity.getBonusType() == ARENA_BONUS_TYPE.GLOBAL_MAP else ()


@dependency.replace_none_kwargs(lobbyContext=ILobbyContext)
def getBattleModifiersQueues(lobbyContext=None):
    battleModifiersConfig = lobbyContext.getServerSettings().battleModifiersConfig
    textQueues = []
    for queue in SORTIE_QUEUES:
        if getattr(battleModifiersConfig, queue):
            level = queue.split('_')[-1]
            queueName = queue.split('_')[0]
            textQueues.append(backport.text(R.strings.fortifications.battleModifiers.dyn(queueName)(), level=int2roman(int(level))))

    if getattr(battleModifiersConfig, QUEUE_FORT_BATTLE_10):
        queueName = QUEUE_FORT_BATTLE_10.split('_')[0]
        textQueues.append(backport.text(R.strings.fortifications.battleModifiers.dyn(queueName)()))
    return ', '.join(textQueues)


def getBattleModifiersObject(battleModifiers):
    from ExtensionsManager import g_extensionsManager
    import pkgutil
    if 'battle_modifiers' in [ ext.name for ext in g_extensionsManager.activeExtensions ] and pkgutil.find_loader('battle_modifiers_ext'):
        from battle_modifiers_ext.battle_modifiers import BattleModifiers
    else:
        _logger.error('Missing battle_modifiers_ext')
        return
    return BattleModifiers(battleModifiers)


@dependency.replace_none_kwargs(itemsCache=IItemsCache, eventsCache=IEventsCache)
def getClanSeasonProgressLevel(itemsCache=None, eventsCache=None):
    quests = eventsCache.getAllQuests(lambda q: isClanSeasonProgressQuest(q.getID()))
    tokens = itemsCache.items.tokens.getTokenCount(CLAN_SEASON_PROGRESS_PREFIX + CLAN_SEASON_PROGRESS_POSTFIX)
    return min(len(quests), tokens)


def isStrongholdEntity(prbEntity):
    from gui.prb_control.entities.stronghold.unit.entity import StrongholdBrowserEntity
    from gui.prb_control.entities.stronghold.unit.entity import StrongholdEntity
    return isinstance(prbEntity, (StrongholdBrowserEntity, StrongholdEntity))


def getBattleModifiersDomain():
    from gui.prb_control.dispatcher import g_prbLoader
    from gui.prb_control.entities.stronghold.unit.entity import StrongholdBrowserEntity
    from gui.prb_control.entities.stronghold.unit.entity import StrongholdEntity
    dispatcher = g_prbLoader.getDispatcher()
    prbEntity = dispatcher.getEntity()
    if isinstance(prbEntity, (StrongholdBrowserEntity, StrongholdEntity)):
        return BATTLE_MODIFIERS_DOMAIN
    return BATTLE_MODIFIERS_DOMAIN_GM if prbEntity.getQueueType() == QUEUE_TYPE.SPEC_BATTLE and prbEntity.getBonusType() == ARENA_BONUS_TYPE.GLOBAL_MAP else BATTLE_MODIFIERS_DOMAIN
