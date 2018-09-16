# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/web_client_api/ui/vehicle.py
from gui.shared import event_dispatcher
from gui.Scaleform.daapi.settings.views import VIEW_ALIAS
from helpers import dependency
from skeletons.gui.game_control import IVehicleComparisonBasket
from web_client_api import W2CSchema, Field, w2c

class _VehicleSchema(W2CSchema):
    vehicle_id = Field(required=True, type=int)


class _VehiclePreviewSchema(W2CSchema):
    vehicle_id = Field(required=True, type=int)
    back_url = Field(required=False, type=basestring)


class VehicleCompareWebApiMixin(object):
    comparisonBasket = dependency.descriptor(IVehicleComparisonBasket)

    @w2c(_VehicleSchema, 'vehicle_add_to_comparison')
    def addVehicleToCompare(self, cmd):
        self.comparisonBasket.addVehicle(cmd.vehicle_id)


class VehicleComparisonBasketWebApiMixin(object):

    @w2c(W2CSchema, 'comparison_basket')
    def openVehicleComparisonBasket(self, _):
        event_dispatcher.showVehicleCompare()


class VehiclePreviewWebApiMixin(object):

    @w2c(_VehiclePreviewSchema, 'vehicle_preview')
    def openVehiclePreview(self, cmd):
        event_dispatcher.showVehiclePreview(cmd.vehicle_id, previewAlias=self._getVehiclePreviewReturnAlias(cmd))

    def _getVehiclePreviewReturnAlias(self, cmd):
        return VIEW_ALIAS.LOBBY_HANGAR
