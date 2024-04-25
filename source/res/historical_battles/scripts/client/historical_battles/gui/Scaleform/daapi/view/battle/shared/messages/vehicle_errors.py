# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: historical_battles/scripts/client/historical_battles/gui/Scaleform/daapi/view/battle/shared/messages/vehicle_errors.py
from gui.doc_loaders import messages_panel_reader
from gui.Scaleform.daapi.view.battle.shared.messages import vehicle_errors
_HB_VEHICLE_ERROR_MESSAGES_PATH = 'historical_battles/gui/vehicle_errors_panel.xml'

class HistoricalBattlesVehicleErrorMessages(vehicle_errors.VehicleErrorMessages):

    def _populate(self):
        super(HistoricalBattlesVehicleErrorMessages, self)._populate()
        _, _, messages = messages_panel_reader.readXML(_HB_VEHICLE_ERROR_MESSAGES_PATH)
        self._messages.update(messages)
