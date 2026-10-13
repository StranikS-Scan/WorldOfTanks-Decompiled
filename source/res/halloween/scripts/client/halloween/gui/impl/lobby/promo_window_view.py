# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: halloween/scripts/client/halloween/gui/impl/lobby/promo_window_view.py
from __future__ import absolute_import
from account_helpers import AccountSettings
from frameworks.wulf import ViewSettings, WindowFlags, ViewFlags, WindowLayer
from gui.impl.gen import R
from gui.impl.pub.lobby_window import LobbyNotificationWindow
from halloween.gui.impl.gen.view_models.views.lobby.promo_window_view_model import PromoWindowViewModel
from halloween.gui.impl.lobby.base_view import BaseView
from halloween.gui.halloween_account_settings import AccountSettingsKeys
from halloween.uilogging.loggers import HWMetricsLogger
from halloween.uilogging.logging_constants import HWLogKeys, HWLogActions
from helpers import dependency, int2roman
from halloween.skeletons.halloween_artefacts_controller import IHalloweenArtefactsController
from halloween.skeletons.halloween_controller import IHalloweenController

class PromoWindowView(BaseView):
    __hwArtefactsCtrl = dependency.descriptor(IHalloweenArtefactsController)
    __halloweenCtrl = dependency.descriptor(IHalloweenController)
    __slots__ = ()
    layoutID = R.views.halloween.mono.lobby.promo()

    def __init__(self, layoutID=None):
        settings = ViewSettings(layoutID or self.layoutID, ViewFlags.VIEW, PromoWindowViewModel())
        super(PromoWindowView, self).__init__(settings)
        self.__uiLogger = HWMetricsLogger(HWLogKeys.PROMO_VIEW)

    @property
    def isHiddenMenu(self):
        return self._hwController.isEventPrb()

    @property
    def viewModel(self):
        return super(PromoWindowView, self).getViewModel()

    def _onLoading(self, *args, **kwargs):
        super(PromoWindowView, self)._onLoading(*args, **kwargs)
        self.__uiLogger.onStartView(HWLogActions.LIFETIME)
        vehicle = self.__hwArtefactsCtrl.getMainGiftVehicle()
        with self.viewModel.transaction() as model:
            model.setStartDate(self.__halloweenCtrl.getModeSettings().startDate)
            model.setEndDate(self.__halloweenCtrl.getModeSettings().endDate)
            model.setRegularArtefactsLength(len(self.__hwArtefactsCtrl.regularArtefacts()))
        if vehicle:
            with self.viewModel.transaction() as vm:
                vm.setVehicleUserName(vehicle.userName)
                vm.setVehicleLevel(int2roman(vehicle.level))
                vm.setVehicleType(vehicle.type)
                vm.setVehicleIsPremium(vehicle.isPremium)

    def _subscribe(self):
        super(PromoWindowView, self)._subscribe()
        self.viewModel.onClose += self._onClose

    def _unsubscribe(self):
        super(PromoWindowView, self)._unsubscribe()
        self.viewModel.onClose -= self._onClose

    def _onClose(self):
        settings = AccountSettings.getSettings(AccountSettingsKeys.EVENT_KEY)
        settings[AccountSettingsKeys.PROMO_SCREEN_SHOWED] = True
        AccountSettings.setSettings(AccountSettingsKeys.EVENT_KEY, settings)
        self.destroyWindow()

    def _finalize(self):
        self.__uiLogger.onStopView(HWLogActions.LIFETIME)
        super(PromoWindowView, self)._finalize()


class PromoWindow(LobbyNotificationWindow):

    def __init__(self, layoutID, parent=None):
        super(PromoWindow, self).__init__(wndFlags=WindowFlags.WINDOW_FULLSCREEN | WindowFlags.WINDOW, content=PromoWindowView(layoutID=layoutID), parent=parent, layer=WindowLayer.TOP_WINDOW)
