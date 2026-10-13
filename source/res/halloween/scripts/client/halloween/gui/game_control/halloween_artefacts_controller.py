# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: halloween/scripts/client/halloween/gui/game_control/halloween_artefacts_controller.py
from __future__ import absolute_import
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
from gui.prb_control.events_dispatcher import g_eventDispatcher
from gui.shared.utils import decorators
from constants import EVENT_CLIENT_DATA, PREMIUM_ENTITLEMENTS
from gui.server_events.bonuses import getNonQuestBonuses, VehiclesBonus, mergeBonuses, CustomizationsBonus, NationalBlueprintBonus, IntelligenceBlueprintBonus
from gui.shared.gui_items.Vehicle import Vehicle
from gui.shared.gui_items import GUI_ITEM_TYPE
from halloween.gui.halloween_gui_constants import FUNCTIONAL_FLAG
from halloween.gui.shared.gui_items.processors.processors import OpenArtefactProcessor
from halloween.skeletons.halloween_controller import IHalloweenController
from halloween.skeletons.halloween_artefacts_controller import IHalloweenArtefactsController
from halloween.skeletons.halloween_twitch_con_controller import IHalloweenTwitchConController
from halloween_common.halloween_constants import ArtefactsSettings, ArtefactType, RENT_VEHICLE_PREFIX, ARTEFACT_ID_MASK, HWStoryChoiceSettings
from halloween.gui.server_events.bonuses import CerfTokenBonus
from helpers import dependency
from items.components.c11n_constants import Rarity
from skeletons.account_helpers.settings_core import ISettingsCore
from skeletons.gui.customization import ICustomizationService
from skeletons.gui.server_events import IEventsCache
from skeletons.gui.shared import IItemsCache
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
PHASE_COMPLETION_QUEST_BR_CONDITION = ('halloween_phase', 'greater')
TOTAL_PHASE_COUNT = 4
_blueprints_national_order = [ str('blueprint_national_' + nation) for nation in GUI_NATIONS ]
BONUS_ORDER = ['lootBox',
 'dossier',
 HWStoryChoiceSettings.FAKE_MEDAL,
 'vehicles',
 'slots',
 'cerfToken',
 'tmanToken',
 'tankmen',
 'crewSkins',
 ArtefactsSettings.CREW_100,
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

class Artefact(namedtuple('Artefact', ('artefactID', 'decodePrice', 'skipPrice', 'bonusRewards', 'questConditions', 'artefactTypes'))):

    def getCtx(self):
        return dict(self._asdict())


def getTokenValue(bonus):
    token = first(bonus.getTokens().keys(), '')
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


def isArtefactQuest(qID):
    return qID.startswith(ArtefactsSettings.QUEST_PREFIX)


class HalloweenArtefactsController(IHalloweenArtefactsController, IGlobalListener):
    itemsCache = dependency.descriptor(IItemsCache)
    eventsCache = dependency.descriptor(IEventsCache)
    settingsCore = dependency.descriptor(ISettingsCore)
    halloweenCtrl = dependency.descriptor(IHalloweenController)
    c11n = dependency.descriptor(ICustomizationService)
    twitchConCtrl = dependency.descriptor(IHalloweenTwitchConController)

    def __init__(self):
        super(HalloweenArtefactsController, self).__init__()
        self.onArtefactStatusUpdated = Event.Event()
        self.onArtefactKeyUpdated = Event.Event()
        self.onArtefactSettingsUpdated = Event.Event()
        self._artefacts = {}
        self._selectedArtefactID = None
        self._needSelectNextSlide = False
        self._choiceID = None
        return

    def fini(self):
        self.stopGlobalListening()
        g_clientUpdateManager.removeObjectCallbacks(self)
        self.halloweenCtrl.onSettingsUpdate -= self.__updateSettings
        self.onArtefactStatusUpdated.clear()
        self.onArtefactKeyUpdated.clear()
        self.onArtefactSettingsUpdated.clear()
        self._artefacts = {}
        self._selectedArtefactID = None
        self._needSelectNextSlide = False
        return

    def isEnabled(self):
        return self._getConfig().get('enabled', False)

    def onDisconnected(self):
        super(HalloweenArtefactsController, self).onDisconnected()
        self._selectedArtefactID = None
        self._needSelectNextSlide = False
        self.stopGlobalListening()
        return

    def onAvatarBecomePlayer(self):
        super(HalloweenArtefactsController, self).onAvatarBecomePlayer()
        self._needSelectNextSlide = False
        self.stopGlobalListening()

    def onLobbyInited(self, event):
        super(HalloweenArtefactsController, self).onLobbyInited(event)
        self.startGlobalListening()
        g_clientUpdateManager.addCallbacks({'tokens': self.__handleTokensUpdate,
         'eventsData.' + str(EVENT_CLIENT_DATA.QUEST): self.__onQuestsUpdated})
        self.halloweenCtrl.onSettingsUpdate += self.__updateSettings

    def onLobbyStarted(self, ctx):
        super(HalloweenArtefactsController, self).onLobbyStarted(ctx)
        self._needSelectNextSlide = False
        self._initArtefacts()

    def onPrbEntitySwitched(self):
        if self.prbEntity.getModeFlags() & FUNCTIONAL_FLAG.HALLOWEEN:
            return
        self._needSelectNextSlide = False

    @property
    def needSelectNextSlide(self):
        return self._needSelectNextSlide

    @needSelectNextSlide.setter
    def needSelectNextSlide(self, value):
        self._needSelectNextSlide = value

    @property
    def selectedArtefactID(self):
        return self._selectedArtefactID if self._selectedArtefactID in self._artefacts else None

    @selectedArtefactID.setter
    def selectedArtefactID(self, artefactID):
        self._selectedArtefactID = artefactID

    def artefactsSorted(self):
        return sorted(self._artefacts.values(), key=lambda artefact: self.getIndex(artefact.artefactID))

    def regularArtefacts(self):
        return self.artefactsSorted()[:-1]

    def getFinalArtefact(self):
        return next((x for x in self._artefacts.values() if ArtefactType.FINAL in x.artefactTypes), None)

    def getOpenedArtefactToken(self, artefactID):
        return artefactID + self._getConfig().get('openedSuffix', '')

    def geArtefactIDFromOpenToken(self, token):
        return token.replace(self._getConfig().get('openedSuffix', ''), '')

    def isFinalArtefact(self, artefect):
        return ArtefactType.FINAL in artefect.artefactTypes

    def getArtefact(self, artefactID):
        return self._artefacts.get(artefactID)

    def isArtefactOpened(self, artefactID):
        openedTokenID = self.getOpenedArtefactToken(artefactID)
        return self.eventsCache.questsProgress.getTokenCount(openedTokenID) > 0

    def isArtefactReceived(self, artefactID):
        return self.eventsCache.questsProgress.getTokenCount(artefactID) > 0

    def setChoice(self, choiceID):
        self._choiceID = choiceID

    def getChoiceID(self):
        return self._choiceID

    def getArtefactKeyQuantity(self):
        return self.eventsCache.questsProgress.getTokenCount(ArtefactsSettings.KEY_TOKEN)

    def getCurrentArtefactProgress(self):
        return sum(list((int(self.isArtefactOpened(artefactID)) for artefactID in self._artefacts)))

    def getAvailableArtefactProgress(self):
        return sum(list((int(self.isArtefactReceived(artefactID)) for artefactID in self._artefacts)))

    def getMaxArtefactsProgress(self):
        return len(self._artefacts) - 1

    def getArtefactsCount(self):
        return len(self._artefacts)

    def getMainGiftVehicle(self):
        finalArtefact = self.getFinalArtefact()
        if not finalArtefact:
            return None
        else:
            for bonus in finalArtefact.bonusRewards:
                if not isinstance(bonus, VehiclesBonus):
                    continue
                vehiclesBonuses = bonus.getVehicles()
                mainVehicleBonus = vehiclesBonuses[0] if vehiclesBonuses else []
                return next((b for b in mainVehicleBonus if isinstance(b, Vehicle)), None)

            return None

    def getMainGiftStyle(self):
        finalArtefact = self.getFinalArtefact()
        if not finalArtefact:
            return None
        else:
            for bonus in finalArtefact.bonusRewards:
                if not isinstance(bonus, CustomizationsBonus):
                    continue
                bonuses = bonus.getList()
                for item in bonuses:
                    customization = self.itemsCache.items.getItemByCD(item.get('intCD', 0))
                    if customization and customization.itemTypeID == GUI_ITEM_TYPE.STYLE:
                        return customization

            return None

    def getRareAttachmentsFromArtefact(self, artefactID):
        artefact = self.getArtefact(artefactID)
        if not artefact:
            return []
        attachments = []
        for bonus in artefact.bonusRewards:
            if not isinstance(bonus, CustomizationsBonus):
                continue
            bonuses = bonus.getList()
            for item in bonuses:
                c11nItem = self.c11n.getItemByCD(item.get('intCD', 0))
                if c11nItem and c11nItem.itemTypeID == GUI_ITEM_TYPE.ATTACHMENT and c11nItem.rarity in Rarity.UI_EFFECT:
                    attachments.append(c11nItem)

        return attachments

    def isArtefactHasTwitchConCertificate(self, artefactID):
        artefact = self.getArtefact(artefactID)
        if not artefact:
            return False
        for bonus in artefact.bonusRewards:
            if not isinstance(bonus, CerfTokenBonus):
                continue
            return self.twitchConCtrl.getCertificateTokenName() in bonus.getTokens()

        return False

    def isExistUnreceivedTwitchConCertificate(self):
        return any((not self.isArtefactOpened(artefactID) and self.isArtefactHasTwitchConCertificate(artefactID) for artefactID in self._artefacts))

    def getArtefactIDForAccessToVehicle(self, vehTypeCD):
        for artefactID, artefact in self._getArtefacts().items():
            accessToVehicle = artefact.get('accessToVehicle')
            if accessToVehicle == vehTypeCD:
                return artefactID

        return None

    def getLackOfKeysForArtefact(self, artefactID):
        return max(0, self.__getArtefactKeyCost(artefactID) - self.getArtefactKeyQuantity())

    def getLackOfKeysForArtefacts(self):
        keysCount = 0
        for artefactID in self._artefacts:
            keysCount += self.__getArtefactKeyCost(artefactID)

        return max(0, keysCount - self.getArtefactKeyQuantity())

    def getQuest(self, questID):
        return self.eventsCache.getHiddenQuests(lambda q: q.getID() in [questID]).get(questID)

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

    def resetSelectedArtefactID(self):
        self._selectedArtefactID = None
        return

    def _initArtefacts(self):
        quests = self.eventsCache.getAllQuests(lambda q: isArtefactQuest(q.getID()))
        self._artefacts = dict(((artefactID, Artefact(artefactID, ArtefactPrice(*self._getArtefactPrice(artefactID)), ArtefactPrice(*self._getArtefactQuestSkipPrice(artefactID)), self._getArtefactBonuses(artefactID, quests), self._getArtefactQuestConditions(artefactID, quests), self._getArtefactTypes(artefactID))) for artefactID in self._getArtefacts().keys()))

    def _getArtefactTypes(self, artefactID):
        return self._getArtefacts().get(artefactID, {}).get('type', [])

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
        if ArtefactType.FINAL in self._getArtefactTypes(artefactID):
            quest = quests.get(artefactID)
            if quest:
                return sorted(quest.getBonuses(), key=getBonusPriority)
            return []
        rewards = []
        artefactConfig = self._getArtefacts().get(artefactID, {})
        bonusesConfig = artefactConfig.get('bonus', {})
        accessToVehicle = artefactConfig.get('accessToVehicle')
        if accessToVehicle:
            rentTime = self._getRentConfig().get('time', 0)
            opendSuffix = self._getRentConfig().get('openedSuffix')
            shopSuffix = self._getRentConfig().get('shopSuffix')
            vehiclesConfig = self._getRentConfig().get('vehicles', {})
            accessShopToken = vehiclesConfig.get(accessToVehicle, {}).get(shopSuffix, 'hw25_unknown')
            accessOpenToken = vehiclesConfig.get(accessToVehicle, {}).get(opendSuffix)
            if not self.eventsCache.questsProgress.getTokenCount(accessShopToken) > 0 or self.eventsCache.questsProgress.getTokenCount(accessOpenToken) > 0:
                rewards.extend(getNonQuestBonuses(VehiclesBonus.VEHICLES_BONUS, {accessToVehicle: {'rent': {'time': rentTime}}}))
        for bonusType, bonusValue in bonusesConfig.items():
            rewards.extend(getNonQuestBonuses(bonusType, bonusValue))

        questsToRun = artefactConfig.get('questsToRun')
        if questsToRun:
            quests = self.eventsCache.getHiddenQuests(lambda q: q.getID() in questsToRun)
            if quests:
                rewards.extend(itertools.chain.from_iterable((q.getBonuses() for q in quests.values())))
        sortedBonuses = sorted(mergeBonuses(rewards), key=getBonusPriority)
        return sortedBonuses

    def _getConfig(self):
        return self.halloweenCtrl.getModeSettings().artefactsSettings

    def _getRentConfig(self):
        return self.halloweenCtrl.getModeSettings().rent

    def _getArtefacts(self):
        return self._getConfig().get('artefacts', {})

    def __getFirstQuestProgress(self, quest):
        for condName in QUEST_BONUS_CONDITIONS:
            cond = quest.bonusCond.getConditions().find(condName)
            if not cond:
                continue
            curProgressData = quest.bonusCond.getProgress().get(None, {})
            totalValue = cond.getTotalValue()
            curProggres = curProgressData.get(cond.getKey(), 0) if not quest.isCompleted() else totalValue
            return (curProggres, totalValue)

        return (0, 1)

    def __handleTokensUpdate(self, diff):
        for token in diff:
            if token.startswith(ArtefactsSettings.KEY_TOKEN):
                self.onArtefactKeyUpdated()
                continue
            if token.startswith(ArtefactsSettings.TOKEN_PREFIX):
                self.onArtefactStatusUpdated(token)
            if token.startswith(RENT_VEHICLE_PREFIX):
                self._initArtefacts()
                self.onArtefactSettingsUpdated()
                g_eventDispatcher.updateUI()

    def __onQuestsUpdated(self, _):
        self._initArtefacts()
        self.onArtefactSettingsUpdated()

    def __updateSettings(self):
        self._initArtefacts()
        self.onArtefactSettingsUpdated()

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
