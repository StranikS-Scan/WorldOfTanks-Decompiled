# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/comp7/comp7_bonus_packer.py
import logging
import typing
from shared_utils import findFirst, first
from dog_tags_common.components_config import componentConfigAdapter
from dog_tags_common.config.common import ComponentViewType
from gui.Scaleform.genConsts.TOOLTIPS_CONSTANTS import TOOLTIPS_CONSTANTS
from gui.impl import backport
from gui.impl.backport import TooltipData, createTooltipData
from gui.impl.gen import R
from gui.impl.gen.view_models.common.bonus_model import BonusModel
from gui.impl.gen.view_models.common.missions.bonuses.token_bonus_model import TokenBonusModel
from gui.impl.gen.view_models.views.lobby.comp7.comp7_bonus_model import Comp7BonusModel, DogTagType
from gui.impl.gen.view_models.views.lobby.comp7.comp7_style_bonus_model import Comp7StyleBonusModel
from gui.impl.lobby.comp7.comp7_bonus_helpers import BonusTypes, getBonusType, splitDossierBonuses
from gui.impl.lobby.comp7.comp7_c11n_helpers import getComp7ProgressionStyleCamouflage
from gui.selectable_reward.constants import SELECTABLE_BONUS_NAME
from gui.server_events.bonuses import getNonQuestBonuses, mergeBonuses, splitBonuses, C11nProgressTokenBonus, COMP7_TOKEN_WEEKLY_REWARD_NAME, getVehicleCrewReward, CountableIntegralBonus, CustomizationsBonus, VehiclesBonus, _BONUSES, TankmenBonus
from gui.shared.gui_items.Tankman import getFullUserName
from gui.shared.gui_items.customization import CustomizationTooltipContext
from gui.shared.missions.packers.bonus import DossierBonusUIPacker, DogTagComponentsUIPacker, BonusUIPacker, BaseBonusUIPacker, BACKPORT_TOOLTIP_CONTENT_ID, SimpleBonusUIPacker, CustomizationBonusUIPacker, VehiclesBonusUIPacker, TokenBonusUIPacker, TankmenBonusUIPacker
from gui.shared.missions.packers.bonus import getDefaultBonusPackersMap
from gui.shared.money import Currency
from helpers import dependency
from items import tankmen
from items.tankmen import getNationConfig
from skeletons.gui.customization import ICustomizationService
from skeletons.gui.game_control import IComp7Controller
from skeletons.gui.offers import IOffersDataProvider
if typing.TYPE_CHECKING:
    from gui.server_events.bonuses import SimpleBonus
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
 BonusTypes.STYLE_PROGRESS,
 BonusTypes.OFFER,
 BonusTypes.CRYSTAL,
 BonusTypes.STYLE)
_YEARLY_REWARD_META_BONUSES_ORDER = (BonusTypes.RENT_VEHICLE,
 BonusTypes.STYLE_3D_PROGRESS,
 BonusTypes.TOKEN,
 BonusTypes.BADGE_SUFFIX,
 BonusTypes.BADGE,
 BonusTypes.CREW,
 BonusTypes.ACHIEVEMENT,
 BonusTypes.OFFER,
 BonusTypes.CRYSTAL,
 BonusTypes.STYLE)

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
     'customizations': Comp7YearlyCustomizationBonusUIPacker(),
     'modernizedDevice': Comp7YearlyModernizedDeviceBonusUIPacker(),
     'tankmen': Comp7YearlyCrewBonusUIPacker(),
     'battleToken': Comp7YearlyTokensUIPacker()})
    return BonusUIPacker(mapping)


def _getComp7YearlyBonuses():
    bonuses = _BONUSES.copy()
    bonuses.update({'slots': Comp7YearlySlotsBonus,
     'customizations': Comp7YearlyCustomizationsBonus})
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
        return backport.text(R.strings.comp7.rewards.bonus.style_progress(), name=camo.userName)


class Comp7YearlyStylePacker(Comp7StyleProgressBonusUIPacker):

    @classmethod
    def _pack(cls, bonus):
        return [ cls._packSingleBonus(bonus, level) for level in range(bonus.getProgressLevel(), 0, -1) ]

    @classmethod
    def _getToolTip(cls, bonus):
        return [ cls._packTooltip(bonus, level) for level in range(bonus.getProgressLevel(), 0, -1) ]


class Comp7YearlyCustomizationBonusUIPacker(CustomizationBonusUIPacker):
    _ICON_NAME = 'style'

    @classmethod
    def _packSingleBonus(cls, bonus, item, label):
        model = super(Comp7YearlyCustomizationBonusUIPacker, cls)._packSingleBonus(bonus, item, label)
        item = bonus.getC11nItem(item)
        styleID = item.id
        model.setStyleID(styleID)
        model.setIcon(cls._ICON_NAME)
        model.setLabel(item.userName)
        return model

    @classmethod
    def _getBonusModel(cls):
        return Comp7StyleBonusModel()


class Comp7YearlyModernizedDeviceBonusUIPacker(TokenBonusUIPacker):
    BONUS_NAME = 'modernized_devices_t{}_gift'

    @classmethod
    def _pack(cls, bonus):
        model = Comp7BonusModel()
        name = cls.BONUS_NAME.format(bonus.getTierLevel())
        model.setName(name)
        return [model]

    @classmethod
    def _getToolTip(cls, bonus):
        return [createTooltipData(bonus.getTooltip())]


class Comp7CustomizationBonusUIPacker(CustomizationBonusUIPacker):
    _ICON_NAME = 'progressionStyle'

    @classmethod
    def _packSingleBonus(cls, bonus, item, label):
        model = super(Comp7CustomizationBonusUIPacker, cls)._packSingleBonus(bonus, item, label)
        item = bonus.getC11nItem(item)
        styleID = item.id
        model.setStyleID(styleID)
        model.setIcon(cls._ICON_NAME)
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
        model.setLabel(backport.text(R.strings.comp7.yearlyRewards.rewards.crew()))
        model.setTooltipContentId(str(R.views.lobby.comp7.tooltips.CrewMembersTooltip()))
        return [model]

    @classmethod
    def _getToolTip(cls, bonus):
        return [createTooltipData()]

    @classmethod
    def _getBonusModel(cls):
        return Comp7BonusModel()


class Comp7YearlyTokensUIPacker(TokenBonusUIPacker):
    _COMP7_STYLE_TOKEN = 'comp7_4_style_token'
    _BONUS_NAME = 'styleProgressToken'
    _VEHICLE = 'A174_T57_58_Rush_Ep1'

    @classmethod
    def _getTokenBonusType(cls, tokenID, complexToken):
        return cls._COMP7_STYLE_TOKEN if tokenID.startswith(cls._COMP7_STYLE_TOKEN) else super(Comp7YearlyTokensUIPacker, cls)._getTokenBonusType(tokenID, complexToken)

    @classmethod
    def _getTokenBonusPackers(cls):
        packers = super(Comp7YearlyTokensUIPacker, cls)._getTokenBonusPackers()
        packers.update({cls._COMP7_STYLE_TOKEN: cls.__packStyleToken})
        return packers

    @classmethod
    def _getTooltipsPackers(cls):
        packers = super(Comp7YearlyTokensUIPacker, cls)._getTooltipsPackers()
        packers.update({cls._COMP7_STYLE_TOKEN: cls.__packStyleTooltip})
        return packers

    @classmethod
    def _packToken(cls, bonusPacker, bonus, *args):
        model = Comp7StyleBonusModel()
        return bonusPacker(model, bonus, *args)

    @classmethod
    def __packStyleToken(cls, model, _, __, token):
        styleId = cls.__getStyleId(token)
        model.setName(cls._BONUS_NAME)
        model.setStyleID(styleId)
        model.setLabel(backport.text(R.strings.comp7.style3dTooltip.num(styleId)()))
        tooltipId = R.views.lobby.comp7.tooltips.Style3dTooltip()
        model.setTooltipContentId(str(tooltipId))
        return model

    @classmethod
    def __packStyleTooltip(cls, _, token):
        return TooltipData(tooltip=None, isSpecial=True, specialAlias=None, specialArgs=[cls.__getStyleId(token), backport.text(R.strings.usa_vehicles.dyn(cls._VEHICLE)())], isWulfTooltip=False)

    @classmethod
    def __getStyleId(cls, token):
        _, styleId = token.id.split(':')
        return int(styleId)


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
    _comp7Controller = dependency.descriptor(IComp7Controller)
    _offersDataProvider = dependency.descriptor(IOffersDataProvider)

    @classmethod
    def _pack(cls, bonus):
        models = []
        giftCount = cls._getGiftCount(bonus)
        if giftCount > 0:
            model = TokenBonusModel()
            model.setName('deluxe_gift')
            model.setLabel(backport.text(R.strings.comp7.rewards.bonus.deluxe_gift()))
            model.setValue(str(giftCount))
            models.append(model)
        return models

    @classmethod
    def _getToolTip(cls, bonus):
        return [createTooltipData(isSpecial=True, specialAlias=TOOLTIPS_CONSTANTS.COMP7_SELECTABLE_REWARD)] if cls._getGiftCount(bonus) > 0 else []

    @classmethod
    def _getGiftCount(cls, bonus):
        tokens = {t:v.get('count', 0) for t, v in bonus.getValue().iteritems() if cls._comp7Controller.isComp7OfferToken(t)}
        offers = {cls._offersDataProvider.getOfferByToken(token):count for token, count in tokens.iteritems()}
        return sum([ cls.__getOfferGiftCount(offer, count) for offer, count in offers.iteritems() ])

    @classmethod
    def __getOfferGiftCount(cls, offer, count):
        return offer.giftTokenCount * count if offer is not None else count


class Comp7YearlyMetaOfferPacker(Comp7OfferBonusUIPacker):

    @classmethod
    def _getGiftCount(cls, bonus):
        return sum([ v.get('count', 0) for t, v in bonus.getValue().iteritems() if cls._comp7Controller.isComp7OfferToken(t) ])


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
        bonusData.extend(getNonQuestBonuses(key, value, bonusesDict=_getComp7YearlyBonuses()))

    return packQuestBonuses(bonusData, bonusPacker=getComp7YearlyBonusPacker(), order=_YEARLY_REWARDS_BONUSES_ORDER)


def packYearlyRewardCrew(bonus):
    bonusData = getNonQuestBonuses('vehicles', bonus)
    crewReward = getVehicleCrewReward(first(bonusData))
    return packQuestBonuses([crewReward], bonusPacker=getComp7YearlyBonusPacker(), order=_YEARLY_REWARDS_BONUSES_ORDER)


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


class Comp7YearlySlotsBonus(CountableIntegralBonus):

    def isShowInGUI(self):
        return False


class Comp7YearlyCustomizationsBonus(CustomizationsBonus):

    def isShowInGUI(self):
        item = self.getCustomizations()[0]
        return False if not item else not self.getC11nItem(item).is3D
