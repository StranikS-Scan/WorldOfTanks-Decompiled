# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: last_stand/scripts/client/last_stand/gui/game_control/ls_artefacts_controller.py
import typing
import itertools
from collections import namedtuple
from adisp import adisp_async
import Event
import nations
from gui import GUI_NATIONS
from gui.ClientUpdateManager import g_clientUpdateManager
from gui import SystemMessages
from gui.impl import backport
from gui.prb_control.entities.listener import IGlobalListener
from gui.shared.utils import decorators
from constants import EVENT_CLIENT_DATA, PREMIUM_ENTITLEMENTS
from gui.server_events.bonuses import getNonQuestBonuses, mergeBonuses, NationalBlueprintBonus, IntelligenceBlueprintBonus, LootBoxTokensBonus, ItemsBonus
from last_stand.gui.ls_gui_constants import FUNCTIONAL_FLAG
from last_stand.gui.shared.gui_items.processors.processors import OpenArtefactProcessor
from last_stand.skeletons.ls_controller import ILSController
from last_stand.skeletons.ls_artefacts_controller import ILSArtefactsController
from last_stand_common.last_stand_constants import ArtefactsSettings, ArtefactType, ARTEFACT_ID_MASK
from helpers import dependency
from skeletons.gui.customization import ICustomizationService
from skeletons.gui.server_events import IEventsCache
from shared_utils import first
from gui.shared.money import Currency
from gui.shared.utils.requesters.blueprints_requester import getFragmentNationID
if typing.TYPE_CHECKING:
    from gui.server_events.bonuses import TokensBonus, SimpleBonus
QuestConditions = namedtuple('QuestConditions', ('name', 'description', 'totalValue', 'progress'))
QuestConditions.__new__.__defaults__ = ('', '', 0, 0)
ArtefactPrice = namedtuple('ArtefactPrice', ('currency', 'amount'))
ArtefactPrice.__new__.__defaults__ = (None, 0)
QUEST_BONUS_CONDITIONS = ('cumulative', 'cumulativeExt', 'cumulativeSum', 'vehicleKillsCumulative', 'vehicleDamageCumulative', 'vehicleStunCumulative', 'battles')
PHASE_COMPLETION_QUEST_BR_CONDITION = ('ls_phase', 'greater')
TOTAL_PHASE_COUNT = 4
_blueprints_national_order = [ str('blueprint_national_' + nation) for nation in GUI_NATIONS ]
BONUS_ORDER = ['lootBox',
 'dossier',
 'vehicles',
 'slots',
 'tmanToken',
 'tankmen',
 'crewSkins',
 'berths',
 'customizations',
 'crewBooks',
 PREMIUM_ENTITLEMENTS.VIP,
 PREMIUM_ENTITLEMENTS.PLUS,
 PREMIUM_ENTITLEMENTS.BASIC,
 Currency.BPCOIN,
 'battlePassPoints',
 ArtefactsSettings.KEY_TOKEN,
 Currency.CRYSTAL,
 Currency.GOLD,
 Currency.CREDITS,
 'xp',
 Currency.FREE_XP,
 Currency.EQUIP_COIN,
 'battle_bonus_x5',
 'crew_bonus_x3',
 'battlePassQuestChainToken',
 'tokens',
 'battleToken',
 'vehicleXP',
 'tankmenXP',
 'goodies',
 'items',
 'blueprints_universal'] + _blueprints_national_order + ['blueprints', 'blueprintsAny']

class Artefact(namedtuple('Artefact', ('artefactID', 'decodePrice', 'skipPrice', 'bonusRewards', 'questConditions', 'artefactTypes', 'difficulty'))):

    def getCtx(self):
        return dict(self._asdict())


def getTokenValue(bonus):
    token = first(bonus.getTokens().iterkeys(), '')
    return 'battle_bonus_x5' if token.startswith('xpx5') or token.startswith('Expx5') else token


def getBlueprintsValue(bonus):
    fragmentCD = bonus.getValue()[0]
    if isinstance(bonus, NationalBlueprintBonus):
        blueprintNation = nations.MAP.get(getFragmentNationID(fragmentCD), nations.NONE_INDEX)
        return str('blueprint_national_' + blueprintNation)
    return 'blueprints_universal' if isinstance(bonus, IntelligenceBlueprintBonus) else 'blueprints'


_VALUE_GETTER_MAP = {'tokens': getTokenValue,
 'battleToken': getTokenValue,
 'blueprints': getBlueprintsValue}

def getBonusPriority(bonus):
    bonusType = bonus.getName()
    _getter = _VALUE_GETTER_MAP.get(bonusType)
    bonusValue = _getter(bonus) if _getter else None
    if bonusValue in BONUS_ORDER:
        position = BONUS_ORDER.index(bonusValue)
    elif bonusType in BONUS_ORDER:
        position = BONUS_ORDER.index(bonusType)
    else:
        position = len(BONUS_ORDER) + 1
    return position


def compareBonusesByPriority(bonus1, bonus2):
    return cmp(getBonusPriority(bonus1), getBonusPriority(bonus2))


def isArtefactQuest(qID):
    return qID.startswith(ArtefactsSettings.QUEST_PREFIX)


class LSArtefactsController(ILSArtefactsController, IGlobalListener):
    eventsCache = dependency.descriptor(IEventsCache)
    lsCtrl = dependency.descriptor(ILSController)
    c11n = dependency.descriptor(ICustomizationService)

    def __init__(self):
        super(LSArtefactsController, self).__init__()
        self.onArtefactStatusUpdated = Event.Event()
        self.onArtefactKeyUpdated = Event.Event()
        self.onArtefactSettingsUpdated = Event.Event()
        self._artefacts = {}
        self._rewardsSettings = {}
        self._selectedArtefactID = None
        return

    def fini(self):
        self.stopGlobalListening()
        g_clientUpdateManager.removeObjectCallbacks(self)
        self.lsCtrl.onSettingsUpdate -= self.__updateSettings
        self.onArtefactStatusUpdated.clear()
        self.onArtefactKeyUpdated.clear()
        self.onArtefactSettingsUpdated.clear()
        self._artefacts = {}
        self._rewardsSettings = {}
        self._selectedArtefactID = None
        return

    def isEnabled(self):
        return self._getConfig().get('enabled', False)

    def onDisconnected(self):
        super(LSArtefactsController, self).onDisconnected()
        self.stopGlobalListening()

    def onAvatarBecomePlayer(self):
        super(LSArtefactsController, self).onAvatarBecomePlayer()
        self.stopGlobalListening()

    def onLobbyStarted(self, ctx):
        super(LSArtefactsController, self).onLobbyStarted(ctx)
        self._selectedArtefactID = None
        g_clientUpdateManager.addCallbacks({'tokens': self.__handleTokensUpdate,
         'eventsData.' + str(EVENT_CLIENT_DATA.QUEST): self.__onQuestsUpdated})
        self.lsCtrl.onSettingsUpdate += self.__updateSettings
        self._initArtefacts()
        self._rewardsSettings = self._getRewardsSettings()
        return

    def onLobbyInited(self, event):
        self.startGlobalListening()

    def onPrbEntitySwitched(self):
        if self.prbEntity.getModeFlags() & FUNCTIONAL_FLAG.LAST_STAND:
            return
        else:
            self._selectedArtefactID = None
            return

    @property
    def selectedArtefactID(self):
        return self._selectedArtefactID if self._selectedArtefactID in self._artefacts else None

    @selectedArtefactID.setter
    def selectedArtefactID(self, artefactID):
        self._selectedArtefactID = artefactID

    def resetSelectedArtefactID(self):
        self._selectedArtefactID = None
        return

    def artefactsSorted(self):
        return sorted(self._artefacts.itervalues(), key=lambda artefact: self.getIndex(artefact.artefactID))

    def regularArtefacts(self):
        return self.artefactsSorted()[:-1]

    def getFinalArtefact(self):
        return next((x for x in self._artefacts.itervalues() if ArtefactType.FINAL in x.artefactTypes), None)

    def getKingRewardArtefact(self):
        return next((x for x in self._artefacts.itervalues() if ArtefactType.KING_REWARD in x.artefactTypes), None)

    def geArtefactIDFromOpenToken(self, token):
        return token.replace(self._getConfig().get('openedSuffix', ''), '')

    def isFinalArtefact(self, artefect):
        return ArtefactType.FINAL in artefect.artefactTypes

    def isKingRewardArtefact(self, artefect):
        return ArtefactType.KING_REWARD in artefect.artefactTypes

    def getArtefact(self, artefactID):
        return self._artefacts.get(artefactID)

    def isArtefactOpened(self, artefactID):
        openedTokenID = artefactID + self._getConfig().get('openedSuffix', '')
        return self.eventsCache.questsProgress.getTokenCount(openedTokenID) > 0

    def isArtefactReceived(self, artefactID):
        return self.eventsCache.questsProgress.getTokenCount(artefactID) > 0

    def getArtefactKeyQuantity(self):
        return self.eventsCache.questsProgress.getTokenCount(ArtefactsSettings.KEY_TOKEN)

    def getCurrentArtefactProgress(self):
        return sum(list((int(self.isArtefactOpened(artefactID)) for artefactID in self._artefacts)))

    def getAvailableArtefactProgress(self):
        return sum(list((int(self.isArtefactReceived(artefactID)) for artefactID in self._artefacts)))

    def getMaxArtefactsProgress(self):
        return len(self._artefacts)

    def getArtefactsCount(self):
        return len(self._artefacts)

    def getMainGift(self):
        kingRewardArtefact = self.getKingRewardArtefact()
        if not kingRewardArtefact:
            return None
        else:
            for bonus in kingRewardArtefact.bonusRewards:
                if not isinstance(bonus, ItemsBonus):
                    continue
                return bonus

            return None

    def isArtefactHasLootBoxGift(self, artefactID):
        artefact = self.getArtefact(artefactID)
        if not artefact:
            return False
        for bonus in artefact.bonusRewards:
            if isinstance(bonus, LootBoxTokensBonus):
                return True

        return False

    def isAnyArtefactsHasLootBoxGift(self):
        return any((self.isArtefactHasLootBoxGift(artefactID) for artefactID in self._artefacts.iterkeys()))

    @property
    def hiddenBonusStyleIDs(self):
        return self._rewardsSettings.get('hiddenStyles', [])

    def getLackOfKeysForArtefact(self, artefactID):
        return max(0, self.__getArtefactKeyCost(artefactID) - self.getArtefactKeyQuantity())

    def getLackOfKeysForArtefacts(self):
        keysCount = 0
        for artefactID in self._artefacts:
            keysCount += self.__getArtefactKeyCost(artefactID)

        return max(0, keysCount - self.getArtefactKeyQuantity())

    @adisp_async
    @decorators.adisp_process('updating')
    def openArtefact(self, artefactID, isSkipQuest, callback):
        result = yield OpenArtefactProcessor(self, artefactID, isSkipQuest).request()
        if result.userMsg:
            SystemMessages.pushMessage(result.userMsg, type=result.sysMsgType)
        callback(result.success)

    def isProgressCompleted(self):
        return self.getCurrentArtefactProgress() >= self.getMaxArtefactsProgress()

    def getArtefactIDByIndex(self, index):
        return ARTEFACT_ID_MASK.format(index=index)

    def getIndex(self, artefactID):
        _, index, __ = artefactID.split(':')
        return int(index)

    def _initArtefacts(self):
        quests = self.eventsCache.getAllQuests(lambda q: isArtefactQuest(q.getID()))
        self._artefacts = dict(((artefactID, Artefact(artefactID, ArtefactPrice(*self._getArtefactPrice(artefactID)), ArtefactPrice(*self._getArtefactQuestSkipPrice(artefactID)), self._getArtefactBonuses(artefactID, quests), self._getArtefactQuestConditions(artefactID, quests), self._getArtefactTypes(artefactID), self._getArtefactDifficulty(artefactID))) for artefactID in self._getArtefacts().iterkeys()))

    def _getArtefactTypes(self, artefactID):
        return self._getArtefacts().get(artefactID, {}).get('type', [])

    def _getArtefactDifficulty(self, artefactID):
        return self._getArtefacts().get(artefactID, {}).get('difficulty', 0)

    def _getArtefactQuestSkipPrice(self, artefactID):
        return self._getArtefacts().get(artefactID, {}).get('questSkipCost', (None, 0))

    def _getArtefactPrice(self, artefactID):
        return self._getArtefacts().get(artefactID, {}).get('cost', (None, 0))

    @classmethod
    def _formatter(cls, value):
        return backport.getNiceNumberFormat(value)

    def _getArtefactQuestConditions(self, artefactID, quests):
        quest = quests.get(artefactID)
        if quest is not None:
            curProgress, totalValue = self.__getFirstQuestProgress(quest)
            description = quest.getDescription()
            if totalValue is not None:
                curProgressStr, totalValueStr = self._formatter(int(curProgress)), self._formatter(int(totalValue))
                description = description.format(total=totalValueStr, current=curProgressStr if not self.isArtefactOpened(artefactID) else totalValueStr)
            return QuestConditions(quest.getUserName(), description, totalValue, curProgress)
        else:
            return QuestConditions()

    def _getArtefactBonuses(self, artefactID, quests):
        rewards = []
        artefactConfig = self._getArtefacts().get(artefactID, {})
        bonusesConfig = artefactConfig.get('bonus', {})
        for bonusType, bonusValue in bonusesConfig.iteritems():
            rewards.extend(getNonQuestBonuses(bonusType, bonusValue))

        questsToRun = artefactConfig.get('questsToRun')
        if questsToRun:
            quests = self.eventsCache.getHiddenQuests(lambda q: q.getID() in questsToRun)
            if quests:
                rewards.extend(itertools.chain.from_iterable((q.getBonuses() for q in quests.itervalues())))
        sortedBonuses = sorted(mergeBonuses(rewards), cmp=compareBonusesByPriority)
        return sortedBonuses

    def _getConfig(self):
        return self.lsCtrl.getModeSettings().artefactsSettings

    def _getArtefacts(self):
        return self._getConfig().get('artefacts', {})

    def _getRewardsSettings(self):
        return self.lsCtrl.getModeSettings().rewardsSettings

    def __getFirstQuestProgress(self, quest):
        for condName in QUEST_BONUS_CONDITIONS:
            cond = quest.bonusCond.getConditions().find(condName)
            if not cond:
                continue
            curProgressData = quest.bonusCond.getProgress().get(None, {})
            totalValue = cond.getTotalValue()
            curProgres = curProgressData.get(cond.getKey(), 0) if not quest.isCompleted() else totalValue
            return (curProgres, totalValue)

        return (None, None)

    def __handleTokensUpdate(self, diff):
        for token in diff:
            if token.startswith(ArtefactsSettings.KEY_TOKEN):
                self.onArtefactKeyUpdated()
                continue
            if token.startswith(ArtefactsSettings.TOKEN_PREFIX):
                self.onArtefactStatusUpdated(token)
                if self._getConfig().get('openedSuffix', '') in token:
                    self._initArtefacts()

    def __onQuestsUpdated(self, _):
        self._initArtefacts()
        self.onArtefactSettingsUpdated()

    def __updateSettings(self):
        self._initArtefacts()
        self.onArtefactSettingsUpdated()
        self._rewardsSettings = self._getRewardsSettings()

    def __getArtefactKeyCost(self, artefactID):
        artefact = self.getArtefact(artefactID)
        if not artefact:
            return 0
        elif self.isArtefactOpened(artefactID):
            return 0
        else:
            if artefact.skipPrice.currency is not None and not self.isArtefactReceived(artefactID):
                amount = artefact.skipPrice.amount
            else:
                amount = artefact.decodePrice.amount
            return amount
