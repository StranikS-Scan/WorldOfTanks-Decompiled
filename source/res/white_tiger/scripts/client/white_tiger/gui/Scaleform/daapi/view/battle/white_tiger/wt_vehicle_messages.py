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
