# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/wot_anniversary/bonus_packers.py
import logging
import typing
from gui.Scaleform.genConsts.TOOLTIPS_CONSTANTS import TOOLTIPS_CONSTANTS
from gui.impl import backport
from gui.impl.backport import TooltipData
from gui.impl.gen import R
from gui.impl.gen.view_models.constants.item_highlight_types import ItemHighlightTypes
from gui.impl.gen.view_models.views.lobby.wot_anniversary.vehicle_bonus_model import VehicleBonusModel
from gui.impl.gen.view_models.views.lobby.wot_anniversary.wot_anniversary_bonus_model import WotAnniversaryBonusModel
from gui.server_events.awards_formatters import BATTLE_BONUS_X5_TOKEN, AWARDS_SIZES
from gui.server_events.bonuses import getNonQuestBonuses, splitBonuses, C11nProgressTokenBonus, getMergedCompensatedBonuses
from gui.server_events.recruit_helper import getRecruitInfo
from gui.shared.gui_items import GUI_ITEM_TYPE, GUI_ITEM_TYPE_NAMES
from gui.shared.gui_items.Vehicle import getIconResourceName, getNationLessName
from gui.shared.gui_items.customization import CustomizationTooltipContext
from gui.shared.missions.packers.bonus import BACKPORT_TOOLTIP_CONTENT_ID, getDefaultBonusPackersMap, BonusUIPacker, BaseBonusUIPacker, CustomizationBonusUIPacker, TokenBonusUIPacker, VehiclesBonusUIPacker
from helpers import dependency
from helpers.dependency import replace_none_kwargs
from items.tankmen import RECRUIT_TMAN_TOKEN_PREFIX
from skeletons.gui.customization import ICustomizationService
from skeletons.gui.wot_anniversary import IWotAnniversaryController
if typing.TYPE_CHECKING:
    from typing import List, Dict
    from gui.impl.gen.view_models.common.missions.bonuses.token_bonus_model import TokenBonusModel
    from gui.server_events.bonuses import SimpleBonus, TmanTemplateTokensBonus, TokensBonus
    from gui.shared.gui_items.customization.c11n_items import Style
_logger = logging.getLogger(__name__)

class WotAnniversaryCustomizationBonusUIPacker(CustomizationBonusUIPacker):

    @classmethod
    def _packSingleBonus(cls, bonus, item, label):
        model = super(WotAnniversaryCustomizationBonusUIPacker, cls)._packSingleBonus(bonus, item, label)
        c11nItem = bonus.getC11nItem(item)
        model.setIcon(c11nItem.itemTypeName)
        model.setLabel(c11nItem.userName)
        if c11nItem.itemTypeID == GUI_ITEM_TYPE.ATTACHMENT:
            model.setOverlayType(c11nItem.rarity)
        return model

    @classmethod
    def _getBonusModel(cls):
        return WotAnniversaryBonusModel()


class WotAnniversaryRewardCustomizationBonusUIPacker(WotAnniversaryCustomizationBonusUIPacker):

    @classmethod
    def _packSingleBonus(cls, bonus, item, label):
        model = super(WotAnniversaryRewardCustomizationBonusUIPacker, cls)._packSingleBonus(bonus, item, label)
        c11nItem = bonus.getC11nItem(item)
        if c11nItem.itemTypeID == GUI_ITEM_TYPE.ATTACHMENT:
            model.setIcon(c11nItem.name)
            model.setName(GUI_ITEM_TYPE_NAMES[GUI_ITEM_TYPE.ATTACHMENT])
        return model

    @classmethod
    def _getBonusModel(cls):
        return WotAnniversaryBonusModel()


class StyleProgressBonusUIPacker(BaseBonusUIPacker):
    _c11nService = dependency.descriptor(ICustomizationService)

    @classmethod
    def _pack(cls, bonus):
        return [cls._packSingleBonus(bonus)]

    @classmethod
    def _packSingleBonus(cls, bonus):
        styleID = bonus.getStyleID()
        level = bonus.getProgressLevel()
        style = cls._c11nService.getItemByID(GUI_ITEM_TYPE.STYLE, styleID)
        model = WotAnniversaryBonusModel()
        cls._packCommon(bonus, model)
        model.setIcon(style.itemTypeName)
        model.setOverlayType(ItemHighlightTypes.PROGRESSION_STYLE_UPGRADED + str(level))
        model.setLabel(style.userName)
        return model

    @classmethod
    def _getToolTip(cls, bonus):
        styleID = bonus.getStyleID()
        level = bonus.getProgressLevel()
        style = cls._c11nService.getItemByID(GUI_ITEM_TYPE.STYLE, styleID)
        return [TooltipData(tooltip=None, isSpecial=True, specialAlias=TOOLTIPS_CONSTANTS.TECH_CUSTOMIZATION_ITEM_AWARD, specialArgs=CustomizationTooltipContext(itemCD=style.intCD, level=level))]

    @classmethod
    def _getContentId(cls, bonus):
        return [BACKPORT_TOOLTIP_CONTENT_ID]


class RewardsStyleProgressBonusUIPacker(StyleProgressBonusUIPacker):

    @classmethod
    def _packSingleBonus(cls, bonus):
        styleID = bonus.getStyleID()
        level = bonus.getProgressLevel()
        style = cls._c11nService.getItemByID(GUI_ITEM_TYPE.STYLE, styleID)
        model = WotAnniversaryBonusModel()
        cls._packCommon(bonus, model)
        model.setIcon('style_progress_{}_{}'.format(styleID, level))
        model.setLabel(style.userName)
        return model


class TmanTemplateBonusPacker(BaseBonusUIPacker):

    @classmethod
    def _pack(cls, bonus):
        result = []
        for tokenID in bonus.getTokens():
            if tokenID.startswith(RECRUIT_TMAN_TOKEN_PREFIX):
                packed = cls._packTmanTemplateToken(tokenID, bonus)
                if packed is not None:
                    result.append(packed)

        return result

    @classmethod
    def _packTmanTemplateToken(cls, tokenID, bonus):
        recruitInfo = getRecruitInfo(tokenID)
        if recruitInfo is None:
            _logger.error('Received wrong tman_template token from server: %s', tokenID)
            return
        else:
            model = WotAnniversaryBonusModel()
            cls._packCommon(bonus, model)
            model.setIcon(recruitInfo.getDynIconName())
            model.setLabel(recruitInfo.getFullUserName())
            return model

    @classmethod
    def _getToolTip(cls, bonus):
        tooltipData = []
        for tokenID in bonus.getTokens():
            if tokenID.startswith(RECRUIT_TMAN_TOKEN_PREFIX):
                tooltipData.append(TooltipData(tooltip=None, isSpecial=True, specialAlias=TOOLTIPS_CONSTANTS.TANKMAN_NOT_RECRUITED, specialArgs=[tokenID]))

        return tooltipData

    @classmethod
    def _getContentId(cls, bonus):
        return [ BACKPORT_TOOLTIP_CONTENT_ID for tokenID in bonus.getTokens() if tokenID.startswith(RECRUIT_TMAN_TOKEN_PREFIX) ]

    @classmethod
    def __getBonusImageName(cls, recruitInfo):
        return 'tank{}man'.format('wo' if recruitInfo.isFemale() else '')


class WotAnniversaryTokenBonusUIPacker(TokenBonusUIPacker):

    @classmethod
    def _getTokenBonusPackers(cls):
        packer = super(WotAnniversaryTokenBonusUIPacker, cls)._getTokenBonusPackers()
        packer[BATTLE_BONUS_X5_TOKEN] = cls.__packBattleBonusX5Token
        return packer

    @classmethod
    def __packBattleBonusX5Token(cls, model, bonus, *args):
        model.setName(BATTLE_BONUS_X5_TOKEN)
        model.setValue(str(bonus.getCount()))
        model.setLabel(backport.text(R.strings.tooltips.quests.bonuses.token.battle_bonus_x5.label()))
        model.setIconBig(backport.image(R.images.gui.maps.icons.quests.bonuses.dyn(AWARDS_SIZES.BIG).dyn(BATTLE_BONUS_X5_TOKEN)()))
        model.setIconSmall(backport.image(R.images.gui.maps.icons.quests.bonuses.dyn(AWARDS_SIZES.SMALL).dyn(BATTLE_BONUS_X5_TOKEN)()))
        return model


class WotAnniversaryVehiclesBonusUIPacker(VehiclesBonusUIPacker):
    _SPECIAL_ALIAS = TOOLTIPS_CONSTANTS.EXTENDED_AWARD_VEHICLE

    @classmethod
    def _getCompensation(cls, vehicle, bonus):
        return []

    @classmethod
    def _packVehicleBonusModel(cls, bonus, vInfo, isRent, vehicle):
        model = VehicleBonusModel()
        model.setName(cls._createUIName(bonus, isRent))
        model.setLabel(vehicle.shortUserName)
        model.setIcon(getIconResourceName(getNationLessName(vehicle.name)))
        model.setVehicleName(getNationLessName(vehicle.name))
        model.setVehicleLevel(vehicle.level)
        model.setVehicleType(vehicle.type)
        model.setNation(vehicle.nationName)
        model.setIsElite(vehicle.isElite)
        return model

    @classmethod
    def _packTooltip(cls, bonus, vehicle, vehInfo):
        tooltipData = super(WotAnniversaryVehiclesBonusUIPacker, cls)._packTooltip(bonus, vehicle, vehInfo)
        tmanRoleLevel = bonus.getTmanRoleLevel(vehInfo)
        tooltipData.specialArgs.extend([tmanRoleLevel > 0, True, False])
        return tooltipData


def getWotAnniversaryBonusPacker():
    mapping = getDefaultBonusPackersMap()
    mapping.update({'customizations': WotAnniversaryCustomizationBonusUIPacker(),
     C11nProgressTokenBonus.BONUS_NAME: StyleProgressBonusUIPacker()})
    return BonusUIPacker(mapping)


def getWotAnniversaryRewardBonusPacker():
    mapping = getDefaultBonusPackersMap()
    mapping.update({'customizations': WotAnniversaryRewardCustomizationBonusUIPacker(),
     C11nProgressTokenBonus.BONUS_NAME: RewardsStyleProgressBonusUIPacker(),
     'tmanToken': TmanTemplateBonusPacker(),
     'tokens': WotAnniversaryTokenBonusUIPacker(),
     'vehicles': WotAnniversaryVehiclesBonusUIPacker()})
    return BonusUIPacker(mapping)


@replace_none_kwargs(wotAnniversaryController=IWotAnniversaryController)
def composeBonuses(rewards, wotAnniversaryController=None):
    bonuses = []
    mergedRewards = getMergedCompensatedBonuses([rewards])
    for key, value in mergedRewards.items():
        bonuses.extend(getNonQuestBonuses(key, value))

    bonuses = splitBonuses(bonuses)
    bonuses = filter(wotAnniversaryController.bonusLayoutManager.getIsVisible, bonuses)
    bonuses.sort(key=wotAnniversaryController.bonusLayoutManager.getPriority, reverse=True)
    return bonuses
