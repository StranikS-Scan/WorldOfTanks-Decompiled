# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/vehicle_preview/style_progression_preview.py
from gui.Scaleform.daapi.view.lobby.vehicle_preview.style_preview import VehicleStylePreview
from gui.Scaleform.genConsts.VEHPREVIEW_CONSTANTS import VEHPREVIEW_CONSTANTS

class VehicleStyleProgressionPreview(VehicleStylePreview):

    def __init__(self, ctx=None):
        super(VehicleStyleProgressionPreview, self).__init__(ctx)
        self.__styleLevel = ctx.get('styleLevel')
        self.__isShowCloseBtn = ctx.get('showCloseBtn', False)
        self.__availableLevel = self.__getAvailableLevel(ctx)
        self.__ctx = ctx

    def setBottomPanel(self, linkage=None):
        self.as_setBottomPanelS(linkage)

    def registerFlashComponent(self, component, alias, *args):
        if alias == VEHPREVIEW_CONSTANTS.BOTTOM_PANEL_STYLE_PROGRESSION_PY_ALIAS:
            super(VehicleStyleProgressionPreview, self).registerFlashComponent(component, alias, self.__ctx)

    def _onRegisterFlashComponent(self, viewPy, alias):
        super(VehicleStyleProgressionPreview, self)._onRegisterFlashComponent(viewPy, alias)
        if alias == VEHPREVIEW_CONSTANTS.BOTTOM_PANEL_STYLE_PROGRESSION_PY_ALIAS:
            viewPy.setStyleLevel(self.__styleLevel)
            viewPy.setAvailableLevel(self.__availableLevel)
            viewPy.setCtx(self.__ctx)

    def _populate(self):
        self.setBottomPanel(VEHPREVIEW_CONSTANTS.BOTTOM_PANEL_STYLE_PROGRESSION_LINKAGE)
        super(VehicleStyleProgressionPreview, self)._populate()

    def _getData(self):
        result = super(VehicleStyleProgressionPreview, self)._getData()
        result['showCloseBtn'] = self.__isShowCloseBtn
        return result

    def __getAvailableLevel(self, ctx):
        style = ctx['style']
        return ctx.get('availableLevel', self.__styleLevel) if style.isQuestsProgression else style.getProgressionLevel()
