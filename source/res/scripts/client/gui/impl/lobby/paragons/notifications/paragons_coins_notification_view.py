# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/paragons/notifications/paragons_coins_notification_view.py
from CurrentVehicle import g_currentVehicle
from gui.impl.gen.view_models.views.lobby.paragons.navigation_view_model import TabId
from gui.impl.gen.view_models.views.lobby.paragons.notifications.paragons_coins_notification_view_model import ParagonsCoinsNotificationViewModel
from gui.impl.lobby.gf_notifications.notification_base import NotificationBase
from gui.impl.lobby.paragons.paragons_window_events import showParagonsNavigationView
from gui.impl.wrappers.function_helpers import replaceNoneKwargsModel
from gui.shared import event_dispatcher as shared_events
from helpers import dependency
from skeletons.gui.game_control import IParagonsController

class ParagonsCoinsNotification(NotificationBase):
    __slots__ = ()
    __paragonsController = dependency.descriptor(IParagonsController)

    def __init__(self, resId, *args, **kwargs):
        model = ParagonsCoinsNotificationViewModel()
        super(ParagonsCoinsNotification, self).__init__(resId, model, *args, **kwargs)

    @property
    def viewModel(self):
        return super(ParagonsCoinsNotification, self).getViewModel()

    def _onLoading(self, *args, **kwargs):
        super(ParagonsCoinsNotification, self)._onLoading(*args, **kwargs)
        with self.viewModel.transaction() as model:
            model.setIsPopUp(self._isPopUp)
            model.setMinVehicleCount(self.__paragonsController.minUnlockedNecessaryLevelVehiclesCount)
            self._updateCount(model=model)
            self._updateAvailability(model=model)

    def _getEvents(self):
        return ((self.viewModel.goToParagons, self.__goToParagons), (self.viewModel.goToTechTree, self.__goToTechTree))

    @replaceNoneKwargsModel
    def _updateCount(self, model=None):
        model.setCount(self._linkageData.toDict().get('count', 0))

    @replaceNoneKwargsModel
    def _updateAvailability(self, model=None):
        model.setIsEntryPointAvailable(self._linkageData.toDict().get('isParagonsEntryPointAvailable', False))

    def __goToParagons(self):
        if self._canNavigate():
            showParagonsNavigationView(tabId=TabId.CHAPTERS)

    def __goToTechTree(self):
        if self._canNavigate() and g_currentVehicle.isPresent():
            shared_events.showVehicleTechTreeView(g_currentVehicle.item.intCD)
