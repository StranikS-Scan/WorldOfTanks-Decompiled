# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: white_tiger/scripts/client/white_tiger/gui/Scaleform/daapi/view/battle/white_tiger/wt_vehicle_errors.py
from gui.doc_loaders import messages_panel_reader
from constants import EQUIPMENT_STAGES
from gui.Scaleform.daapi.view.battle.shared.messages import VehicleErrorMessages
_VEHICLE_MESSAGES_FILE = 'gui/wt_vehicle_errors.xml'

class WTVehicleErrorMessages(VehicleErrorMessages):

    def __init__(self):
        super(WTVehicleErrorMessages, self).__init__()
        self.activeEquipments = None
        return

    def _populate(self):
        super(WTVehicleErrorMessages, self)._populate()
        _, _, messages = messages_panel_reader.readXML(_VEHICLE_MESSAGES_FILE)
        self._messages.update(messages)

    def _addGameListeners(self):
        super(WTVehicleErrorMessages, self)._addGameListeners()
        ctrl = self.sessionProvider.shared.equipments
        if ctrl is not None:
            ctrl.onEquipmentUpdated += self.__onEquipmentUpdated
        return

    def _removeGameListeners(self):
        ctrl = self.sessionProvider.shared.equipments
        if ctrl is not None:
            ctrl.onEquipmentUpdated -= self.__onEquipmentUpdated
        super(WTVehicleErrorMessages, self)._removeGameListeners()
        return

    def __onEquipmentUpdated(self, intCD, item):
        descriptor = item.getDescriptor()
        if 'lockShot' in descriptor.rawTags:
            if self.__isBarrier(descriptor, item) or self.__isMissile(descriptor, item):
                self.activeEquipments = item.getDescriptor().name
                self._keyReplacers['cantShootGunLocked'] = self.__replace
            else:
                self.activeEquipments = None
                self._keyReplacers.pop('cantShootGunLocked', None)
        return

    def __replace(self, key, args):
        return self.activeEquipments + '/' + key

    def __isBarrier(self, descriptor, item):
        return descriptor.name == 'wt_barrier' and item.getStage() == EQUIPMENT_STAGES.ACTIVE

    def __isMissile(self, descriptor, item):
        stage = item.getStage()
        return descriptor.name == 'wt_missile' and (stage == EQUIPMENT_STAGES.ACTIVE or stage == EQUIPMENT_STAGES.COOLDOWN)
