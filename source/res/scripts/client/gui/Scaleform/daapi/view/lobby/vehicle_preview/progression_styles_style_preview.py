# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/vehicle_preview/progression_styles_style_preview.py
from gui.Scaleform.daapi.view.lobby.vehicle_preview.style_preview import VehicleStylePreview
from gui.Scaleform.genConsts.VEHPREVIEW_CONSTANTS import VEHPREVIEW_CONSTANTS

class ProgressionStylesStylePreview(VehicleStylePreview):

    def __init__(self, ctx=None):
        super(ProgressionStylesStylePreview, self).__init__(ctx)
        self.__styleLevel = ctx.get('styleLevel')

    def setBottomPanel(self, linkage=None):
        self.as_setBottomPanelS(linkage)

    def _onRegisterFlashComponent(self, viewPy, alias):
        super(ProgressionStylesStylePreview, self)._onRegisterFlashComponent(viewPy, alias)
        if alias == VEHPREVIEW_CONSTANTS.PROGRESSION_STYLES_BUYING_PANEL_PY_ALIAS:
            viewPy.setStyleLevel(self.__styleLevel)

    def _populate(self):
        self.setBottomPanel(VEHPREVIEW_CONSTANTS.PROGRESSION_STYLES_BUYING_PANEL_LINKAGE)
        super(ProgressionStylesStylePreview, self)._populate()
