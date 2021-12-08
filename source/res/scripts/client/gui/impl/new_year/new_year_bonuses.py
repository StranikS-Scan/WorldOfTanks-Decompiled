# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/new_year/new_year_bonuses.py
from gui.impl import backport
from gui.impl.gen import R
from gui.server_events.bonuses import SimpleBonus
from gui.shared.utils.functions import makeTooltip
from helpers import dependency
from new_year.ny_constants import NyBonusNames
from ny_common.settings import NYVehBranchConsts
from skeletons.new_year import INewYearController

class NYAlbumsAccess(SimpleBonus):

    def __init__(self):
        super(NYAlbumsAccess, self).__init__(NyBonusNames.ALBUM_ACCESS, '')

    def getTooltip(self):
        return makeTooltip(backport.text(R.strings.ny.levelsRewards.album.tooltip.header()), backport.text(R.strings.ny.levelsRewards.album.tooltip.body()))


class NYVehicleSlot(SimpleBonus):

    def __init__(self, slotType):
        super(NYVehicleSlot, self).__init__(NyBonusNames.VEHICLE_SLOT, '')
        self.__slotType = slotType

    def getSlotType(self):
        return self.__slotType


@dependency.replace_none_kwargs(nyController=INewYearController)
def extendBonusesByLevel(bonuses, level, nyController=None):
    levelInfo = nyController.getLevel(level)
    if levelInfo.isLastLevel():
        bonuses.append(NYAlbumsAccess())
    if levelInfo.hasTankSlot():
        for vehSlot in nyController.getVehicleBranch().getVehicleSlots():
            slotType = vehSlot.getRestrictionType()
            if slotType == NYVehBranchConsts.LEVEL and vehSlot.getLevel() == level:
                bonuses.append(NYVehicleSlot(slotType))
                break
