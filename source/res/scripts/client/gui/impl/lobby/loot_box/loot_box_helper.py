# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/loot_box/loot_box_helper.py
import logging
import weakref
from collections import namedtuple, OrderedDict
import BigWorld
from gui import SystemMessages
from gui.Scaleform.daapi.view.lobby.missions.awards_formatters import LootBoxBonusComposer
from gui.impl import backport
from gui.impl.auxiliary.rewards_helper import CrewBonusTypes, getRewardRendererModelPresenter, getVehByStyleCD, DEF_COMPENSATION_PRESENTERS, preparationRewardsCurrency, checkAndFillCustomizations, checkAndFillTokens, splitPremiumDays, checkAndFillVehicles, LootNewYearToyPresenter, LootNewYearFragmentsPresenter, LootVehicleVideoRewardPresenter, LootVideoWithCongratsRewardPresenter
from gui.impl.auxiliary.rewards_helper import getRewardTooltipContent
from gui.impl.gen import R
from gui.impl.gen.view_models.views.loot_box_view.loot_congrats_types import LootCongratsTypes
from gui.impl.lobby.loot_box.loot_box_sounds import playSound, LootBoxViewEvents
from gui.impl.new_year.tooltips.toy_content import RegularToyContent, MegaToyContent
from gui.server_events.awards_formatters import getLootboxesAutoOpenAwardsPacker, getNYAwardsPacker
from gui.server_events.bonuses import getNonQuestBonuses
from gui.shared import EVENT_BUS_SCOPE, event_dispatcher
from gui.shared import events
from gui.shared import g_eventBus
from gui.shared.event_dispatcher import showHangar, showStylePreview
from gui.shared.events import GameEvent
from gui.shared.money import Currency
from gui.shared.notifications import NotificationPriorityLevel
from helpers import dependency, isPlayerAccount
from items import new_year
from new_year.ny_constants import CURRENT_NY_TOYS_BONUS, CURRENT_NY_FRAGMENTS_BONUS
from skeletons.gui.customization import ICustomizationService
from skeletons.gui.shared import IItemsCache
MAX_BOXES_TO_OPEN = 5
ADDITIONAL_AWARDS_COUNT = 6
LOOT_BOX_REWARDS = 'lootBoxRewards'
_AUTO_MAX_COUNT = 99999
_BONUSES_ORDER = (CURRENT_NY_FRAGMENTS_BONUS,
 CURRENT_NY_TOYS_BONUS,
 Currency.CREDITS,
 Currency.GOLD,
 Currency.CRYSTAL,
 'slots',
 'customizations',
 'vehicles',
 'tankmen',
 'premium',
 'freeXP',
 'freeXPFactor',
 'creditsFactor',
 'items',
 'berths',
 'dossier',
 'goodies',
 'tokens',
 'blueprints',
 'crewSkins',
 CrewBonusTypes.CREW_BOOK_BONUSES,
 CrewBonusTypes.CREW_SKIN_BONUSES,
 'finalBlueprints')
_AUTO_OPEN_BONUSES_ORDER = (CURRENT_NY_FRAGMENTS_BONUS,
 'customizations',
 'vehicles',
 Currency.GOLD,
 Currency.CREDITS,
 'premium',
 'tmanToken')
SpecialRewardData = namedtuple('SpecialRewardData', ('sourceName', 'congratsType', 'congratsSourceId', 'vehicleName', 'vehicleLvl', 'vehicleIsElite', 'vehicleType'))
_MODEL_PRESENTERS = {'vehicles': LootVehicleVideoRewardPresenter(),
 'tmanToken': LootVideoWithCongratsRewardPresenter(LootCongratsTypes.CONGRAT_TYPE_TANKMAN),
 'customizations': LootVideoWithCongratsRewardPresenter(LootCongratsTypes.CONGRAT_TYPE_STYLE),
 CURRENT_NY_TOYS_BONUS: LootNewYearToyPresenter(),
 CURRENT_NY_FRAGMENTS_BONUS: LootNewYearFragmentsPresenter()}
_logger = logging.getLogger(__name__)

def showRestrictedSysMessage():

    def _showRestrictedSysMessage():
        SystemMessages.pushMessage(text=backport.text(R.strings.lootboxes.restrictedMessage.body()), type=SystemMessages.SM_TYPE.ErrorHeader, priority=NotificationPriorityLevel.HIGH, messageData={'header': backport.text(R.strings.lootboxes.restrictedMessage.header())})

    BigWorld.callback(0.0, _showRestrictedSysMessage)


@dependency.replace_none_kwargs(itemsCache=IItemsCache, c11nService=ICustomizationService)
def showStyledVehicleByStyleCD(styleIntCD, itemsCache=None, c11nService=None):
    vehicle = getVehByStyleCD(styleIntCD)
    style = itemsCache.items.getItemByCD(styleIntCD)
    if vehicle.isInInventory:

        def _callback():
            c11nService.getCtx().previewStyle(style, _ExitCallback())

        c11nService.showCustomization(vehicle.invID, _callback)
    else:

        def _callback():
            event_dispatcher.showHangar()
            _showLootBoxWindows()

        showStylePreview(vehicle.intCD, style, style.getDescription(), _callback, _closeLootBoxWindows, backBtnDescrLabel=backport.text(R.strings.vehicle_preview.header.backBtn.descrLabel.personalAwards()))
    _hideLootBoxWindows()


class LootBoxShowHideCloseHandler(object):
    __slots__ = ('__target',)

    def __init__(self):
        self.__target = None
        return

    def startListen(self, target):
        self.__target = weakref.proxy(target)
        g_eventBus.addListener(GameEvent.HIDE_LOOT_BOX_WINDOWS, self.__onHideLBWindow)
        g_eventBus.addListener(GameEvent.SHOW_LOOT_BOX_WINDOWS, self.__onShowLBWindow)
        g_eventBus.addListener(GameEvent.CLOSE_LOOT_BOX_WINDOWS, self.__onCloseLBWindow)

    def stopListen(self):
        self.__target = None
        g_eventBus.removeListener(GameEvent.HIDE_LOOT_BOX_WINDOWS, self.__onHideLBWindow)
        g_eventBus.removeListener(GameEvent.SHOW_LOOT_BOX_WINDOWS, self.__onShowLBWindow)
        g_eventBus.removeListener(GameEvent.CLOSE_LOOT_BOX_WINDOWS, self.__onCloseLBWindow)
        return

    def __onHideLBWindow(self, _=None):
        if self.__target:
            self.__target.hide()

    def __onShowLBWindow(self, _=None):
        if self.__target:
            self.__target.show()
            fireSpecialRewardsClosed()

    def __onCloseLBWindow(self, _=None):
        if self.__target:
            self.__target.destroy()


def getLootboxRendererModelPresenter(reward):
    return getRewardRendererModelPresenter(reward, _MODEL_PRESENTERS, DEF_COMPENSATION_PRESENTERS)


def showLootBoxMultyOpen(lootBoxItem, rewards, parent=None):
    from gui.impl.lobby.loot_box.loot_box_multi_open_view import LootBoxMultiOpenWindow
    window = LootBoxMultiOpenWindow(lootBoxItem, rewards, parent)
    window.load()


def showLootBoxReward(lootBoxItem, rewards, parent=None):
    from gui.impl.lobby.loot_box.loot_box_reward_view import LootBoxRewardWrapperWindow
    window = LootBoxRewardWrapperWindow(lootBoxItem, rewards, parent)
    window.load()


def fireHideRewardView():
    g_eventBus.handleEvent(events.LootboxesEvent(events.LootboxesEvent.ON_REWARD_VIEW_CLOSED), EVENT_BUS_SCOPE.LOBBY)


def fireCloseToHangar():
    playSound(LootBoxViewEvents.ENTRY_VIEW_EXIT)
    _closeLootBoxWindows()


def fireHideMultiOpenView():
    g_eventBus.handleEvent(events.LootboxesEvent(events.LootboxesEvent.ON_MULTI_OPEN_VIEW_CLOSED), EVENT_BUS_SCOPE.LOBBY)


def fireSpecialRewardsClosed():
    g_eventBus.handleEvent(events.LootboxesEvent(events.LootboxesEvent.ON_SHOW_SPECIAL_REWARDS_CLOSED), EVENT_BUS_SCOPE.LOBBY)


def showLootBoxSpecialReward(responseDict, parent=None):
    from gui.impl.lobby.loot_box.loot_box_special_reward_view import LootBoxSpecialRewardWindow
    congratsType = responseDict.get('congratsType')
    congratsSourceId = responseDict.get('congratsSourceId')
    sourceName = responseDict.get('sourceName')
    if sourceName and congratsSourceId is not None and congratsType is not None:
        specialRewardData = SpecialRewardData(sourceName=sourceName, congratsType=congratsType, congratsSourceId=int(congratsSourceId), vehicleName=responseDict.get('vehicleName'), vehicleIsElite=responseDict.get('vehicleIsElite'), vehicleLvl=responseDict.get('vehicleLvl'), vehicleType=responseDict.get('vehicleType'))
        window = LootBoxSpecialRewardWindow(specialRewardData, parent)
        window.load()
    return


def getTooltipContent(event, storedTooltipData):
    tooltipContent = getRewardTooltipContent(event, storedTooltipData)
    if tooltipContent is not None:
        return tooltipContent
    elif event.contentID == R.views.lobby.new_year.tooltips.ny_regular_toy_tooltip_content.NyRegularToyTooltipContent():
        toyID = event.getArgument('toyID')
        return RegularToyContent(toyID)
    elif event.contentID == R.views.lobby.new_year.tooltips.ny_mega_toy_tooltip_content.NyMegaToyTooltipContent():
        toyID = event.getArgument('toyID')
        return MegaToyContent(toyID)
    else:
        return


def getAutoOpenLootboxBonuses(rewards, size='big'):
    preparationRewardsCurrency(rewards)
    formatter = LootBoxBonusComposer(_AUTO_MAX_COUNT, getLootboxesAutoOpenAwardsPacker())
    bonuses = []
    if rewards:
        for bonusType, bonusValue in rewards.iteritems():
            if bonusType == 'premium':
                splitDays = splitPremiumDays(bonusValue)
                for day in splitDays:
                    bonus = getNonQuestBonuses(bonusType, day)
                    bonuses.extend(bonus)

            if bonusType == 'vehicles' and isinstance(bonusValue, list):
                for vehicleData in bonusValue:
                    bonus = getNonQuestBonuses(bonusType, vehicleData)
                    bonuses.extend(bonus)

            bonus = getNonQuestBonuses(bonusType, bonusValue)
            bonuses.extend(bonus)

    bonuses.sort(key=_autoOpenKeySortOrder)
    return formatter.getFormattedBonuses(bonuses, size)


def getLootboxBonuses(rewards, size='big', maxAwardCount=ADDITIONAL_AWARDS_COUNT):
    preparationRewardsCurrency(rewards)
    specialRewardType = ''
    formatter = LootBoxBonusComposer(maxAwardCount, getNYAwardsPacker())
    bonuses = []
    alwaysVisibleBonuses = []
    if rewards:
        for bonusType, bonusValue in rewards.iteritems():
            if bonusType == 'vehicles' and isinstance(bonusValue, list):
                for vehicleData in bonusValue:
                    bonus = getNonQuestBonuses(bonusType, vehicleData)
                    if checkAndFillVehicles(bonus, alwaysVisibleBonuses, bonuses):
                        specialRewardType = LootCongratsTypes.CONGRAT_TYPE_VEHICLE

            if bonusType == 'customizations':
                bonus = getNonQuestBonuses(bonusType, bonusValue)
                if checkAndFillCustomizations(bonus, alwaysVisibleBonuses, bonuses):
                    specialRewardType = LootCongratsTypes.CONGRAT_TYPE_STYLE
            if bonusType == 'tokens':
                bonus = getNonQuestBonuses(bonusType, bonusValue)
                if checkAndFillTokens(bonus, alwaysVisibleBonuses, bonuses):
                    specialRewardType = LootCongratsTypes.CONGRAT_TYPE_TANKMAN
            if bonusType == 'premium':
                splitDays = splitPremiumDays(bonusValue)
                for day in splitDays:
                    bonus = getNonQuestBonuses(bonusType, day)
                    bonuses.extend(bonus)

            if bonusType == CURRENT_NY_TOYS_BONUS:
                orderedToys = _getToysSortedByRank(bonusValue)
                bonus = getNonQuestBonuses(bonusType, orderedToys)
                bonuses.extend(bonus)
            bonus = getNonQuestBonuses(bonusType, bonusValue)
            bonuses.extend(bonus)

        bonuses.sort(key=_keySortOrder)
        _handlePremTankSpecialCase(bonuses)
    formattedBonuses = formatter.getVisibleFormattedBonuses(bonuses, alwaysVisibleBonuses, size)
    return (formattedBonuses, specialRewardType)


def worldDrawEnabled(value):
    if isPlayerAccount():
        BigWorld.worldDrawEnabled(value)


def _getToysSortedByRank(toys):
    ordered = OrderedDict()
    sortedList = sorted(toys.iteritems(), cmp=_sortToysByRank, reverse=True)
    for toy in sortedList:
        ordered[toy[0]] = toy[1]

    return ordered


def _sortToysByRank(toy1, toy2):
    toyDescr1 = new_year.g_cache.toys.get(toy1[0])
    toyDescr2 = new_year.g_cache.toys.get(toy2[0])
    return cmp(toyDescr1.rank, toyDescr2.rank)


class _ExitCallback(object):
    _c11nService = dependency.descriptor(ICustomizationService)

    def __init__(self):
        self.__wasCalled = False

    def apply(self):
        if not self.__wasCalled:
            _showLootBoxWindows()
            self.__wasCalled = True

    def close(self):
        if not self.__wasCalled:
            self._c11nService.getCtx().onCloseWindow()
            _showLootBoxWindows()
            self.__wasCalled = True

    def destroy(self):
        if not self.__wasCalled:
            _closeLootBoxWindows()
            self.__wasCalled = True


def _goHangarAndRestoreLootboxWindows():
    showHangar()
    _showLootBoxWindows()


def _showLootBoxWindows():
    playSound(LootBoxViewEvents.ENTRY_VIEW_ENTER)
    g_eventBus.handleEvent(GameEvent(GameEvent.SHOW_LOOT_BOX_WINDOWS))
    worldDrawEnabled(False)


def _hideLootBoxWindows():
    worldDrawEnabled(True)
    playSound(LootBoxViewEvents.ENTRY_VIEW_EXIT)
    g_eventBus.handleEvent(GameEvent(GameEvent.HIDE_LOOT_BOX_WINDOWS))


def _closeLootBoxWindows():
    worldDrawEnabled(True)
    g_eventBus.handleEvent(GameEvent(GameEvent.CLOSE_LOOT_BOX_WINDOWS))


def _keySortOrder(bonus):
    return _BONUSES_ORDER.index(bonus.getName()) if bonus.getName() in _BONUSES_ORDER else len(_BONUSES_ORDER)


def _autoOpenKeySortOrder(bonus):
    if bonus.getName() in _AUTO_OPEN_BONUSES_ORDER:
        return _AUTO_OPEN_BONUSES_ORDER.index(bonus.getName())
    addIndex = 1 if bonus.getName() == CURRENT_NY_TOYS_BONUS else 0
    return len(_AUTO_OPEN_BONUSES_ORDER) + addIndex


def _handlePremTankSpecialCase(bonuses):
    premTankIndex = -1
    slotsIndex = -1
    for bonus in bonuses:
        if bonus.getName() == 'vehicles':
            premTankIndex = bonuses.index(bonus)
        if bonus.getName() == 'slots':
            slotsIndex = bonuses.index(bonus)

    if premTankIndex > -1:
        slotBonus = bonuses.pop(slotsIndex)
        bonuses.insert(premTankIndex, slotBonus)
