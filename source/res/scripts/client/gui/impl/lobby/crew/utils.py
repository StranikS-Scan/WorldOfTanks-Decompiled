# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/crew/utils.py
import itertools
import typing
from collections import namedtuple, defaultdict
import Settings
import SoundGroups
import nations
from SoundGroups import CREW_GENDER_SWITCHES
from gui import GUI_NATIONS_ORDER_INDEX
from gui.impl import backport
from gui.impl.gen import R
from gui.impl.gen.view_models.views.lobby.common.reward_item_model import RewardItemModel
from gui.impl.gen.view_models.views.lobby.crew.common.filter_toggle_group_model import ToggleGroupType
from gui.impl.gen.view_models.views.lobby.crew.common.info_tip_model import InfoTipModel
from gui.impl.gen.view_models.views.lobby.crew.popovers.filter_popover_view_model import VehicleSortColumn
from gui.impl.gen.view_models.views.lobby.crew.tankman_model import TankmanLocation
from gui.impl.lobby.crew.filter import GRADE_PREMIUM, GRADE_ELITE, GRADE_PRIMARY
from gui.Scaleform.genConsts.STORE_CONSTANTS import STORE_CONSTANTS
from gui.shared.gui_items.Vehicle import VEHICLE_TYPES_ORDER_INDICES, VEHICLE_TAGS
from gui.shared.utils.requesters import REQ_CRITERIA
from helpers import strcmp, i18n, dependency
from items.components.crew_books_constants import CREW_BOOK_RARITY
from shared_utils import CONST_CONTAINER
from skeletons.gui.shared import IItemsCache
if typing.TYPE_CHECKING:
    from gui.shared.utils.requesters import RequestCriteria
    from gui.shared.gui_items.crew_book import CrewBook
    from typing import Dict, Set
VEHICLE_TAGS_FILTER = (VEHICLE_TAGS.PREMIUM_IGR, VEHICLE_TAGS.WOT_PLUS)
DocumentRecord = namedtuple('DocumentRecord', ['id', 'group', 'value'])

class TRAINING_TIPS(CONST_CONTAINER):
    CHOOSE_ANY_CREW_MEMBER = 'chooseAnyCrewMember'
    NOT_TRAINED_THIS_VEHICLE = 'notTrainedThisVehicle'
    NOT_FULL_CREW = 'notFullCrew'
    NOT_FULL_AND_NOT_TRAINED_CREW = 'notFullAndNotTrainedCrew'
    LOW_PE_CREW = 'LowPECrew'
    LOW_PE_NOT_FULL_CREW = 'LowPENotFullCrew'
    LOW_PE_NOT_TRAINED_CREW = 'LowPENotTrainedCrew'
    LOW_PE_NOT_TRAINED_NOT_FULL = 'LowPENotTrainedNotFullCrew'
    LOW_PE_TIPS_PERSONAL = 'LowPEtipsPersonal'
    WILL_FULL_TRAINED_PERSONAL = 'WillFullTrainedPersonal'
    WILL_FULL_TRAINED_FEW_MEMBERS = 'WillFullTrainedFewMembers'
    WILL_FULL_TRAINED_CREW = 'WillFullTrainedCrew'
    FULL_TRAINED_PERSONAL = 'FullTrainedPersonal'
    FULL_TRAINED_FEW_MEMBERS = 'FullTrainedFewMembers'
    ALL_FULL_TRAINED = 'AllFullTrained'
    tips = {CHOOSE_ANY_CREW_MEMBER: 1,
     NOT_TRAINED_THIS_VEHICLE: 11,
     NOT_FULL_CREW: 12,
     NOT_FULL_AND_NOT_TRAINED_CREW: 13,
     LOW_PE_CREW: 14,
     LOW_PE_NOT_FULL_CREW: 15,
     LOW_PE_NOT_TRAINED_CREW: 16,
     LOW_PE_NOT_TRAINED_NOT_FULL: 17,
     LOW_PE_TIPS_PERSONAL: 18,
     WILL_FULL_TRAINED_PERSONAL: 19,
     WILL_FULL_TRAINED_FEW_MEMBERS: 20,
     WILL_FULL_TRAINED_CREW: 21,
     FULL_TRAINED_PERSONAL: 22,
     FULL_TRAINED_FEW_MEMBERS: 23,
     ALL_FULL_TRAINED: 24}


def setTextFormatter(tipID, forPlaceHolders):
    text = backport.text(R.strings.tooltips.quickTraining.dyn(tipID)())
    return i18n.makeString(text, **forPlaceHolders) if forPlaceHolders else text


def getTip(tipID, tipType, **forPlaceHolders):
    tip = InfoTipModel()
    tip.setId(TRAINING_TIPS.tips[tipID])
    tip.setText(setTextFormatter(tipID, forPlaceHolders))
    tip.setType(tipType)
    return tip


def loadDoNotOpenTips():
    doNotOpenTips = []
    userPrefs = Settings.g_instance.userPrefs
    if userPrefs is None or not userPrefs.has_key(Settings.QUICK_TRANING_TIPS):
        return doNotOpenTips
    else:
        ds = userPrefs[Settings.QUICK_TRANING_TIPS]
        for key, _ in TRAINING_TIPS.infoTips.items():
            isDoNotOpenTip = ds.readBool(key, False)
            if isDoNotOpenTip:
                doNotOpenTips.append(key)

        return doNotOpenTips


def saveDoNotOpenTip(doNotOpenTip):
    userPrefs = Settings.g_instance.userPrefs
    if userPrefs is None:
        return
    else:
        if not userPrefs.has_key(Settings.QUICK_TRANING_TIPS):
            userPrefs.write(Settings.QUICK_TRANING_TIPS, '')
        ds = userPrefs[Settings.QUICK_TRANING_TIPS]
        ds.writeBool(doNotOpenTip, True)
        return


def buildPopoverTankFilterCriteria(filters):
    criteria = REQ_CRITERIA.UNLOCKED
    criteria |= REQ_CRITERIA.INVENTORY
    criteria |= ~REQ_CRITERIA.VEHICLE.IS_CREW_LOCKED
    criteria |= ~getRentCriteria()
    criteria |= ~REQ_CRITERIA.VEHICLE.EVENT_BATTLE
    criteria |= ~REQ_CRITERIA.VEHICLE.BATTLE_ROYALE
    for field, value in filters.items():
        if not value:
            continue
        if field == ToggleGroupType.NATION.value:
            criteria |= REQ_CRITERIA.NATIONS(tuple((nations.INDICES[item] for item in value)))
        if field == ToggleGroupType.VEHICLETYPE.value and value:
            criteria |= REQ_CRITERIA.VEHICLE.CLASSES(tuple(value))
        if field == ToggleGroupType.TANKMANROLE.value and value:
            roleCriteria = REQ_CRITERIA.NONE
            for role in value:
                roleCriteria ^= REQ_CRITERIA.VEHICLE.HAS_ROLE(role)

            criteria |= roleCriteria
        if field == ToggleGroupType.VEHICLETIER.value and value:
            criteria |= REQ_CRITERIA.VEHICLE.LEVELS(tuple((int(item) for item in value)))
        if field == ToggleGroupType.VEHICLEGRADE.value and value:
            value = value - {TankmanLocation.INTANK.value, TankmanLocation.INBARRACKS.value}
            if not value:
                continue
            gradeCriteria = REQ_CRITERIA.NONE
            if GRADE_PREMIUM in value:
                gradeCriteria ^= REQ_CRITERIA.VEHICLE.PREMIUM
            if GRADE_ELITE in value:
                gradeCriteria ^= REQ_CRITERIA.CUSTOM(lambda vehicle: vehicle.isElite and not vehicle.isPremium)
            if GRADE_PRIMARY in value:
                gradeCriteria ^= REQ_CRITERIA.VEHICLE.FAVORITE
            criteria |= gradeCriteria

    return criteria


def buildPopoverTankKeySortCriteria(field):
    if field == VehicleSortColumn.TIER.value:
        return REQ_CRITERIA.CUSTOM(lambda item: item.level)
    if field == VehicleSortColumn.NAME.value:
        return REQ_CRITERIA.CUSTOM(lambda item: item.searchableUserName)
    if field == VehicleSortColumn.TYPE.value:
        criteria = REQ_CRITERIA.CUSTOM(lambda item: VEHICLE_TYPES_ORDER_INDICES[item.type])
        return criteria | REQ_CRITERIA.CUSTOM(lambda item: item.isPremium)


def getRentCriteria():
    return REQ_CRITERIA.CUSTOM(lambda item: item.isRented and not item.isWotPlus)


def getDocGroupValues(tankman, config, listGetter, valueGetter, sortNeeded=True):
    result = []
    isFemale = tankman.descriptor.isFemale
    for gIdx, group in config.getGroups(isFemale).iteritems():
        if not group.notInShop and group.isFemales == isFemale:
            for dIdx in listGetter(group):
                result.append(DocumentRecord(dIdx, gIdx, valueGetter(dIdx)))

    if sortNeeded:
        result = sorted(result, key=lambda sortField: sortField.value, cmp=lambda a, b: strcmp(unicode(a), unicode(b)))
    return result


def jsonArgsConverter(fields=()):
    from functools import wraps
    from json import loads

    def inner(func):

        @wraps(func)
        def wrapper(self, jsonData, *args, **kwargs):
            newArgs = tuple(((loads(data) if isinstance(data, (str, unicode)) else data) for data in (jsonData.get(field) for field in fields if field))) + args
            return func(self, *newArgs, **kwargs)

        return wrapper

    return inner


ALT_VOICES_PREVIEW = itertools.cycle(('vo_enemy_hp_damaged_by_projectile_by_player', 'vo_enemy_fire_started_by_player', 'vo_enemy_killed_by_player'))

def playRecruitVoiceover(voiceoverParams):
    SoundGroups.g_instance.setSwitch(CREW_GENDER_SWITCHES.GROUP, voiceoverParams.genderSwitch)
    SoundGroups.g_instance.soundModes.setMode(voiceoverParams.languageMode)
    sound = SoundGroups.g_instance.getSound2D(next(ALT_VOICES_PREVIEW))
    sound.play()
    return sound


def discountPercent(value, defaultValue):
    return int(100 * (1 - float(value) / defaultValue)) if defaultValue else 0


@dependency.replace_none_kwargs(itemsCache=IItemsCache)
def packCompensationData(books, rewardsArray, tooltipData, itemsCache=None):
    bookTypeOrder = [CREW_BOOK_RARITY.CREW_EPIC, CREW_BOOK_RARITY.CREW_RARE, CREW_BOOK_RARITY.CREW_COMMON]
    booksDataByType = defaultdict(lambda : {'amount': 0,
     'books': []})
    for key, value in books.iteritems():
        book = itemsCache.items.getItemByCD(key)
        if book is None:
            continue
        typeData = booksDataByType[book.getBookType()]
        typeData['amount'] += value
        typeData['books'].append((book, value))

    booksAmount = 0
    for key in bookTypeOrder:
        if key not in booksDataByType:
            continue
        value = booksDataByType[key]
        tooltipData[key] = sorted(value['books'], cmp=lambda item, other: cmp(GUI_NATIONS_ORDER_INDEX.get(item[0].getNation()), GUI_NATIONS_ORDER_INDEX.get(other[0].getNation())))
        reward = RewardItemModel()
        reward.setIcon(key + '_pack')
        reward.setValue(str(value['amount']))
        reward.setName('crewBooks')
        reward.setType('crewBooks')
        reward.setLabel(backport.text(R.strings.crew_books.items.dyn(key).noNationUppercaseName()))
        reward.setTooltipId(key)
        reward.setTooltipContentId(str(R.views.lobby.crew.tooltips.ConversionTooltip()))
        rewardsArray.addViewModel(reward)
        booksAmount += 1

    return booksAmount


BOOSTER_ICON_MAPPING = {'enemyShotPredictorBattleBooster': 'commander_enemyShotPredictor',
 'practicalityBattleBooster': 'commander_practical',
 'lastEffortBattleBooster': 'radioman_lastEffort',
 'sixthSenseBattleBooster': 'commander_sixthSense'}

@dependency.replace_none_kwargs(itemsCache=IItemsCache)
def packBoostersCompensationData(boosters, rewardsArray, tooltipData, itemsCache=None):
    for boosterReplacement in boosters:
        newEqCD = boosterReplacement['newEqCD']
        count = boosterReplacement['count']
        tooltipId = str(newEqCD)
        tooltipData[tooltipId] = {'oldDirectiveID': boosterReplacement['oldEqCD'],
         'newDirectiveID': newEqCD,
         'amount': count}
        booster = itemsCache.items.getItemByCD(newEqCD)
        reward = RewardItemModel()
        reward.setItem(BOOSTER_ICON_MAPPING.get(booster.name))
        reward.setValue(str(count))
        reward.setName('items')
        reward.setType('items')
        reward.setLabel(booster.userName)
        reward.setTooltipId(tooltipId)
        reward.setOverlayType(STORE_CONSTANTS.BATTLE_BOOSTER)
        reward.setTooltipContentId(str(R.views.lobby.crew.tooltips.DirectiveConversionTooltip()))
        rewardsArray.addViewModel(reward)


def convertMoneyToTuple(money):
    return (money.credits, money.gold, money.crystal)
