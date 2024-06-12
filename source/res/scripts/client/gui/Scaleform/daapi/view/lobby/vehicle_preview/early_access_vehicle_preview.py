# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/vehicle_preview/early_access_vehicle_preview.py
from gui.Scaleform.daapi.settings.views import VIEW_ALIAS
from gui.Scaleform.daapi.view.lobby.vehicle_preview.sound_constants import RESEARCH_PREVIEW_SOUND_SPACE
from gui.Scaleform.daapi.view.lobby.vehicle_preview.vehicle_preview import VehiclePreview
from gui.impl import backport
from gui.impl.gen import R
from gui.impl.lobby.early_access.early_access_window_events import updateVisibilityHangarHeaderMenu, showEarlyAccessVehicleView
from gui.shared import event_dispatcher
from helpers import dependency
from skeletons.gui.game_control import IEarlyAccessController

class EarlyAccessVehiclePreview(VehiclePreview):
    _COMMON_SOUND_SPACE = RESEARCH_PREVIEW_SOUND_SPACE
    __BOTTOM_PANEL_FLASH_PATH = 'net.wg.gui.lobby.vehiclePreview.bottomPanel.VPBottomPanelEarlyAccess'
    __earlyAccessController = dependency.descriptor(IEarlyAccessController)

    def __init__(self, ctx=None):
        super(EarlyAccessVehiclePreview, self).__init__(ctx)
        self.__isFromVehicleView = ctx.get('isFromVehicleView', False)
        self._needToResetAppearance = True

    def setBottomPanel(self):
        self.as_setBottomPanelS(self.__BOTTOM_PANEL_FLASH_PATH)

    def _populate(self):
        super(EarlyAccessVehiclePreview, self)._populate()
        if self.__isFromVehicleView:
            updateVisibilityHangarHeaderMenu(isVisible=False)

    def _dispose(self):
        if self.__isFromVehicleView:
            updateVisibilityHangarHeaderMenu(isVisible=True)
        super(EarlyAccessVehiclePreview, self)._dispose()

    def _getData(self):
        result = super(EarlyAccessVehiclePreview, self)._getData()
        result['showCloseBtn'] = not self.__isFromVehicleView
        return result

    def _processBackClick(self, ctx=None):
        isPaused = self.__earlyAccessController.isPaused()
        if isPaused and (self.__isFromVehicleView or self._backAlias == VIEW_ALIAS.LOBBY_HANGAR):
            event_dispatcher.showHangar()
        elif self._backAlias == VIEW_ALIAS.LOBBY_HANGAR:
            self._needToResetAppearance = False
            showEarlyAccessVehicleView(selectedVehicleCD=self._vehicleCD)
        else:
            self._needToResetAppearance = not (self.__isFromVehicleView and self._previewBackCb is not None)
            super(EarlyAccessVehiclePreview, self)._processBackClick(ctx)
        return

    def _getBackBtnLabel(self):
        return backport.text(R.strings.early_access.vehiclePreview.backToVehicleScreen()) if (self.__isFromVehicleView or self._backAlias == VIEW_ALIAS.LOBBY_HANGAR) and not self.__earlyAccessController.isPaused() else super(EarlyAccessVehiclePreview, self)._getBackBtnLabel()

    def _getExitEvent(self):
        exitEvent = super(EarlyAccessVehiclePreview, self)._getExitEvent()
        exitEvent.ctx.update({'isFromVehicleView': self.__isFromVehicleView})
        return exitEvent
