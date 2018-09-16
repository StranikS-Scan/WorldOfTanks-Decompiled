# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/web_client_api/ui/hangar.py
from gui.shared import event_dispatcher as shared_events
from web_client_api import W2CSchema, w2c, Field

class _OpenHangarTabSchema(W2CSchema):
    vehicle_id = Field(required=False, type=int)


class HangarTabWebApiMixin(object):

    @w2c(_OpenHangarTabSchema, 'hangar')
    def openHangar(self, cmd):
        if cmd.vehicle_id:
            shared_events.selectVehicleInHangar(cmd.vehicle_id)
        else:
            shared_events.showHangar()


class HangarWindowsWebApiMixin(object):

    @w2c(W2CSchema, 'show_currency_exchange_window')
    def openCurrencyExchangeWindow(self, _):
        shared_events.showExchangeCurrencyWindow()

    @w2c(W2CSchema, 'show_xp_exchange_window')
    def openXPExchangeWindow(self, _):
        shared_events.showExchangeXPWindow()
