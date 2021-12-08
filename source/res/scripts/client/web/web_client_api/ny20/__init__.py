# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/web/web_client_api/ny20/__init__.py
from gui.shared import event_dispatcher
from gui.shared.gui_items.loot_box import NewYearLootBoxes
from web.web_client_api import w2capi, W2CSchema, Field, w2c
from web.web_client_api.ui import ProfileTabWebApiMixin, VehiclePreviewWebApiMixin, TechTreeTabWebApiMixin, VehicleComparisonBasketWebApiMixin, MissionsWebApiMixin, BarracksWebApiMixin, ShopWebApiMixin, StorageWebApiMixin, PersonalMissionsWebApiMixin, StrongholdsWebApiMixin, BadgesWebApiMixin

class _OpenHangarTabSchema(W2CSchema):
    vehicle_id = Field(required=False, type=int)


class _OpenLootBoxViewSchema(W2CSchema):
    category = Field(required=False, type=basestring)


class LootBoxHangarTabWebApi(object):

    @w2c(_OpenHangarTabSchema, 'hangar')
    def openHangar(self, cmd):
        event_dispatcher.hideWebBrowserOverlay()
        if cmd.vehicle_id:
            event_dispatcher.selectVehicleInHangar(cmd.vehicle_id)
        else:
            event_dispatcher.showHangar()


@w2capi(name='open_tab', key='tab_id')
class LootBoxOpenTabWebApi(LootBoxHangarTabWebApi, ProfileTabWebApiMixin, VehiclePreviewWebApiMixin, TechTreeTabWebApiMixin, VehicleComparisonBasketWebApiMixin, MissionsWebApiMixin, BarracksWebApiMixin, ShopWebApiMixin, StorageWebApiMixin, StrongholdsWebApiMixin, PersonalMissionsWebApiMixin, BadgesWebApiMixin):
    pass


@w2capi(name='ny20', key='action')
class LootBoxWebApi(object):

    @w2c(_OpenLootBoxViewSchema, 'open_loot_box_view')
    def openLootBoxEntryView(self, cmd):
        event_dispatcher.showHangar()
        event_dispatcher.hideWebBrowserOverlay()
        event_dispatcher.showLootBoxEntry(NewYearLootBoxes.PREMIUM, cmd.category)
