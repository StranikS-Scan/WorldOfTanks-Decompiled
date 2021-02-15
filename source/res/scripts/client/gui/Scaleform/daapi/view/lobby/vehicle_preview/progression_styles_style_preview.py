# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/vehicle_preview/progression_styles_style_preview.py
from gui.Scaleform.daapi.view.lobby.vehicle_preview.style_preview import VehicleStylePreview
from gui.Scaleform.genConsts.VEHPREVIEW_CONSTANTS import VEHPREVIEW_CONSTANTS

class ProgressionStylesStylePreview(VehicleStylePreview):

    def setBottomPanel(self, linkage=None):
        self.as_setBottomPanelS(linkage)

    def _populate(self):
        self.setBottomPanel(VEHPREVIEW_CONSTANTS.PROGRESSION_STYLES_BUYING_PANEL_LINKAGE)
        super(ProgressionStylesStylePreview, self)._populate()
