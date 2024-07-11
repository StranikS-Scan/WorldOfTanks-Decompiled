# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: races/scripts/client/races/gui/impl/lobby/races_lobby_view/ui_packers.py
import typing
import logging
from gui_lootboxes.gui.bonuses.bonuses_packers import LootBoxTokensBonusUIPacker
from gui_lootboxes.gui.impl.gen.view_models.views.lobby.gui_lootboxes.vehicle_bonus_model import VehicleBonusModel, VehicleType
from gui.Scaleform.genConsts.TOOLTIPS_CONSTANTS import TOOLTIPS_CONSTANTS
from gui.impl import backport
from gui.impl.backport import TooltipData
from gui.impl.gen import R
from gui.impl.gen.view_models.common.missions.bonuses.token_bonus_model import TokenBonusModel
from gui.impl.gen.view_models.common.missions.bonuses.big_icon_bonus_model import BigIconBonusModel
from gui.shared.gui_items.Vehicle import getNationLessName
from gui.shared.missions.packers.bonus import BonusUIPacker, getDefaultBonusPackersMap, VehiclesBonusUIPacker, BACKPORT_TOOLTIP_CONTENT_ID, SimpleBonusUIPacker
from gui.shared.missions.packers.events import DailyQuestUIDataPacker
from gui.shared.utils.functions import makeTooltip
from gui.server_events.recruit_helper import getRecruitInfo
from items.tankmen import RECRUIT_TMAN_TOKEN_PREFIX
if typing.TYPE_CHECKING:
    from gui.server_events.formatters import TokenComplex
PROGRESSION_TOKEN = 'races:progression_token'
_logger = logging.getLogger(__name__)
if typing.TYPE_CHECKING:
    from typing import Dict, Callable, TypeVar, Optional
    from gui.server_events.formatters import TokenComplex
    from gui.server_events.bonuses import TokensBonus
    TokenBonusType = TypeVar('TokenBonusType', bound=TokensBonus)
    from gui.impl.gen.view_models.common.missions.daily_quest_model import DailyQuestModel

class RacesTokenBonusUIPacker(LootBoxTokensBonusUIPacker):

    @classmethod
    def _getTokenBonusType(cls, tokenID, complexToken):
        return tokenID if tokenID == PROGRESSION_TOKEN else super(RacesTokenBonusUIPacker, cls)._getTokenBonusType(tokenID, complexToken)

    @classmethod
    def _getTooltipsPackers(cls):
        tooltips = super(RacesTokenBonusUIPacker, cls)._getTooltipsPackers()
        tooltips.update({PROGRESSION_TOKEN: cls.__getRacesToolTip})
        return tooltips

    @classmethod
    def _getTokenBonusPackers(cls):
        packers = super(RacesTokenBonusUIPacker, cls)._getTokenBonusPackers()
        packers.update({PROGRESSION_TOKEN: cls.__packRacesToken})
        return packers

    @classmethod
    def __packRacesToken(cls, model, bonus, *args):
        return cls.__packRacesTokenCommon(model, bonus, 'races_point')

    @classmethod
    def __packRacesTokenCommon(cls, model, bonus, name):
        model.setName(name)
        model.setValue(str(bonus.getCount()))
        return model

    @classmethod
    def __getRacesToolTip(cls, *_):
        return makeTooltip(header=backport.text(R.strings.races.tooltip.racesPoints.header()), body=backport.text(R.strings.races.tooltip.racesPoints.description()))


class RacesVehiclesBonusUIPacker(VehiclesBonusUIPacker):

    @classmethod
    def _packVehicleBonusModel(cls, bonus, vehInfo, isRent, vehicle):
        model = VehicleBonusModel()
        model.setName(bonus.getName())
        model.setVehicleName(getNationLessName(vehicle.name))
        model.setType(VehicleType(vehicle.type))
        model.setNationTag(vehicle.nationName)
        model.setLevel(vehicle.level)
        model.setIsCompensation(bonus.isCompensation())
        model.setIsElite(vehicle.isElite)
        model.setIsRent(vehicle.isRented)
        model.setInInventory(vehicle.isInInventory)
        model.setWasSold(vehicle.restoreInfo is not None)
        if isRent:
            model.setRentDays(bonus.getRentDays(vehInfo) or 0)
            model.setRentBattles(bonus.getRentBattles(vehInfo) or 0)
        model.setLabel(cls._getLabel(vehicle))
        model.setShortVehicleLabel(vehicle.shortUserName)
        return model

    @classmethod
    def _packVehicles(cls, bonus, vehicles):
        packedVehicles = []
        for vehicle, vehInfo in vehicles:
            packedVehicles.append(cls._packVehicle(bonus, vehInfo, vehicle))

        return packedVehicles


class TmanTemplateBonusPacker(SimpleBonusUIPacker):
    _WOMAN_ICON = 'tankwoman'
    _MAN_ICON = 'tankman'

    @classmethod
    def _pack(cls, bonus):
        result = []
        for tokenID in bonus.getTokens().iterkeys():
            if tokenID.startswith(RECRUIT_TMAN_TOKEN_PREFIX):
                packed = cls._packTmanTemplateToken(tokenID, bonus)
                if packed is None:
                    _logger.error('Received wrong tman_template token from server: %s', tokenID)
                else:
                    result.append(packed)

        return result

    @classmethod
    def _packTmanTemplateToken(cls, tokenID, bonus):
        recruit = getRecruitInfo(tokenID)
        if recruit is None:
            return
        else:
            model = cls._getBonusModel()
            cls._packCommon(bonus, model)
            model.setIcon(cls._WOMAN_ICON if recruit.isFemale() else cls._MAN_ICON)
            model.setBigIcon(recruit.getGroupName())
            model.setLabel(recruit.getFullUserName())
            return model

    @classmethod
    def _getToolTip(cls, bonus):
        tooltipData = []
        for tokenID in bonus.getTokens().iterkeys():
            if tokenID.startswith(RECRUIT_TMAN_TOKEN_PREFIX):
                tooltipData.append(TooltipData(tooltip=None, isSpecial=True, specialAlias=TOOLTIPS_CONSTANTS.TANKMAN_NOT_RECRUITED, specialArgs=[tokenID]))

        return tooltipData

    @classmethod
    def _getContentId(cls, bonus):
        result = []
        for tokenID in bonus.getTokens().iterkeys():
            if tokenID.startswith(RECRUIT_TMAN_TOKEN_PREFIX):
                result.append(BACKPORT_TOOLTIP_CONTENT_ID)

        return result

    @classmethod
    def _getBonusModel(cls):
        return BigIconBonusModel()


def getRacesBonusPacker():
    mapping = getDefaultBonusPackersMap()
    tokensPacker = RacesTokenBonusUIPacker()
    mapping.update({'battleToken': tokensPacker,
     'vehicles': RacesVehiclesBonusUIPacker(),
     'tmanToken': TmanTemplateBonusPacker()})
    return BonusUIPacker(mapping)


def fillQuestsModel(questsModel, quests, tooltipData):
    questsModel.clear()
    questsModel.reserve(len(quests))
    for quest in quests.itervalues():
        packer = DailyQuestUIDataPacker(quest, bonusPackerGetter=getRacesBonusPacker)
        bonusModel = packer.pack()
        tooltipData.update(packer.getTooltipData())
        questsModel.addViewModel(bonusModel)

    questsModel.invalidate()
