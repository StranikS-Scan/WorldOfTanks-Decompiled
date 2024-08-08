# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/wot_anniversary/bonuses.py
import logging
from typing import Dict, List, Optional, TYPE_CHECKING
from Vehicle import Vehicle
from gui.Scaleform.genConsts.TOOLTIPS_CONSTANTS import TOOLTIPS_CONSTANTS
from gui.impl import backport
from gui.impl.backport import createTooltipData, TooltipData
from gui.impl.gen import R
from gui.impl.gen.view_models.common.bonus_model import BonusModel
from gui.impl.gen.view_models.common.missions.bonuses.icon_bonus_model import IconBonusModel
from gui.impl.gen.view_models.views.lobby.wot_anniversary.login_bonus_model import LoginBonusModel, State as LoginBonusState
from gui.impl.gen.view_models.views.lobby.wot_anniversary.vehicle_bonus_model import VehicleBonusModel
from gui.impl.lobby.awards.packers import MultiAwardVehiclesBonusUIPacker
from gui.impl.lobby.common.view_helpers import packBonusTooltip
from gui.server_events.awards_formatters import BATTLE_BONUS_X5_TOKEN
from gui.server_events.bonuses import SimpleBonus
from gui.server_events.event_items import Quest
from gui.shared.gui_items.Vehicle import getIconResourceName, getNationLessName
from gui.shared.gui_items.customization import CustomizationTooltipContext
from gui.shared.missions.packers.bonus import getDefaultBonusPackersMap, BonusUIPacker, GroupsBonusUIPacker, getDefaultBonusPacker, BaseBonusUIPacker, VehiclesBonusUIPacker, GoodiesBonusUIPacker, SimpleBonusUIPacker, TokenBonusUIPacker
from gui.shared.money import Currency
from gui.wot_anniversary.utils import isTokenQuestUnlocked
from gui.wot_anniversary.wot_anniversary_constants import WOT_ANNIVERSARY_LOGIN_UNLOCK_TOKEN
if TYPE_CHECKING:
    from frameworks.wulf import Array
    from gui.server_events.bonuses import VehiclesBonus, C11nProgressTokenBonus
_logger = logging.getLogger(__name__)

class SetOfCustomizationBonus(SimpleBonus):
    BONUS_NAME = 'customizations'

    def __init__(self, value):
        super(SetOfCustomizationBonus, self).__init__(self.BONUS_NAME, value)


class SetOfCustomizationBonusPacker(SimpleBonusUIPacker):

    @classmethod
    def _pack(cls, bonus):
        return [cls._packSingleBonus(bonus, None)]

    @classmethod
    def _packSingleBonus(cls, bonus, _):
        model = IconBonusModel()
        cls._packCommon(bonus, model)
        itemTypeName, (itemValue, itemCount) = bonus.getValue()
        model.setValue(str(itemValue))
        model.setIcon(str(itemTypeName))
        model.setLabel(backport.text(R.strings.wot_anniversary.bonuses.setOfDecals(), count=itemCount))
        return model

    @classmethod
    def _getBonusModel(cls):
        return IconBonusModel()


class VehiclesBonusPacker(MultiAwardVehiclesBonusUIPacker):

    @classmethod
    def _packVehicleBonusModel(cls, bonus, vehInfo, isRent, vehicle):
        model = LoginBonusModel()
        model.setName(cls._createUIName(bonus, isRent))
        model.setIsCompensation(bonus.isCompensation())
        model.setLabel(cls._getLabel(vehicle))
        return model


class WotAnniversaryGroupsBonusPacker(GroupsBonusUIPacker):

    @classmethod
    def _pack(cls, bonus):
        model = LoginBonusModel()
        cls._packCommon(bonus, model)
        model.setIcon('default')
        return [model]

    @classmethod
    def _getToolTip(cls, bonus):
        return [createTooltipData(isSpecial=True, specialArgs=[bonus.getValue()])]

    @classmethod
    def _getContentId(cls, bonus):
        return [R.views.lobby.wot_anniversary.tooltips.RandomRewardTooltip()]


class CustomizationProgressBonusUIPacker(BaseBonusUIPacker):

    @classmethod
    def _pack(cls, bonus):
        return [cls._packSingleBonus(bonus)]

    @classmethod
    def _packSingleBonus(cls, bonus):
        model = cls._getBonusModel()
        model.setName('customizations')
        model.setIsCompensation(bonus.isCompensation())
        model.setLabel(bonus.getC11nItem().userName)
        model.setIcon(str(bonus.getC11nItem().itemTypeName))
        model.setValue(str(bonus.getProgressLevel()))
        return model

    @classmethod
    def _getBonusModel(cls):
        return IconBonusModel()

    @classmethod
    def _getToolTip(cls, bonus):
        tooltipData = [TooltipData(tooltip=None, isSpecial=True, specialAlias=TOOLTIPS_CONSTANTS.TECH_CUSTOMIZATION_ITEM_AWARD, specialArgs=CustomizationTooltipContext(itemCD=bonus.getC11nItem().intCD, showInventoryBlock=True))]
        return tooltipData


class CustomizationProgressLoginBonusPacker(CustomizationProgressBonusUIPacker):

    @classmethod
    def _getBonusModel(cls):
        return LoginBonusModel()


class WotAnniversaryVehiclesBonusUIPacker(VehiclesBonusUIPacker):

    @classmethod
    def _packVehicles(cls, bonus, vehicles):
        packedVehicles = []
        for vehicle, vehInfo in vehicles:
            packedVehicles.append(cls._packVehicle(bonus, vehInfo, vehicle))

        return packedVehicles

    @classmethod
    def _packVehicleBonusModel(cls, bonus, vehInfo, isRent, vehicle):
        model = VehicleBonusModel()
        cls.__fillVehicle(model, vehicle)
        model.setName(bonus.getName())
        return model

    @classmethod
    def __fillVehicle(cls, model, vehicle):
        model.setIsElite(not vehicle.getEliteStatusProgress().toUnlock or vehicle.isElite)
        model.setVehicleLvl(vehicle.level)
        model.setVehicleName(vehicle.userName)
        model.setVehicleType(vehicle.type)
        model.setBigIcon(getIconResourceName(getNationLessName(vehicle.name)))


class WotAnniversaryGoodiesBonusPacker(GoodiesBonusUIPacker):

    @classmethod
    def _packSingleBoosterBonus(cls, bonus, booster, count):
        return cls._packIconBonusModel(bonus, booster.getFullNameForResource(), count, booster.getDescription())


class WotAnniversaryTokenBonusPacker(TokenBonusUIPacker):

    @classmethod
    def _getTokenBonusPackers(cls):
        tokenBonusPackers = super(WotAnniversaryTokenBonusPacker, cls)._getTokenBonusPackers()
        tokenBonusPackers.update({BATTLE_BONUS_X5_TOKEN: cls.__packBattleBonusX5Token})
        return tokenBonusPackers

    @classmethod
    def __packBattleBonusX5Token(cls, model, bonus, *args):
        model.setName(BATTLE_BONUS_X5_TOKEN)
        model.setValue(str(bonus.getCount()))
        model.setLabel(backport.text(R.strings.wot_anniversary.bonuses.battleBonusX5()))
        return model


class WotAnniversaryEventCoinBonusPacker(SimpleBonusUIPacker):

    @classmethod
    def _pack(cls, bonus):
        label = backport.text(R.strings.wot_anniversary.bonuses.coin())
        return [cls._packSingleBonus(bonus, label if label else '')]


def getWotAnniversaryBonusPacker():
    mapping = getDefaultBonusPackersMap()
    mapping.update({'vehicles': VehiclesBonusPacker(),
     'tokens': WotAnniversaryTokenBonusPacker(),
     'groups': WotAnniversaryGroupsBonusPacker(),
     'styleProgress': CustomizationProgressLoginBonusPacker(),
     'goodies': WotAnniversaryGoodiesBonusPacker(),
     SetOfCustomizationBonus.BONUS_NAME: SetOfCustomizationBonusPacker(),
     Currency.EVENT_COIN: WotAnniversaryEventCoinBonusPacker()})
    return BonusUIPacker(mapping)


def getWotAnniversaryAwardPacker():
    mapping = getDefaultBonusPackersMap()
    mapping.update({'vehicles': WotAnniversaryVehiclesBonusUIPacker(),
     'styleProgress': CustomizationProgressBonusUIPacker()})
    return BonusUIPacker(mapping)


def packBonusModelAndTooltipDataFromQuests(quests, bonusModelsList, tooltipData, packer=None):
    packer = packer or getDefaultBonusPacker()
    tooltipIndex = 0 if tooltipData is None else len(tooltipData)
    for quest in quests:
        bonuses = quest.getBonuses()
        bonuses = [ b for b in bonuses if b.getName() in ('vehicles', 'groups', 'styleProgress') ]
        if quest.isCompleted():
            state = LoginBonusState.COLLECTED
        elif isTokenQuestUnlocked(quest, WOT_ANNIVERSARY_LOGIN_UNLOCK_TOKEN):
            state = LoginBonusState.AVAILABLE
        else:
            state = LoginBonusState.LOCKED
        for bonus in (b for b in bonuses if b.isShowInGUI()):
            bonusList = packer.pack(bonus)
            bTooltipList = packer.getToolTip(bonus)
            bContentIdList = packer.getContentId(bonus)
            for bIndex, bModel in enumerate(bonusList):
                bModel.setIndex(bIndex)
                tooltipIndex = packBonusTooltip(bModel, bIndex, bTooltipList, bContentIdList, tooltipData, tooltipIndex)
                bModel.setState(state)
                bonusModelsList.addViewModel(bModel)

    return
