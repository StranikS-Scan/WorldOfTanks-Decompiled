# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: mt_birthday/scripts/client/mt_birthday/web/web_client_api/ticket_exchange/ticket_exchange.py
import logging
import typing
from gui.impl import backport
from gui.impl.gen import R
from helpers import dependency
from helpers.gui_utils import getMouseScreenPosition
from web.web_client_api import w2c, W2CSchema, w2capi, Field
from gui.Scaleform.daapi.settings.views import VIEW_ALIAS
from gui.Scaleform.genConsts.TOOLTIPS_CONSTANTS import TOOLTIPS_CONSTANTS
from gui.shared.event_dispatcher import showVehiclePreviewWithoutBottomPanel, showHangar, showStylePreview
from gui.shared.gui_items import GUI_ITEM_TYPE
from skeletons.gui.app_loader import IAppLoader
from skeletons.gui.shared import IItemsCache
from skeletons.gui.customization import ICustomizationService
from mt_birthday.skeletons.mt_birthday_controller import ITanksBirthdayController
from mt_birthday.gui.shared.event_dispatcher import showTicketExchange, closeBirthdayMainView
from web.web_client_api.common import ItemPackEntry, ItemPackType
if typing.TYPE_CHECKING:
    from gui.Scaleform.framework.entities.abstract.ToolTipMgrMeta import ToolTipMgrMeta
_logger = logging.getLogger(__name__)

class _VehiclePreviewSchema(W2CSchema):
    vehCD = Field(required=True, type=int)


class _StylePreviewSchema(W2CSchema):
    vehCD = Field(required=True, type=int)
    styleID = Field(required=True, type=int)


class TicketExchangeWebApiMixin(object):
    __tankBirthdayController = dependency.descriptor(ITanksBirthdayController)
    __itemsCache = dependency.descriptor(IItemsCache)
    __c11nService = dependency.descriptor(ICustomizationService)

    @w2c(_VehiclePreviewSchema, 'show_tank_preview')
    def openTankPreview(self, cmd):
        showVehiclePreviewWithoutBottomPanel(cmd.vehCD, backCallback=self.__getPreviewCallback, previewAlias=VIEW_ALIAS.VEHICLE_PREVIEW, backBtnLabel=self.__backBtnLabel, itemsPack=(ItemPackEntry(type=ItemPackType.CREW_100, groupID=1),))

    @w2c(_StylePreviewSchema, 'show_style_preview')
    def openStylePreview(self, cmd):
        style = self.__c11nService.getItemByID(GUI_ITEM_TYPE.STYLE, cmd.styleID)
        showStylePreview(cmd.vehCD, style, style.getDescription(), backCallback=self.__getPreviewCallback, backBtnDescrLabel=self.__backBtnLabel)

    @w2c(W2CSchema, 'show_golden_ticket_tooltip')
    def showLootboxGuaranteedRewardTooltip(self, cmd):
        self.__getTooltipMgr().onCreateWulfTooltip(TOOLTIPS_CONSTANTS.BIRTHDAY_GOLDEN_TICKET, [], *map(int, getMouseScreenPosition()))

    @w2c(W2CSchema, 'close_birthday_main_view')
    def closeBirthdayMainView(self, cmd):
        closeBirthdayMainView()

    @property
    def __backBtnLabel(self):
        return backport.text(R.strings.vehicle_preview.header.backBtn.descrLabel.ticketExchange())

    def __getPreviewCallback(self):
        if self.__tankBirthdayController.isEnabled() and self.__tankBirthdayController.isTicketExchangeEnabled:
            showTicketExchange()
        else:
            _logger.error("Ticket exchange event isn't enabled.")
            showHangar()

    def __getTooltipMgr(self):
        appLoader = dependency.instance(IAppLoader)
        return appLoader.getApp().getToolTipMgr()


@w2capi(name='ticket_exchange', key='action')
class TicketExchangeWebApi(TicketExchangeWebApiMixin):
    pass
