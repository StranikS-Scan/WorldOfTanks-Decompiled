# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/hangar/event/event_vehicle_confirmation.py
from gui import SystemMessages
from gui.Scaleform.daapi.view.lobby.hangar.event.event_confirmation import EventConfirmationView
from gui.server_events.game_event.vehicles_controller import VehicleItemBuyer
from gui.shared.utils import decorators
from gui.shared.view_helpers.blur_manager import CachedBlur

class EventBuyVehicleConfirmationView(EventConfirmationView):

    def __init__(self, *args, **kwargs):
        super(EventBuyVehicleConfirmationView, self).__init__(*args, **kwargs)
        self.__blur = None
        return

    def setParentWindow(self, window):
        super(EventBuyVehicleConfirmationView, self).setParentWindow(window)
        self.__blur = CachedBlur(enabled=True, ownLayer=window.layer, blurAnimRepeatCount=1)

    def onCancelClick(self):
        self.destroy()

    def onBuyClick(self):
        self.__buyVehicle()

    def _dispose(self):
        super(EventBuyVehicleConfirmationView, self)._dispose()
        self.__blur.fini()
        self.__blur = None
        return

    @decorators.process('updating')
    def __buyVehicle(self):
        ctx = self._ctx
        currency, price = ctx['currency'], ctx['price']
        vehTypeCompDescr = ctx['vehTypeCompDescr']
        result = yield VehicleItemBuyer(vehTypeCompDescr, currency, price).request()
        if result.userMsg:
            SystemMessages.pushMessage(result.userMsg, type=result.sysMsgType)
        self.destroy()
