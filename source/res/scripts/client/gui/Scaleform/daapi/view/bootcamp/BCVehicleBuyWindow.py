# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/bootcamp/BCVehicleBuyWindow.py
from gui.Scaleform.daapi.view.lobby.vehicle_obtain_windows import VehicleBuyWindow
from gui.Scaleform.daapi.settings.views import VIEW_ALIAS
from gui.Scaleform.genConsts.VEHICLE_BUY_WINDOW_ALIASES import VEHICLE_BUY_WINDOW_ALIASES
from bootcamp.BootcampGarage import g_bootcampGarage

class BCVehicleBuyWindow(VehicleBuyWindow):

    @property
    def buyComponent(self):
        return self.getComponent(VIEW_ALIAS.BOOTCAMP_VEHICLE_BUY_VIEW)

    def onWindowClose(self):
        super(BCVehicleBuyWindow, self).onWindowClose()
        g_bootcampGarage.runViewAlias('vehiclePreview')

    def _onRegisterFlashComponent(self, viewPy, alias):
        super(BCVehicleBuyWindow, self)._onRegisterFlashComponent(viewPy, alias)
        if alias == VIEW_ALIAS.BOOTCAMP_VEHICLE_BUY_VIEW:
            viewPy.onAcademyClicked += self.__onAcademyClick

    def _onUnregisterFlashComponent(self, viewPy, alias):
        if alias == VIEW_ALIAS.BOOTCAMP_VEHICLE_BUY_VIEW:
            viewPy.onAcademyClicked -= self.__onAcademyClick
        super(BCVehicleBuyWindow, self)._onUnregisterFlashComponent(viewPy, alias)

    def _populate(self):
        super(BCVehicleBuyWindow, self)._populate()
        self.as_setEnabledSubmitBtnS(False)

    def _getContentLinkageFields(self):
        return {'contentLinkage': VEHICLE_BUY_WINDOW_ALIASES.CONTENT_BUY_BOOTCAMP_VIEW_UI,
         'isContentDAAPI': True,
         'contentAlias': VIEW_ALIAS.BOOTCAMP_VEHICLE_BUY_VIEW}

    def __onAcademyClick(self):
        self.as_setEnabledSubmitBtnS(True)
        g_bootcampGarage.hidePrevShowNextHint()
