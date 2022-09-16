# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/comp7/comp7_bonus_helpers.py
import enum
import typing
from constants import PREMIUM_ENTITLEMENTS
from dog_tags_common.components_config import componentConfigAdapter
from dog_tags_common.config.common import ComponentViewType
from gui.server_events.bonuses import C11nProgressTokenBonus
from gui.shared.gui_items import GUI_ITEM_TYPE
from gui.shared.money import Currency
from shared_utils import first
if typing.TYPE_CHECKING:
    from gui.server_events.bonuses import SimpleBonus, ItemsBonus, CustomizationsBonus, GoodiesBonus, CrewBooksBonus, PlusPremiumDaysBonus, CreditsBonus, CrystalBonus, DogTagComponentBonus, VehiclesBonus, DossierBonus

class BonusTypes(enum.IntEnum):
    NONE = 0
    ACHIEVEMENT = 1
    DELUXE_DEVICE = 2
    CREWBOOK = 3
    PREMIUM = 4
    CRYSTAL = 5
    CREDITS = 6
    OPTIONAL_DEVICE = 7
    BOOSTER = 8
    EQUIPMENT = 9
    BATTLE_BOOSTER = 10
    RENT_VEHICLE = 11
    STYLE = 12
    STYLE_PROGRESS = 13
    BADGE = 14
    BADGE_SUFFIX = 15
    DOGTAG_ENGRAVING = 16
    DOGTAG_BACKGROUND = 17


def getBonusType(bonus):
    return _BONUS_HELPERS_MAP.get(bonus.getName(), _BaseBonusHelper).getBonusType(bonus)


class _BaseBonusHelper(object):

    @staticmethod
    def getBonusType(bonus):
        return BonusTypes.NONE


class _ItemsBonusHelper(_BaseBonusHelper):

    @staticmethod
    def getBonusType(bonus):
        item = first(bonus.getItems().keys())
        itemTypeID = item.itemTypeID
        if itemTypeID == GUI_ITEM_TYPE.BATTLE_BOOSTER:
            return BonusTypes.BATTLE_BOOSTER
        if item.itemTypeID == GUI_ITEM_TYPE.EQUIPMENT:
            return BonusTypes.EQUIPMENT
        if item.itemTypeID == GUI_ITEM_TYPE.OPTIONALDEVICE:
            if item.isDeluxe:
                return BonusTypes.DELUXE_DEVICE
            return BonusTypes.OPTIONAL_DEVICE
        return BonusTypes.NONE


class _CustomizationsBonusHelper(_BaseBonusHelper):

    @staticmethod
    def getBonusType(bonus):
        return BonusTypes.STYLE


class _GoodiesBonusHelper(_BaseBonusHelper):

    @staticmethod
    def getBonusType(bonus):
        booster = first(bonus.getBoosters().keys())
        return BonusTypes.BOOSTER if booster is not None else BonusTypes.NONE


class _CrewBooksBonusHelper(_BaseBonusHelper):

    @staticmethod
    def getBonusType(bonus):
        return BonusTypes.CREWBOOK


class _VehiclesBonusHelper(_BaseBonusHelper):

    @staticmethod
    def getBonusType(bonus):
        return BonusTypes.RENT_VEHICLE


class _DogTagBonusHelper(_BaseBonusHelper):

    @staticmethod
    def getBonusType(bonus):
        component = first(bonus.getUnlockedComponents())
        dogTagViewType = componentConfigAdapter.getComponentById(component.componentId).viewType
        if dogTagViewType == ComponentViewType.ENGRAVING:
            return BonusTypes.DOGTAG_ENGRAVING
        return BonusTypes.DOGTAG_BACKGROUND if dogTagViewType == ComponentViewType.BACKGROUND else BonusTypes.NONE


class _DossierBonusHelper(_BaseBonusHelper):

    @staticmethod
    def getBonusType(bonus):
        achievement = first(bonus.getAchievements())
        if achievement is not None:
            return BonusTypes.ACHIEVEMENT
        else:
            badge = first(bonus.getBadges())
            if badge is not None:
                if badge.isSuffixLayout():
                    return BonusTypes.BADGE_SUFFIX
                return BonusTypes.BADGE
            return BonusTypes.NONE


class _PremiumBonusHelper(_BaseBonusHelper):

    @staticmethod
    def getBonusType(bonus):
        return BonusTypes.PREMIUM


class _CreditsBonusHelper(_BaseBonusHelper):

    @staticmethod
    def getBonusType(bonus):
        return BonusTypes.CREDITS


class _CrystalBonusHelper(_BaseBonusHelper):

    @staticmethod
    def getBonusType(bonus):
        return BonusTypes.CRYSTAL


class _StyleProgressBonusHelper(_BaseBonusHelper):

    @staticmethod
    def getBonusType(bonus):
        return BonusTypes.STYLE_PROGRESS


_BONUS_HELPERS_MAP = {'items': _ItemsBonusHelper,
 'customizations': _CustomizationsBonusHelper,
 'goodies': _GoodiesBonusHelper,
 'crewBooks': _CrewBooksBonusHelper,
 'vehicles': _VehiclesBonusHelper,
 'dogTagComponents': _DogTagBonusHelper,
 'dossier': _DossierBonusHelper,
 PREMIUM_ENTITLEMENTS.PLUS: _PremiumBonusHelper,
 Currency.CREDITS: _CreditsBonusHelper,
 Currency.CRYSTAL: _CrystalBonusHelper,
 C11nProgressTokenBonus.BONUS_NAME: _StyleProgressBonusHelper}
