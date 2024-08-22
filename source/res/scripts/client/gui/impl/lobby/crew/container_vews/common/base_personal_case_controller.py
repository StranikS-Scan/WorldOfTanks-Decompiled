# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/crew/container_vews/common/base_personal_case_controller.py
import typing
from Event import Event
from gui.impl.dialogs.dialogs import showRetrainSingleDialog
from gui.impl.lobby.container_views.base.controllers import InteractionController
from gui.impl.lobby.crew.container_vews.common.base_personal_case_events import BasePersonalCaseComponentViewEvents
from gui.shared import event_dispatcher
from wg_async import wg_async, wg_await
if typing.TYPE_CHECKING:
    from typing import Callable, List, Tuple
    from gui.impl.lobby.container_views.base.components import ComponentBase
    from gui.impl.lobby.container_views.base.events import ComponentEventsBase

class BasePersonalCaseController(InteractionController):

    def _getEventsProvider(self):
        return BasePersonalCaseComponentViewEvents()

    def _getEvents(self):
        return [(self.eventsProvider.onChangeVehicleClick, self._onChangeVehicleClick), (self.eventsProvider.onRetrainClick, self._onRetrainClick)]

    def _onChangeVehicleClick(self, tankmanInvID):
        event_dispatcher.showTankChange(tankmanInvID=tankmanInvID, previousViewID=self.view.getParentView().currentTabId)

    @wg_async
    def _onRetrainClick(self, viewKey):
        currVehicle = self.context.tankmanCurrentVehicle
        nativeVehicle = self.context.tankmanNativeVehicle
        vehCD = currVehicle.intCD if currVehicle else nativeVehicle.intCD
        yield wg_await(showRetrainSingleDialog(self.context.tankmanID, vehCD, targetSlotIdx=self.context.tankman.vehicleSlotIdx if self.context.tankman.isInTank else None, parentViewKey=viewKey))
        return
