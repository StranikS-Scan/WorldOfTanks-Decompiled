# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: halloween/scripts/client/halloween/gui/Scaleform/daapi/view/battle/messages/vehicle_errors.py
from gui.doc_loaders import messages_panel_reader
from gui.Scaleform.daapi.view.battle.shared.messages import VehicleErrorMessages

class HalloweenVehicleErrorMessages(VehicleErrorMessages):
    HW_XML_PATH = 'halloween/gui/vehicle_errors_panel.xml'

    def _populate(self):
        super(HalloweenVehicleErrorMessages, self)._populate()
        _, _, messages = messages_panel_reader.readXML(self.HW_XML_PATH)
        self._messages.update(messages)
