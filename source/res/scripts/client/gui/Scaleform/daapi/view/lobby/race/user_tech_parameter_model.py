# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/race/user_tech_parameter_model.py
from racing_event_config import RacingVehicles, VehicleProperties, RACING_VEHICLES_PROPERTIES
from gui.impl import backport
from gui.impl.gen import R
from gui.impl.gen.view_models.views.race.tech_parameters_cmp_view_model import TechParametersCmpViewModel
from helpers import dependency
from skeletons.gui.shared import IItemsCache

class UserTechParameterModel(TechParametersCmpViewModel):
    itemsCache = dependency.descriptor(IItemsCache)

    def setVehicleIntCD(self, vehIntCD):
        vehicle = self.itemsCache.items.getItemByCD(vehIntCD)
        if vehicle is None or vehicle.intCD not in RacingVehicles.ALL:
            return
        else:
            vehProps = RACING_VEHICLES_PROPERTIES.get(vehIntCD)
            if vehProps is None:
                return
            with self.transaction() as model:
                model.setEngineSpeed('{} {}'.format(vehProps[VehicleProperties.SPEED][0], backport.text(R.strings.festival.race.hangar.techParameters.kmph())))
                model.setEngineSpeedHighlight(vehProps[VehicleProperties.SPEED][1])
                secTxt = backport.text(R.strings.festival.race.hangar.techParameters.sec())
                model.setEngineAcceleration('{} {}'.format(vehProps[VehicleProperties.ACCELERATION][0], secTxt))
                model.setEngineAccelerationHighlight(vehProps[VehicleProperties.ACCELERATION][1])
                handlingValue = backport.text(R.strings.festival.race.hangar.techParameters.chassis_handling.dyn(vehProps[VehicleProperties.CHASSIS_HANDLING][0])())
                model.setChassisHandling(handlingValue)
                model.setChassisHandlingHighlight(vehProps[VehicleProperties.CHASSIS_HANDLING][1])
                model.setGunDpm(vehProps[VehicleProperties.DPM][0])
                model.setGunDpmHighlight(vehProps[VehicleProperties.DPM][1])
                model.setGunReload('{} {}'.format(vehProps[VehicleProperties.GUN_RELOAD][0], secTxt))
                model.setGunReloadHighlight(vehProps[VehicleProperties.GUN_RELOAD][1])
                model.setBodyArmor(vehProps[VehicleProperties.ARMOR][0])
                model.setBodyArmorHighlight(vehProps[VehicleProperties.ARMOR][1])
            return
