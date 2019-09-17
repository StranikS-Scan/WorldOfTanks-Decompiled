# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/web_client_api/festival/shared.py
from gui.shared import event_dispatcher as shared_events
from web_client_api import w2c, W2CSchema, Field

class _OpenHangarTabSchema(W2CSchema):
    vehicle_id = Field(required=False, type=int)


class HangarTabWebApiMixin(object):

    @w2c(_OpenHangarTabSchema, 'hangar')
    def openHangar(self, cmd):
        shared_events.hideWebBrowserOverlay()
        if cmd.vehicle_id:
            shared_events.selectVehicleInHangar(cmd.vehicle_id)
        else:
            shared_events.showHangar()
