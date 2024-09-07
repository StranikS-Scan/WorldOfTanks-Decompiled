# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/vehicle_preview/info/bottom_panel_early_access.py
from frameworks.wulf import ViewSettings, ViewFlags, ViewModel
from gui.Scaleform.daapi.view.meta.VehiclePreviewBottomPanelEarlyAccessMeta import VehiclePreviewBottomPanelEarlyAccessMeta
from gui.impl.gen import R
from gui.impl.gen.view_models.views.lobby.early_access.early_access_preview_bottom_panel_model import EarlyAccessPreviewBottomPanelModel
from gui.impl.lobby.early_access.tooltips.early_access_vehicle_locked_tooltip import EarlyAccessVehicleLockedTooltip
from gui.impl.pub import ViewImpl

class VehiclePreviewBottomPanelEarlyAccess(VehiclePreviewBottomPanelEarlyAccessMeta):

    def setIsBlockedVehicle(self, value):
        self.__view.setIsBlockedVehicle(value)

    def _makeInjectView(self, *args):
        self.__view = _EarlyAccessBottomPanelView()
        return self.__view


class _EarlyAccessBottomPanelView(ViewImpl):

    def __init__(self):
        settings = ViewSettings(R.views.lobby.vehicle_preview.buying_panel.EarlyAccessPanel())
        settings.flags = ViewFlags.VIEW
        settings.model = EarlyAccessPreviewBottomPanelModel()
        super(_EarlyAccessBottomPanelView, self).__init__(settings)
        self.__isBlockedVehicle = False

    @property
    def viewModel(self):
        return super(_EarlyAccessBottomPanelView, self).getViewModel()

    def createToolTipContent(self, event, contentID):
        if contentID == R.views.lobby.early_access.tooltips.EarlyAccessCommonDescriptionTooltip():
            return ViewImpl(ViewSettings(contentID, model=ViewModel()))
        return EarlyAccessVehicleLockedTooltip() if contentID == R.views.lobby.early_access.tooltips.EarlyAccessVehicleLockedTooltip() else super(_EarlyAccessBottomPanelView, self).createToolTipContent(event, contentID)

    def setIsBlockedVehicle(self, value):
        self.__isBlockedVehicle = value

    def _onLoaded(self, *args, **kwargs):
        self.viewModel.setIsBlockedVehicle(self.__isBlockedVehicle)
