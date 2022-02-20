# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/lunar_ny/popovers/entry_point_popover.py
import typing
import logging
from adisp import process
from constants import Configs
from frameworks.wulf import ViewSettings
from gui.impl.gen import R
from gui.impl.gen.view_models.views.lobby.lunar_ny.envelopes_popover_model import EnvelopesPopoverModel
from gui.impl.lobby.lunar_ny.lunar_ny_helpers import showEnvelopesSendView
from gui.impl.lobby.missions.daily_quests_view import DailyTabs
from gui.impl.pub.view_impl import PopOverViewImpl
from gui.impl.wrappers.function_helpers import replaceNoneKwargsModel
from gui.server_events.events_dispatcher import showDailyQuests
from gui.shared import g_eventBus
from gui.shared.events import OpenLinkEvent
from helpers import dependency
from lunar_ny import ILunarNYController
from lunar_ny.lunar_ny_constants import EnvelopeTypes
from skeletons.gui.lobby_context import ILobbyContext
from uilogging.lunar_ny.loggers import LunarPopoverBuyBtnLogger, LunarPopoverSendBtn
_logger = logging.getLogger(__name__)

class EnvelopesPopover(PopOverViewImpl):
    __slots__ = ()
    __lunarNYController = dependency.descriptor(ILunarNYController)
    __lobbyContext = dependency.descriptor(ILobbyContext)

    def __init__(self):
        settings = ViewSettings(layoutID=R.views.lobby.lunar_ny.popovers.LunarNyPopover(), model=EnvelopesPopoverModel())
        super(EnvelopesPopover, self).__init__(settings)

    @property
    def viewModel(self):
        return self.getViewModel()

    def _onLoading(self, *args, **kwargs):
        super(EnvelopesPopover, self)._onLoading(*args, **kwargs)
        self.__lobbyContext.getServerSettings().onServerSettingsChange += self.__onServerSettingChanged
        self.__lunarNYController.giftSystem.onEnvelopesEntitlementUpdated += self.__onEnvelopesEntitlementUpdated
        self.viewModel.onSendClick += self.__showEnvelopesSendView
        self.viewModel.onBuyClick += self.__showBuyView
        self.viewModel.onQuestsClick += self.__showQuestsView
        with self.viewModel.transaction() as model:
            self.__updateCount(model=model)
            self.__updateEnvelopesEnabledFlags(model=model)

    def _finalize(self):
        self.viewModel.onSendClick -= self.__showEnvelopesSendView
        self.viewModel.onBuyClick -= self.__showBuyView
        self.viewModel.onQuestsClick -= self.__showQuestsView
        self.__lunarNYController.giftSystem.onEnvelopesEntitlementUpdated -= self.__onEnvelopesEntitlementUpdated
        self.__lobbyContext.getServerSettings().onServerSettingsChange -= self.__onServerSettingChanged
        super(EnvelopesPopover, self)._finalize()

    def __getIsEnvelopeEnabledByType(self, envelopeType):
        isDisabledGiftForSendById = self.__lunarNYController.giftSystem.isDisabledGiftForSendById
        receivedEnvelopes = self.__lunarNYController.receivedEnvelopes
        lootbox = receivedEnvelopes.getLootBoxByEnvelopeType(envelopeType)
        return lootbox is not None and not isDisabledGiftForSendById(lootbox.getID())

    def __onServerSettingChanged(self, diff):
        if {Configs.LUNAR_NY_EVENT_CONFIG.value, Configs.GIFTS_CONFIG.value}.intersection(diff):
            giftSystem = self.__lunarNYController.giftSystem
            if self.__lunarNYController.isActive() and giftSystem.isGiftEventActive():
                self.__updateEnvelopesEnabledFlags()
            else:
                self.destroy()

    @replaceNoneKwargsModel
    def __updateCount(self, model=None):
        giftSystem = self.__lunarNYController.giftSystem
        model.setFreeCount(giftSystem.getEnvelopesEntitlementCountByType(EnvelopeTypes.FREE))
        model.setPaidCount(giftSystem.getEnvelopesEntitlementCountByType(EnvelopeTypes.PAID))
        model.setPremiumCount(giftSystem.getEnvelopesEntitlementCountByType(EnvelopeTypes.PREMIUM_PAID))

    @replaceNoneKwargsModel
    def __updateEnvelopesEnabledFlags(self, model=None):
        model.setGiftSystemIsEnabled(self.__lunarNYController.isGiftSystemEventActive())
        model.setFreeIsEnabled(self.__getIsEnvelopeEnabledByType(EnvelopeTypes.FREE))
        model.setPaidIsEnabled(self.__getIsEnvelopeEnabledByType(EnvelopeTypes.PAID))
        model.setPremiumIsEnabled(self.__getIsEnvelopeEnabledByType(EnvelopeTypes.PREMIUM_PAID))

    def __showEnvelopesSendView(self, args):
        envelopeType = args.get('envelopeType', None)
        if envelopeType is not None:
            showEnvelopesSendView(EnvelopeTypes(envelopeType))
            LunarPopoverSendBtn().logSendBtnClick(envelopeType)
        else:
            _logger.warning('Argument "envelopeType" doesn\'t exist')
        return

    @process
    def __showBuyView(self, args):
        url = yield self.__lunarNYController.getEnvelopesExternalShopURL()
        g_eventBus.handleEvent(OpenLinkEvent(OpenLinkEvent.SPECIFIED, url))
        self.destroyWindow()
        envelopeType = args.get('envelopeType', None)
        LunarPopoverBuyBtnLogger().logBuyBtnClick(envelopeType)
        return

    def __showQuestsView(self):
        showDailyQuests(subTab=DailyTabs.QUESTS)

    def __onEnvelopesEntitlementUpdated(self):
        self.__updateCount()
