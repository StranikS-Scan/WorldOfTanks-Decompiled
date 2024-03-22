# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/comp7/comp7_bonus_packer.py
import logging
import typing
from shared_utils import findFirst
from constants import OFFER_TOKEN_PREFIX
from dog_tags_common.components_config import componentConfigAdapter
from dog_tags_common.config.common import ComponentViewType
from gui.Scaleform.genConsts.TOOLTIPS_CONSTANTS import TOOLTIPS_CONSTANTS
from gui.impl import backport
from gui.impl.backport import TooltipData, createTooltipData
from gui.impl.gen import R
from gui.impl.gen.view_models.views.lobby.comp7.comp7_bonus_model import Comp7BonusModel, DogTagType
from gui.impl.gen.view_models.views.lobby.comp7.comp7_style_bonus_model import Comp7StyleBonusModel
from gui.impl.lobby.comp7.comp7_bonus_helpers import BonusTypes, getBonusType, splitDossierBonuses
from gui.impl.lobby.comp7.comp7_c11n_helpers import getComp7ProgressionStyleCamouflage
from gui.server_events.bonuses import getNonQuestBonuses, mergeBonuses, splitBonuses, C11nProgressTokenBonus, COMP7_TOKEN_WEEKLY_REWARD_NAME, getVehicleCrewReward, VehiclesBonus
from gui.shared.gui_items.customization import CustomizationTooltipContext
from gui.shared.missions.packers.bonus import DossierBonusUIPacker, DogTagComponentsUIPacker, BonusUIPacker, BaseBonusUIPacker, BACKPORT_TOOLTIP_CONTENT_ID, SimpleBonusUIPacker, CustomizationBonusUIPacker, VehiclesBonusUIPacker, TokenBonusUIPacker
from gui.shared.missions.packers.bonus import getDefaultBonusPackersMap
from gui.shared.money import Currency
from helpers import dependency
from items import tankmen
from items.tankmen import getNationConfig
from skeletons.gui.customization import ICustomizationService
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
_YEARLY_REWARDS_BONUSES_ORDER = (BonusTypes.STYLE_PROGRESS,
 BonusTypes.RENT_VEHICLE,
 BonusTypes.BADGE_SUFFIX,
 BonusTypes.BADGE,
 BonusTypes.STYLE,
 BonusTypes.ACHIEVEMENT)

def getComp7BonusPacker():
    mapping = getDefaultBonusPackersMap()
    mapping.update({'dossier': Comp7DossierBonusUIPacker(),
     'dogTagComponents': Comp7DogTagUIPacker(),
     'customizations': Comp7CustomizationBonusUIPacker(),
     'vehicles': Comp7VehicleBonusUIPacker(),
     'tankmen': Comp7TankmenBonusUIPacker(),
     'battleToken': Comp7TokenUIPacker(),
     Currency.CRYSTAL: Comp7CrystalBonusPacker(),
     C11nProgressTokenBonus.BONUS_NAME: Comp7StyleProgressBonusUIPacker(),
     COMP7_TOKEN_WEEKLY_REWARD_NAME: Comp7TokenWeeklyRewardUIPacker()})
    return BonusUIPacker(mapping)


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
    def _getBonusModel(cls):
        return Comp7StyleBonusModel()

    @classmethod
    def _pack(cls, bonus):
        return [cls._packSingleBonus(bonus)]

    @classmethod
    def _packSingleBonus(cls, bonus):
        model = cls._getBonusModel()
        cls._packCommon(bonus, model)
        styleID = bonus.getStyleID()
        branchID = bonus.getBranchID()
        progressLevel = bonus.getProgressLevel()
        camo = getComp7ProgressionStyleCamouflage(styleID, branchID, progressLevel)
        if camo is not None:
            icon = cls.__getIcon(styleID, progressLevel)
            label = cls.__getLabel(camo)
        else:
            _logger.error('Missing camouflage for Comp7StyleProgressBonus: styleID=%s; level=%s', styleID, progressLevel)
            icon = ''
            label = ''
        model.setIcon(icon)
        model.setLabel(label)
        model.setStyleID(styleID)
        model.setBranchID(branchID)
        model.setProgressLevel(progressLevel)
        return model

    @classmethod
    def _getToolTip(cls, bonus):
        styleID = bonus.getStyleID()
        branchID = bonus.getBranchID()
        progressLevel = bonus.getProgressLevel()
        camo = getComp7ProgressionStyleCamouflage(styleID, branchID, progressLevel)
        tooltipData = TooltipData(tooltip=None, isSpecial=True, specialAlias=TOOLTIPS_CONSTANTS.TECH_CUSTOMIZATION_ITEM_AWARD, specialArgs=CustomizationTooltipContext(itemCD=camo.intCD, skipQuestValidation=True))
        return [tooltipData]

    @classmethod
    def _getContentId(cls, bonus):
        return [BACKPORT_TOOLTIP_CONTENT_ID]

    @staticmethod
    def __getIcon(styleID, progressLevel):
        return 'style_progress_{styleID}_{progressLevel}'.format(styleID=styleID, progressLevel=progressLevel)

    @staticmethod
    def __getLabel(camo):
        return backport.text(R.strings.comp7.rewards.bonus.style_progress(), name=camo.userName)


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
        tankmanData = tankmen.TankmanDescr(compactDescr=bonus)
        model = Comp7BonusModel()
        model.setName('tankman')
        model.setGroupName(cls.__getTankmanGroupName(tankmanData))
        return model

    @classmethod
    def _getToolTip(cls, bonus):
        tooltipData = []
        for tankmanData in bonus.getValue():
            tankman = tankmen.TankmanDescr(compactDescr=tankmanData)
            tooltipData.append(createTooltipData(isSpecial=True, specialAlias=TOOLTIPS_CONSTANTS.SPECIAL_TANKMAN, specialArgs=(tankman, cls.__getTankmanGroupName(tankman))))

        return tooltipData

    @classmethod
    def __getTankmanGroupName(cls, tankmanData):
        premiumGroups = getNationConfig(tankmanData.nationID).premiumGroups
        tankmanGroup = findFirst(lambda group: group.groupID == tankmanData.gid, premiumGroups.itervalues())
        return tankmanGroup.name


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


class Comp7TokenUIPacker(TokenBonusUIPacker):
    _OFFER_TOKEN = 'offer'

    @classmethod
    def _getTokenBonusType(cls, tokenID, complexToken):
        return cls._OFFER_TOKEN if tokenID.startswith(OFFER_TOKEN_PREFIX) else super(Comp7TokenUIPacker, cls)._getTokenBonusType(tokenID, complexToken)

    @classmethod
    def _getTokenBonusPackers(cls):
        packers = super(Comp7TokenUIPacker, cls)._getTokenBonusPackers()
        packers[cls._OFFER_TOKEN] = cls.__packOffer
        return packers

    @classmethod
    def _getTooltipsPackers(cls):
        packers = super(Comp7TokenUIPacker, cls)._getTooltipsPackers()
        packers[cls._OFFER_TOKEN] = cls.__getOfferTooltip
        return packers

    @classmethod
    def __packOffer(cls, model, *_):
        model.setIconSmall(backport.image(R.images.gui.maps.icons.quests.bonuses.small.deluxe_gift()))
        model.setIconBig(backport.image(R.images.gui.maps.icons.quests.bonuses.big.deluxe_gift()))
        return model

    @classmethod
    def __getOfferTooltip(cls, *_):
        return createTooltipData(isSpecial=True, specialAlias=TOOLTIPS_CONSTANTS.COMP7_SELECTABLE_REWARD)


def packQuestBonuses(bonuses, bonusPacker, order=None):
    packedBonuses = []
    packedToolTips = []
    bonuses = mergeBonuses(bonuses)
    bonuses = splitBonuses(bonuses)
    bonuses = splitDossierBonuses(bonuses)
    if order is not None:
        bonuses.sort(key=_getSortKey(order))
    for bonus in bonuses:
        if bonus.isShowInGUI():
            packedBonuses.extend(bonusPacker.pack(bonus))
            packedToolTips.extend(bonusPacker.getToolTip(bonus))

    return (packedBonuses, packedToolTips)


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
    bonusObjects = []
    for key, value in bonuses.iteritems():
        bonusObjects.extend(getNonQuestBonuses(key, value))

    for bonus in bonusObjects:
        if bonus.getName() == VehiclesBonus.VEHICLES_BONUS:
            bonusObjects.append(getVehicleCrewReward(bonus))

    result = packQuestBonuses(bonusObjects, bonusPacker=getComp7BonusPacker(), order=_YEARLY_REWARDS_BONUSES_ORDER)
    return result


def _getSortKey(order):

    def getSortKey(bonus):
        bonusType = getBonusType(bonus)
        try:
            return order.index(bonusType)
        except ValueError:
            return len(order)

    return getSortKey
