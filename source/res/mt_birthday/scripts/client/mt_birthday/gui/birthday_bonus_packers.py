# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: mt_birthday/scripts/client/mt_birthday/gui/birthday_bonus_packers.py
import logging
import typing
from gui.Scaleform.genConsts.TOOLTIPS_CONSTANTS import TOOLTIPS_CONSTANTS
from gui.impl import backport
from gui.impl.backport import createTooltipData
from gui.impl.gen import R
from gui.impl.gen.view_models.common.missions.bonuses.bonus_model import BonusModel
from gui.impl.gen.view_models.common.missions.bonuses.icon_bonus_model import IconBonusModel
from gui.impl.gen.view_models.common.missions.bonuses.token_bonus_model import TokenBonusModel
from gui.server_events.bonuses import EntitlementBonus, CurrenciesBonus, CustomizationsBonus
from gui.server_events.recruit_helper import getRecruitInfo
from gui.shared.gui_items import GUI_ITEM_TYPE
from gui.shared.missions.packers.bonus import BaseBonusUIPacker, TmanTemplateBonusPacker, VehiclesBonusUIPacker, getLocalizedBonusName, SimpleBonusUIPacker, BACKPORT_TOOLTIP_CONTENT_ID, CustomizationBonusUIPacker
from items.tankmen import RECRUIT_TMAN_TOKEN_PREFIX
from mt_birthday.birthday_constants import BIRTHDAY_GOLDEN_TICKET, BIRTHDAY_STAMP_CODE, BIRTHDAY_GOLDEN_TICKET_CURRENCY
from mt_birthday.gui.impl.gen.view_models.views.lobby.common.vehicle_model import VehicleModel, VehicleType
from gui.shared.gui_items.Vehicle import getNationLessName
if typing.TYPE_CHECKING:
    from gui.server_events.bonuses import TmanTemplateTokensBonus
    from gui.shared.gui_items.Vehicle import Vehicle
_logger = logging.getLogger(__name__)

class BirthdayEntitlementBonusUIPacker(BaseBonusUIPacker):

    @classmethod
    def _pack(cls, bonus):
        entitlementID = bonus.getValue().id
        packer = cls._getEntitlementPackers().get(entitlementID)
        return [packer(bonus) if packer else cls._packEntitlement(bonus)]

    @classmethod
    def _getContentId(cls, bonus):
        getters = cls._getEntitlementContentIdGetters()
        contentGetter = getters.get(bonus.getValue().id)
        return [contentGetter() if contentGetter else BACKPORT_TOOLTIP_CONTENT_ID]

    @classmethod
    def _getToolTip(cls, bonus):
        getters = cls._getEntitlementTooltipGetters()
        tooltipGetter = getters.get(bonus.getValue().id)
        return [tooltipGetter() if tooltipGetter else createTooltipData(bonus.getTooltip())]

    @classmethod
    def _getEntitlementPackers(cls):
        return {BIRTHDAY_GOLDEN_TICKET: cls._packEntitlement,
         BIRTHDAY_STAMP_CODE: cls._packEntitlement}

    @classmethod
    def _getEntitlementContentIdGetters(cls):
        return {BIRTHDAY_GOLDEN_TICKET: R.views.mt_birthday.lobby.tooltips.GoldTicketTooltip,
         BIRTHDAY_STAMP_CODE: R.views.mt_birthday.lobby.tooltips.PostStampTooltip}

    @classmethod
    def _getEntitlementTooltipGetters(cls):
        return {BIRTHDAY_GOLDEN_TICKET: cls.__createGoldenTicketTooltip,
         BIRTHDAY_STAMP_CODE: cls.__createStampTooltip}

    @classmethod
    def __createStampTooltip(cls):
        return createTooltipData(isSpecial=True, specialAlias=TOOLTIPS_CONSTANTS.BIRTHDAY_GIFT_SYSTEM_POSTMARK)

    @classmethod
    def __createGoldenTicketTooltip(cls):
        return createTooltipData(isSpecial=True, specialAlias=TOOLTIPS_CONSTANTS.BIRTHDAY_GOLDEN_TICKET)

    @classmethod
    def _packEntitlement(cls, bonus):
        model = BonusModel()
        entitlementID = bonus.getValue().id
        model.setLabel(EntitlementBonus.getUserName(entitlementID))
        model.setName(entitlementID)
        model.setValue(str(bonus.getValue().amount))
        return model


class BirthdayCurrencyBonusUIPacker(SimpleBonusUIPacker):

    @classmethod
    def _pack(cls, bonus):
        currencyCode = bonus.getCode()
        packer = cls._getCurrencyPackers().get(currencyCode)
        return [packer(bonus) if packer else cls._packCurrency(bonus)]

    @classmethod
    def _getContentId(cls, bonus):
        getters = cls._getCurrencyContentIdGetters()
        contentGetter = getters.get(bonus.getCode())
        return [contentGetter() if contentGetter else BACKPORT_TOOLTIP_CONTENT_ID]

    @classmethod
    def _getToolTip(cls, bonus):
        getters = cls._getCurrencyTooltipGetters()
        tooltipGetter = getters.get(bonus.getCode())
        return [tooltipGetter() if tooltipGetter else createTooltipData(bonus.getTooltip())]

    @classmethod
    def _getCurrencyPackers(cls):
        return {BIRTHDAY_GOLDEN_TICKET_CURRENCY: cls._packCurrency}

    @classmethod
    def _getCurrencyContentIdGetters(cls):
        return {BIRTHDAY_GOLDEN_TICKET_CURRENCY: R.views.mt_birthday.lobby.tooltips.GoldTicketTooltip}

    @classmethod
    def _getCurrencyTooltipGetters(cls):
        return {BIRTHDAY_GOLDEN_TICKET_CURRENCY: cls.__createGoldenTicketTooltip}

    @classmethod
    def __createGoldenTicketTooltip(cls):
        return createTooltipData(isSpecial=True, specialAlias=TOOLTIPS_CONSTANTS.BIRTHDAY_GOLDEN_TICKET)

    @classmethod
    def _packCommon(cls, bonus, model):
        model.setName(bonus.getCode())
        model.setIsCompensation(bonus.isCompensation())
        return model

    @classmethod
    def _packCurrency(cls, bonus):
        label = getLocalizedBonusName(bonus.getCode())
        model = cls._getBonusModel()
        cls._packCommon(bonus, model)
        model.setValue(str(bonus.getValue()))
        model.setLabel(label if label else '')
        return model


class BirthdayTmanBonusUIPacker(TmanTemplateBonusPacker):

    @classmethod
    def _pack(cls, bonus):
        result = []
        for tokenID in bonus.getTokens().iterkeys():
            if tokenID.startswith(RECRUIT_TMAN_TOKEN_PREFIX):
                packed = cls._packTmanTemplateToken(tokenID, bonus)
                if packed is not None:
                    result.append(packed)

        return result

    @classmethod
    def _packTmanTemplateToken(cls, tokenID, bonus):
        recruitInfo = getRecruitInfo(tokenID)
        if recruitInfo is None:
            return
        else:
            model = TokenBonusModel()
            cls._packCommon(bonus, model)
            tokenRecord = bonus.getTokens()[tokenID]
            if tokenRecord.count > 1:
                model.setValue(str(tokenRecord.count))
            model.setLabel(recruitInfo.getFullUserName())
            model.setIcon(recruitInfo.getSourceID())
            model.setUserName(recruitInfo.getFullUserName())
            return model


class BirthdayVehiclesBonusUIPacker(VehiclesBonusUIPacker):

    @classmethod
    def _packVehicleBonusModel(cls, bonus, vehInfo, isRent, vehicle):
        model = VehicleModel()
        model.setName(bonus.getName())
        model.setIsElite(vehicle.isElite)
        model.setLevel(vehicle.level)
        model.setVehicleName(getNationLessName(vehicle.name))
        model.setType(VehicleType(vehicle.type))
        model.setNationTag(vehicle.nationName)
        model.setLabel(cls._getLabel(vehicle))
        model.setShortVehicleLabel(vehicle.shortUserName)
        return model


class BirthdayCustomizationBonusUIPacker(CustomizationBonusUIPacker):

    @classmethod
    def _pack(cls, bonus):
        result = []
        for item in bonus.getCustomizations():
            if item is None:
                continue
            label = cls._getLabel(bonus.getC11nItem(item))
            result.append(cls._packSingleBonus(bonus, item, label))

        return result

    @classmethod
    def _packSingleBonus(cls, bonus, item, label):
        model = cls._getBonusModel()
        cls._packCommon(bonus, model)
        model.setValue(str(item.get('value', 0)))
        model.setIcon(str(bonus.getC11nItem(item).itemTypeName))
        model.setIcon(cls._getIcon(bonus, bonus.getC11nItem(item)))
        model.setLabel(label)
        return model

    @classmethod
    def _getLabel(cls, c11nItem):
        userName = c11nItem.userName
        elementBonusR = R.strings.vehicle_customization.elementBonus.desc.dyn(c11nItem.itemFullTypeName, R.invalid)
        return backport.text(elementBonusR(), value=userName) if elementBonusR else userName

    @classmethod
    def _getIcon(cls, bonus, c11Item):
        itemTypeName = str(c11Item.itemTypeName)
        iconName = '{}_{}'.format(itemTypeName + '_3d' if c11Item.itemTypeID == GUI_ITEM_TYPE.STYLE and c11Item.is3D else itemTypeName, c11Item.innationID)
        if R.images.gui.maps.icons.quests.bonuses.s600x450.dyn(iconName).exists():
            return iconName
        return itemTypeName + '_3d' if c11Item.itemTypeID == GUI_ITEM_TYPE.STYLE and c11Item.is3D else itemTypeName
