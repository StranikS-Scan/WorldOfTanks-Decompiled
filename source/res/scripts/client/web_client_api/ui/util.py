# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/web_client_api/ui/util.py
from gui.Scaleform.daapi.view.lobby.vehiclePreview20.items_kit_helper import lookupItem, showItemTooltip, getCDFromId
from gui.app_loader import g_appLoader
from gui.shared.utils import showInvitationInWindowsBar
from gui.shared.event_dispatcher import runSalesChain
from helpers import time_utils
from helpers import dependency
from skeletons.gui.goodies import IGoodiesCache
from skeletons.gui.shared import IItemsCache
from web_client_api import w2c, W2CSchema, Field, WebCommandException
from web_client_api.common import ItemPackType, ItemPackEntry

def _itemTypeValidator(itemType):
    if not ItemPackType.hasValue(itemType):
        raise WebCommandException('unsupported item type "{}"'.format(itemType))
    return True


class _RunTriggerChainSchema(W2CSchema):
    trigger_chain_id = Field(required=True, type=basestring)


class _ShowCustomTooltipSchema(W2CSchema):
    header = Field(required=True, type=basestring)
    body = Field(required=True, type=basestring)


class _ShowItemTooltipSchema(W2CSchema):
    id = Field(required=True, type=(basestring, int))
    type = Field(required=True, type=basestring, validator=lambda value, data: _itemTypeValidator(value))
    count = Field(required=True, type=int)


class UtilWebApiMixin(object):
    itemsCache = dependency.descriptor(IItemsCache)
    goodiesCache = dependency.descriptor(IGoodiesCache)

    @w2c(W2CSchema, 'blink_taskbar')
    def blinkTaskbar(self, cmd):
        showInvitationInWindowsBar()

    @w2c(_RunTriggerChainSchema, 'run_trigger_chain')
    def runTriggerChain(self, cmd):
        chainID = cmd.trigger_chain_id
        runSalesChain(chainID)

    @w2c(_ShowItemTooltipSchema, 'show_item_tooltip')
    def showItemTooltip(self, cmd):
        itemType = cmd.type
        itemId = getCDFromId(itemType=cmd.type, itemId=cmd.id)
        itemsCount = cmd.count
        rawItem = ItemPackEntry(type=itemType, id=itemId, count=itemsCount)
        item = lookupItem(rawItem, self.itemsCache, self.goodiesCache)
        showItemTooltip(self.__getTooltipMgr(), rawItem, item)

    @w2c(_ShowCustomTooltipSchema, 'show_custom_tooltip')
    def showCustomTooltip(self, cmd):
        tooltip = '{{HEADER}}{header}{{/HEADER}}{{BODY}}{body}{{/BODY}}'.format(header=cmd.header, body=cmd.body)
        self.__getTooltipMgr().onCreateComplexTooltip(tooltip, 'INFO')

    @w2c(W2CSchema, 'hide_tooltip')
    def hideToolTip(self, cmd):
        self.__getTooltipMgr().hide()

    @w2c(W2CSchema, 'server_timestamp')
    def getCurrentLocalServerTimestamp(self, cmd):
        return time_utils.getCurrentLocalServerTimestamp()

    @staticmethod
    def __getTooltipMgr():
        return g_appLoader.getApp().getToolTipMgr()
