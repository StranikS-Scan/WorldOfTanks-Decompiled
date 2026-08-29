# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: white_tiger/scripts/client/white_tiger/gui/Scaleform/daapi/view/battle/white_tiger/wt_vehicle_messages.py
from gui.Scaleform.daapi.view.battle.shared.messages import VehicleMessages
from gui.doc_loaders import messages_panel_reader
_VEHICLE_MESSAGES_FILE = 'gui/wt_vehicle_messages_panel.xml'

class WTVehicleMessages(VehicleMessages):

    def _populate(self):
        super(WTVehicleMessages, self)._populate()
        _, _, messages = messages_panel_reader.readXML(_VEHICLE_MESSAGES_FILE)
        self._messages.update(messages)

    def _addGameListeners(self):
        super(WTVehicleMessages, self)._addGameListeners()
        ctrl = self.sessionProvider.shared.equipments
        if ctrl is not None:
            ctrl.onEquipmentUpdated += self.__onEquipmentUpdated
        return

    def _removeGameListeners(self):
        ctrl = self.sessionProvider.shared.equipments
        if ctrl is not None:
            ctrl.onEquipmentUpdated -= self.__onEquipmentUpdated
        super(WTVehicleMessages, self)._removeGameListeners()
        return

    def __onEquipmentUpdated(self, _, item):
        if item is None:
            return
        else:
            postfix = ''
            if item.becomeActive:
                postfix = 'ACTIVATE'
            if postfix:
                self.showMessage(item.getDescriptor().name.upper(), {}, postfix=postfix)
            return
