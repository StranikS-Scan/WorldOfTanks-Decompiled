# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/lunar_ny/envelopes/send_envelopes_view.py
from account_helpers import AccountSettings
from account_helpers.AccountSettings import LUNAR_NY_ENTITLEMENTS_VIEWED, LUNAR_NY_PROGRESSION_TOKENS_VIEWED
from gui.impl.gen import R
from gui.impl.gen.view_models.views.lobby.lunar_ny.main_view.send_envelopes.send_envelopes_model import SendEnvelopesModel
from gui.impl.lobby.lunar_ny.lunar_ny_base_main_view_component import BaseLunarNYViewComponent
from gui.impl.lobby.lunar_ny.lunar_ny_helpers import showEnvelopesSendView, createRewardTooltip
from gui.impl.lobby.lunar_ny.lunar_ny_model_helpers import fillEnvelopesProgressionModel
from gui.impl.lobby.lunar_ny.tooltips.envelope_tooltip import EnvelopeTooltip
from gui.impl.lobby.missions.daily_quests_view import DailyTabs
from gui.server_events.events_dispatcher import showDailyQuests
from gui.shared import g_eventBus
from gui.shared.events import OpenLinkEvent
from helpers import dependency
from lunar_ny import ILunarNYController
from lunar_ny.lunar_ny_constants import EnvelopeTypes
from lunar_ny.lunar_ny_sounds import LUNAR_NY_SEND_ENVELOPES_SOUND_SPACE
from skeletons.gui.lobby_context import ILobbyContext
from uilogging.lunar_ny.loggers import LunarBuyBtnLogger, LunarBuyAdditionalBtnLogger
_TYPE_PRIORITY = (EnvelopeTypes.PREMIUM_PAID, EnvelopeTypes.PAID, EnvelopeTypes.FREE)

class SendEnvelopesView(BaseLunarNYViewComponent[SendEnvelopesModel]):
    __slots__ = ('__toolTipsData',)
    __lunarNYController = dependency.descriptor(ILunarNYController)
    __lobbyContext = dependency.descriptor(ILobbyContext)
    _SOUND_SPACE_SETTINGS = LUNAR_NY_SEND_ENVELOPES_SOUND_SPACE

    def __init__(self, viewModel, view):
        super(SendEnvelopesView, self).__init__(viewModel, view)
        self.__toolTipsData = {}

    def setActive(self, isActive):
        super(SendEnvelopesView, self).setActive(isActive)
        with self._viewModel.transaction() as model:
            self.__updateCount(model=model)
            self.__toolTipsData.clear()
            fillEnvelopesProgressionModel(model.envelopesProgression, self.__lunarNYController.progression.getProgressionConfig(), self.__lunarNYController.progression.getSentEnvelopesCount(), withBonuses=True, tooltipsData=self.__toolTipsData)

    def createToolTipContent(self, event, contentID):
        tooltipData = self.__toolTipsData.get(event.getArgument('tooltipID'), None)
        if tooltipData is not None:
            return createRewardTooltip(contentID, tooltipData)
        elif contentID == R.views.lobby.lunar_ny.tooltips.EnvelopeTooltip():
            envelopeType = event.getArgument('envelopeType')
            return EnvelopeTooltip(envelopeType=envelopeType)
        else:
            return super(SendEnvelopesView, self).createToolTipContent(event, contentID)

    def onLoading(self, initCtx, isActive):
        super(SendEnvelopesView, self).onLoading(initCtx, isActive)
        self.__lunarNYController.giftSystem.onEnvelopesEntitlementUpdated += self.__onEnvelopesEntitlementUpdated
        self.__lunarNYController.progression.onProgressionUpdated += self.__onProgressionUpdated

    def finalize(self):
        super(SendEnvelopesView, self).finalize()
        self.__toolTipsData.clear()

    def _addListeners(self):
        self._viewModel.onQuestsClick += self.__showQuestView
        self._viewModel.onBuyClick += self.__showBuyView
        self._viewModel.onSendClick += self.__showEnvelopesSendView
        self._viewModel.onBuyInAdditionClick += self.__showExternalEventShop
        self._viewModel.envelopesProgression.onAnimationProgressionEnd += self.__onAnimationProgressionEnd

    def _removeListeners(self):
        self._viewModel.onBuyInAdditionClick -= self.__showExternalEventShop
        self._viewModel.onSendClick -= self.__showEnvelopesSendView
        self._viewModel.onBuyClick -= self.__showBuyView
        self._viewModel.onQuestsClick -= self.__showQuestView
        self._viewModel.envelopesProgression.onAnimationProgressionEnd -= self.__onAnimationProgressionEnd
        self.__lunarNYController.progression.onProgressionUpdated -= self.__onProgressionUpdated
        self.__lunarNYController.giftSystem.onEnvelopesEntitlementUpdated -= self.__onEnvelopesEntitlementUpdated

    def __onEnvelopesEntitlementUpdated(self):
        self.__updateCount(self._viewModel)

    def __updateCount(self, model):
        giftSystem = self.__lunarNYController.giftSystem
        model.setFreeCount(giftSystem.getEnvelopesEntitlementCountByType(EnvelopeTypes.FREE))
        model.setPaidCount(giftSystem.getEnvelopesEntitlementCountByType(EnvelopeTypes.PAID))
        model.setPremiumCount(giftSystem.getEnvelopesEntitlementCountByType(EnvelopeTypes.PREMIUM_PAID))
        AccountSettings.setSettings(LUNAR_NY_ENTITLEMENTS_VIEWED, giftSystem.getEnvelopesEntitlementCount())

    def __showQuestView(self):
        showDailyQuests(subTab=DailyTabs.QUESTS)

    def __showBuyView(self, args):
        g_eventBus.handleEvent(OpenLinkEvent(OpenLinkEvent.SPECIFIED, self.__lunarNYController.getEnvelopesExternalShopURL()))
        envelopeType = args.get('envelopeType')
        LunarBuyBtnLogger().logClick(envelopeType)

    def __showEnvelopesSendView(self, args=None):
        showEnvelopesSendView(args.get('envelopeType', None))
        return

    def __showExternalEventShop(self):
        g_eventBus.handleEvent(OpenLinkEvent(OpenLinkEvent.SPECIFIED, self.__lunarNYController.getEnvelopesExternalShopURL()))
        LunarBuyAdditionalBtnLogger().logClick()

    def __onProgressionUpdated(self):
        self.__toolTipsData.clear()
        fillEnvelopesProgressionModel(self._viewModel.envelopesProgression, self.__lunarNYController.progression.getProgressionConfig(), self.__lunarNYController.progression.getSentEnvelopesCount(), withBonuses=True, tooltipsData=self.__toolTipsData)

    def __onAnimationProgressionEnd(self):
        AccountSettings.setSettings(LUNAR_NY_PROGRESSION_TOKENS_VIEWED, self.__lunarNYController.progression.getSentEnvelopesCount())
