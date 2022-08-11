# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/wot_anniversary/wot_anniversary_bonuses_packers.py
import logging
import typing
from gui.impl import backport
from gui.impl.gen import R
from gui.impl.gen.view_models.common.missions.bonuses.bonus_model import BonusModel
from gui.impl.gen.view_models.views.lobby.wot_anniversary.vehicle_bonus_model import VehicleBonusModel
from gui.shared.missions.packers.bonus import BonusUIPacker, getDefaultBonusPackersMap, VehiclesBonusUIPacker, CustomizationBonusUIPacker
if typing.TYPE_CHECKING:
    from gui.shared.gui_items.Vehicle import Vehicle
    from gui.server_events.bonuses import VehiclesBonus
_logger = logging.getLogger(__name__)

def getWotAnniversaryBonusPacker():
    mapping = getDefaultBonusPackersMap()
    mapping.update({'vehicles': WotAnniversaryVehiclesBonusUIPacker(),
     'customizations': WotAnniversaryCustomizationBonusUIPacker()})
    return BonusUIPacker(mapping)


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


class WotAnniversaryCustomizationBonusUIPacker(CustomizationBonusUIPacker):

    @classmethod
    def _packSingleBonus(cls, bonus, item, label):
        model = super(WotAnniversaryCustomizationBonusUIPacker, cls)._packSingleBonus(bonus, item, label)
        customization = bonus.getC11nItem(item)
        model.setLabel(backport.text(R.strings.wot_anniversary.finalRewardScreen.customizationLabel(), name=customization.userName))
        return model


def packBonusModelAndTooltipData(bonuses, bonusModelsList, tooltipData=None):
    bonusIndexTotal = 0
    if tooltipData is not None:
        bonusIndexTotal = len(tooltipData)
    packer = getWotAnniversaryBonusPacker()
    for bonus in bonuses:
        if bonus.isShowInGUI():
            bonusList = packer.pack(bonus)
            bonusTooltipList = []
            bonusContentIdList = []
            if bonusList and tooltipData is not None:
                bonusTooltipList = packer.getToolTip(bonus)
                bonusContentIdList = packer.getContentId(bonus)
            for bonusIndex, item in enumerate(bonusList):
                item.setIndex(bonusIndex)
                bonusModelsList.addViewModel(item)
                if tooltipData is not None:
                    tooltipIdx = str(bonusIndexTotal)
                    item.setTooltipId(tooltipIdx)
                    if bonusTooltipList:
                        tooltipData[tooltipIdx] = bonusTooltipList[bonusIndex]
                    if bonusContentIdList:
                        item.setTooltipContentId(str(bonusContentIdList[bonusIndex]))
                    bonusIndexTotal += 1

    return
