# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/secret_event/__init__.py
import logging
import re
from collections import OrderedDict, namedtuple
from functools import partial
import BigWorld
import gui.server_events as server_events
from PlayerEvents import g_playerEvents
from adisp import process
from constants import EventPackTypes
from gui.Scaleform.daapi.settings.views import VIEW_ALIAS
from gui.Scaleform.daapi.view.lobby.missions.awards_formatters import LinkedSetAwardsComposer
from gui.Scaleform.daapi.view.lobby.missions.cards_formatters import MissionBonusAndPostBattleCondFormatter
from gui.Scaleform.genConsts.TOOLTIPS_CONSTANTS import TOOLTIPS_CONSTANTS
from gui.app_loader.decorators import sf_lobby
from gui.impl.backport.backport_tooltip import BackportTooltipWindow, createTooltipData
from gui.impl.gen import R
from gui.impl.gen.view_models.views.lobby.secret_event.action_menu_model import ActionMenuModel
from gui.impl.gen.view_models.views.lobby.secret_event.characteristics_skill_model import CharacteristicsSkillModel
from gui.impl.gen.view_models.views.lobby.secret_event.reward_model import RewardModel
from gui.prb_control.entities.base.ctx import PrbAction
from gui.prb_control.entities.base.listener import IPrbListener
from gui.prb_control.settings import PREBATTLE_ACTION_NAME
from gui.server_events.awards_formatters import AWARDS_SIZES, AwardsPacker, getLinkedSetFormattersMap, DossierBonusFormatter
from gui.server_events.events_helpers import isSecretEvent
from gui.shared import g_eventBus, events, EVENT_BUS_SCOPE
from gui.shared.money import Money
from gui.shared.utils.functions import getAbsoluteUrl
from helpers import dependency
from helpers.i18n import makeString
from items import vehicles
from shared_utils import first
from skeletons.gui.game_event_controller import IGameEventController
from skeletons.gui.server_events import IEventsCache
from skeletons.gui.shared import IItemsCache
_logger = logging.getLogger(__name__)

class BaseTabSettings(object):

    def __init__(self, tabID, name, tooltipHeader, tooltipDesc, layoutID, viewClass, isBlur):
        self.id = tabID
        self.name = name
        self.tooltipHeader = tooltipHeader
        self.tooltipDesc = tooltipDesc
        self.layoutID = layoutID
        self.viewClass = viewClass
        self.isBlur = isBlur

    @property
    def isNotification(self):
        return False


class BerlinTabSettings(BaseTabSettings):

    @property
    def isNotification(self):
        event = dependency.instance(IGameEventController)
        return event.isBerlinStarted() and not event.istBerlinTabShown()


def getTabs():
    from gui.impl.lobby.secret_event.action_about_view import ActionAboutView
    from gui.impl.lobby.secret_event.action_hangar_view import ActionHangarView
    from gui.impl.lobby.secret_event.action_missions_view import ActionMissionsView
    from gui.impl.lobby.secret_event.action_subdivision_view import ActionSubdivisionView
    from gui.impl.lobby.secret_event.action_berlin_view import ActionBerlinView
    from gui.impl.lobby.secret_event.action_order_view import ActionOrderView
    return OrderedDict([(ActionMenuModel.BASE, BaseTabSettings(ActionMenuModel.BASE, R.strings.event.menu.base(), R.strings.event.menu.base.header(), R.strings.event.menu.base.desc(), R.views.lobby.secretEvent.ActionHangarWindow(), ActionHangarView, False)),
     (ActionMenuModel.MISSION, BaseTabSettings(ActionMenuModel.MISSION, R.strings.event.menu.mission(), R.strings.event.menu.mission.header(), R.strings.event.menu.mission.desc(), R.views.lobby.secretEvent.ActionMissionsWindow(), ActionMissionsView, True)),
     (ActionMenuModel.SUBDIVISION, BaseTabSettings(ActionMenuModel.SUBDIVISION, R.strings.event.menu.subdivision(), R.strings.event.menu.subdivision.header(), R.strings.event.menu.subdivision.desc(), R.views.lobby.secretEvent.UnitsWindow(), ActionSubdivisionView, True)),
     (ActionMenuModel.ORDERS, BaseTabSettings(ActionMenuModel.ORDERS, R.strings.event.menu.orders(), R.strings.event.menu.orders.header(), R.strings.event.menu.orders.desc(), R.views.lobby.secretEvent.ActionOrderWindow(), ActionOrderView, True)),
     (ActionMenuModel.SHOP, BaseTabSettings(ActionMenuModel.SHOP, R.strings.event.menu.shop(), R.strings.event.menu.shop.header(), R.strings.event.menu.shop.desc(), None, None, False)),
     (ActionMenuModel.ABOUT, BaseTabSettings(ActionMenuModel.ABOUT, R.strings.event.menu.about(), R.strings.event.menu.about.header(), R.strings.event.menu.about.desc(), R.views.lobby.secretEvent.ActionAboutWindow(), ActionAboutView, False)),
     (ActionMenuModel.BERLIN, BerlinTabSettings(ActionMenuModel.BERLIN, R.strings.event.menu.berlin(), R.strings.event.menu.berlin.header(), R.strings.event.menu.berlin.desc(), R.views.lobby.secretEvent.ActionBerlinWindow(), ActionBerlinView, False))])


def convertPriceToMoney(currency, amount):
    return Money(**{currency: amount})


def convertPriceToTuple(currency, amount):
    price = Money(**{currency: amount})
    return (price.credits, price.gold, price.crystal)


class SE20DossierBonusFormatter(DossierBonusFormatter):

    @classmethod
    def _getImages(cls, bonus):
        return {AWARDS_SIZES.SMALL: bonus.getIcon48x48(),
         AWARDS_SIZES.BIG: bonus.getBig80x80Icon()}


class SE20RewardComposer(LinkedSetAwardsComposer):

    def __init__(self, displayedAwardsCount, awardsFormatter=None):
        if awardsFormatter is None:
            mapping = getLinkedSetFormattersMap()
            mapping.update(dossier=SE20DossierBonusFormatter())
            awardsFormatter = AwardsPacker(mapping)
        super(SE20RewardComposer, self).__init__(displayedAwardsCount, awardsFormatter)
        return

    PRIORITY_REWARDS = ['premium_plus', 'battleToken', 'vehicles']

    def _packBonus(self, bonus, size=AWARDS_SIZES.SMALL):
        result = super(SE20RewardComposer, self)._packBonus(bonus, size=size)
        if bonus.label == 'x1':
            result['label'] = ''
        result['highlightIcon'] = bonus.getHighlightIcon(size)
        result['overlayIcon'] = bonus.getOverlayIcon(size)
        return result

    def getPreformattedBonuses(self, bonuses):
        return sorted(super(SE20RewardComposer, self).getPreformattedBonuses(bonuses), key=lambda bonus: bonus.bonusName not in self.PRIORITY_REWARDS)

    def _packBonuses(self, preformattedBonuses, size):
        mergedBonuses = []
        if len(preformattedBonuses) > self._displayedRewardsCount:
            displayBonuses = []
            for bonus in preformattedBonuses:
                (displayBonuses if bonus.bonusName in self.PRIORITY_REWARDS else mergedBonuses).append(bonus)

        else:
            displayBonuses = preformattedBonuses
        result = [ self._packBonus(bonus, size) for bonus in displayBonuses ]
        if mergedBonuses:
            result.append(self._packMergedBonuses(mergedBonuses, AWARDS_SIZES.BIG))
        return result

    @classmethod
    def _getShortBonusesData(cls, preformattedBonuses, size=AWARDS_SIZES.SMALL):
        return [ {'name': bonus.userName,
         'label': bonus.getFormattedLabel() if bonus.label != 'x1' else '',
         'imgSource': bonus.getImage(size),
         'highlightIcon': bonus.getHighlightIcon(size),
         'overlayIcon': bonus.getOverlayIcon(size)} for bonus in preformattedBonuses ]


class RewardListMixin(object):
    DEFAULT_REWARD_CACHE_KEY = -1
    REWARD_TOOLTIPID_TEMPLATE = 'rewardTooltip_{:d}_{:d}'
    REWARD_TOOLTIPID_REGEXP = re.compile(REWARD_TOOLTIPID_TEMPLATE.replace('{:d}', '(-?\\d*)'))
    MAX_REWARDS_LIST_COUNT = 3
    _eventsCache = dependency.descriptor(IEventsCache)
    _gameEventController = dependency.descriptor(IGameEventController)

    def __init__(self):
        self.__rewardCache = {}
        self.__bonusRewards = {}

    def getRewards(self, gameEventItem, cacheKey=None, iconSizes=(AWARDS_SIZES.BIG,)):
        cacheKey = cacheKey if cacheKey is not None else self.DEFAULT_REWARD_CACHE_KEY
        iconSizes = iconSizes or (AWARDS_SIZES.BIG,)
        for size in iconSizes:
            rewards = self.__rewardCache.get(cacheKey, {}).get(size)
            if rewards and cacheKey is self.DEFAULT_REWARD_CACHE_KEY:
                _logger.warning('Get cache by default key')
            if rewards is None and gameEventItem:
                rewards = SE20RewardComposer(self.MAX_REWARDS_LIST_COUNT).getFormattedBonuses(gameEventItem.getBonuses(), size)
                self.__rewardCache.setdefault(cacheKey, {})[size] = rewards

        size = iconSizes[0]
        rewards = self.__rewardCache.get(cacheKey, {}).get(size, [])
        if not rewards:
            _logger.error('No rewards for: %s, by: %s', gameEventItem, (cacheKey, size))
        return rewards

    def getReward(self, gameEventItem, idx, cacheKey=None):
        rewards = self.getRewards(gameEventItem, cacheKey)
        return rewards[idx] if len(rewards) > idx else None

    def createToolTip(self, event):
        tooltipId = event.getArgument('tooltipId')
        searchResult = self.REWARD_TOOLTIPID_REGEXP.search(tooltipId)
        if searchResult:
            cacheKey, idx = map(int, searchResult.groups())
            reward = self.getReward(None, idx, cacheKey)
            if reward:
                window = BackportTooltipWindow(createTooltipData(tooltip=reward.get('tooltip'), isSpecial=reward['isSpecial'], specialAlias=reward['specialAlias'], specialArgs=reward['specialArgs']), self.getParentWindow())
                window.load()
                return window
        return

    @classmethod
    def fillStubRewardList(cls, listModel, rewards, completed=False, cacheKey=None):
        cls.fillStubRewardListWithIndex(listModel, enumerate(rewards), completed, cacheKey)

    @classmethod
    def fillStubRewardListWithIndex(cls, listModel, indexedRewards, completed=False, cacheKey=None):
        listModel.clearItems()
        cacheKey = cacheKey if cacheKey is not None else cls.DEFAULT_REWARD_CACHE_KEY
        for idx, reward in indexedRewards:
            rewardVM = RewardModel()
            cls.fillReward(reward, rewardVM, idx, completed, cacheKey)
            listModel.addViewModel(rewardVM)

        listModel.invalidate()
        return

    @classmethod
    def fillReward(cls, reward, rewardVM, idx, completed=False, cacheKey=None):
        rewardVM.setId(idx)
        rewardVM.setTooltipId(cls.REWARD_TOOLTIPID_TEMPLATE.format(cacheKey, idx))
        rewardVM.setIcon(getAbsoluteUrl(reward['imgSource']))
        highlightIcon = reward.get('highlightIcon')
        if highlightIcon:
            rewardVM.setHighlightIcon(getAbsoluteUrl(highlightIcon))
        overlayIcon = reward.get('overlayIcon')
        if overlayIcon:
            rewardVM.setOverlayIcon(getAbsoluteUrl(overlayIcon))
        rewardVM.setCompleted(completed)
        rewardVM.setLabelCount(reward['label'])

    def _finalize(self):
        self.__rewardCache = {}


class ProgressMixin(object):
    ProgressionData = namedtuple('ProgressionData', 'gameEventItem currentProgress maxProgress level isCompleted isAvailable')

    @classmethod
    def getCommonProgressionData(cls, gameEventProgress):
        return cls.ProgressionData(gameEventProgress, gameEventProgress.getCurrentProgress(), gameEventProgress.getTotalProgress(), gameEventProgress.getCurrentProgressLevel(), gameEventProgress.isCompleted(), any((item.isAvailable() for item in gameEventProgress.getItems())))

    @classmethod
    def getCurrenProgresstItem(cls, gameEventProgress):
        return gameEventProgress.getNextProgressItem() or gameEventProgress.getCurrentProgressItem()

    @classmethod
    def getCurrentProgressionData(cls, gameEventProgress, fixLevel=True):
        return cls.getProgressionData(cls.getCurrenProgresstItem(gameEventProgress), fixLevel)

    @classmethod
    def getProgressionData(cls, gameEventItem, fixLevel=False):
        return cls.ProgressionData(gameEventItem, gameEventItem.getCurrentProgress(), gameEventItem.getMaxProgress(), gameEventItem.getLevel() + (fixLevel & gameEventItem.isCompleted()), gameEventItem.isCompleted(), gameEventItem.isAvailable())

    @classmethod
    def getAllProgressionData(cls, gameEventProgress):
        return [ cls.getProgressionData(gameEventItem) for gameEventItem in gameEventProgress.getItems()[1:] ]


class VehicleMixin(object):
    VehicleData = namedtuple('VehicleData', 'typeCompDescr vehicle level isCurrent isUnlocked')

    @classmethod
    def getVehicleDataByLevel(cls, gameEventProgress, level, curentLevel=None):
        typeCompDescr = first(gameEventProgress.getVehiclesByLevel(level))
        if typeCompDescr is not None:
            currentLevel = curentLevel or gameEventProgress.getCurrentProgressLevel()
            vehicle = gameEventProgress.getVehicle(typeCompDescr)
            return cls.VehicleData(typeCompDescr, vehicle, level + 1, currentLevel == level, currentLevel >= level)
        else:
            return

    @classmethod
    def getVehicleData(cls, gameEventProgress, curentLevel=None):
        return [ cls.getVehicleDataByLevel(gameEventProgress, level, curentLevel) for level in xrange(gameEventProgress.getMaxLevel() + 1) ]


class AbilitiesMixin(object):
    AbilitiesData = namedtuple('AbilitiesData', 'id_ icon iconDynAccessor name description isEnabled level')
    ICON_PATH = '../maps/icons/secretEvent/abilities/{0}.png'
    NO_IMAGE_NAME = 'noImage'
    NO_IMAGE_ICON = R.images.gui.maps.icons.secretEvent.abilities.dyn(NO_IMAGE_NAME)

    @classmethod
    def _getAbilityLevel(cls, abilityName):
        level = abilityName[-1]
        return 1 if not level.isdigit() else int(level)

    @classmethod
    def getAbilitiesData(cls, gameEventProgress, maxLevel=None, currentLevel=None):
        maxLevel = maxLevel if maxLevel is not None else gameEventProgress.getMaxLevel()
        currentLevel = currentLevel if currentLevel is not None else gameEventProgress.getCurrentProgressLevel()
        currentAbilities = gameEventProgress.getAbilitiesByLevel(currentLevel)
        allAbilities = gameEventProgress.getAbilitiesByLevel(maxLevel)
        abilities = []
        for id_, _ in enumerate(allAbilities):
            abilityID = currentAbilities[id_] if len(currentAbilities) > id_ else allAbilities[id_]
            abilityDescr = vehicles.g_cache.equipments()[abilityID]
            iconDynAccessor = R.images.gui.maps.icons.secretEvent.abilities.c_48x48.dyn(abilityDescr.iconName, cls.NO_IMAGE_ICON)
            icon = cls.ICON_PATH.format(cls.NO_IMAGE_NAME if iconDynAccessor is cls.NO_IMAGE_ICON else abilityDescr.iconName)
            abilities.append(cls.AbilitiesData(abilityID, icon, iconDynAccessor, makeString(abilityDescr.userString), makeString(abilityDescr.description), len(currentAbilities) > id_, cls._getAbilityLevel(abilityDescr.name)))

        return abilities

    @classmethod
    def fillAbilitiesList(cls, listModel, gameEventProgress, maxLevel=None, currentLevel=None):
        listModel.clearItems()
        for abilitiesData in cls.getAbilitiesData(gameEventProgress, maxLevel, currentLevel):
            item = CharacteristicsSkillModel()
            item.setId(abilitiesData.id_)
            item.setSkillName(abilitiesData.name)
            item.setSkillDescription(abilitiesData.description)
            item.setIcon(abilitiesData.iconDynAccessor())
            item.setIsEnabled(abilitiesData.isEnabled)
            listModel.addViewModel(item)

        listModel.invalidate()


class SEConditionFormatter(MissionBonusAndPostBattleCondFormatter):

    def _getFormattedField(self, *args, **kwargs):
        pass

    def _packCondition(self, *args, **kwargs):
        pass

    def _packConditions(self, *args, **kwargs):
        pass

    @classmethod
    def _packSeparator(cls, key):
        pass


class EnergyMixin(IPrbListener):
    _eventsCache = dependency.descriptor(IEventsCache)
    _itemsCache = dependency.descriptor(IItemsCache)
    _condFormatter = SEConditionFormatter()
    _energyTypes = {}
    EnergyData = namedtuple('EnergyData', 'id_ currentCount maxCount nextRechargeTime nextRechargeCount hangarIcon hangarIcon96x96 hangarIcon192x192 tooltipId isSelected orderType modifier hangarIcon250x250')
    BattleQuestData = namedtuple('BattleQuestData', 'id_ groupID isCompleted description icon maxProgress currentProgress isCumulative')

    @classmethod
    def _getBattleQuest(cls, energyID):
        quests = []
        for quest in cls._eventsCache.getQuests(filterFunc=lambda x: isSecretEvent(x.getGroupID())).itervalues():
            if not quest.isCompleted():
                bonuses = quest.getBonuses('tokens')
                for bonus in bonuses:
                    for tokenID in bonus.getTokens():
                        if tokenID == energyID:
                            quests.append(quest)

        quests = sorted(quests, key=lambda quest: quest.getID())
        return first((quest for quest in quests if quest.isAvailable()), first(quests))

    @classmethod
    def getBattleQuestData(cls, energyID):
        quest = cls._getBattleQuest(energyID)
        if quest is not None:
            condition = first(first(cls._condFormatter.format(quest), []))
            if condition:
                icon = R.images.gui.maps.icons.quests.battleCondition.c_128.dyn('icon_battle_condition_{}_128x128'.format(condition.iconKey))()
                if condition.total is not None:
                    total = condition.total
                    current = condition.current
                    isCumulative = True
                else:
                    current = 0
                    total = first(condition.titleData.args)
                    isCumulative = False
                    if isinstance(total, (int, float, long)):
                        total = int(total)
                    else:
                        total = 0
                return cls.BattleQuestData(quest.getID(), quest.getGroupID(), quest.isCompleted(), first(condition.descrData.args, ''), icon, total, current, isCumulative)
        return

    @classmethod
    def getEnergyData(cls, commanderProgress, energyID, orderType=None, forceEnabled=False):
        energy = commanderProgress.getEnergy(energyID)
        currentCount = energy.getCurrentCount()
        hangarIcon = R.images.gui.maps.icons.secretEvent.certificate.c_192x192.dyn('certificateX{}_{}_{}'.format(energy.modifier, commanderProgress.getID(), int(forceEnabled or currentCount > 0)))
        hangarIcon96x96 = R.images.gui.maps.icons.secretEvent.certificate.c_96x96.dyn('certificateX{}_{}_{}'.format(energy.modifier, commanderProgress.getID(), int(forceEnabled or currentCount > 0)))
        hangarIcon192x192 = R.images.gui.maps.icons.secretEvent.certificate.c_192x192.dyn('certificateX{}_{}_{}'.format(energy.modifier, commanderProgress.getID(), int(forceEnabled or currentCount > 0)))
        hangarIcon250x250 = R.images.gui.maps.icons.secretEvent.certificate.c_250x250.dyn('certificateX{}_{}_{}'.format(energy.modifier, commanderProgress.getID(), int(forceEnabled or currentCount > 0)))
        isSelected = commanderProgress.getCurrentEnergy() == energy
        return cls.EnergyData(energy.energyID, currentCount, energy.getMaxCount(), energy.getNextRechargeTime(), energy.getNextRechargeCount(), hangarIcon(), hangarIcon96x96(), hangarIcon192x192(), TOOLTIPS_CONSTANTS.EVENT_BONUSES_BASIC_INFO, isSelected, orderType, energy.modifier, hangarIcon250x250()) if energy else None

    @classmethod
    def getShopItems(cls, gameEventController, commanderID, modifier):
        result = {}
        for item in gameEventController.getShop().getPacksByType(EventPackTypes.ENERGY_OF_GENERAL):
            if item.generalID == commanderID and item.energyModifier == modifier:
                result[item.packID] = item

        return result

    @classmethod
    def fillPriceByShopItem(cls, priceVm, shopItem):
        stats = cls._itemsCache.items.stats
        currency, price = shopItem.getPrice()
        discount = shopItem.getDiscount()
        priceVm.setCurrencyType(currency)
        priceVm.setValue(price)
        priceVm.setIsDiscount(bool(discount))
        priceVm.setDiscountValue(discount)
        priceVm.setIsEnough(not bool(stats.money.getShortage(convertPriceToMoney(currency, price))))

    @sf_lobby
    def __app(self):
        return None

    @process
    def showMission(self, battleQuestData, secretEventTabMenuItem=None):
        if battleQuestData:
            readyToSwitch = yield self.__app.fadeMgr.startFade(settings={'duration': 0.65})
            if readyToSwitch:
                result = yield self.prbDispatcher.doSelectAction(PrbAction(PREBATTLE_ACTION_NAME.RANDOM))
                if result:
                    BigWorld.callback(1.0, partial(server_events.events_dispatcher.showMissionsSecretEvent, battleQuestData.groupID, battleQuestData.id_, secretEventTabMenuItem))


class EventViewMixin(object):
    eventsCache = dependency.descriptor(IEventsCache)

    def _onEventResyncCompleted(self):
        if not self.eventsCache.isEventEnabled():
            self._closeView()
            g_eventBus.handleEvent(events.LoadViewEvent(VIEW_ALIAS.LOBBY_HANGAR), EVENT_BUS_SCOPE.LOBBY)
            g_eventBus.handleEvent(events.HangarVehicleEvent(events.HangarVehicleEvent.LOBBY_TYPE_CHANGED, ctx={'lobbyType': None}), scope=EVENT_BUS_SCOPE.LOBBY)
        return

    def _eventCacheSubscribe(self):
        self.eventsCache.onSyncCompleted += self._onEventResyncCompleted

    def _eventCacheUnsubscribe(self):
        self.eventsCache.onSyncCompleted -= self._onEventResyncCompleted

    def _closeView(self):
        pass


class ViewModelRestoreMixin(object):
    __viewModelForRestore = None

    def __init__(self):
        self.__tempModel = None
        return

    @classmethod
    def saveViewModelForRestore(cls, viewModel):
        if viewModel is not None and cls.__onDisconnected not in g_playerEvents.onDisconnected:
            g_playerEvents.onDisconnected += cls.__onDisconnected
        cls.__viewModelForRestore = viewModel
        return

    @classmethod
    def getViewModelForRestore(cls):
        return cls.__viewModelForRestore

    @property
    def tempModel(self):
        return self.__tempModel

    def saveViewModel(self, viewModelFactory, fillMethod, *args, **kwargs):
        self.__tempModel = viewModelFactory(*args, **kwargs)
        fillMethod()
        self.saveViewModelForRestore(self.__tempModel)
        self.__tempModel = None
        return

    @classmethod
    def __onDisconnected(cls):
        g_playerEvents.onDisconnected -= cls.__onDisconnected
        if cls.__viewModelForRestore is not None:
            cls.__viewModelForRestore.unbind()
            cls.__viewModelForRestore = None
        return


def getCallbackOnVideo(state=True):
    from gui.Scaleform.framework.entities.view_sound_manager import ViewSoundsManager
    from gui.impl.lobby.secret_event.sound_constants import SOUND
    path = SOUND.VIDEO_OVERLAY_STATE
    state = '{}_on'.format(path) if state else '{}_off'.format(path)
    return lambda : ViewSoundsManager.setState(path, state)
