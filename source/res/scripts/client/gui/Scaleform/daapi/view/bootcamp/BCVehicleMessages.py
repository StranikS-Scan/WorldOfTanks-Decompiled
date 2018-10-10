# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/bootcamp/BCVehicleMessages.py
from gui.Scaleform.daapi.view.battle.shared import messages
_VEHICLE_MESSAGES_FILE = 'bc_vehicle_messages_panel.xml'

class BCVehicleMessages(messages.VehicleMessages):

    def __init__(self):
        super(BCVehicleMessages, self).__init__()
        self.setSettingFile(_VEHICLE_MESSAGES_FILE)
