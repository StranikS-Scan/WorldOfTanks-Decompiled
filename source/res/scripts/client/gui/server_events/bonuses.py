# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/server_events/bonuses.py
import copy
import logging
import typing
from collections import namedtuple
from functools import partial
from operator import itemgetter
import BigWorld
from adisp import process
from blueprints.BlueprintTypes import BlueprintTypes
from blueprints.FragmentTypes import getFragmentType
from constants import EVENT_TYPE as _ET, DOSSIER_TYPE, LOOTBOX_TOKEN_PREFIX, PREMIUM_ENTITLEMENTS, CURRENCY_TOKEN_PREFIX, RESOURCE_TOKEN_PREFIX
from debug_utils import LOG_ERROR, LOG_CURRENT_EXCEPTION
from dossiers2.custom.records import RECORD_DB_IDS
from dossiers2.ui.achievements import ACHIEVEMENT_BLOCK, BADGES_BLOCK
from gui import makeHtmlString
from gui.app_loader.decorators import sf_lobby
from gui.game_control.links import URLMacros
from gui.impl import backport
from gui.impl.gen import R
from gui.Scaleform.framework import ViewTypes
from gui.Scaleform.genConsts.BOOSTER_CONSTANTS import BOOSTER_CONSTANTS
from gui.Scaleform.genConsts.TEXT_ALIGN import TEXT_ALIGN
from gui.Scaleform.genConsts.TOOLTIPS_CONSTANTS import TOOLTIPS_CONSTANTS
from gui.Scaleform.locale.BADGE import BADGE
from gui.Scaleform.locale.QUESTS import QUESTS
from gui.Scaleform.locale.RES_ICONS import RES_ICONS
from gui.Scaleform.locale.TOOLTIPS import TOOLTIPS
from gui.Scaleform.locale.VEHICLE_CUSTOMIZATION import VEHICLE_CUSTOMIZATION
from gui.Scaleform.settings import getBadgeIconPath, BADGES_ICONS, ICONS_SIZES
from gui.server_events.awards_formatters import AWARDS_SIZES, AWARDS_SIZES_EXT
from gui.server_events.formatters import parseComplexToken
from gui.server_events.recruit_helper import getRecruitInfo
from gui.shared.formatters import text_styles
from gui.shared.gui_items.crew_skin import localizedFullName
from gui.shared.gui_items import GUI_ITEM_TYPE, GUI_ITEM_TYPE_INDICES
from gui.shared.gui_items.Tankman import getRoleUserName, calculateRoleLevel, Tankman
from gui.shared.gui_items.customization import CustomizationTooltipContext
from gui.shared.gui_items.dossier.factories import getAchievementFactory
from gui.shared.gui_items.crew_book import orderCmp
from gui.shared.money import Currency, Money
from gui.shared.utils.functions import makeTooltip, stripColorTagDescrTags
from gui.shared.utils.requesters.blueprints_requester import getFragmentNationID, getVehicleCDForNational
from gui.shared.utils.requesters.blueprints_requester import getVehicleCDForIntelligence
from gui.shared.utils.requesters.blueprints_requester import makeNationalCD, makeIntelligenceCD
from helpers import dependency
from helpers import getLocalizedData, i18n
from helpers import time_utils
from helpers.i18n import makeString as _ms
from items import vehicles, tankmen
from items.components import c11n_components as cc
from items.components.crew_skins_constants import NO_CREW_SKIN_ID
from items.tankmen import RECRUIT_TMAN_TOKEN_PREFIX
from nations import NAMES
from personal_missions import PM_BRANCH, PM_BRANCH_TO_FREE_TOKEN_NAME
from optional_bonuses import BONUS_MERGERS
from shared_utils import makeTupleByDict, CONST_CONTAINER
from skeletons.gui.customization import ICustomizationService
from skeletons.gui.game_control import IEventProgressionController
from skeletons.gui.goodies import IGoodiesCache
from skeletons.gui.server_events import IEventsCache
from skeletons.gui.shared import IItemsCache
from gui.server_events.awards_formatters import BATTLE_BONUS_X5_TOKEN
from battle_pass_common import BATTLE_PASS_TOKEN_PREFIX
DEFAULT_CREW_LVL = 50
_CUSTOMIZATIONS_SCALE = 44.0 / 128
_EPIC_AWARD_STATIC_VO_ENTRIES = {'compensationTooltip': QUESTS.BONUSES_COMPENSATION,
 'hasCompensation': False,
 'highlightType': '',
 'overlayType': ''}
_ZERO_COMPENSATION_MONEY = Money(credits=0, gold=0)
_CUSTOMIZATION_BONUSES = frozenset(['camouflage',
 'style',
 'paint',
 'modification',
 'projection_decal',
 'personal_number'])
_logger = logging.getLogger(__name__)

def _getAchievement(block, record, value):
    if block == ACHIEVEMENT_BLOCK.RARE:
        record = value
        value = 0
    try:
        achieve = getAchievementFactory((block, record)).create(value=value)
        if achieve.isAvailableInQuest():
            return achieve
    except Exception:
        LOG_ERROR('There is error while getting bonus dossier record name')
        LOG_CURRENT_EXCEPTION()

    return None


def _isAchievement(block):
    return block in ACHIEVEMENT_BLOCK.ALL


def _isBadge(block):
    return block == BADGES_BLOCK


class SimpleBonus(object):
    itemsCache = dependency.descriptor(IItemsCache)

    def __init__(self, name, value, isCompensation=False, ctx=None, compensationReason=None):
        self._name = name
        self._value = value
        self._isCompensation = isCompensation
        self._ctx = ctx or {}
        self._compensationReason = compensationReason

    def getName(self):
        return self._name

    def getValue(self):
        return self._value

    def setValue(self, value):
        self._value = value

    def isCompensation(self):
        return self._isCompensation

    def getCompensationReason(self):
        return self._compensationReason

    def getContext(self):
        return self._ctx

    def formatValue(self):
        return str(self._value) if self._value else None

    def format(self):
        return self._format(styleSubset='bonuses')

    def carouselFormat(self):
        return self._format(styleSubset='carouselBonuses')

    def formattedList(self):
        formattedObj = self.format()
        return [formattedObj] if formattedObj else []

    def isShowInGUI(self):
        return True

    def getIcon(self):
        pass

    def getTooltipIcon(self):
        pass

    def getTooltip(self):
        return _getItemTooltip(self._name)

    def getDescription(self):
        return i18n.makeString('#quests:bonuses/%s/description' % self._name, value=self.formatValue())

    def getList(self):
        return None

    def getWrappedEpicBonusList(self):
        awardItem = R.strings.tooltips.awardItem.dyn(self._name)
        return [{'id': 0,
          'type': 'custom/{}'.format(self.getName()),
          'value': self.getValue(),
          'icon': {AWARDS_SIZES.SMALL: self.getIconBySize(AWARDS_SIZES.SMALL),
                   AWARDS_SIZES.BIG: self.getIconBySize(AWARDS_SIZES.BIG)},
          'name': backport.text(awardItem.header()) if awardItem else '',
          'description': backport.text(awardItem.body()) if awardItem else ''}]

    def __getCommonAwardsVOs(self, iconSize='small', align=TEXT_ALIGN.CENTER, withCounts=False):
        itemInfo = {'imgSource': self.getIconBySize(iconSize),
         'label': self.getIconLabel(),
         'tooltip': self.getTooltip(),
         'align': align}
        if withCounts:
            if isinstance(self._value, int):
                itemInfo['count'] = self._value
            else:
                itemInfo['count'] = 1
        return itemInfo

    def getEpicAwardVOs(self, withDescription=False, iconSize='big', withCounts=False):
        itemInfo = self.__getCommonAwardsVOs(iconSize, align=TEXT_ALIGN.CENTER, withCounts=withCounts)
        itemInfo.update(_EPIC_AWARD_STATIC_VO_ENTRIES)
        if withDescription:
            itemInfo['title'] = i18n.makeString(TOOLTIPS.getAwardHeader(self._name))
            itemInfo['description'] = i18n.makeString(TOOLTIPS.getAwardBody(self._name))
        return [itemInfo]

    def getIconBySize(self, size):
        iconName = RES_ICONS.getBonusIcon(size, self.getName())
        if iconName is None:
            iconName = RES_ICONS.getBonusIcon(size, 'default')
        return iconName

    def getIconLabel(self):
        return text_styles.hightlight('x{}'.format(self.getValue()))

    def hasIconFormat(self):
        return False

    def _format(self, styleSubset):
        formattedValue = self.formatValue()
        if self._name is not None and formattedValue is not None:
            text = makeHtmlString('html_templates:lobby/quests/{}'.format(styleSubset), self._name, {'value': formattedValue})
            if text != self._name:
                return text
        return formattedValue


class IntegralBonus(SimpleBonus):

    def getCount(self):
        return int(self._value)

    def formatValue(self):
        return backport.getIntegralFormat(self._value) if self._value else None


class FloatBonus(SimpleBonus):

    def formatValue(self):
        return backport.getNiceNumberFormat(self._value) if self._value else None


class CountableIntegralBonus(IntegralBonus):
    pass


class CreditsBonus(IntegralBonus):

    def getIcon(self):
        return backport.image(R.images.gui.maps.icons.library.CreditsIcon_1())

    def getTooltipIcon(self):
        return RES_ICONS.MAPS_ICONS_REFERRAL_AWARD_CREDITS

    def getList(self):
        return [{'value': self.formatValue(),
          'itemSource': backport.image(R.images.gui.maps.icons.quests.bonuses.small.credits()),
          'tooltip': TOOLTIPS.AWARDITEM_CREDITS}]

    def hasIconFormat(self):
        return True

    def getIconLabel(self):
        return text_styles.credits(self.getValue())


class GoldBonus(SimpleBonus):

    def getIcon(self):
        return backport.image(R.images.gui.maps.icons.library.GoldIcon_1())

    def getList(self):
        return [{'value': self.formatValue(),
          'itemSource': backport.image(R.images.gui.maps.icons.quests.bonuses.small.gold()),
          'tooltip': TOOLTIPS.AWARDITEM_GOLD}]

    def hasIconFormat(self):
        return True

    def getIconLabel(self):
        return text_styles.gold(self.getValue())


class CrystalBonus(IntegralBonus):

    def getIcon(self):
        return backport.image(R.images.gui.maps.icons.library.CrystalIconBig())

    def getList(self):
        return [{'value': self.formatValue(),
          'itemSource': backport.image(R.images.gui.maps.icons.library.CrystalIconBig()),
          'tooltip': TOOLTIPS.AWARDITEM_CRYSTAL}]

    def hasIconFormat(self):
        return True

    def getIconLabel(self):
        return text_styles.crystal(self.getValue())


class EventCoinBonus(IntegralBonus):

    def getIcon(self):
        return backport.image(R.images.gui.maps.icons.library.EventCoinIconBig())

    def getList(self):
        return [{'value': self.formatValue(),
          'itemSource': backport.image(R.images.gui.maps.icons.library.EventCoinIconBig()),
          'tooltip': TOOLTIPS.AWARDITEM_EVENTCOIN}]

    def hasIconFormat(self):
        return True

    def getIconLabel(self):
        return text_styles.eventCoin(self.getValue())


class FreeXpBonus(IntegralBonus):

    def getList(self):
        return [{'value': self.formatValue(),
          'itemSource': backport.image(R.images.gui.maps.icons.quests.bonuses.small.freeExp()),
          'tooltip': TOOLTIPS.AWARDITEM_FREEXP}]

    def hasIconFormat(self):
        return True

    def getIconLabel(self):
        return text_styles.hightlight(self.getValue())


class _PremiumDaysBonus(IntegralBonus):

    def hasIconFormat(self):
        return True

    def getIconBySize(self, size):
        return RES_ICONS.getBonusIcon(size, '{}_{}'.format(self.getName(), self.getValue()))

    def getIconLabel(self):
        pass


class BasicPremiumDaysBonus(_PremiumDaysBonus):

    def getList(self):
        return [{'itemSource': backport.image(R.images.gui.maps.icons.quests.bonuses.small.premium_1()),
          'tooltip': TOOLTIPS.AWARDITEM_PREMIUM}]


class PlusPremiumDaysBonus(_PremiumDaysBonus):

    def getList(self):
        return [{'itemSource': backport.image(R.images.gui.maps.icons.quests.bonuses.small.premium_plus_1()),
          'tooltip': TOOLTIPS.AWARDITEM_PREMIUM}]


class MetaBonus(SimpleBonus):

    def __init__(self, *args, **kwargs):
        super(MetaBonus, self).__init__(*args, **kwargs)
        self.__onLobbyLoadedCallbacks = []

    @sf_lobby
    def __app(self):
        pass

    def isShowInGUI(self):
        return False

    def formatValue(self):
        return getLocalizedData({'value': self._value}, 'value')

    def getActions(self):
        return self._value.get('actions', {}).iteritems()

    def handleAction(self, action, params):
        if action == 'browse':
            self.__handleBrowseAction(params)
        else:
            NotImplementedError('Action "%s" handler is not implemented', action)

    @process
    def __handleBrowseAction(self, params):
        from gui.shared.event_dispatcher import showBrowserOverlayView
        url = params.get('url')
        if url is None:
            _logger.warning('Browse url is empty')
            return
        else:
            url = yield URLMacros().parse(url)
            target = params.get('target')
            if target is None:
                _logger.warning('Browse target is empty')
                return
            if target == 'internal':
                if self.__isLobbyLoaded():
                    showBrowserOverlayView(url)
                else:
                    self.__app.loaderManager.onViewLoaded += self.__onViewLoaded
                    self.__onLobbyLoadedCallbacks.append(partial(showBrowserOverlayView, url))
            elif target == 'external':
                BigWorld.wg_openWebBrowser(url)
            else:
                _logger.warning('Invalid browse target: %s', target)
            return

    def __isLobbyLoaded(self):
        container = self.__app.containerManager.getContainer(ViewTypes.LOBBY_SUB)
        return container is not None

    def __onViewLoaded(self, pyView, _):
        if pyView.viewType == ViewTypes.LOBBY_SUB:
            for callback in self.__onLobbyLoadedCallbacks:
                callback()

            self.__onLobbyLoadedCallbacks = []
            self.__app.loaderManager.onViewLoaded -= self.__onViewLoaded


class TokensBonus(SimpleBonus):
    _TOKEN_RECORD = namedtuple('_TOKEN_RECORD', ['id',
     'expires',
     'count',
     'limit'])

    def isShowInGUI(self):
        return False

    def formatValue(self):
        return None

    def getTokens(self):
        result = {}
        for tID, d in self._value.iteritems():
            expires = d.get('expires', {'at': None}) or {'at': None}
            result[tID] = self._TOKEN_RECORD(tID, expires.values()[0], d.get('count', 0), d.get('limit'))

        return result

    def getCount(self):
        return sum((v.get('count', 0) for v in self._value.values()))


class ResourceBonus(TokensBonus):

    def __init__(self, name, value, prefix, isCompensation=False, ctx=None):
        super(TokensBonus, self).__init__(name, value, isCompensation, ctx)
        self._tokenId = self._value.keys()[0]
        self._resourceName = self._tokenId.replace(prefix, '')

    def isShowInGUI(self):
        return True

    @property
    def tokenId(self):
        return self._tokenId

    @property
    def resourceName(self):
        return self._resourceName


class ProgressionXPToken(TokensBonus):

    def __init__(self, name, value, isCompensation=False, ctx=None):
        super(ProgressionXPToken, self).__init__(name, value, isCompensation, ctx)
        self._name = 'progressionXPToken'

    def isShowInGUI(self):
        return True


class BattleTokensBonus(TokensBonus):
    eventsCache = dependency.descriptor(IEventsCache)
    __eventProgression = dependency.descriptor(IEventProgressionController)

    def __init__(self, name, value, isCompensation=False, ctx=None):
        super(TokensBonus, self).__init__(name, value, isCompensation, ctx)
        self._name = 'battleToken'

    def isShowInGUI(self):
        return True

    def formatValue(self):
        result = []
        for tokenID, _ in self._value.iteritems():
            complexToken = parseComplexToken(tokenID)
            if complexToken.isDisplayable:
                userName = self._getUserName(complexToken.styleID)
                result.append(i18n.makeString(TOOLTIPS.MISSIONS_TOKEN_HEADER, name=userName))

        return ', '.join(result) if result else None

    def getWrappedEpicBonusList(self):
        result = []
        for tokenID, value in self._value.iteritems():
            if tokenID == self.__eventProgression.rewardPointsTokenID:
                result.append({'id': 0,
                 'value': value.get('count', 1),
                 'icon': {AWARDS_SIZES.SMALL: backport.image(R.images.gui.maps.icons.epicBattles.rewardPoints.c_48x48()),
                          AWARDS_SIZES.BIG: backport.image(R.images.gui.maps.icons.epicBattles.rewardPoints.c_80x80())},
                 'type': 'custom/reward_point'})

        return result

    def _getUserName(self, styleID):
        webCache = self.eventsCache.prefetcher
        return i18n.makeString(webCache.getTokenInfo(styleID))


class BattlePassTokensBonus(TokensBonus):

    def __init__(self, name, value, isCompensation=False, ctx=None):
        super(TokensBonus, self).__init__(name, value, isCompensation, ctx)
        self._name = 'battlePassToken'

    def isShowInGUI(self):
        return False


class LootBoxTokensBonus(TokensBonus):
    itemsCache = dependency.descriptor(IItemsCache)

    def __init__(self, value, isCompensation=False, ctx=None):
        super(TokensBonus, self).__init__('battleToken', value, isCompensation, ctx)

    def isShowInGUI(self):
        return True

    def format(self):
        return ', '.join(self.formattedList())

    def formattedList(self):
        result = []
        for tokenID, tokenVal in self._value.iteritems():
            lootBox = self.itemsCache.items.tokens.getLootBoxByTokenID(tokenID)
            if lootBox is not None:
                result.append(makeHtmlString('html_templates:lobby/quests/bonuses', 'lootBox', {'lootBoxType': lootBox.getType(),
                 'value': tokenVal['count']}))

        return result


class TmanTemplateTokensBonus(TokensBonus):

    def __init__(self, value, isCompensation=False, ctx=None):
        super(TokensBonus, self).__init__('tmanToken', value, isCompensation, ctx)

    def isShowInGUI(self):
        return True

    def getWrappedEpicBonusList(self):
        result = []
        for tID, tokenRecord in self.getTokens().iteritems():
            recruitInfo = getRecruitInfo(tID)
            if recruitInfo.isFemale():
                bonusImageName = 'tankwoman'
            else:
                bonusImageName = 'tankman'
            result.append({'id': tID,
             'type': self.getName(),
             'value': tokenRecord.count,
             'icon': {AWARDS_SIZES.SMALL: backport.image(R.images.gui.maps.icons.quests.bonuses.dyn(AWARDS_SIZES.SMALL).dyn(bonusImageName)()),
                      AWARDS_SIZES.BIG: backport.image(R.images.gui.maps.icons.quests.bonuses.dyn(AWARDS_SIZES.BIG).dyn(bonusImageName)())},
             'name': recruitInfo.getFullUserNameByNation(0),
             'description': recruitInfo.getDescription()})

        return result


class X5BattleTokensBonus(TokensBonus):

    def __init__(self, value, isCompensation=False, ctx=None):
        super(TokensBonus, self).__init__('tokens', value, isCompensation, ctx)

    def isShowInGUI(self):
        return True

    def getUserName(self):
        return backport.text(R.strings.quests.bonusName.battle_bonus_x5())


class EntitlementBonus(SimpleBonus):
    _ENTITLEMENT_RECORD = namedtuple('_ENTITLEMENT_RECORD', ['id', 'amount'])
    _FORMATTED_AMOUNT = ('ranked_202007_access',)

    @staticmethod
    def hasConfiguredResources(entitlementID):
        if not R.strings.quests.bonusName.entitlements.dyn(entitlementID):
            return False
        for size in AWARDS_SIZES.ALL():
            if not R.images.gui.maps.icons.quests.bonuses.dyn(size).dyn(entitlementID):
                return False

        return True

    @classmethod
    def isFormattedAmount(cls, entitlementID):
        return entitlementID in cls._FORMATTED_AMOUNT

    @classmethod
    def getUserName(cls, entitlementID):
        return backport.text(R.strings.quests.bonusName.entitlements.dyn(entitlementID)()) if cls.hasConfiguredResources(entitlementID) else ''

    @classmethod
    def getUserNameWithCount(cls, entitlementID, count):
        if cls.hasConfiguredResources(entitlementID) and count > 0:
            if cls.isFormattedAmount(entitlementID):
                res = R.strings.messenger.serviceChannelMessages.battleResults.quests.entitlements.fmtMultiplier()
                formattedCountStr = backport.text(res, count=backport.getIntegralFormat(count)) if count > 1 else ''
            else:
                countRes = R.strings.messenger.serviceChannelMessages.battleResults.quests.entitlements.multiplier()
                formattedCountStr = backport.text(countRes, count=backport.getIntegralFormat(count))
            return text_styles.concatStylesToSingleLine(cls.getUserName(entitlementID), formattedCountStr)

    def isShowInGUI(self):
        value = self.getValue()
        return value.amount > 0 and self.hasConfiguredResources(value.id)

    def getEpicAwardVOs(self, withDescription=False, iconSize='big', withCounts=False):
        return []

    def getIconBySize(self, size):
        value = self.getValue()
        return backport.image(R.images.gui.maps.icons.quests.bonuses.dyn(size).dyn(value.id)()) if self.hasConfiguredResources(value.id) else ''

    def getTooltip(self):
        return _getItemTooltip(self.getValue().id)

    def getValue(self):
        return self._ENTITLEMENT_RECORD(*self._value)

    def getWrappedEpicBonusList(self):
        value = self.getValue()
        descriptionRes = R.strings.tooltips.awardItem.dyn(value.id)
        return [{'id': value.id,
          'value': value.amount,
          'type': 'custom/{}'.format(self.getName()),
          'name': self.getUserName(value.id),
          'description': backport.text(descriptionRes.body()) if descriptionRes else '',
          'icon': {AWARDS_SIZES.BIG: self.getIconBySize(AWARDS_SIZES.BIG),
                   AWARDS_SIZES.SMALL: self.getIconBySize(AWARDS_SIZES.SMALL)}}]

    def formatValue(self):
        value = self.getValue()
        formattedValue = self.getUserNameWithCount(value.id, value.amount)
        return formattedValue if formattedValue else None


def personalMissionsTokensFactory(name, value, isCompensation=False, ctx=None):
    from gui.server_events.finders import PERSONAL_MISSION_TOKEN
    completionTokenID = PERSONAL_MISSION_TOKEN % (ctx['campaignID'], ctx['operationID'])
    result = []
    for tID, tValue in value.iteritems():
        if tID in PM_BRANCH_TO_FREE_TOKEN_NAME.values():
            result.append(FreeTokensBonus({tID: tValue}, isCompensation, ctx))
        if tID == completionTokenID:
            result.append(CompletionTokensBonus({tID: tValue}, isCompensation, ctx))
        result.append(TokensBonus(name, {tID: tValue}, isCompensation, ctx))

    return result


def createBonusFromTokens(result, prefix, bonusId, value):
    bonus = getNonQuestBonuses(bonusId.replace(prefix, ''), value.get('count'))
    if bonus:
        result.append(bonus[0])


@dependency.replace_none_kwargs(eventProgressionController=IEventProgressionController)
def tokensFactory(name, value, isCompensation=False, ctx=None, eventProgressionController=None):
    result = []
    for tID, tValue in value.iteritems():
        if tID.startswith(LOOTBOX_TOKEN_PREFIX):
            result.append(LootBoxTokensBonus({tID: tValue}, isCompensation, ctx))
        if tID.startswith(RECRUIT_TMAN_TOKEN_PREFIX):
            result.append(TmanTemplateTokensBonus({tID: tValue}, isCompensation, ctx))
        if tID.startswith(BATTLE_BONUS_X5_TOKEN):
            result.append(X5BattleTokensBonus({tID: tValue}, isCompensation, ctx))
        if tID.startswith(BATTLE_PASS_TOKEN_PREFIX):
            result.append(BattlePassTokensBonus(name, {tID: tValue}, isCompensation, ctx))
        if tID.startswith(CURRENCY_TOKEN_PREFIX):
            createBonusFromTokens(result, CURRENCY_TOKEN_PREFIX, tID, tValue)
        if tID.startswith(RESOURCE_TOKEN_PREFIX):
            result.append(ResourceBonus(name, {tID: tValue}, RESOURCE_TOKEN_PREFIX, isCompensation, ctx))
        if eventProgressionController.isAvailable() and tID.startswith(eventProgressionController.getProgressionXPTokenID()):
            result.append(ProgressionXPToken(name, {tID: tValue}, isCompensation, ctx))
        result.append(BattleTokensBonus(name, {tID: tValue}, isCompensation, ctx))

    return result


def entitlementsFactory(name, value, isCompensation=False, ctx=None):
    return [ EntitlementBonus(name, (eID, eValue.get('count', 0)), isCompensation, ctx) for eID, eValue in value.iteritems() ]


class FreeTokensBonus(TokensBonus):

    def __init__(self, value, isCompensation=False, ctx=None, hasPawned=False):
        super(FreeTokensBonus, self).__init__('freeTokens', value, isCompensation, ctx)
        self.__hasPawnedTokens = hasPawned

    def isShowInGUI(self):
        return self.getCount() > 0

    def formatValue(self):
        return str(self.getCount())

    def format(self):
        return makeHtmlString('html_templates:lobby/quests/bonuses', self._name, {'value': self.formatValue()})

    def areTokensPawned(self):
        return self.__hasPawnedTokens

    def getImageFileName(self):
        return '_'.join((self.getName(), str(self.__determineBranchID())))

    def __determineBranchID(self):
        result = PM_BRANCH.REGULAR
        for branch, token in PM_BRANCH_TO_FREE_TOKEN_NAME.iteritems():
            if token in self._value:
                result = branch

        return result


class CompletionTokensBonus(TokensBonus):

    def __init__(self, value, isCompensation=False, ctx=None):
        super(CompletionTokensBonus, self).__init__('completionTokens', value, isCompensation, ctx)

    def isShowInGUI(self):
        return self.getCount() > 0

    def formatValue(self):
        return str(self.getCount())

    def format(self):
        return makeHtmlString('html_templates:lobby/quests/bonuses', self._name, {'value': self.formatValue()})


class ItemsBonus(SimpleBonus):

    def getItems(self):
        if self._value is not None:
            _getItem = self.itemsCache.items.getItemByCD
            return dict(((_getItem(intCD), count) for intCD, count in self._value.iteritems()))
        else:
            return {}

    def format(self):
        result = []
        for item, count in self.getItems().iteritems():
            if item is not None and count:
                result.append(i18n.makeString('#quests:bonuses/items/name', name=item.userName, count=count))

        return ', '.join(result) if result else None

    def getList(self):
        result = []
        for item, count in self.getItems().iteritems():
            if item is not None and count:
                description = item.fullDescription
                if item.itemTypeID in (GUI_ITEM_TYPE.OPTIONALDEVICE, GUI_ITEM_TYPE.EQUIPMENT):
                    description = stripColorTagDescrTags(description)
                tooltip = makeTooltip(header=item.userName, body=description)
                result.append({'value': backport.getIntegralFormat(count),
                 'itemSource': item.icon,
                 'tooltip': tooltip})

        return result

    def getWrappedEpicBonusList(self):
        result = []
        for item, count in self.getItems().iteritems():
            if item is not None and count:
                typeName = item.itemTypeName
                if item.itemTypeID in (GUI_ITEM_TYPE.BATTLE_BOOSTER, GUI_ITEM_TYPE.EQUIPMENT, GUI_ITEM_TYPE.VEHICLE_MODULES):
                    typeName = 'equipment'
                result.append({'id': item.intCD,
                 'type': 'item/{}'.format(typeName),
                 'value': count,
                 'icon': {AWARDS_SIZES.SMALL: item.getBonusIcon(AWARDS_SIZES.SMALL),
                          AWARDS_SIZES.BIG: item.getBonusIcon(AWARDS_SIZES.BIG)},
                 'name': item.userName,
                 'description': item.shortDescriptionSpecial.format(colorTagOpen='', colorTagClose='')})

        return result

    def hasIconFormat(self):
        return True

    def __getCommonAwardsVOs(self, item, count, iconSize='small', align=TEXT_ALIGN.RIGHT, withCounts=False):
        itemInfo = {'imgSource': item.getBonusIcon(iconSize),
         'label': text_styles.stats('x{}'.format(count)),
         'tooltip': self.makeItemTooltip(item),
         'align': align}
        if withCounts:
            itemInfo['count'] = count
        return itemInfo

    def getEpicAwardVOs(self, withDescription=False, iconSize='big', withCounts=False):
        result = []
        for item, count in self.getItems().iteritems():
            itemInfo = self.__getCommonAwardsVOs(item, count, iconSize, align=TEXT_ALIGN.CENTER, withCounts=withCounts)
            itemInfo.update(_EPIC_AWARD_STATIC_VO_ENTRIES)
            result.append(itemInfo)

        return result

    @staticmethod
    def makeItemTooltip(item):
        description = item.fullDescription
        if item.itemTypeID in (GUI_ITEM_TYPE.OPTIONALDEVICE, GUI_ITEM_TYPE.EQUIPMENT):
            description = stripColorTagDescrTags(description)
        return makeTooltip(header=item.userName, body=description)


class GoodiesBonus(SimpleBonus):
    goodiesCache = dependency.descriptor(IGoodiesCache)

    def getBoosters(self):
        return self._getGoodies(self.goodiesCache.getBooster)

    def getDiscounts(self):
        return self._getGoodies(self.goodiesCache.getDiscount)

    def getDemountKits(self):
        return self._getGoodies(self.goodiesCache.getDemountKit)

    def _getGoodies(self, goodieGetter):
        goodies = {}
        if self._value is not None:
            for boosterID, info in self._value.iteritems():
                goodie = goodieGetter(int(boosterID))
                if goodie is not None and goodie.enabled:
                    goodies[goodie] = info.get('count', 1)

        return goodies

    def format(self):
        return ', '.join(self.formattedList())

    @staticmethod
    def __makeBoosterVO(booster):
        return {'icon': booster.icon,
         'showCount': False,
         'qualityIconSrc': booster.getQualityIcon(),
         'slotLinkage': BOOSTER_CONSTANTS.SLOT_UI,
         'showLeftTime': False,
         'boosterId': booster.boosterID}

    def hasIconFormat(self):
        return True

    def getList(self):
        result = []
        for booster, count in sorted(self.getBoosters().iteritems(), key=lambda (booster, count): booster.boosterType):
            if booster is not None:
                result.append({'value': backport.getIntegralFormat(count),
                 'tooltip': TOOLTIPS_CONSTANTS.BOOSTERS_BOOSTER_INFO,
                 'boosterVO': self.__makeBoosterVO(booster)})

        for discount, count in sorted(self.getDiscounts().iteritems()):
            if discount is not None:
                tooltip = makeTooltip(header=discount.userName, body=discount.description)
                result.append({'value': discount.getFormattedValue(),
                 'itemSource': discount.icon,
                 'tooltip': tooltip})

        return result

    def getWrappedEpicBonusList(self):
        result = []
        for booster, count in self.getBoosters().iteritems():
            if booster is not None:
                result.append({'id': booster.boosterID,
                 'type': 'goodie/{}'.format(booster.getTypeAsString()),
                 'value': count,
                 'icon': {AWARDS_SIZES.SMALL: RES_ICONS.getBonusIcon(AWARDS_SIZES.SMALL, booster.boosterGuiType),
                          AWARDS_SIZES.BIG: RES_ICONS.getBonusIcon(AWARDS_SIZES.BIG, booster.boosterGuiType)},
                 'name': booster.userName,
                 'description': booster.getBonusDescription()})

        for discount, count in self.getDiscounts().iteritems():
            if discount is not None:
                result.append({'id': discount.discountID,
                 'type': 'discount/{}'.format(discount.targetType),
                 'value': discount.getFormattedValue(),
                 'icon': {AWARDS_SIZES.SMALL: discount.icon,
                          AWARDS_SIZES.BIG: discount.bigIcon},
                 'name': discount.userName,
                 'description': discount.getBonusDescription()})

        return result

    def formattedList(self):
        result = []
        for booster, count in self.getBoosters().iteritems():
            if booster is not None:
                result.append(i18n.makeString('#quests:bonuses/boosters/name', name=booster.userName, quality=booster.qualityStr, count=count))

        for discount, count in self.getDiscounts().iteritems():
            if discount is not None:
                result.append(i18n.makeString('#quests:bonuses/discount/name', name=discount.userName, targetName=discount.targetName, effectValue=discount.getFormattedValue(), count=count))

        for demountKit, count in self.getDemountKits().iteritems():
            result.append(backport.text(R.strings.quests.bonuses.items.name(), name=demountKit.userName, count=count))

        return result

    def __getCommonAwardsVOs(self, item, count, iconSize='small', align=TEXT_ALIGN.RIGHT, withCounts=False):
        itemData = {'imgSource': RES_ICONS.getBonusIcon(iconSize, item.boosterGuiType),
         'label': text_styles.hightlight('x{}'.format(count)),
         'align': align}
        itemData.update(self.__itemTooltip(item))
        if withCounts:
            itemData['count'] = count
        return itemData

    def getEpicAwardVOs(self, withDescription=False, iconSize='big', withCounts=False):
        result = []
        for booster, count in self.getBoosters().iteritems():
            if booster is not None:
                itemData = self.__getCommonAwardsVOs(booster, count, iconSize, align=TEXT_ALIGN.CENTER, withCounts=withCounts)
                itemData.update(_EPIC_AWARD_STATIC_VO_ENTRIES)
                result.append(itemData)

        return result

    @staticmethod
    def __itemTooltip(booster):
        return {'isSpecial': True,
         'specialAlias': TOOLTIPS_CONSTANTS.BOOSTERS_BOOSTER_INFO,
         'specialArgs': [booster.boosterID]}


class VehiclesBonus(SimpleBonus):

    @classmethod
    def isNonZeroCompensation(cls, vehInfo):
        compensatedNumber = vehInfo.get('compensatedNumber', 0)
        compensation = vehInfo.get('customCompensation')
        if compensatedNumber and compensation is not None:
            money = Money(*compensation)
            if money == _ZERO_COMPENSATION_MONEY:
                return False
        return True

    def formatValue(self):
        result = []
        for item, _ in self.getVehicles():
            result.append(item.shortUserName)

        return ', '.join(result)

    def format(self):
        return ', '.join(self.formattedList())

    def formattedList(self):
        result = []
        for item, vehInfo in self.getVehicles():
            tmanRoleLevel = self.getTmanRoleLevel(vehInfo)
            rentDays = self.getRentDays(vehInfo)
            vInfoLabels = []
            if rentDays is not None:
                rentDaysStr = makeHtmlString('html_templates:lobby/quests/bonuses', 'rentDays', {'value': str(rentDays)})
                vInfoLabels.append(rentDaysStr)
            if tmanRoleLevel is not None:
                crewLvl = i18n.makeString('#quests:bonuses/vehicles/crewLvl', tmanRoleLevel)
                vInfoLabels.append(crewLvl)
            if vInfoLabels:
                result.append(text_styles.standard(i18n.makeString('#quests:bonuses/vehicles/name', name=text_styles.main(item.userName), vehInfo='; '.join(vInfoLabels))))
            result.append(text_styles.main(item.userName))

        return result

    def getWrappedEpicBonusList(self):
        result = []
        for item, _ in self.getVehicles():
            result.append({'id': item.intCD,
             'type': 'vehicle/{}'.format(item.type),
             'value': 1,
             'icon': {AWARDS_SIZES.SMALL: item.iconSmall,
                      AWARDS_SIZES.BIG: item.icon}})

        return result

    def getIcon(self):
        return backport.image(R.images.gui.maps.icons.library.tank())

    def getTooltipIcon(self):
        vehicle, _ = self.getVehicles()[0]
        return vehicle.icon

    def getVehicles(self):
        result = []
        if self._value is not None:
            if isinstance(self._value, dict):
                for intCD, vehInfo in self._value.iteritems():
                    item = self.itemsCache.items.getItemByCD(intCD)
                    if item is not None and not item.isOnlyForBattleRoyaleBattles:
                        result.append((item, vehInfo))

            elif isinstance(self._value, list):
                for subDict in self._value:
                    for intCD, vehInfo in subDict.iteritems():
                        item = self.itemsCache.items.getItemByCD(intCD)
                        if item is not None and not item.isOnlyForBattleRoyaleBattles:
                            result.append((item, vehInfo))

        return result

    def isRentVehicle(self, vehInfo):
        return True if self.getRentBattles(vehInfo) or self.getRentDays(vehInfo) or self.getRentWins(vehInfo) else False

    def compensation(self, vehicle, bonus):
        bonuses = []
        for curVehicle, vehInfo in self.getVehicles():
            compensatedNumber = vehInfo.get('compensatedNumber', 0)
            compensation = vehInfo.get('customCompensation')
            if compensatedNumber and compensation is not None and curVehicle == vehicle:
                money = Money(*compensation)
                while compensatedNumber > 0:
                    for currency, value in money.iteritems():
                        if value:
                            cls = _BONUSES.get(currency)
                            bonuses.append(cls(currency, value, isCompensation=True, compensationReason=bonus))

                    compensatedNumber -= 1

        return bonuses

    def checkIsCompensatedVehicle(self, vehicle):
        for curVehicle, vehInfo in self.getVehicles():
            compensation = vehInfo.get('customCompensation')
            return curVehicle == vehicle and compensation

        return False

    def getIconLabel(self):
        pass

    def __getCommonAwardsVOs(self, vehicle, vehInfo, iconSize='small', align=TEXT_ALIGN.RIGHT, withCounts=False):
        vehicleVO = self.__getVehicleVO(vehicle, vehInfo, partial(RES_ICONS.getBonusIcon, iconSize))
        vehicleVO.update({'label': self.getIconLabel()})
        vehicleVO['align'] = align
        if withCounts:
            vehicleVO['count'] = 1
        return vehicleVO

    def getEpicAwardVOs(self, withDescription=False, iconSize='big', withCounts=False):
        result = []
        for vehicle, vehInfo in self.getVehicles():
            vehicleVO = self.__getCommonAwardsVOs(vehicle, vehInfo, iconSize, align=TEXT_ALIGN.CENTER, withCounts=withCounts)
            vehicleVO.update(_EPIC_AWARD_STATIC_VO_ENTRIES)
            if withDescription:
                vehicleVO['title'] = i18n.makeString(TOOLTIPS.getAwardHeader(self._name))
                vehicleVO['description'] = i18n.makeString(TOOLTIPS.getAwardBody(self._name))
            result.append(vehicleVO)

        return result

    @classmethod
    def getTmanRoleLevel(cls, vehInfo):
        if 'noCrew' not in vehInfo:
            if 'crewLvl' in vehInfo:
                return calculateRoleLevel(vehInfo.get('crewLvl', DEFAULT_CREW_LVL), vehInfo.get('crewFreeXP', 0))
            if 'tankmen' in vehInfo:
                for tman in vehInfo['tankmen']:
                    if isinstance(tman, str):
                        tankmanDecsr = tankmen.TankmanDescr(compactDescr=tman)
                        if tankmanDecsr.role == Tankman.ROLES.COMMANDER:
                            return calculateRoleLevel(tankmanDecsr.roleLevel, tankmanDecsr.freeXP)
                    if tman['role'] == Tankman.ROLES.COMMANDER:
                        return calculateRoleLevel(tman.get('roleLevel', DEFAULT_CREW_LVL), tman.get('freeXP', 0))

        return None

    @staticmethod
    def getRentDays(vehInfo):
        if 'rent' not in vehInfo:
            return None
        else:
            time = vehInfo.get('rent', {}).get('time')
            if time:
                if time == float('inf'):
                    return None
                if time <= time_utils.DAYS_IN_YEAR:
                    return int(time)
                return None
            return None

    @staticmethod
    def getRentBattles(vehInfo):
        return vehInfo.get('rent', {}).get('battles')

    @staticmethod
    def getRentWins(vehInfo):
        return vehInfo.get('rent', {}).get('wins')

    @staticmethod
    def getRentSeason(vehInfo):
        return vehInfo.get('rent', {}).get('season')

    def __getVehicleVO(self, vehicle, vehicleInfo, iconGetter):
        tmanRoleLevel = self.getTmanRoleLevel(vehicleInfo)
        rentDays = self.getRentDays(vehicleInfo)
        if rentDays:
            iconName = 'vehicles_rent'
            rentExpiryTime = time_utils.getCurrentTimestamp() + rentDays * time_utils.ONE_DAY
        else:
            iconName = 'vehicles'
            rentExpiryTime = 0
        return {'imgSource': iconGetter(iconName),
         'isSpecial': True,
         'specialAlias': TOOLTIPS_CONSTANTS.AWARD_VEHICLE,
         'specialArgs': [vehicle.intCD, tmanRoleLevel, rentExpiryTime]}


class BadgesGroupBonus(SimpleBonus):

    def getBadges(self):
        groupID = self._value
        badges = self.itemsCache.items.getBadges()
        return [ badge for badge in badges.itervalues() if groupID == badge.group ]


class DossierBonus(SimpleBonus):

    def getRecords(self):
        records = {}
        if self._value is not None:
            for dossierType in self._value:
                if dossierType != DOSSIER_TYPE.CLAN:
                    popUpRecords = {}
                    if self._ctx and 'popUpRecords' in self._ctx:
                        popUpRecords = dict(self._ctx['popUpRecords'])
                    for name, data in self._value[dossierType].iteritems():
                        block = name[0]
                        if block == BADGES_BLOCK:
                            blid = int(name[1])
                        else:
                            blid = RECORD_DB_IDS.get(name, 0)
                        val = popUpRecords.get(blid)
                        if val is None:
                            val = data.get('value', 0)
                        records[name] = val

        return records

    def getAchievements(self):
        return self.__getItems(_isAchievement)

    def getAchievementsFromDossier(self, statsBlock):
        result = []
        for record in self.getRecords().iterkeys():
            achievement = statsBlock.getAchievement(record)
            if achievement is not None:
                result.append(achievement)

        return result

    def getBadges(self):
        result = []
        badges = None
        for (block, record), _ in self.getRecords().iteritems():
            if _isBadge(block):
                badgeID = int(record)
                if badges is None:
                    badges = self.itemsCache.items.getBadges()
                if badgeID in badges:
                    result.append(badges[badgeID])

        return result

    def format(self):
        return ', '.join(self.formattedList())

    def formattedList(self):
        return [ achievement.getUserName() for achievement in self.getAchievements() ]

    def getWrappedEpicBonusList(self):
        result = []
        for block, record in self.getRecords().iterkeys():
            if block in ('singleAchievements', 'achievements'):
                blockID = RECORD_DB_IDS[block, record]
            else:
                blockID = record
            icons = self.__getEpicBonusImages(block, record)
            if not icons or not icons['small'] and not icons['big']:
                icons = self.__getAchievementImages(record)
            result.append({'id': blockID,
             'name': record,
             'type': block,
             'value': 1,
             'icon': icons})

        return result

    def __getEpicBonusImages(self, block, record):
        if block == 'playerBadges':
            return {AWARDS_SIZES_EXT.SMALL: getBadgeIconPath(BADGES_ICONS.X48, record),
             AWARDS_SIZES_EXT.BIG: getBadgeIconPath(BADGES_ICONS.X80, record),
             AWARDS_SIZES_EXT.HUGE: getBadgeIconPath(BADGES_ICONS.X110, record)}
        return {AWARDS_SIZES.SMALL: RES_ICONS.getEpicAchievementIcon(ICONS_SIZES.X48, record),
         AWARDS_SIZES.BIG: RES_ICONS.getEpicAchievementIcon(ICONS_SIZES.X80, record)} if block == 'singleAchievements' else {}

    def __getAchievementImages(self, record):
        smallId = R.images.gui.maps.icons.achievement.num(ICONS_SIZES.X48).dyn(record)()
        bigId = R.images.gui.maps.icons.achievement.num(ICONS_SIZES.X80).dyn(record)()
        return {AWARDS_SIZES.SMALL: backport.image(smallId) if smallId > 0 else '',
         AWARDS_SIZES.BIG: backport.image(bigId) if smallId > 0 else ''}

    def __getCommonAwardsVOs(self, block, record, iconSize='small', withCounts=False):
        badgesIconSizes = {'big': BADGES_ICONS.X80,
         'small': BADGES_ICONS.X48}
        if _isBadge(block):
            header = i18n.makeString(BADGE.badgeName(record))
            body = i18n.makeString(BADGE.badgeDescriptor(record))
            note = i18n.makeString(BADGE.BADGE_NOTE)
            badgeVO = {'imgSource': getBadgeIconPath(badgesIconSizes[iconSize], record),
             'label': '',
             'tooltip': makeTooltip(header, body, note)}
            if withCounts:
                badgeVO['count'] = 1
            return badgeVO
        else:
            return None

    def getEpicAwardVOs(self, withDescription=False, iconSize='big', withCounts=False):
        result = []
        for (block, record), _ in self.getRecords().iteritems():
            badgeVO = self.__getCommonAwardsVOs(block, record, iconSize, withCounts=withCounts)
            if not badgeVO:
                continue
            badgeVO['align'] = TEXT_ALIGN.CENTER
            badgeVO.update(_EPIC_AWARD_STATIC_VO_ENTRIES)
            if withDescription:
                badgeVO['title'] = i18n.makeString(BADGE.badgeName(record))
                badgeVO['description'] = i18n.makeString(BADGE.badgeDescriptor(record))
            result.append(badgeVO)

        return result

    def __getItems(self, filterFunc):
        result = []
        for (block, record), value in self.getRecords().iteritems():
            if filterFunc(block):
                achieve = _getAchievement(block, record, value)
                if achieve is not None:
                    result.append(achieve)

        return result


class PersonalMissionDossierBonus(DossierBonus):

    def isShowInGUI(self):
        return bool(self.getBadges())


class TankmenBonus(SimpleBonus):
    _TankmanInfoRecord = namedtuple('_TankmanInfoRecord', ['nationID',
     'role',
     'vehicleTypeID',
     'firstNameID',
     'fnGroupID',
     'lastNameID',
     'lnGroupID',
     'iconID',
     'iGroupID',
     'isPremium',
     'roleLevel',
     'freeXP',
     'skills',
     'isFemale',
     'freeSkills'])

    def formatValue(self):
        result = []
        for group in self.getTankmenGroups().itervalues():
            if group['skills']:
                labelI18nKey = '#quests:bonuses/item/tankmen/with_skills'
            else:
                labelI18nKey = '#quests:bonuses/item/tankmen/no_skills'
            result.append(i18n.makeString(labelI18nKey, **group))

        return ' '.join(result)

    def getTankmenData(self):
        result = []
        if self._value is not None:
            for tankmanData in self._value:
                if isinstance(tankmanData, str):
                    result.append(self._makeTmanInfoByDescr(tankmen.TankmanDescr(compactDescr=tankmanData)))
                result.append(makeTupleByDict(self._TankmanInfoRecord, tankmanData))

        return result

    def getTankmenGroups(self):
        groups = {}
        for tmanInfo in self.getTankmenData():
            roleLevel = calculateRoleLevel(tmanInfo.roleLevel, tmanInfo.freeXP, typeID=(tmanInfo.nationID, tmanInfo.vehicleTypeID))
            if tmanInfo.vehicleTypeID not in groups:
                vehIntCD = vehicles.makeIntCompactDescrByID('vehicle', tmanInfo.nationID, tmanInfo.vehicleTypeID)
                groups[tmanInfo.vehicleTypeID] = {'vehName': self.itemsCache.items.getItemByCD(vehIntCD).shortUserName,
                 'skills': len(tmanInfo.skills),
                 'roleLevel': roleLevel}
            group = groups[tmanInfo.vehicleTypeID]
            group['skills'] += len(tmanInfo.skills)
            group['roleLevel'] = min(group['roleLevel'], roleLevel)

        return groups

    def getIcon(self):
        return backport.image(R.images.gui.maps.icons.library.tankman())

    def getTooltipIcon(self):
        for tmanInfo in self.getTankmenData():
            if tmanInfo.isFemale:
                return RES_ICONS.MAPS_ICONS_QUESTS_TANKMANFEMALEGRAY

        return RES_ICONS.MAPS_ICONS_REFERRAL_REFSYS_MEN_BW

    def getCount(self):
        return len(self._value) if self._value is not None else 0

    @classmethod
    def _makeTmanInfoByDescr(cls, td):
        return cls._TankmanInfoRecord(td.nationID, td.role, td.vehicleTypeID, td.firstNameID, -1, td.lastNameID, -1, td.iconID, -1, td.isPremium, td.roleLevel, td.freeXP, td.skills, td.isFemale, [])


class TankwomanBonus(TankmenBonus):

    def __init__(self, name, value, isCompensation=False, ctx=None):
        super(TankwomanBonus, self).__init__(name, value, isCompensation)
        self._name = 'tankwomanBonus'

    def formatValue(self):
        result = []
        for tmanInfo in self.getTankmenData():
            if tmanInfo.isFemale:
                result.append(i18n.makeString(QUESTS.BONUSES_ITEM_TANKWOMAN))
            result.append(i18n.makeString(QUESTS.BONUSES_TANKMEN_DESCRIPTION, value=getRoleUserName(tmanInfo.role)))

        return ', '.join(result)


class CustomizationsBonus(SimpleBonus):
    c11n = dependency.descriptor(ICustomizationService)

    def getList(self):
        result = []
        separator = ''
        customizations = self.getCustomizations()
        customizationsCountMax = len(customizations) - 1
        if customizationsCountMax > 0:
            separator = ', '
        for count, itemData in enumerate(customizations):
            boundVehicle = itemData.get('vehTypeCompDescr')
            boundToCurrentVehicle = itemData.get('boundToCurrentVehicle', False)
            item = self.getC11nItem(itemData)
            value = itemData.get('value', 0)
            valueStr = None
            if value > 1:
                valueStr = text_styles.main(i18n.makeString(QUESTS.BONUSES_CUSTOMIZATION_VALUE, count=value))
            key = VEHICLE_CUSTOMIZATION.getElementBonusDesc(item.itemFullTypeName)
            bonusDesc = ''
            if key is not None:
                bonusDesc = _ms(key, value=item.userName)
                if value > 0:
                    bonusDesc = bonusDesc + ' ' + _ms(VEHICLE_CUSTOMIZATION.ELEMENTBONUS_FACTOR, count=value)
                if count < customizationsCountMax:
                    bonusDesc = bonusDesc + separator
            result.append({'intCD': item.intCD,
             'texture': item.icon,
             'value': value,
             'valueStr': valueStr,
             'boundVehicle': boundVehicle,
             'boundToCurrentVehicle': boundToCurrentVehicle,
             'showPrice': False,
             'description': bonusDesc})

        return result

    def getWrappedEpicBonusList(self):
        result = []
        for itemData in self.getCustomizations():
            itemType = itemData.get('custType')
            itemTypeID = self.__getItemTypeID(itemType)
            item = self.c11n.getItemByID(itemTypeID, itemData.get('id'))
            smallIcon = item.getBonusIcon(AWARDS_SIZES.SMALL)
            bigIcon = item.getBonusIcon(AWARDS_SIZES.BIG)
            typeStr = itemType
            if itemType == 'decal':
                typeStr = 'decal/1'
            elif itemType in _CUSTOMIZATION_BONUSES:
                typeStr = ''.join([typeStr, '/all'])
            if itemType == 'style':
                smallIcon = RES_ICONS.getBonusIcon(AWARDS_SIZES.SMALL, itemType)
                bigIcon = RES_ICONS.getBonusIcon(AWARDS_SIZES.BIG, itemType)
            result.append({'id': itemData.get('id'),
             'type': typeStr,
             'value': itemData.get('value', 0),
             'icon': {AWARDS_SIZES.SMALL: smallIcon,
                      AWARDS_SIZES.BIG: bigIcon},
             'name': item.longUserName,
             'description': item.longDescriptionSpecial,
             'intCD': item.intCD})

        return result

    def getCustomizations(self):
        return self._value or []

    def compensation(self):
        bonuses = []
        substitutes = []
        cache = vehicles.g_cache.customization20()
        for customizationItem in self._value:
            c11nItem = self.getC11nItem(customizationItem)
            itemType, itemId = cc.splitIntDescr(c11nItem.intCD)
            c11nComponent = cache.itemTypes[itemType][itemId]
            count = customizationItem.get('value')
            inventoryCount = c11nItem.inventoryCount
            maxNumber = c11nComponent.maxNumber
            compensationCount = count - max(0, maxNumber - inventoryCount)
            if compensationCount > 0 and maxNumber != 0:
                realCount = count - compensationCount
                if realCount > 0:
                    substituteItem = copy.deepcopy(customizationItem)
                    substituteItem['value'] = realCount
                    substitutes.append(substituteItem)
                compensation = customizationItem.get('customCompensation')
                money = Money.makeMoney(compensation)
                if money is not None:
                    for currency, value in money.iteritems():
                        if value:
                            cls = _BONUSES.get(currency)
                            bonuses.append(cls(currency, value * compensationCount, isCompensation=True))

            substitutes.append(copy.deepcopy(customizationItem))

        bonuses.insert(0, CustomizationsBonus('customizations', substitutes))
        return bonuses

    def getC11nItem(self, item):
        itemTypeName = item.get('custType')
        itemID = item.get('id')
        itemTypeID = self.__getItemTypeID(itemTypeName)
        c11nItem = self.c11n.getItemByID(itemTypeID, itemID)
        return c11nItem

    def getEpicAwardVOs(self, withDescription=False, iconSize='big', withCounts=False):
        result = []
        for item, data in zip(self.getCustomizations(), self.getList()):
            itemData = self.__getCommonAwardsVOs(item, data, iconSize, align=TEXT_ALIGN.CENTER, withCounts=withCounts)
            itemData.update(_EPIC_AWARD_STATIC_VO_ENTRIES)
            if withDescription:
                c11nItem = self.getC11nItem(item)
                itemData['description'] = c11nItem.userType
                itemData['title'] = c11nItem.userName
            result.append(itemData)

        return result

    def __getCommonAwardsVOs(self, item, data, iconSize='small', align=TEXT_ALIGN.RIGHT, withCounts=False):
        c11nItem = self.getC11nItem(item)
        count = item.get('value', 1)
        itemData = {'imgSource': RES_ICONS.getBonusIcon(iconSize, c11nItem.itemTypeName),
         'label': text_styles.hightlight('x{}'.format(count)),
         'align': align}
        itemData.update(self.__itemTooltip(data))
        if withCounts:
            itemData['count'] = count
        return itemData

    def __itemTooltip(self, data):
        return {'isSpecial': True,
         'specialAlias': TOOLTIPS_CONSTANTS.TECH_CUSTOMIZATION_ITEM,
         'specialArgs': CustomizationTooltipContext(itemCD=data['intCD'], showInventoryBlock=data['showPrice'])}

    @staticmethod
    def __getItemTypeID(itemTypeName):
        if itemTypeName == 'projection_decal':
            itemTypeID = GUI_ITEM_TYPE.PROJECTION_DECAL
        elif itemTypeName == 'personal_number':
            itemTypeID = GUI_ITEM_TYPE.PERSONAL_NUMBER
        else:
            itemTypeID = GUI_ITEM_TYPE_INDICES.get(itemTypeName)
        return itemTypeID


class BoxBonus(SimpleBonus):

    class HandlerNames(object):
        pass

    def __init__(self, name, value, isCompensation=False, ctx=None):
        super(BoxBonus, self).__init__(name, value, isCompensation)
        self.__iconsHandlerData = ('', None)
        self.__tooltipType = None
        self.__iconHandlers = {}
        return

    def setupIconHandler(self, handlerData, handlerParams):
        self.__iconsHandlerData = (handlerData, handlerParams)

    def setTooltipType(self, tooltipType):
        self.__tooltipType = tooltipType

    def getIconBySize(self, size):
        handlerName, params = self.__iconsHandlerData
        handler = self.__iconHandlers.get(handlerName)
        return handler(params, size) if handler else None

    def getIconLabel(self):
        pass

    def getTooltip(self):
        name = self._name
        if self.__tooltipType is not None:
            name = '/'.join([name, self.__tooltipType])
        return _getItemTooltip(name)


def randomBlueprintBonusFactory(name, value, isCompensation=False, ctx=None):
    blueprintBonuses = []
    for params, fragmentCount in value.iteritems():
        blueprintBonuses.append(RandomBlueprintBonus(name, (params, fragmentCount), isCompensation, ctx))

    return blueprintBonuses


def blueprintBonusFactory(name, value, isCompensation=False, ctx=None):
    blueprintBonuses = []
    for fragmentCD, fragmentCount in sorted(value.iteritems(), key=itemgetter(0)):
        fragmentType = getFragmentType(fragmentCD)
        if fragmentType == BlueprintTypes.VEHICLE:
            blueprintBonuses.append(VehicleBlueprintBonus(name, (fragmentCD, fragmentCount), isCompensation, ctx))
        if fragmentType == BlueprintTypes.INTELLIGENCE_DATA:
            vehicleCD = getVehicleCDForIntelligence(fragmentCD)
            blueprintBonuses.append(IntelligenceBlueprintBonus(name, (vehicleCD, fragmentCount), isCompensation, ctx))
        if fragmentType == BlueprintTypes.NATIONAL:
            vehicleCD = getVehicleCDForNational(fragmentCD)
            blueprintBonuses.append(NationalBlueprintBonus(name, (vehicleCD, fragmentCount), isCompensation, ctx))

    return blueprintBonuses


class BlueprintsBonusSubtypes(CONST_CONTAINER):
    FINAL_FRAGMENT = 'BlueprintFinalFragmentCongrats'
    UNIVERSAL_FRAGMENT = 'BlueprintUniversalFragmentCongrats'
    NATION_FRAGMENT = 'BlueprintNationFragmentCongrats'
    VEHICLE_FRAGMENT = 'BlueprintVehicleFragmentCongrats'
    RANDOM_FRAGMENT = 'BlueprintRandomFragmentCongrats'
    USE_CONGRATS = (FINAL_FRAGMENT, VEHICLE_FRAGMENT)


class RandomBlueprintBonus(SimpleBonus):
    _HTML_TEMPLATE = 'anyBlueprints'

    def getBlueprintName(self):
        return BlueprintsBonusSubtypes.RANDOM_FRAGMENT

    def getBlueprintSpecialAlias(self):
        return TOOLTIPS_CONSTANTS.BLUEPRINT_RANDOM_INFO

    def getBlueprintSpecialArgs(self):
        return None

    def formatBlueprintValue(self):
        pass

    def getImageCategory(self):
        pass

    def getImage(self, size='big'):
        return RES_ICONS.getBlueprintFragment(size, self.getImageCategory())

    def getCount(self):
        return self._value[1]

    def getTooltip(self):
        pass

    def canPacked(self):
        return False

    def _getFormattedMessage(self, styleSubset, formattedValue):
        return makeHtmlString('html_templates:lobby/quests/{}'.format(styleSubset), self._HTML_TEMPLATE, {'value': formattedValue})

    def _format(self, styleSubset):
        formattedValue = str(self.getValue()[1])
        text = ''
        if formattedValue is not None:
            text = self._getFormattedMessage(styleSubset, formattedValue)
        return text


class VehicleBlueprintBonus(SimpleBonus):
    _HTML_TEMPLATE = 'vehicleBlueprints'

    def __init__(self, name, value, isCompensation=False, ctx=None):
        super(VehicleBlueprintBonus, self).__init__(name, value, isCompensation, ctx)
        if self._isFinalFragment():
            self._name = 'finalBlueprints'

    def getBlueprintName(self):
        return BlueprintsBonusSubtypes.FINAL_FRAGMENT if self._isFinalFragment() else BlueprintsBonusSubtypes.VEHICLE_FRAGMENT

    def getBlueprintSpecialAlias(self):
        return TOOLTIPS_CONSTANTS.BLUEPRINT_INFO if self._isFinalFragment() else TOOLTIPS_CONSTANTS.BLUEPRINT_FRAGMENT_INFO

    def getBlueprintSpecialArgs(self):
        return self._getFragmentCD()

    def formatBlueprintValue(self):
        return text_styles.neutral(self.itemsCache.items.getItemByCD(self._getFragmentCD()).shortUserName)

    def getImageCategory(self):
        return 'vehicle_complete' if self._isFinalFragment() else 'vehicle'

    def getImage(self, size='big'):
        return RES_ICONS.getBlueprintFragment(size, self.getImageCategory())

    def getCount(self):
        return self._value[1]

    def getTooltip(self):
        pass

    def getWrappedEpicBonusList(self):
        result = []
        result.append({'id': self._getFragmentCD(),
         'type': 'custom/{}'.format(self.getName()),
         'value': self.getCount(),
         'icon': {AWARDS_SIZES.SMALL: self.getImage(),
                  AWARDS_SIZES.BIG: self.getImage()},
         'name': self.getBlueprintTooltipName(),
         'description': self._getDescription()})
        return result

    def canPacked(self):
        return False

    def getBlueprintTooltipName(self):
        return backport.text(R.strings.tooltips.blueprint.VehicleBlueprintTooltip.header())

    def _getDescription(self):
        return backport.text(R.strings.tooltips.blueprint.VehicleBlueprintTooltip.descriptionFirst())

    def _getFragmentCD(self):
        return self._value[0]

    def _getFormattedMessage(self, styleSubset, formattedValue):
        vehicleName = self.itemsCache.items.getItemByCD(self._getFragmentCD()).shortUserName
        return makeHtmlString('html_templates:lobby/quests/{}'.format(styleSubset), self._HTML_TEMPLATE, {'vehicleName': vehicleName,
         'value': formattedValue})

    def _format(self, styleSubset):
        formattedValue = str(self.getValue()[1])
        text = ''
        if formattedValue is not None:
            text = self._getFormattedMessage(styleSubset, formattedValue)
        return text

    def _isFinalFragment(self):
        level = self.itemsCache.items.getItemByCD(self._getFragmentCD()).level
        filledCount, totalCount = self.itemsCache.items.blueprints.getBlueprintCount(self._getFragmentCD(), level)
        return True if filledCount == totalCount else False


class IntelligenceBlueprintBonus(VehicleBlueprintBonus):
    _HTML_TEMPLATE = 'universalBlueprints'

    def getBlueprintName(self):
        return BlueprintsBonusSubtypes.UNIVERSAL_FRAGMENT

    def getBlueprintSpecialArgs(self):
        return int(makeIntelligenceCD(self._getFragmentCD()))

    def getImageCategory(self):
        pass

    def getBlueprintSpecialAlias(self):
        return TOOLTIPS_CONSTANTS.BLUEPRINT_FRAGMENT_INFO

    def formatBlueprintValue(self):
        pass

    def canPacked(self):
        return self._ctx.get('isPacked', False) and self.getCount() > 1

    def getBlueprintTooltipName(self):
        return backport.text(R.strings.tooltips.blueprint.BlueprintFragmentTooltip.intelFragment())

    def _getDescription(self):
        return backport.text(R.strings.tooltips.blueprint.BlueprintFragmentTooltip.intelDescription())

    def _getFormattedMessage(self, styleSubset, formattedValue):
        return makeHtmlString('html_templates:lobby/quests/{}'.format(styleSubset), self._HTML_TEMPLATE, {'value': formattedValue})

    def _isFinalFragment(self):
        return False


class NationalBlueprintBonus(VehicleBlueprintBonus):
    _HTML_TEMPLATE = 'nationBlueprints'

    def getBlueprintName(self):
        return BlueprintsBonusSubtypes.NATION_FRAGMENT

    def getBlueprintSpecialArgs(self):
        return int(makeNationalCD(self._getFragmentCD()))

    def getImageCategory(self):
        import nations
        return nations.NAMES[self.__getNationID()]

    def getBlueprintSpecialAlias(self):
        return TOOLTIPS_CONSTANTS.BLUEPRINT_FRAGMENT_INFO

    def formatBlueprintValue(self):
        pass

    def canPacked(self):
        return self._ctx.get('isPacked', False) and self.getCount() > 1

    def getBlueprintTooltipName(self):
        return i18n.makeString(TOOLTIPS.BLUEPRINT_BLUEPRINTFRAGMENTTOOLTIP_NATIONALFRAGMENT)

    def _getDescription(self):
        return i18n.makeString(TOOLTIPS.BLUEPRINT_BLUEPRINTFRAGMENTTOOLTIP_NATIONALDESCRIPTION, nation=self._localizedNationName())

    def _localizedNationName(self):
        nationID = self.__getNationID()
        return backport.text(R.strings.nations.dyn(NAMES[nationID]).genetiveCase())

    def _getFormattedMessage(self, styleSubset, formattedValue):
        return makeHtmlString('html_templates:lobby/quests/{}'.format(styleSubset), self._HTML_TEMPLATE, {'nationName': self._localizedNationName(),
         'value': formattedValue})

    def _isFinalFragment(self):
        return False

    def __getNationID(self):
        return getFragmentNationID(self._getFragmentCD())


class CrewSkinsBonus(SimpleBonus):

    def getItems(self):
        if self._value is None:
            return []
        else:
            getItem = self.itemsCache.items.getCrewSkin
            result = []
            crewSkinID = self._value.get('id', NO_CREW_SKIN_ID)
            count = self._value.get('count', 0)
            customCompensation = self._value.get('customCompensation', None)
            compensatedNumber = self._value.get('compensatedNumber', None)
            if crewSkinID != NO_CREW_SKIN_ID and (count > 0 or customCompensation is not None):
                crewSkinItem = getItem(crewSkinID)
                if crewSkinItem is not None:
                    if customCompensation is not None and compensatedNumber is not None:
                        customCompensation = (customCompensation,)
                    if compensatedNumber > 0:
                        result.append((crewSkinItem,
                         0,
                         customCompensation,
                         compensatedNumber))
                    if count > 0:
                        result.append((crewSkinItem,
                         count,
                         None,
                         0))
            return result

    def format(self):
        return ', '.join(self.formattedList())

    def formattedList(self):
        sortedByRarity = {}
        for item, count, _, _ in self.getItems():
            if count:
                rarity = item.getRarity()
                totalCount = sortedByRarity.setdefault(rarity, 0)
                sortedByRarity[rarity] = totalCount + count

        result = []
        for rarity, count in sortedByRarity.iteritems():
            result.append(makeHtmlString('html_templates:lobby/quests/bonuses', 'crewSkin', {'value': count,
             'rarity': str(rarity)}))

        return result

    def getWrappedEpicBonusList(self):
        result = []
        for item, count, _, _ in self.getItems():
            if item is not None:
                result.append({'id': item.intCD,
                 'name': localizedFullName(item),
                 'description': item.getDescription(),
                 'type': 'item/{}'.format(item.itemTypeName),
                 'value': count,
                 'icon': {AWARDS_SIZES.SMALL: backport.image(R.images.gui.maps.icons.tankmen.icons.small.crewSkins.dyn(item.getIconID())()),
                          AWARDS_SIZES.BIG: backport.image(R.images.gui.maps.icons.tankmen.icons.big.crewSkins.dyn(item.getIconID())())}})

        return result

    def compensation(self, compensatedNumber, customCompensation, bonus):
        bonuses = []
        if compensatedNumber > 0 and customCompensation is not None:
            money = Money(*customCompensation)
            currencies = money.getSetCurrencies(byWeight=True)
            for currency in currencies:
                cls = _BONUSES.get(currency)
                bonuses.append(cls(currency, money.get(currency=currency), isCompensation=True, compensationReason=bonus))

        return bonuses

    def __getCommonAwardsVOs(self, item, count, iconSize='small', align=TEXT_ALIGN.RIGHT, withCounts=False):
        itemInfo = {'imgSource': item.getBonusIcon(iconSize),
         'label': text_styles.stats('x{}'.format(count)),
         'align': align,
         'isSpecial': True,
         'specialArgs': [item.id],
         'specialAlias': TOOLTIPS_CONSTANTS.CREW_SKIN}
        if withCounts:
            itemInfo['count'] = count
        return itemInfo


class CrewBooksBonus(SimpleBonus):

    def getItems(self):
        if self._value is None:
            return []
        else:
            getItem = self.itemsCache.items.getItemByCD
            result = []
            for crewBookCD, count in self._value.iteritems():
                crewBookItem = getItem(crewBookCD)
                if crewBookItem is not None:
                    result.append((crewBookItem, count))

            return sorted(result, lambda x, y: orderCmp(x[0], y[0]))

    def format(self):
        return ', '.join(self.formattedList())

    def formattedList(self):
        result = []
        for item, count in self.getItems():
            result.append(makeHtmlString('html_templates:lobby/quests/bonuses', 'crewBook', {'type': item.getBookType(),
             'nation': item.getNation(),
             'value': count,
             'name': item.userName}))

        return result

    def getWrappedEpicBonusList(self):
        result = []
        for item, count in self.getItems():
            if item is not None:
                result.append({'id': item.intCD,
                 'type': 'item/{}'.format(item.itemTypeName),
                 'value': count,
                 'icon': {AWARDS_SIZES.SMALL: item.getOldStyleIcon(AWARDS_SIZES.SMALL),
                          AWARDS_SIZES.BIG: item.getOldStyleIcon(AWARDS_SIZES.BIG)},
                 'name': item.userName,
                 'description': item.fullDescription})

        return result

    def __getCommonAwardsVOs(self, item, count, iconSize='small', align=TEXT_ALIGN.RIGHT, withCounts=False):
        itemInfo = {'imgSource': item.getBonusIcon(iconSize),
         'label': text_styles.stats('x{}'.format(count)),
         'align': align,
         'isSpecial': True,
         'specialArgs': [item.id],
         'specialAlias': None}
        if withCounts:
            itemInfo['count'] = count
        return itemInfo


class EpicAbilityPtsBonus(SimpleBonus):
    pass


class ItemsBonusFactory(object):
    CREW_BOOKS_BONUS_CLASS = CrewBooksBonus
    ITEMS_BONUS_CLASS = ItemsBonus

    def __call__(self, name, value, isCompensation=False, ctx=None):
        itemBonusesDict = {}
        crewBooksBonusesDict = {}
        itemBonuses = []
        for intCD, count in value.iteritems():
            itemTypeID, _, _ = vehicles.parseIntCompactDescr(intCD)
            bonusesDict = crewBooksBonusesDict if itemTypeID == GUI_ITEM_TYPE.CREW_BOOKS else itemBonusesDict
            bonusesDict[intCD] = count

        if crewBooksBonusesDict:
            itemBonuses.append(self.CREW_BOOKS_BONUS_CLASS('crewBooks', crewBooksBonusesDict, isCompensation, ctx))
        if itemBonusesDict:
            itemBonuses.append(self.ITEMS_BONUS_CLASS(name, itemBonusesDict, isCompensation, ctx))
        return itemBonuses


class CrewSkinsBonusFactory(object):
    CREW_SKINS_BONUS_CLASS = CrewSkinsBonus

    def __call__(self, name, value, isCompensation=False, ctx=None):
        bonuses = []
        for crewSkinData in value:
            bonuses.append(self.CREW_SKINS_BONUS_CLASS(name=name, value=crewSkinData, isCompensation=isCompensation, ctx=ctx))

        return bonuses


_BONUSES = {Currency.CREDITS: CreditsBonus,
 Currency.GOLD: GoldBonus,
 Currency.CRYSTAL: CrystalBonus,
 Currency.EVENT_COIN: EventCoinBonus,
 'strBonus': SimpleBonus,
 'groups': SimpleBonus,
 'xp': IntegralBonus,
 'freeXP': FreeXpBonus,
 'tankmenXP': IntegralBonus,
 'xpFactor': FloatBonus,
 'creditsFactor': FloatBonus,
 'freeXPFactor': FloatBonus,
 'tankmenXPFactor': FloatBonus,
 'dailyXPFactor': FloatBonus,
 'slots': CountableIntegralBonus,
 'berths': CountableIntegralBonus,
 PREMIUM_ENTITLEMENTS.BASIC: BasicPremiumDaysBonus,
 PREMIUM_ENTITLEMENTS.PLUS: PlusPremiumDaysBonus,
 'vehicles': VehiclesBonus,
 'meta': MetaBonus,
 'tokens': {'default': tokensFactory,
            _ET.BATTLE_QUEST: tokensFactory,
            _ET.TOKEN_QUEST: tokensFactory,
            _ET.PERSONAL_QUEST: tokensFactory,
            _ET.PERSONAL_MISSION: personalMissionsTokensFactory,
            _ET.ELEN_QUEST: tokensFactory},
 'dossier': {'default': DossierBonus,
             _ET.PERSONAL_MISSION: PersonalMissionDossierBonus},
 'tankmen': {'default': TankmenBonus,
             _ET.PERSONAL_MISSION: TankwomanBonus},
 'customizations': CustomizationsBonus,
 'goodies': GoodiesBonus,
 'items': ItemsBonusFactory(),
 'oneof': BoxBonus,
 'badgesGroup': BadgesGroupBonus,
 'blueprints': blueprintBonusFactory,
 'blueprintsAny': randomBlueprintBonusFactory,
 'crewSkins': CrewSkinsBonusFactory(),
 'entitlements': entitlementsFactory,
 'rankedDailyBattles': CountableIntegralBonus,
 'rankedBonusBattles': CountableIntegralBonus}
HIDDEN_BONUSES = (MetaBonus,)
_BONUSES_PRIORITY = ('tokens', 'oneof')
_BONUSES_ORDER = dict(((n, idx) for idx, n in enumerate(_BONUSES_PRIORITY)))

def compareBonuses(bonusName1, bonusName2):
    if bonusName1 not in _BONUSES_ORDER and bonusName2 not in _BONUSES_ORDER:
        return cmp(bonusName1, bonusName2)
    if bonusName1 not in _BONUSES_ORDER:
        return 1
    return -1 if bonusName2 not in _BONUSES_ORDER else _BONUSES_ORDER[bonusName1] - _BONUSES_ORDER[bonusName2]


def _getFromTree(tree, path):
    if not tree or not path:
        return
    else:
        key = path[0]
        subTree = None
        if key in tree:
            subTree = tree[key]
        elif 'default' in tree:
            subTree = tree['default']
        return _getFromTree(subTree, path[1:]) if isinstance(subTree, dict) else subTree


def _initFromTree(key, name, value, isCompensation=False, ctx=None):
    factory = _getFromTree(_BONUSES, key)
    if factory is not None:
        result = factory(name, value, isCompensation, ctx)
        if result is not None:
            if not isinstance(result, list):
                return [result]
            return result
    return []


def getBonuses(quest, name, value, isCompensation=False, ctx=None):
    questType = quest.getType()
    key = [name, questType]
    ctx = ctx or {}
    if questType in (_ET.BATTLE_QUEST, _ET.TOKEN_QUEST, _ET.PERSONAL_QUEST) and name == 'tokens':
        parentsName = quest.getParentsName()
        for n, v in value.iteritems():
            if n in parentsName:
                questNames = parentsName[n]
                if questNames:
                    v.update({'questNames': questNames})

    elif questType == _ET.PERSONAL_MISSION:
        ctx.update({'operationID': quest.getOperationID(),
         'chainID': quest.getChainID(),
         'campaignID': quest.getCampaignID(),
         'areTokensPawned': False})
    return _initFromTree(key, name, value, isCompensation, ctx=ctx)


def getTutorialBonuses(name, value):
    if name == 'dossier':
        key = (name, 'default')
    else:
        key = (name,)
    return _initFromTree(key, name, value)


def getEventBoardsBonusObj(name, value):
    return _initFromTree((name, _ET.ELEN_QUEST), name, value)


def getNonQuestBonuses(name, value, ctx=None):
    return _initFromTree((name, 'default'), name, value, ctx=ctx)


def getOfferBonuses(name, value, ctx=None):
    from account_helpers.offers.offer_bonuses import OfferBonusAdapter, OFFER_BONUSES
    offerBonuses = []
    isCompensation = False
    offerBonusFactory = _getFromTree(OFFER_BONUSES, (name, 'default'))
    if offerBonusFactory is not None:
        result = offerBonusFactory(name, value, isCompensation, ctx)
        if result is not None:
            offerBonuses = result if isinstance(result, list) else [result]
    else:
        bonuses = getNonQuestBonuses(name, value)
        offerBonuses = [ OfferBonusAdapter(bonus) for bonus in bonuses ]
    return offerBonuses


def getSimpleTooltipData(name):
    return (TOOLTIPS.getAwardHeader(name), TOOLTIPS.getAwardBody(name))


def _getItemTooltip(name):
    data = getSimpleTooltipData(name)
    header = i18n.makeString(data[0])
    body = i18n.makeString(data[1])
    return makeTooltip(header or None, body or None) if header or body else ''


def mergeBonuses(bonuses):
    merged = copy.deepcopy(bonuses)
    if len(merged) > 1:
        i = 0
        while i < len(merged) - 1:
            j = i + 1
            while j < len(merged):
                mergFunc = getMergeBonusFunction(merged[i], merged[j])
                if mergFunc and merged[i].getName() == merged[j].getName():
                    merged[i], needPop = mergFunc(merged[i], merged[j])
                    if needPop:
                        merged.pop(j)
                    else:
                        j += 1
                j += 1

            i += 1

    return merged


def getMergeBonusFunction(lhv, rhv):

    def hasOneBaseClass(l, r, cls):
        return isinstance(l, cls) and isinstance(r, cls)

    def ofSameClassWithBase(l, r, cls):
        return hasOneBaseClass(l, r, cls) and type(l) is type(r)

    if ofSameClassWithBase(lhv, rhv, CrewSkinsBonus):
        return None
    elif hasOneBaseClass(lhv, rhv, ItemsBonus):
        return mergeItemsBonuses
    elif hasOneBaseClass(lhv, rhv, IntegralBonus) or hasOneBaseClass(lhv, rhv, GoldBonus):
        return mergeIntegralBonuses
    else:
        return mergeSimpleBonuses if ofSameClassWithBase(lhv, lhv, SimpleBonus) else None


def mergeItemsBonuses(lhv, rhv):
    merged = copy.deepcopy(lhv)
    for key in merged.getValue():
        if key in rhv.getValue():
            merged.getValue()[key] += rhv.getValue()[key]

    for key, value in rhv.getValue().iteritems():
        if key not in merged.getValue():
            merged.getValue()[key] = value

    return (merged, True)


def mergeIntegralBonuses(lhv, rhv):
    merged = copy.deepcopy(lhv)
    merged.setValue(merged.getValue() + rhv.getValue())
    return (merged, True)


def mergeSimpleBonuses(lhv, rhv):
    merged = copy.deepcopy(lhv)
    value = merged.getValue()
    needPop = False
    if isinstance(value, tuple):
        lKey, lValue = value
        rKey, rValue = rhv.getValue()
        if lKey == rKey:
            merged.setValue((lKey, lValue + rValue))
            needPop = True
    elif isinstance(value, dict):
        merged.setValue(__mergeDicts(value, rhv.getValue()))
        needPop = True
    return (merged, needPop)


def __mergeDicts(lhv, rhv):
    merged = copy.deepcopy(lhv)
    for key in merged.keys():
        if key in rhv:
            if isinstance(merged[key], dict):
                merged[key] = __mergeDicts(merged[key], rhv[key])
            else:
                merged[key] = merged[key] + rhv[key]

    for key in rhv.keys():
        if key not in merged:
            merged[key] = rhv[key]

    return merged


def getMergedBonusesFromDicts(bonusesList):
    result = {}
    for bonuses in bonusesList:
        for bonusName, bonusValue in bonuses.iteritems():
            if bonusName in BONUS_MERGERS:
                BONUS_MERGERS[bonusName](result, bonusName, bonusValue, False, 1, None)
            _logger.warning('BONUS_MERGERS has not bonus %s', bonusName)

    return result


def splitBonuses(bonuses):
    split = []
    for bonus in bonuses:
        splitFunc = getSplitBonusFunction(bonus)
        if splitFunc:
            split.extend(splitFunc(bonus))
        split.append(bonus)

    return split


def getSplitBonusFunction(bonus):
    if isinstance(bonus, CrewSkinsBonus):
        return None
    elif isinstance(bonus, CustomizationsBonus):
        return splitCustomizationsBonus
    elif isinstance(bonus, (IntegralBonus, GoldBonus)):
        return splitIntegralBonuses
    else:
        return splitSimpleBonuses if isinstance(bonus, SimpleBonus) else None


def splitIntegralBonuses(bonus):
    return [bonus]


def splitSimpleBonuses(bonus):
    split = []
    value = bonus.getValue()
    if isinstance(value, dict):
        for key, sub in value.iteritems():
            item = copy.deepcopy(bonus)
            item.setValue({key: sub})
            split.append(item)

    elif isinstance(value, list):
        for sub in value:
            item = copy.deepcopy(bonus)
            item.setValue([sub])
            split.append(item)

    else:
        split.append(bonus)
    return split


def splitCustomizationsBonus(bonus):
    split = []
    value = bonus.getValue()
    camoItem = None
    for sub in value:
        if sub.get('custType', '') == 'camouflage':
            if camoItem is None:
                camoItem = copy.deepcopy(bonus)
                camoItem.setValue([])
            oldValue = camoItem.getValue()
            oldValue.append(sub)
            camoItem.setValue(oldValue)
        item = copy.deepcopy(bonus)
        item.setValue([sub])
        split.append(item)

    if camoItem is not None:
        split.append(camoItem)
    return split
