# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/battle/comp7/messages/player_messages.py
from comp7_common import ROLE_EQUIPMENT_TAG
from constants import EQUIPMENT_STAGES, ROLE_TYPE_TO_LABEL
from helpers import dependency
from gui.Scaleform.daapi.view.battle.shared.messages import PlayerMessages
from points_of_interest_shared import ENEMY_VEHICLE_ID
from skeletons.gui.game_control import IComp7Controller
_ROLE_EQUIPMENT_READY = 'ROLE_EQUIPMENT_READY'
_POI_EQUIPMENT_USED = 'POI_EQUIPMENT_USED'
_POI_EQUIPMENT_USED_BY_ENEMY = 'POI_EQUIPMENT_USED_BY_ENEMY'
_POI_EQUIPMENT_USED_BY_ALLY = 'POI_EQUIPMENT_USED_BY_ALLY'
_ROLE_EQUIPMENT_APPLIED = 'ROLE_EQUIPMENT_APPLIED'
_ROLE_EQUIPMENT_PROMOTED = 'ROLE_EQUIPMENT_PROMOTED'

class Comp7PlayerMessages(PlayerMessages):
    __comp7Controller = dependency.descriptor(IComp7Controller)

    def _addGameListeners(self):
        super(Comp7PlayerMessages, self)._addGameListeners()
        equipmentCtrl = self.sessionProvider.shared.equipments
        if equipmentCtrl is not None:
            equipmentCtrl.onEquipmentUpdated += self.__onEquipmentUpdated
            equipmentCtrl.onRoleEquipmentStateChanged += self.__onRoleEquipmentStateChanged
        poiCtrl = self.sessionProvider.dynamic.pointsOfInterest
        if poiCtrl is not None:
            poiCtrl.onPoiEquipmentUsed += self.__onPoiEquipmentUsed
        return

    def _removeGameListeners(self):
        equipmentCtrl = self.sessionProvider.shared.equipments
        if equipmentCtrl is not None:
            equipmentCtrl.onRoleEquipmentStateChanged -= self.__onRoleEquipmentStateChanged
            equipmentCtrl.onEquipmentUpdated -= self.__onEquipmentUpdated
        poiCtrl = self.sessionProvider.dynamic.pointsOfInterest
        if poiCtrl is not None:
            poiCtrl.onPoiEquipmentUsed -= self.__onPoiEquipmentUsed
        super(Comp7PlayerMessages, self)._removeGameListeners()
        return

    def __onEquipmentUpdated(self, _, item):
        if ROLE_EQUIPMENT_TAG not in item.getTags():
            return
        if item.getStage() == EQUIPMENT_STAGES.ACTIVE and item.getPrevStage() != EQUIPMENT_STAGES.ACTIVE:
            equipment = item.getDescriptor()
            self.sessionProvider.shared.messages.showVehicleMessage(_ROLE_EQUIPMENT_APPLIED, {'name': equipment.userString})
        if item.becomeReady and item.becomeAvailable:
            equipment = item.getDescriptor()
            self.sessionProvider.shared.messages.showVehicleMessage(_ROLE_EQUIPMENT_READY, {'equipment': equipment.userString})

    def __onPoiEquipmentUsed(self, equipment, vehicleID):
        if vehicleID == self.sessionProvider.shared.vehicleState.getControllingVehicleID():
            self.sessionProvider.shared.messages.showVehicleMessage(_POI_EQUIPMENT_USED, {'equipment': equipment.userString})
        elif vehicleID == ENEMY_VEHICLE_ID:
            self.showMessage(_POI_EQUIPMENT_USED_BY_ENEMY, {'equipment': equipment.userString})
        else:
            self.showMessage(_POI_EQUIPMENT_USED_BY_ALLY, {'name': self.sessionProvider.getCtx().getPlayerFullName(vehicleID, showClan=False),
             'equipment': equipment.userString})

    def __onRoleEquipmentStateChanged(self, state, previousState=None):
        if state is None or previousState is None:
            return
        else:
            if state.level > previousState.level:
                vehicle = self.sessionProvider.shared.vehicleState.getControllingVehicle()
                if vehicle is None or not hasattr(vehicle, 'typeDescriptor'):
                    return
                roleType = ROLE_TYPE_TO_LABEL.get(vehicle.typeDescriptor.role)
                equipment = self.__comp7Controller.getRoleEquipment(roleType)
                self.sessionProvider.shared.messages.showVehicleMessage(_ROLE_EQUIPMENT_PROMOTED, {'name': equipment.userString})
            return
