# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/session_progress_rewards/session_progress_rewards_bonus_packers.py
import copy
import typing
from gui.impl.backport import createTooltipData
from gui.impl.gen import R
from gui.impl.gen.view_models.views.lobby.daily.session_progress_reward_bonus_model import SessionProgressRewardBonusModel
from gui.server_events.bonuses import getServiceBonuses
from gui.shared.gui_items.Vehicle import getNationLessName
from gui.shared.missions.packers.bonus import getDefaultBonusPackersMap, BonusUIPacker, VehiclesBonusUIPacker, SimpleBonusUIPacker, BACKPORT_TOOLTIP_CONTENT_ID
from gui.shared.money import Currency
if typing.TYPE_CHECKING:
    from gui.server_events.bonuses import VehiclesBonus
    from gui.shared.gui_items.Vehicle import Vehicle

def getSessionProgressRewardsBonusPacker():
    mapping = getDefaultBonusPackersMap()
    mapping.update({'vehicles': SessionProgressRewardsVehicleBonusUIPacker()})
    return BonusUIPacker(mapping)


def getSessionProgressRewardsCompensationTooltipPacker():
    mapping = getDefaultBonusPackersMap()
    mapping.update({'vehicles': SessionProgressRewardsVehicleBonusUIPacker(),
     Currency.CREDITS: SessionProgressRewardsCompensationBonusUIPacker(),
     Currency.GOLD: SessionProgressRewardsCompensationBonusUIPacker()})
    return BonusUIPacker(mapping)


def _iterVehicleInfos(bonusValue):
    return bonusValue.itervalues() if isinstance(bonusValue, dict) else (vehInfo for subDict in bonusValue for vehInfo in subDict.itervalues())


class SessionProgressRewardsVehicleBonusUIPacker(VehiclesBonusUIPacker):

    @classmethod
    def _packVehicleBonusModel(cls, bonus, vehInfo, isRent, vehicle):
        model = SessionProgressRewardBonusModel()
        model.setName(cls._createUIName(bonus, isRent))
        model.setIsCompensation(bonus.isCompensation())
        nationLessName = getNationLessName(vehicle.name)
        model.setLabel(cls._getLabel(vehicle))
        model.setValue(nationLessName)
        model.setVehicleName(nationLessName)
        model.setVehicleType(vehicle.type)
        model.setVehicleLevel(vehicle.level)
        model.setIsElite(vehicle.isElite)
        return model

    @classmethod
    def _packVehicles(cls, bonus, vehicles):
        packedVehicles = []
        for vehicle, vehInfo in vehicles:
            compensation = bonus.compensation(vehicle, bonus)
            if compensation:
                for bonusComp in compensation:
                    packedVehicles.extend(SessionProgressRewardsCompensationBonusUIPacker.pack(bonusComp))

            packedVehicles.append(cls._packVehicle(bonus, vehInfo, vehicle))

        return packedVehicles

    @classmethod
    def _packCompensationTooltip(cls, bonusComp, vehicle):
        return SessionProgressRewardsCompensationBonusUIPacker.getToolTip(bonusComp)

    @classmethod
    def _getContentId(cls, bonus):
        contentIds = []
        for vehicle, _ in bonus.getVehicles():
            compensation = bonus.compensation(vehicle, bonus)
            if compensation:
                for bonusComp in compensation:
                    contentIds.extend(SessionProgressRewardsCompensationBonusUIPacker.getContentId(bonusComp))

            contentIds.append(BACKPORT_TOOLTIP_CONTENT_ID)

        return contentIds


class SessionProgressRewardsCompensationBonusUIPacker(SimpleBonusUIPacker):

    @classmethod
    def _packSingleBonus(cls, bonus, label):
        model = super(SessionProgressRewardsCompensationBonusUIPacker, cls)._packSingleBonus(bonus, label)
        model.setCompensatedBonus(bonus.getCompensationReason().getName() if bonus.getCompensationReason() else '')
        return model

    @classmethod
    def _getBonusModel(cls):
        return SessionProgressRewardBonusModel()

    @classmethod
    def _getToolTip(cls, bonus):
        return [createTooltipData(tooltip=None, isSpecial=True, specialAlias=None, specialArgs=[cls._getCompensatedBonus(bonus), bonus])]

    @classmethod
    def _getCompensatedBonus(cls, bonus):
        compensatedBonus = bonus.getCompensationReason()
        if compensatedBonus and compensatedBonus.getName() == 'vehicles':
            bonusValue = copy.deepcopy(compensatedBonus.getValue())
            for vehInfo in _iterVehicleInfos(bonusValue):
                if vehInfo.get('compensatedNumber', 0) > 0:
                    vehInfo['compensatedNumber'] -= 1

            packed = getServiceBonuses(compensatedBonus.getName(), bonusValue)
            if packed:
                return packed[0]
        return compensatedBonus

    @classmethod
    def _getContentId(cls, bonus):
        return [R.views.lobby.daily.tooltips.SessionProgressRewardsCompensationTooltip()]
