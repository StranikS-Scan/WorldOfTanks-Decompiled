# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/common/vehicle_model_helpers.py
import typing
from frameworks.wulf.view.array import fillViewModelsArray
from gui.impl.gen.view_models.common.vehicle_mechanic_model import VehicleMechanicModel
from gui.impl.gen.view_models.views.lobby.common.vehicle_model import VehicleModel
from gui.impl.lobby.platoon.platoon_helpers import removeNationFromTechName
from gui.shared.gui_items.Vehicle import Vehicle
from gui.shared.utils.functions import replaceHyphenToUnderscore
if typing.TYPE_CHECKING:
    from frameworks.wulf import Array
    from typing import Optional, Iterable

def fillVehicleModel(model, vehicleItem, tags=None):
    model.setIsPremium(vehicleItem.isElite)
    model.setName(vehicleItem.descriptor.type.shortUserString)
    model.setLongName(vehicleItem.descriptor.type.userString)
    model.setTechName(replaceHyphenToUnderscore(removeNationFromTechName(vehicleItem.name)))
    model.setTier(vehicleItem.level)
    model.setRoleKey(vehicleItem.roleLabel)
    model.setType(vehicleItem.type)
    model.setNation(vehicleItem.nationName)
    model.setVehicleCD(vehicleItem.compactDescr)
    if not tags:
        return
    model.setTags(','.join(frozenset(tags) & vehicleItem.tags))


def fillVehicleMechanicsArray(mechanicsArray, vehicleItem):
    mechanics = []
    for mechanic in vehicleItem.getVehicleMechanicItems():
        mechanicModel = VehicleMechanicModel()
        mechanicModel.setName(mechanic.guiName)
        mechanicModel.setIsSpecial(mechanic.isSpecial)
        mechanicModel.setHasVideo(mechanic.hasVideo)
        mechanics.append(mechanicModel)

    fillViewModelsArray(mechanics, mechanicsArray)
