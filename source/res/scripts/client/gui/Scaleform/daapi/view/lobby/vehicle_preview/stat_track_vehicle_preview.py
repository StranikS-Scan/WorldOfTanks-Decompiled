# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/vehicle_preview/stat_track_vehicle_preview.py
from gui.Scaleform.daapi.view.lobby.vehicle_preview.vehicle_preview import VehiclePreview
from gui.Scaleform.daapi.view.meta.VehiclePreviewBottomPanelStatTrackMeta import VehiclePreviewBottomPanelStatTrackMeta
from gui.Scaleform.genConsts.VEHPREVIEW_CONSTANTS import VEHPREVIEW_CONSTANTS
from gui.impl import backport
from gui.impl.gen import R

class StatTrackVehiclePreview(VehiclePreview):

    def setBottomPanel(self):
        self.as_setBottomPanelS(VEHPREVIEW_CONSTANTS.BOTTOM_PANEL_STAT_TRACK_LINKAGE)


class VehiclePreviewBottomPanelStatTrack(VehiclePreviewBottomPanelStatTrackMeta):

    def _populate(self):
        super(VehiclePreviewBottomPanelStatTrack, self)._populate()
        self.as_setDataS({'label': backport.text(R.strings.vehicle_preview.statTrackerPanel.label())})
