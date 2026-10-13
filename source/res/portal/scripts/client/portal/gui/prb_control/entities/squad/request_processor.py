# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: portal/scripts/client/portal/gui/prb_control/entities/squad/request_processor.py
from gui.prb_control.entities.base.unit.requester import UnitRequestProcessor
from portal_common.portal_constants import CLIENT_UNIT_CMD

class PortalUnitRequestProcessor(UnitRequestProcessor):

    def doRequest(self, ctx, methodName, *args, **kwargs):
        if methodName == 'setVehicle':
            self.__setPortalVehicle(ctx, *args, **kwargs)
            return
        super(PortalUnitRequestProcessor, self).doRequest(ctx, methodName, *args, **kwargs)

    def __setPortalVehicle(self, ctx, *args, **kwargs):
        vehInvID = kwargs.pop('vehInvID', -1)
        setReady = int(kwargs.pop('setReady', False))
        self.doRequest(ctx, 'doUnitCmd', CLIENT_UNIT_CMD.SET_PORTAL_VEHICLE, vehInvID, setReady, '', **kwargs)
