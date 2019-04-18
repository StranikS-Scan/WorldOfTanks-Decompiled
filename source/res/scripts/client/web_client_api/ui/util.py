# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/web_client_api/ui/util.py
from account_helpers import AccountSettings
from account_helpers.AccountSettings import NEW_LOBBY_TAB_COUNTER
from dossiers2.ui.achievements import ACHIEVEMENT_BLOCK
from gui.Scaleform.daapi.settings.views import VIEW_ALIAS
from gui.Scaleform.daapi.view.lobby.header.LobbyHeader import HEADER_BUTTONS_COUNTERS_CHANGED_EVENT
from gui.Scaleform.daapi.view.lobby.vehiclePreview20.items_kit_helper import lookupItem, showItemTooltip, getCDFromId
from gui.Scaleform.genConsts.TOOLTIPS_CONSTANTS import TOOLTIPS_CONSTANTS as TC
from gui.shared import g_eventBus
from gui.shared.events import HasCtxEvent
from gui.shared.gui_items.dossier import dumpDossier
from gui.shared.gui_items.dossier.achievements.abstract import isRareAchievement
from gui.shared.utils import showInvitationInWindowsBar
from gui.shared.event_dispatcher import runSalesChain
from gui.shared.view_helpers import UsersInfoHelper
from gui.shared.utils.functions import makeTooltip
from helpers import time_utils
from helpers import dependency
from messenger.storage import storage_getter
from skeletons.gui.app_loader import IAppLoader
from skeletons.gui.goodies import IGoodiesCache
from skeletons.gui.shared import IItemsCache
from web_client_api import w2c, W2CSchema, Field, WebCommandException
from web_client_api.common import ItemPackType, ItemPackEntry
_COUNTER_IDS_MAP = {'shop': VIEW_ALIAS.LOBBY_STORE}

def _itemTypeValidator(itemType, _=None):
    if not ItemPackType.hasValue(itemType):
        raise WebCommandException('unsupported item type "{}"'.format(itemType))
    return True


def _counterIdValidator(counterId, _=None):
    if counterId not in _COUNTER_IDS_MAP:
        raise WebCommandException('unsupported counter id "{}"'.format(counterId))
    return True


def _counterIdsValidator(idList, _=None):
    return all((_counterIdValidator(id) for id in idList))


class _SetCounterSchema(W2CSchema):
    id = Field(required=True, type=basestring, validator=_counterIdValidator)
    value = Field(required=True, type=(int, basestring))


class _GetCountersSchema(W2CSchema):
    id_list = Field(required=False, type=list, validator=_counterIdsValidator)


class _RunTriggerChainSchema(W2CSchema):
    trigger_chain_id = Field(required=True, type=basestring)


class _ShowToolTipSchema(W2CSchema):
    tooltipType = Field(required=True, type=basestring)
    itemId = Field(required=True, type=(int, basestring))
    blockId = Field(type=basestring, validator=lambda value, _: value in ACHIEVEMENT_BLOCK.ALL)


class _ShowCustomTooltipSchema(W2CSchema):
    header = Field(required=True, type=basestring)
    body = Field(required=True, type=basestring)


class _ShowItemTooltipSchema(W2CSchema):
    id = Field(required=True, type=(basestring, int))
    type = Field(required=True, type=basestring, validator=_itemTypeValidator)
    count = Field(required=True, type=int)


class _ChatAvailabilitySchema(W2CSchema):
    receiver_id = Field(required=True, type=long)


class UtilWebApiMixin(object):
    itemsCache = dependency.descriptor(IItemsCache)
    goodiesCache = dependency.descriptor(IGoodiesCache)

    def __init__(self):
        super(UtilWebApiMixin, self).__init__()
        self.__usersInfoHelper = UsersInfoHelper()

    @w2c(_SetCounterSchema, 'set_counter')
    def setCounterState(self, cmd):
        alias = _COUNTER_IDS_MAP.get(cmd.id)
        if alias is not None:
            g_eventBus.handleEvent(HasCtxEvent(eventType=HEADER_BUTTONS_COUNTERS_CHANGED_EVENT, ctx={'alias': alias,
             'value': cmd.value or ''}))
        return

    @w2c(_GetCountersSchema, 'get_counters')
    def getCountersInfo(self, cmd):
        ids = cmd.id_list or _COUNTER_IDS_MAP.keys()
        counters = AccountSettings.getCounters(NEW_LOBBY_TAB_COUNTER)
        return {id:counters.get(_COUNTER_IDS_MAP[id]) for id in ids if id in _COUNTER_IDS_MAP}

    @w2c(W2CSchema, 'blink_taskbar')
    def blinkTaskbar(self, _):
        showInvitationInWindowsBar()

    @w2c(_RunTriggerChainSchema, 'run_trigger_chain')
    def runTriggerChain(self, cmd):
        chainID = cmd.trigger_chain_id
        runSalesChain(chainID)

    @w2c(_ShowToolTipSchema, 'show_tooltip')
    def showTooltip(self, cmd):
        tooltipType = cmd.tooltipType
        itemId = cmd.itemId
        args = []
        withLongIntArgs = (TC.AWARD_SHELL,)
        withLongBoolArgs = (TC.TECH_CUSTOMIZATION_ITEM, TC.TECH_CUSTOMIZATION_HISTORIC_ITEM)
        withLongOnlyArgs = (TC.AWARD_VEHICLE,
         TC.AWARD_MODULE,
         TC.INVENTORY_BATTLE_BOOSTER,
         TC.BOOSTERS_BOOSTER_INFO,
         TC.BADGE)
        if tooltipType in withLongIntArgs:
            args = [itemId, 0]
        elif tooltipType in withLongBoolArgs:
            args = [itemId, False]
        elif tooltipType in withLongOnlyArgs:
            args = [itemId]
        elif tooltipType == TC.ACHIEVEMENT:
            dossier = self.itemsCache.items.getAccountDossier()
            dossierCompDescr = dumpDossier(self.itemsCache.items.getAccountDossier())
            achievement = dossier.getTotalStats().getAchievement((cmd.blockId, itemId))
            args = [dossier.getDossierType(),
             dossierCompDescr,
             achievement.getBlock(),
             cmd.itemId,
             isRareAchievement(achievement)]
        self.__getTooltipMgr().onCreateTypedTooltip(tooltipType, args, 'INFO')

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
        self.__getTooltipMgr().onCreateComplexTooltip(makeTooltip(header=cmd.header, body=cmd.body), 'INFO')

    @w2c(W2CSchema, 'hide_tooltip')
    def hideToolTip(self, _):
        self.__getTooltipMgr().hide()

    @w2c(W2CSchema, 'server_timestamp')
    def getCurrentLocalServerTimestamp(self, _):
        return time_utils.getCurrentLocalServerTimestamp()

    @storage_getter('users')
    def usersStorage(self):
        return None

    @w2c(_ChatAvailabilitySchema, 'check_if_chat_available')
    def checkIfChatAvailable(self, cmd, ctx):
        callback = ctx.get('callback')
        receiverId = cmd.receiver_id

        def isAvailable():
            receiver = self.__usersInfoHelper.getContact(receiverId)
            return receiver.hasValidName() and not receiver.isIgnored()

        def onNamesReceivedCallback():
            callback(isAvailable())

        if not bool(self.__usersInfoHelper.getUserName(receiverId)):
            self.__usersInfoHelper.onNamesReceived += onNamesReceivedCallback
            self.__usersInfoHelper.syncUsersInfo()
        else:
            return isAvailable()

    def __getTooltipMgr(self):
        appLoader = dependency.instance(IAppLoader)
        return appLoader.getApp().getToolTipMgr()
