# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/vehicle_compare/cmp_helpers.py
import typing
from frameworks.wulf import WindowLayer
from gui.Scaleform.daapi.settings.views import VIEW_ALIAS
from gui.Scaleform.daapi.view.lobby.vehicle_compare.cmp_top_modules import TopModulesChecker
from gui.Scaleform.framework.managers.containers import POP_UP_CRITERIA
from gui.shared.gui_items import GUI_ITEM_TYPE_NAMES, GUI_ITEM_TYPE
from gui.shared.gui_items.Tankman import Tankman
from helpers import dependency
from items import tankmen
from items.components.c11n_components import SeasonType
from items.components.detachment_constants import NO_DETACHMENT_ID
from shared_utils import first
from skeletons.gui.app_loader import IAppLoader
from skeletons.gui.customization import ICustomizationService
from skeletons.gui.shared.gui_items import IGuiItemsFactory
if typing.TYPE_CHECKING:
    from gui.shared.gui_items.Vehicle import Vehicle
    from gui.shared.gui_items.customization.c11n_items import Camouflage
    from gui.Scaleform.daapi.view.lobby.vehicle_compare.cmp_configurator_view import VehicleCompareConfiguratorMain
    from gui.game_control.veh_comparison_basket import PerksData
MODULES_INSTALLING_ORDER = (GUI_ITEM_TYPE.CHASSIS,
 GUI_ITEM_TYPE.TURRET,
 GUI_ITEM_TYPE.GUN,
 GUI_ITEM_TYPE.ENGINE,
 GUI_ITEM_TYPE.RADIO)
NOT_AFFECTED_DEVICES = {}
NOT_AFFECTED_EQUIPMENTS = {'smallRepairkit', 'smallMedkit', 'handExtinguishers'}
OPTIONAL_DEVICE_TYPE_NAME = GUI_ITEM_TYPE_NAMES[GUI_ITEM_TYPE.OPTIONALDEVICE]
EQUIPMENT_TYPE_NAME = GUI_ITEM_TYPE_NAMES[GUI_ITEM_TYPE.EQUIPMENT]
BATTLE_BOOSTER_TYPE_NAME = GUI_ITEM_TYPE_NAMES[GUI_ITEM_TYPE.BATTLE_BOOSTER]

def createTankman(nationID, vehicleTypeID, role, roleLevel, skills):
    descr = tankmen.generateCompactDescr(tankmen.generatePassport(nationID), vehicleTypeID, role, roleLevel, skills)
    return Tankman(descr)


def isEquipmentSame(equipment1, equipment2):
    if equipment1 is None or equipment2 is None:
        return False
    elif len(equipment1) != len(equipment2):
        return False
    else:
        for i in xrange(len(equipment1)):
            if equipment1[i] != equipment2[i]:
                return False

        return True


@dependency.replace_none_kwargs(appLoader=IAppLoader)
def getCmpConfiguratorMainView(appLoader=None):
    cmpConfiguratorMain = appLoader.getApp().containerManager.getView(WindowLayer.SUB_VIEW, {POP_UP_CRITERIA.VIEW_ALIAS: VIEW_ALIAS.VEHICLE_COMPARE_MAIN_CONFIGURATOR})
    return cmpConfiguratorMain


@dependency.replace_none_kwargs(c11nService=ICustomizationService)
def getSuitableCamouflage(vehicle, c11nService=None):
    return first(c11nService.getCamouflages(vehicle=vehicle).itervalues())


def isCamouflageSet(vehicle):
    return bool(vehicle.getBonusCamo())


@dependency.replace_none_kwargs(factory=IGuiItemsFactory)
def applyCamouflage(vehicle, select, factory=None):
    if select:
        camo = getSuitableCamouflage(vehicle)
        if camo:
            season = first(camo.seasons)
            outfit = vehicle.getOutfit(season)
            outfit = outfit or factory.createOutfit(vehicleCD=vehicle.descriptor.makeCompactDescr())
            outfit.hull.slotFor(GUI_ITEM_TYPE.CAMOUFLAGE).set(camo.intCD)
            vehicle.setCustomOutfit(season, outfit)
    else:
        removeVehicleCamouflages(vehicle)


def removeVehicleCamouflages(vehicle):
    for season in SeasonType.SEASONS:
        outfit = vehicle.getOutfit(season)
        if outfit:
            outfit.hull.slotFor(GUI_ITEM_TYPE.CAMOUFLAGE).clear()


def getVehicleModules(vehicle):
    return (vehicle.chassis,
     vehicle.turret,
     vehicle.gun,
     vehicle.engine,
     vehicle.radio)


def getVehicleTopModules(vehicle):
    checker = TopModulesChecker(vehicle)
    topModules = checker.process()
    checker.clear()
    return sorted(topModules, key=lambda module: MODULES_INSTALLING_ORDER.index(module.itemTypeID))


def setPerksController(vehicle, perks):
    vehicle.stopPerksController()
    vehicle.initPerksController(NO_DETACHMENT_ID, perks.perks)
