# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/bob/bob_bonuses_packers.py
import logging
import typing
from gui.battle_pass.battle_pass_bonuses_packers import BattlePassPremiumDaysPacker, ExtendedCrewBookBonusUIPacker, ExtendedCreditsBonusUIPascker
from gui.dog_tag_composer import dogTagComposer
from gui.impl.backport import TooltipData
from gui.impl.gen.view_models.common.missions.bonuses.extended_icon_bonus_model import ExtendedIconBonusModel
from gui.impl.gen.view_models.common.missions.bonuses.extended_item_bonus_model import ExtendedItemBonusModel
from gui.shared.gui_items import GUI_ITEM_TYPE
from gui.shared.missions.packers.bonus import BonusUIPacker, getDefaultBonusPackersMap, DossierBonusUIPacker, ItemBonusUIPacker, GoodiesBonusUIPacker, SimpleBonusUIPacker, CustomizationBonusUIPacker, VehiclesBonusUIPacker, DogTagComponentsUIPacker
from gui.shared.money import Currency
if typing.TYPE_CHECKING:
    from gui.server_events.bonuses import SimpleBonus
    from gui.impl.gen.view_models.common.missions.bonuses.bonus_model import BonusModel
_logger = logging.getLogger(__name__)

def getBobBonusPacker():
    mapping = getDefaultBonusPackersMap()
    mapping.update({'premium_plus': BattlePassPremiumDaysPacker(),
     'dossier': BobDossierBonusPacker(),
     'customizations': BobCustomizationPacker(),
     'items': ExtendedItemBonusUIPacker(),
     'crewBooks': ExtendedCrewBookBonusUIPacker(),
     'goodies': ExtendedGoodiesBonusUIPacker(),
     'slots': ExtendedSlotsPacker(),
     'vehicles': BobVehiclesPacker(),
     Currency.CREDITS: ExtendedCreditsBonusUIPascker(),
     'dogTagComponents': ExtendedDogTagComponentsPacker()})
    return BonusUIPacker(mapping)


def packBonusModelAndTooltipData(bonuses, bonusModelsList, tooltipData=None):
    bonusIndexTotal = 0
    if tooltipData is not None:
        bonusIndexTotal = len(tooltipData)
    packer = getBobBonusPacker()
    for bonus in bonuses:
        if bonus.isShowInGUI():
            bonusList = packer.pack(bonus)
            bonusTooltipList = []
            if bonusList and tooltipData is not None:
                bonusTooltipList = packer.getToolTip(bonus)
            for bonusIndex, item in enumerate(bonusList):
                item.setIndex(bonusIndex)
                bonusModelsList.addViewModel(item)
                if tooltipData is not None and bonusTooltipList:
                    tooltipIdx = str(bonusIndexTotal)
                    item.setTooltipId(tooltipIdx)
                    tooltipData[tooltipIdx] = bonusTooltipList[bonusIndex]
                    bonusIndexTotal += 1

    return


class BobDossierBonusPacker(DossierBonusUIPacker):

    @classmethod
    def _packSingleBonus(cls, bonus, dossierIconName, dossierNamePostfix, dossierValue, dossierLabel):
        model = super(BobDossierBonusPacker, cls)._packSingleBonus(bonus, dossierIconName, dossierNamePostfix, dossierValue, dossierLabel)
        model.setUserName(dossierLabel)
        return model

    @classmethod
    def _getBonusModel(cls):
        return ExtendedIconBonusModel()


class ExtendedItemBonusUIPacker(ItemBonusUIPacker):

    @classmethod
    def _packSingleBonus(cls, bonus, item, count):
        model = super(ExtendedItemBonusUIPacker, cls)._packSingleBonus(bonus, item, count)
        if item.itemTypeID == GUI_ITEM_TYPE.OPTIONALDEVICE:
            model.setUserName(item.userName)
        elif item.itemTypeID == GUI_ITEM_TYPE.BATTLE_BOOSTER:
            model.setItem(item.name)
            model.setUserName(item.userName)
        return model

    @classmethod
    def _getBonusModel(cls):
        return ExtendedItemBonusModel()


class ExtendedGoodiesBonusUIPacker(GoodiesBonusUIPacker):

    @classmethod
    def _packIconBonusModel(cls, bonus, icon, count, label):
        model = super(ExtendedGoodiesBonusUIPacker, cls)._packIconBonusModel(bonus, icon, count, label)
        model.setUserName(label)
        return model

    @classmethod
    def _getBonusModel(cls):
        return ExtendedIconBonusModel()


class ExtendedSlotsPacker(SimpleBonusUIPacker):

    @classmethod
    def _packSingleBonus(cls, bonus, label):
        model = super(ExtendedSlotsPacker, cls)._packSingleBonus(bonus, label)
        model.setUserName(label)
        return model

    @classmethod
    def _getBonusModel(cls):
        return ExtendedItemBonusModel()


class BobCustomizationPacker(CustomizationBonusUIPacker):

    @classmethod
    def _packSingleBonus(cls, bonus, item, label):
        model = super(BobCustomizationPacker, cls)._packSingleBonus(bonus, item, label)
        itemCustomization = bonus.getC11nItem(item)
        model.setIcon('{}_{}'.format(itemCustomization.itemTypeName, itemCustomization.id))
        model.setUserName(label)
        return model

    @classmethod
    def _getBonusModel(cls):
        return ExtendedIconBonusModel()


class BobVehiclesPacker(VehiclesBonusUIPacker):

    @classmethod
    def _packVehicleBonusModel(cls, bonus, isRent, vehicle):
        model = super(BobVehiclesPacker, cls)._packVehicleBonusModel(bonus, isRent, vehicle)
        model.setIcon(vehicle.name.split(':', 1)[-1])
        model.setUserName(vehicle.userName)
        return model

    @classmethod
    def _getBonusModel(cls):
        return ExtendedIconBonusModel()


class ExtendedDogTagComponentsPacker(DogTagComponentsUIPacker):

    @classmethod
    def _packDogTag(cls, bonus, dogTagRecord):
        model = super(ExtendedDogTagComponentsPacker, cls)._packDogTag(bonus, dogTagRecord)
        model.setUserName(dogTagComposer.getComponentTitle(dogTagRecord.componentId))
        return model

    @classmethod
    def _getBonusModel(cls):
        return ExtendedIconBonusModel()
