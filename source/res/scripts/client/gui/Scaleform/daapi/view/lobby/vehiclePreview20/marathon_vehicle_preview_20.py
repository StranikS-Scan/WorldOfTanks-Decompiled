# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/vehiclePreview20/marathon_vehicle_preview_20.py
import typing
from gui.Scaleform.daapi.view.lobby.vehiclePreview20.vehicle_preview_20 import VehiclePreview20
from gui.server_events.events_dispatcher import showMissionsMarathon
from gui.impl import backport
from gui.impl.gen import R

class MarathonVehiclePreview20(VehiclePreview20):

    def __init__(self, ctx=None):
        super(MarathonVehiclePreview20, self).__init__(ctx)
        self._showBottomPanel = False

    def _processBackClick(self, ctx=None):
        showMissionsMarathon()

    def _getBackBtnLabel(self):
        return backport.text(R.strings.vehicle_preview.header.backBtn.descrLabel.marathon())
