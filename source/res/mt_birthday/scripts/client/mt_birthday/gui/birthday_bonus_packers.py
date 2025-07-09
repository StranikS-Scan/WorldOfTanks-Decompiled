# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: mt_birthday/scripts/client/mt_birthday/gui/birthday_bonus_packers.py
import logging
import typing
from gui.Scaleform.genConsts.TOOLTIPS_CONSTANTS import TOOLTIPS_CONSTANTS
from gui.impl.backport import createTooltipData
from gui.impl.gen import R
from gui.impl.gen.view_models.common.missions.bonuses.bonus_model import BonusModel
from gui.impl.gen.view_models.common.missions.bonuses.token_bonus_model import TokenBonusModel
from gui.server_events.bonuses import EntitlementBonus
from gui.server_events.recruit_helper import getRecruitInfo
from gui.shared.missions.packers.bonus import BaseBonusUIPacker, TmanTemplateBonusPacker, VehiclesBonusUIPacker
from items.tankmen import RECRUIT_TMAN_TOKEN_PREFIX
from mt_birthday.birthday_constants import BIRTHDAY_2025_GOLDEN_TICKET, BIRTHDAY_2025_STAMP_CODE
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
        result = []
        if packer:
            result.extend(packer(bonus))
        else:
            _logger.warning('Unknown entitlement %s', entitlementID)
        return result

    @classmethod
    def _getContentId(cls, bonus):
        result = []
        getters = cls._getEntitlementContentIdGetters()
        contentGetter = getters.get(bonus.getValue().id)
        if contentGetter:
            result.append(contentGetter())
        return result

    @classmethod
    def _getToolTip(cls, bonus):
        result = []
        getters = cls._getEntitlementTooltipGetters()
        tooltipGetter = getters.get(bonus.getValue().id)
        if tooltipGetter:
            result.append(tooltipGetter())
        return result

    @classmethod
    def _getEntitlementPackers(cls):
        return {BIRTHDAY_2025_GOLDEN_TICKET: cls._packEntitlement,
         BIRTHDAY_2025_STAMP_CODE: cls._packEntitlement}

    @classmethod
    def _getEntitlementContentIdGetters(cls):
        return {BIRTHDAY_2025_GOLDEN_TICKET: R.views.mt_birthday.lobby.tooltips.GoldTicketTooltip,
         BIRTHDAY_2025_STAMP_CODE: R.views.mt_birthday.lobby.tooltips.PostStampTooltip}

    @classmethod
    def _getEntitlementTooltipGetters(cls):
        return {BIRTHDAY_2025_GOLDEN_TICKET: cls.__createGoldenTicketTooltip,
         BIRTHDAY_2025_STAMP_CODE: cls.__createStampTooltip}

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
        return [model]


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
