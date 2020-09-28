# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/wt_event/wt_event_bonuses_packers.py
import logging
import typing
from constants import LOOTBOX_TOKEN_PREFIX
from gui.Scaleform.genConsts.TOOLTIPS_CONSTANTS import TOOLTIPS_CONSTANTS
from gui.impl import backport
from gui.impl.auxiliary.rewards_helper import formatEliteVehicle
from gui.impl.backport import TooltipData, createTooltipData
from gui.impl.gen import R
from gui.impl.gen.view_models.common.missions.bonuses.bonus_model import BonusModel
from gui.impl.gen.view_models.common.missions.bonuses.token_bonus_model import TokenBonusModel
from gui.shared.gui_items.Vehicle import getNationLessName
from gui.shared.utils.functions import makeTooltip
from gui.shared.missions.packers.bonus import BonusUIPacker, getDefaultBonusPackersMap, TokenBonusUIPacker, BaseBonusUIPacker, ItemBonusUIPacker, CustomizationBonusUIPacker, VehiclesBonusUIPacker, CrewSkinBonusUIPacker
from gui.wt_event.wt_event_helpers import getTicketName, VEH_COMP_R_ID, isBossCollectionElement, HUNTER_ELEMENT_NAME, BOSS_ELEMENT_NAME
from helpers import dependency, int2roman
from shared_utils import first
from skeletons.gui.game_control import IGameEventController
from skeletons.gui.shared import IItemsCache
if typing.TYPE_CHECKING:
    from gui.server_events.bonuses import TokensBonus, SimpleBonus
_logger = logging.getLogger(__name__)

def packWtQuestBonusModelAndTooltipData(quest, packer, array, tooltipData=None):
    bonuses = quest.getBonuses()
    bonusIndexTotal = len(tooltipData)
    bonusTooltipList = []
    for bonus in bonuses:
        if bonus.isShowInGUI():
            bonusList = packer.pack(bonus)
            if bonusList and tooltipData is not None:
                bonusTooltipList = packer.getToolTip(bonus)
            for bonusIndex, item in enumerate(bonusList):
                item.setIndex(bonusIndexTotal)
                array.addViewModel(item)
                if tooltipData is not None:
                    tooltipIdx = str(bonusIndexTotal)
                    item.setTooltipId(tooltipIdx)
                    tooltipData[tooltipIdx] = bonusTooltipList[bonusIndex]
                    bonusIndexTotal += 1

    return


def getWtEventBonusPacker(showCompensation=False):
    tokenPacker = WtEventTokenBonusPacker()
    mapping = getDefaultBonusPackersMap()
    mapping.update({'items': WTEventItemBonusUIPacker(),
     'battleToken': tokenPacker,
     'wtTicket': tokenPacker,
     'groups': WtEventGroupBonusPacker(),
     'customizations': WTCustomizationBonusUIPacker(),
     'vehicles': WTVehiclesBonusUIPacker() if not showCompensation else WTVehiclesCompensationBonusUIPacker(),
     'crewSkins': WTCrewSkinBonusUIPacker()})
    return BonusUIPacker(mapping)


class WTVehiclesBonusUIPacker(VehiclesBonusUIPacker):

    @classmethod
    def _needToShowCompensationBonus(cls):
        return False

    @classmethod
    def _packTooltip(cls, bonus, vehicle, vehInfo):
        compensation = bonus.compensation(vehicle, bonus)
        return first(cls._packCompensationTooltip(first(compensation), vehicle)) if bonus.compensation(vehicle, bonus) else super(WTVehiclesBonusUIPacker, cls)._packTooltip(bonus, vehicle, vehInfo)

    @classmethod
    def _packCompensationTooltip(cls, bonusComp, vehicle):
        tooltipDataList = super(WTVehiclesBonusUIPacker, cls)._packCompensationTooltip(bonusComp, vehicle)
        return [ cls.__convertCompensationTooltip(bonusComp, vehicle, tooltipData) for tooltipData in tooltipDataList ]

    @classmethod
    def _packVehicleBonusModel(cls, bonus, vehicle, isRent):
        model = super(WTVehiclesBonusUIPacker, cls)._packVehicleBonusModel(bonus, vehicle, isRent)
        model.setIsCompensation(bool(bonus.compensation(vehicle, bonus)))
        model.setValue(vehicle.shortUserName)
        return model

    @classmethod
    def __convertCompensationTooltip(cls, bonusComp, vehicle, tooltipData):
        specialArgs = {'iconBefore': backport.image(R.images.gui.maps.shop.vehicles.c_180x135.dyn(getNationLessName(vehicle.name))()),
         'labelBefore': '',
         'iconAfter': backport.image(R.images.gui.maps.icons.quests.bonuses.big.gold()),
         'labelAfter': bonusComp.getIconLabel(),
         'bonusName': bonusComp.getName(),
         'vehicleName': vehicle.shortUserName,
         'vehicleType': formatEliteVehicle(vehicle.isElite, vehicle.type),
         'isElite': vehicle.isElite,
         'vehicleLvl': int2roman(vehicle.level)}
        return createTooltipData(tooltip=tooltipData.tooltip, specialAlias=VEH_COMP_R_ID, specialArgs=specialArgs)


class WTVehiclesCompensationBonusUIPacker(WTVehiclesBonusUIPacker):

    @classmethod
    def _needToShowCompensationBonus(cls):
        return True


class WTCustomizationBonusUIPacker(CustomizationBonusUIPacker):
    __gameEventController = dependency.descriptor(IGameEventController)

    @classmethod
    def _packSingleBonus(cls, bonus, item):
        model = super(WTCustomizationBonusUIPacker, cls)._packSingleBonus(bonus, item)
        bonusId, collectionName = cls.__gameEventController.getIdAndCollectionByIntCD(bonus.getC11nItem(item).intCD)
        if collectionName is not None:
            model.setIcon(collectionName + str(bonusId))
        return model


class WTCrewSkinBonusUIPacker(CrewSkinBonusUIPacker):
    __gameEventController = dependency.descriptor(IGameEventController)

    @classmethod
    def _packSingleBonus(cls, bonus, crewSkin, count):
        model = super(WTCrewSkinBonusUIPacker, cls)._packSingleBonus(bonus, crewSkin, count)
        bonusId, collectionName = cls.__gameEventController.getIdAndCollectionByIntCD(crewSkin.intCD)
        if collectionName is not None:
            model.setIcon(collectionName + str(bonusId))
        return model


class WTEventItemBonusUIPacker(ItemBonusUIPacker):

    @classmethod
    def _packSingleBonus(cls, bonus, item, count):
        model = super(WTEventItemBonusUIPacker, cls)._packSingleBonus(bonus, item, count)
        model.setName(item.getGUIEmblemID())
        return model


class WtEventTokenBonusPacker(TokenBonusUIPacker):
    itemsCache = dependency.descriptor(IItemsCache)

    @classmethod
    def _pack(cls, bonus):
        result = super(WtEventTokenBonusPacker, cls)._pack(bonus)
        bonusTokens = bonus.getTokens()
        ticketName = getTicketName()
        for tokenID, token in bonusTokens.iteritems():
            if tokenID.startswith(LOOTBOX_TOKEN_PREFIX):
                result.append(cls._packLootboxToken(token))
            if tokenID == ticketName:
                result.append(cls._packTicketToken(token))

        return result

    @classmethod
    def _packLootboxToken(cls, token):
        model = TokenBonusModel()
        model.setValue(str(token.count))
        lootBox = cls.itemsCache.items.tokens.getLootBoxByTokenID(token.id)
        model.setName(lootBox.getType())
        model.setUserName(lootBox.getUserName())
        return model

    @classmethod
    def _packTicketToken(cls, token):
        model = BonusModel()
        model.setValue(str(token.count))
        model.setName(token.id)
        return model

    @classmethod
    def _getToolTip(cls, bonus):
        result = super(WtEventTokenBonusPacker, cls)._getToolTip(bonus)
        bonusTokens = bonus.getTokens()
        ticketName = getTicketName()
        for tokenID, _ in bonusTokens.iteritems():
            if tokenID.startswith(LOOTBOX_TOKEN_PREFIX):
                result.append(cls._getLootboxToolTip(tokenID))
            if tokenID == ticketName:
                result.append(cls._getTicketToolTip())

        return result

    @classmethod
    def _getLootboxToolTip(cls, tokenID):
        lootBox = cls.itemsCache.items.tokens.getLootBoxByTokenID(tokenID)
        lootBoxType = lootBox.getType()
        return createTooltipData(isWulfTooltip=True, specialAlias=TOOLTIPS_CONSTANTS.WT_EVENT_LOOT_BOX, specialArgs=[lootBoxType])

    @classmethod
    def _getTicketToolTip(cls):
        return createTooltipData(isWulfTooltip=True, specialAlias=TOOLTIPS_CONSTANTS.WT_EVENT_BOSS_TICKET, specialArgs=[])


class WtEventGroupBonusPacker(BaseBonusUIPacker):

    @classmethod
    def _pack(cls, bonus):
        isBoss = isBossCollectionElement(bonus)
        return [] if isBoss is None else [cls._packSingleBonus(bonus, isBoss)]

    @classmethod
    def _packSingleBonus(cls, bonus, isBoss):
        model = BonusModel()
        model.setName(BOSS_ELEMENT_NAME if isBoss else HUNTER_ELEMENT_NAME)
        return model

    @classmethod
    def _getToolTip(cls, bonus):
        isBoss = isBossCollectionElement(bonus)
        if isBoss is None:
            return []
        else:
            if isBoss:
                rCollection = R.strings.wt_event.bonuses.boss_collection.tooltip
            else:
                rCollection = R.strings.wt_event.bonuses.hunter_collection.tooltip
            tooltip = makeTooltip(backport.text(rCollection.header()), backport.text(rCollection.body()))
            return [createTooltipData(tooltip)]
