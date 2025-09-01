# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: comp7/scripts/client/comp7/gui/impl/lobby/comp7_helpers/comp7_bonus_packer.py
import logging
import typing
from comp7.gui.Scaleform.genConsts.TOOLTIPS_CONSTANTS import TOOLTIPS_CONSTANTS as COMP7_TOOLTIPS
from comp7.gui.impl.gen.view_models.views.lobby.comp7_bonus_model import Comp7BonusModel, DogTagType
from comp7.gui.impl.gen.view_models.views.lobby.comp7_style_bonus_model import Comp7StyleBonusModel
from comp7.gui.impl.lobby.comp7_helpers.comp7_bonus_helpers import BonusTypes, getBonusType, splitDossierBonuses, CustomizationsBonusHelper
from comp7.gui.impl.lobby.comp7_helpers.comp7_c11n_helpers import getComp7ProgressionStyleCamouflage
from comp7.gui.impl.lobby.comp7_helpers.comp7_quest_helpers import isComp7OfferYearlyRewardToken
from comp7.gui.selectable_reward.common import Comp7SelectableRewardManager
from comp7.gui.server_events.bonuses import COMP7_TOKEN_WEEKLY_REWARD_NAME
from comp7_common_const import offerRewardGiftToken
from dog_tags_common.components_config import componentConfigAdapter
from dog_tags_common.config.common import ComponentViewType
from gui.Scaleform.genConsts.TOOLTIPS_CONSTANTS import TOOLTIPS_CONSTANTS
from gui.impl import backport
from gui.impl.backport import TooltipData, createTooltipData
from gui.impl.gen import R
from gui.impl.gen.view_models.common.bonus_model import BonusModel
from gui.selectable_reward.constants import SELECTABLE_BONUS_NAME
from gui.server_events.bonuses import getNonQuestBonuses, mergeBonuses, splitBonuses, C11nProgressTokenBonus, getVehicleCrewReward, CountableIntegralBonus, CustomizationsBonus, VehiclesBonus, _BONUSES, TankmenBonus
from gui.shared.gui_items.Tankman import getFullUserName
from gui.shared.gui_items.customization import CustomizationTooltipContext
from gui.shared.missions.packers.bonus import DossierBonusUIPacker, DogTagComponentsUIPacker, BonusUIPacker, BaseBonusUIPacker, BACKPORT_TOOLTIP_CONTENT_ID, SimpleBonusUIPacker, CustomizationBonusUIPacker, VehiclesBonusUIPacker, TokenBonusUIPacker, TankmenBonusUIPacker
from gui.shared.missions.packers.bonus import getDefaultBonusPackersMap
from gui.shared.money import Currency
from helpers import dependency
from items import tankmen
from items.tankmen import getNationConfig
from shared_utils import findFirst, first
from skeletons.gui.customization import ICustomizationService
from skeletons.gui.game_control import IComp7Controller
from skeletons.gui.offers import IOffersDataProvider
from skeletons.gui.shared import IItemsCache
if typing.TYPE_CHECKING:
    from gui.server_events.bonuses import SimpleBonus
    from gui.server_events.bonuses import SelectableBonus
_logger = logging.getLogger(__name__)
_DOG_TAG_VIEW_TYPE_TO_DOG_TAG_TYPE_ENUM = {ComponentViewType.ENGRAVING: DogTagType.ENGRAVING,
 ComponentViewType.BACKGROUND: DogTagType.BACKGROUND}
_RANK_REWARDS_BONUSES_ORDER = (BonusTypes.STYLE_PROGRESS,
 BonusTypes.BADGE_SUFFIX,
 BonusTypes.BADGE,
 BonusTypes.DOGTAG_ENGRAVING,
 BonusTypes.DOGTAG_BACKGROUND,
 BonusTypes.CRYSTAL,
 BonusTypes.STYLE,
 BonusTypes.RENT_VEHICLE)
_TOKENS_REWARDS_BONUSES_ORDER = (BonusTypes.ACHIEVEMENT,
 BonusTypes.DELUXE_DEVICE,
 BonusTypes.CREWBOOK,
 BonusTypes.PREMIUM,
 BonusTypes.CRYSTAL,
 BonusTypes.CREDITS,
 BonusTypes.OPTIONAL_DEVICE,
 BonusTypes.BOOSTER,
 BonusTypes.BATTLE_BOOSTER,
 BonusTypes.EQUIPMENT)
_QUALIFICATION_REWARDS_BONUSES_ORDER = (BonusTypes.STYLE_PROGRESS,
 BonusTypes.BADGE_SUFFIX,
 BonusTypes.BADGE,
 BonusTypes.DOGTAG_BACKGROUND,
 BonusTypes.DOGTAG_ENGRAVING,
 BonusTypes.CRYSTAL,
 BonusTypes.STYLE,
 BonusTypes.RENT_VEHICLE)
_YEARLY_REWARDS_BONUSES_ORDER = (BonusTypes.BADGE_SUFFIX,
 BonusTypes.BADGE,
 BonusTypes.ACHIEVEMENT,
 BonusTypes.STYLE,
 BonusTypes.STYLE_3D,
 BonusTypes.STYLE_PROGRESS,
 BonusTypes.DELUXE_DEVICE,
 BonusTypes.OFFER,
 BonusTypes.CRYSTAL)
_YEARLY_REWARD_META_BONUSES_ORDER = (BonusTypes.OFFER,
 BonusTypes.RENT_VEHICLE,
 BonusTypes.STYLE_3D_PROGRESS,
 BonusTypes.TOKEN,
 BonusTypes.STYLE_3D,
 BonusTypes.BADGE_SUFFIX,
 BonusTypes.BADGE,
 BonusTypes.CREW,
 BonusTypes.ACHIEVEMENT,
 BonusTypes.CRYSTAL,
 BonusTypes.STYLE)
_OFFER_REWARDS_ORDER = ('deluxe', 'modernized_devices_t3')

def _getComp7BonusPackersMap():
    mapping = getDefaultBonusPackersMap()
    mapping.update({'dossier': Comp7DossierBonusUIPacker(),
     'dogTagComponents': Comp7DogTagUIPacker(),
     'customizations': Comp7CustomizationBonusUIPacker(),
     'vehicles': Comp7VehicleBonusUIPacker(),
     'tankmen': Comp7TankmenBonusUIPacker(),
     SELECTABLE_BONUS_NAME: Comp7OfferBonusUIPacker(),
     Currency.CRYSTAL: Comp7CrystalBonusPacker(),
     C11nProgressTokenBonus.BONUS_NAME: Comp7StyleProgressBonusUIPacker(),
     COMP7_TOKEN_WEEKLY_REWARD_NAME: Comp7TokenWeeklyRewardUIPacker()})
    return mapping


def getComp7BonusPacker():
    mapping = _getComp7BonusPackersMap()
    return BonusUIPacker(mapping)


def getComp7YearlyBonusPacker():
    mapping = _getComp7BonusPackersMap()
    mapping.update({C11nProgressTokenBonus.BONUS_NAME: Comp7YearlyStylePacker()})
    return BonusUIPacker(mapping)


def getComp7YearlyMetaBonusPacker():
    mapping = _getComp7BonusPackersMap()
    mapping.update({SELECTABLE_BONUS_NAME: Comp7YearlyMetaOfferPacker(),
     'customizations': Comp7CustomizationBonusUIPacker(),
     'tankmen': Comp7YearlyCrewBonusUIPacker()})
    return BonusUIPacker(mapping)


def _getComp7YearlyBonuses(specificCustomization=None):
    bonuses = _BONUSES.copy()
    bonuses.update({'slots': Comp7YearlySlotsBonus,
     'customizations': specificCustomization or Comp7YearlyCustomizationsBonus})
    return bonuses


class Comp7DossierBonusUIPacker(DossierBonusUIPacker):

    @classmethod
    def _getBadgeTooltip(cls, bonus):
        tooltipData = []
        for badge in bonus.getBadges():
            tooltipData.append(TooltipData(tooltip=None, isSpecial=True, specialAlias=TOOLTIPS_CONSTANTS.BADGE, specialArgs=[badge.badgeID, badge.isSuffixLayout()]))

        return tooltipData


class Comp7DogTagUIPacker(DogTagComponentsUIPacker):

    @classmethod
    def _getBonusModel(cls):
        return Comp7BonusModel()

    @classmethod
    def _packDogTag(cls, bonus, dogTagRecord):
        model = super(Comp7DogTagUIPacker, cls)._packDogTag(bonus, dogTagRecord)
        dogTagComponent = componentConfigAdapter.getComponentById(dogTagRecord.componentId)
        model.setDogTagType(_DOG_TAG_VIEW_TYPE_TO_DOG_TAG_TYPE_ENUM[dogTagComponent.viewType])
        return model


class Comp7CrystalBonusPacker(SimpleBonusUIPacker):

    @classmethod
    def _packSingleBonus(cls, bonus, label):
        model = super(Comp7CrystalBonusPacker, cls)._packSingleBonus(bonus, label)
        model.setIsPeriodic(bonus.getContext().get('isPeriodic', False))
        return model

    @classmethod
    def _getBonusModel(cls):
        return Comp7BonusModel()


class Comp7StyleProgressBonusUIPacker(BaseBonusUIPacker):
    __c11nService = dependency.descriptor(ICustomizationService)

    @classmethod
    def _pack(cls, bonus):
        return [cls._packSingleBonus(bonus)]

    @classmethod
    def _packSingleBonus(cls, bonus, level=None):
        styleID = bonus.getStyleID()
        branchID = bonus.getBranchID()
        level = level or bonus.getProgressLevel()
        model = Comp7StyleBonusModel()
        cls._packCommon(bonus, model)
        camo = getComp7ProgressionStyleCamouflage(styleID, branchID, level)
        if camo is not None:
            icon = cls.__getIcon(styleID, level)
            label = cls.__getLabel(camo)
        else:
            _logger.error('Missing camouflage for Comp7StyleProgressBonus: styleID=%s; level=%s', styleID, level)
            icon = ''
            label = ''
        model.setIcon(icon)
        model.setLabel(label)
        model.setStyleID(styleID)
        model.setBranchID(branchID)
        model.setProgressLevel(level)
        return model

    @classmethod
    def _getToolTip(cls, bonus):
        return [cls._packTooltip(bonus)]

    @classmethod
    def _packTooltip(cls, bonus, level=None):
        styleID = bonus.getStyleID()
        branchID = bonus.getBranchID()
        level = level or bonus.getProgressLevel()
        camo = getComp7ProgressionStyleCamouflage(styleID, branchID, level)
        tooltipData = TooltipData(tooltip=None, isSpecial=True, specialAlias=TOOLTIPS_CONSTANTS.TECH_CUSTOMIZATION_ITEM_AWARD, specialArgs=CustomizationTooltipContext(itemCD=camo.intCD, skipQuestValidation=True))
        return tooltipData

    @classmethod
    def _getContentId(cls, bonus):
        return [BACKPORT_TOOLTIP_CONTENT_ID]

    @staticmethod
    def __getIcon(styleID, progressLevel):
        return 'style_progress_{styleID}_{progressLevel}'.format(styleID=styleID, progressLevel=progressLevel)

    @staticmethod
    def __getLabel(camo):
        return backport.text(R.strings.comp7_ext.rewards.bonus.style_progress(), name=camo.userName)


class Comp7YearlyStylePacker(Comp7StyleProgressBonusUIPacker):

    @classmethod
    def _pack(cls, bonus):
        return [ cls._packSingleBonus(bonus, level) for level in range(bonus.getProgressLevel(), 0, -1) ]

    @classmethod
    def _getToolTip(cls, bonus):
        return [ cls._packTooltip(bonus, level) for level in range(bonus.getProgressLevel(), 0, -1) ]


class Comp7CustomizationBonusUIPacker(CustomizationBonusUIPacker):
    _ICON_NAME = 'style'
    _ICON_NAME_PROGRESSION = 'progressionStyle'

    @classmethod
    def _packSingleBonus(cls, bonus, item, label):
        model = super(Comp7CustomizationBonusUIPacker, cls)._packSingleBonus(bonus, item, label)
        item = bonus.getC11nItem(item)
        styleID = item.id
        model.setStyleID(styleID)
        if item.is3D:
            model.setName('styleProgressToken')
            model.setValue('')
        model.setIcon(cls._ICON_NAME_PROGRESSION if item.isQuestsProgression else cls._ICON_NAME)
        model.setLabel(item.userName)
        return model

    @classmethod
    def _getBonusModel(cls):
        return Comp7StyleBonusModel()


class Comp7VehicleBonusUIPacker(VehiclesBonusUIPacker):

    @classmethod
    def _getLabel(cls, vehicle):
        return vehicle.shortUserName

    @classmethod
    def _packTooltip(cls, bonus, vehicle, vehInfo):
        return createTooltipData(isSpecial=True, specialAlias=TOOLTIPS_CONSTANTS.SHOP_VEHICLE, specialArgs=(vehicle.intCD,))


class Comp7TankmenBonusUIPacker(BaseBonusUIPacker):

    @classmethod
    def _pack(cls, bonus):
        result = []
        for tankmanData in bonus.getValue():
            result.append(cls._packSingleBonus(tankmanData))

        return result

    @classmethod
    def _packSingleBonus(cls, bonus):
        cd = bonus['tmanCompDescr'] if 'tmanCompDescr' in bonus else bonus
        tankmanData = tankmen.TankmanDescr(cd)
        model = Comp7BonusModel()
        model.setName('tankman')
        model.setLabel(getFullUserName(tankmanData.nationID, tankmanData.firstNameID, tankmanData.lastNameID))
        model.setGroupName(cls.__getTankmanGroupName(tankmanData))
        return model

    @classmethod
    def _getToolTip(cls, bonus):
        tooltipData = []
        for tankmanData in bonus.getValue():
            cd = tankmanData['tmanCompDescr'] if 'tmanCompDescr' in tankmanData else tankmanData
            tankman = tankmen.TankmanDescr(cd)
            tooltipData.append(createTooltipData(isSpecial=True, specialAlias=TOOLTIPS_CONSTANTS.SPECIAL_TANKMAN, specialArgs=(tankman, cls.__getTankmanGroupName(tankman))))

        return tooltipData

    @classmethod
    def __getTankmanGroupName(cls, tankmanData):
        premiumGroups = getNationConfig(tankmanData.nationID).premiumGroups
        tankmanGroup = findFirst(lambda group: group.groupID == tankmanData.gid, premiumGroups.itervalues())
        return tankmanGroup.name


class Comp7YearlyCrewBonusUIPacker(TankmenBonusUIPacker):

    @classmethod
    def _pack(cls, bonus):
        model = cls._getBonusModel()
        cls._packCommon(bonus, model)
        model.setName('onslaught_yearly_crew')
        model.setLabel(backport.text(R.strings.comp7_ext.yearlyRewards.rewards.crew()))
        model.setTooltipContentId(str(R.views.comp7.mono.lobby.tooltips.crew_members_tooltip()))
        return [model]

    @classmethod
    def _getToolTip(cls, bonus):
        return [createTooltipData()]

    @classmethod
    def _getBonusModel(cls):
        return Comp7BonusModel()


class Comp7TokenWeeklyRewardUIPacker(TokenBonusUIPacker):

    @classmethod
    def _pack(cls, bonus):
        model = cls._getBonusModel()
        model.setValue(str(bonus.getCount()))
        model.setName(bonus.getName())
        return [model]

    @classmethod
    def _getBonusModel(cls):
        return Comp7BonusModel()

    @classmethod
    def _getToolTip(cls, bonus):
        return [createTooltipData(bonus.getTooltip())]


class Comp7OfferBonusUIPacker(BaseBonusUIPacker):
    _selectableRewardManager = Comp7SelectableRewardManager
    _offersDataProvider = dependency.descriptor(IOffersDataProvider)
    _comp7Controller = dependency.descriptor(IComp7Controller)
    _itemsCache = dependency.descriptor(IItemsCache)

    @classmethod
    def _pack(cls, bonus):
        giftCountPerToken = cls._selectableRewardManager.getGiftCountPerToken(bonus)
        models = []
        for offerToken in sorted(bonus.getValue().iterkeys(), key=_getOfferRewardTokensSortKey(_OFFER_REWARDS_ORDER)):
            giftCount = giftCountPerToken.get(offerToken)
            if giftCount <= 0:
                continue
            offerTokenCategory = offerToken.split(':')[2]
            offerTokenCategoryGift = offerRewardGiftToken(offerTokenCategory)
            model = Comp7BonusModel()
            ownedTokens = cls._itemsCache.items.tokens.getTokensByPrefixAndPostfix(prefix=offerToken)
            hasTokenAndNoGiftToken = len(ownedTokens) == 1
            if hasTokenAndNoGiftToken:
                model.setClaimed(True)
            model.setName(offerTokenCategoryGift)
            model.setLabel(backport.text(R.strings.selectable_reward.tabs.items.dyn(offerTokenCategory)()))
            model.setValue(str(giftCount))
            models.append(model)

        return models

    @classmethod
    def _getToolTip(cls, bonus):
        if cls._selectableRewardManager.getGiftCount(bonus) > 0:
            return [ createTooltipData(isSpecial=True, specialAlias=COMP7_TOOLTIPS.COMP7_SELECTABLE_REWARD, specialArgs=(offerToken,)) for offerToken in bonus.getValue().iterkeys() ]
        return []


class Comp7YearlyMetaOfferPacker(Comp7OfferBonusUIPacker):

    @classmethod
    def _getGiftCount(cls, bonus):
        return sum((v.get('count', 0) for t, v in bonus.getValue().iteritems() if isComp7OfferYearlyRewardToken(t)))


def packQuestBonuses(bonuses, bonusPacker, order=None):
    packedBonuses = []
    packedToolTips = []
    bonuses = mergeBonuses(bonuses)
    bonuses = splitBonuses(bonuses)
    bonuses = splitDossierBonuses(bonuses)
    bonuses = mergeOffers(bonuses)
    if order is not None:
        bonuses.sort(key=_getSortKey(order))
    for bonus in bonuses:
        if bonus.isShowInGUI():
            packedBonuses.extend(bonusPacker.pack(bonus))
            packedToolTips.extend(bonusPacker.getToolTip(bonus))

    return (packedBonuses, packedToolTips)


def mergeOffers(bonuses):
    result = []
    offers = []
    for bonus in bonuses:
        if bonus.getName() == SELECTABLE_BONUS_NAME:
            offers.append(bonus)
        result.append(bonus)

    if offers:
        offerBonus = offers.pop()
        for offer in offers:
            offerBonus.getValue().update(offer.getValue())

        result.append(offerBonus)
    return result


def packRanksRewardsQuestBonuses(quest, periodicQuest=None):
    bonuses = quest.getBonuses()
    if periodicQuest is not None:
        periodicBonuses = periodicQuest.getBonuses()
        for b in periodicBonuses:
            b.updateContext({'isPeriodic': True})

        bonuses.extend(periodicBonuses)
    return packQuestBonuses(bonuses, bonusPacker=getComp7BonusPacker(), order=_RANK_REWARDS_BONUSES_ORDER)


def packTokensRewardsQuestBonuses(quest):
    bonuses = quest.getBonuses()
    return packQuestBonuses(bonuses, bonusPacker=getComp7BonusPacker(), order=_TOKENS_REWARDS_BONUSES_ORDER)


def packQualificationRewardsQuestBonuses(quests):
    bonuses = []
    quests.sort(key=lambda q: q.getID())
    for quest in quests:
        bonuses.extend(quest.getBonuses())

    return packQuestBonuses(bonuses, bonusPacker=getComp7BonusPacker(), order=_QUALIFICATION_REWARDS_BONUSES_ORDER)


def packYearlyRewardsBonuses(bonuses):
    bonusData = []
    for key, value in bonuses.iteritems():
        bonusData.extend(getNonQuestBonuses(key, value, bonusesDict=_getComp7YearlyBonuses(specificCustomization=Comp7YearlyCustomizationsBonus2D)))

    return packQuestBonuses(bonusData, bonusPacker=getComp7YearlyBonusPacker(), order=_YEARLY_REWARDS_BONUSES_ORDER)


def packYearlyRewardVehicleBonuses(bonuses):
    bonusData = []
    vehicleBonus = first(getNonQuestBonuses('vehicles', bonuses.get('vehicles')))
    bonusData.append(getVehicleCrewReward(vehicleBonus))
    customizations = bonuses.get('customizations') or []
    customizations.sort(key=lambda c: c.get('id'), reverse=True)
    bonusData.extend(getNonQuestBonuses('customizations', customizations, bonusesDict=_getComp7YearlyBonuses(specificCustomization=Comp7YearlyCustomizationsBonus3D)))
    return packQuestBonuses(bonusData, bonusPacker=getComp7YearlyBonusPacker(), order=_YEARLY_REWARDS_BONUSES_ORDER)


def packYearlyRewardMetaView(bonuses):
    bonusData = []
    for key, value in bonuses.iteritems():
        bonusData.extend(getNonQuestBonuses(key, value, bonusesDict=_getComp7YearlyBonuses()))

    for bonus in bonusData:
        if bonus.getName() == VehiclesBonus.VEHICLES_BONUS:
            bonusData.append(getVehicleCrewReward(bonus))

    return packQuestBonuses(bonusData, bonusPacker=getComp7YearlyMetaBonusPacker(), order=_YEARLY_REWARD_META_BONUSES_ORDER)


def packSelectedRewardsBonuses(bonuses):
    bonusObjects = []
    for key, value in bonuses.iteritems():
        bonusObjects.extend(getNonQuestBonuses(key, value))

    return packQuestBonuses(bonusObjects, bonusPacker=getComp7BonusPacker())


def _getSortKey(order):

    def getSortKey(bonus):
        bonusType = getBonusType(bonus)
        try:
            return order.index(bonusType)
        except ValueError:
            return len(order)

    return getSortKey


def _getOfferRewardTokensSortKey(order):

    def getSortKey(token):
        reward = token.split(':')[-1]
        try:
            return order.index(reward)
        except ValueError:
            return len(order)

    return getSortKey


class Comp7YearlySlotsBonus(CountableIntegralBonus):

    def isShowInGUI(self):
        return False


class Comp7YearlyCustomizationsBonus(CustomizationsBonus):

    def isShowInGUI(self):
        return bool(CustomizationsBonusHelper.getBonusC11Item(self))


class Comp7YearlyCustomizationsBonus3D(CustomizationsBonus):

    def isShowInGUI(self):
        c11nItem = CustomizationsBonusHelper.getBonusC11Item(self)
        return c11nItem and c11nItem.is3D


class Comp7YearlyCustomizationsBonus2D(CustomizationsBonus):

    def isShowInGUI(self):
        c11nItem = CustomizationsBonusHelper.getBonusC11Item(self)
        return c11nItem and not c11nItem.is3D
