# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/account_dashboard/features/header_feature.py
import logging
import typing
import BigWorld
from WeakMethod import WeakMethodProxy
from constants import QUEUE_TYPE
from gui.ClientUpdateManager import g_clientUpdateManager
from gui.clans.settings import getClanRoleName
from gui.impl import backport
from gui.impl.dialogs import dialogs
from gui.impl.dialogs.gf_builders import ResDialogBuilder
from gui.impl.gen import R
from gui.impl.gen.view_models.views.lobby.account_dashboard.header_model import AccountInfoStateEnum
from gui.impl.lobby.account_completion.tooltips.hangar_tooltip_view import HangarTooltipView
from gui.impl.lobby.account_dashboard.features.base import FeatureItem
from gui.impl.lobby.tooltips.clans import ClanShortInfoTooltipContent
from gui.impl.pub.dialog_window import DialogButtons
from gui.impl.wrappers.function_helpers import replaceNoneKwargsModel
from gui.platform.base.statuses.constants import StatusTypes
from gui.platform.wgnp.demo_account.controller import NICKNAME_CONTEXT
from gui.prb_control.ctrl_events import g_prbCtrlEvents
from gui.prb_control.dispatcher import g_prbLoader
from gui.shared import event_dispatcher
from gui.shared.event_dispatcher import showDemoAccRenamingOverlay, showSteamConfirmEmailOverlay, showSteamAddEmailOverlay
from gui.shared.view_helpers.emblems import EmblemSize, getClanEmblemURL
from helpers import dependency
from skeletons.gui.game_control import IBadgesController, ISteamCompletionController, IPlatoonController
from skeletons.gui.platform.wgnp_controllers import IWGNPSteamAccRequestController, IWGNPDemoAccRequestController
from skeletons.gui.shared import IItemsCache
from skeletons.gui.web import IWebController
from wg_async import wg_async, wg_await
if typing.TYPE_CHECKING:
    from typing import Optional
    from gui.impl.gen.view_models.views.lobby.account_dashboard.header_model import HeaderModel
    from gui.platform.wgnp.steam_account.statuses import SteamAccEmailStatus
    from gui.platform.base.statuses.status import Status
    from gui.impl.gen.view_models.views.lobby.account_dashboard.account_dashboard_model import AccountDashboardModel
_logger = logging.getLogger(__name__)

class HeaderFeature(FeatureItem):
    __itemsCache = dependency.descriptor(IItemsCache)
    __webCtrl = dependency.descriptor(IWebController)
    __badgesController = dependency.descriptor(IBadgesController)
    __wgnpSteamAccCtrl = dependency.descriptor(IWGNPSteamAccRequestController)
    __wgnpDemoAccCtrl = dependency.descriptor(IWGNPDemoAccRequestController)
    __steamRegistrationCtrl = dependency.descriptor(ISteamCompletionController)
    __platoonCtrl = dependency.descriptor(IPlatoonController)

    def __init__(self, viewModel):
        super(HeaderFeature, self).__init__(viewModel)
        self.__notConfirmedEmail = ''
        self.__isDestroyed = False
        self.__confirmationWindow = None
        self._tooltipModelFactories = {R.views.lobby.tooltips.clans.ClanShortInfoTooltipContent(): ClanShortInfoTooltipContent,
         R.views.lobby.account_completion.tooltips.HangarTooltip(): WeakMethodProxy(self.__createHangarTooltipView)}
        return

    def initialize(self, *args, **kwargs):
        super(HeaderFeature, self).initialize(*args, **kwargs)
        self._viewModel.header.onShowBadges += self.__onShowBadges
        self._viewModel.header.onAccountInfoButtonClick += self.__onAccountInfoButtonClick
        self.__badgesController.onUpdated += self.__onBadgesChanged
        g_clientUpdateManager.addCallbacks({'stats.clanInfo': self.__onClanInfoChanged,
         'cache.activeOrders': self.__onClanInfoChanged})
        g_prbCtrlEvents.onPreQueueJoined += self.__onPreQueueJoined
        self.__wgnpSteamAccCtrl.statusEvents.subscribe(StatusTypes.CONFIRMED, self._setEmailConfirmed)
        self.__wgnpSteamAccCtrl.statusEvents.subscribe(StatusTypes.ADDED, self._setEmailActionNeeded)
        self.__wgnpSteamAccCtrl.statusEvents.subscribe(StatusTypes.ADD_NEEDED, self._setEmailActionNeeded)
        demoAccSubscribe = self.__wgnpDemoAccCtrl.statusEvents.subscribe
        demoAccSubscribe(StatusTypes.ADD_NEEDED, self._showDemoAccountRenaming, context=NICKNAME_CONTEXT)
        demoAccSubscribe(StatusTypes.PROCESSING, self._showDemoAccountRenamingInProcess, context=NICKNAME_CONTEXT)
        demoAccSubscribe(StatusTypes.ADDED, self._hideDemoAccountRenaming, context=NICKNAME_CONTEXT)
        demoAccSubscribe(StatusTypes.UNDEFINED, self._hideDemoAccountRenaming, context=NICKNAME_CONTEXT)

    def finalize(self):
        self.__isDestroyed = True
        self._viewModel.header.onShowBadges -= self.__onShowBadges
        self._viewModel.header.onAccountInfoButtonClick -= self.__onAccountInfoButtonClick
        self.__badgesController.onUpdated -= self.__onBadgesChanged
        g_clientUpdateManager.removeObjectCallbacks(self)
        g_prbCtrlEvents.onPreQueueJoined -= self.__onPreQueueJoined
        self.__wgnpSteamAccCtrl.statusEvents.unsubscribe(StatusTypes.CONFIRMED, self._setEmailConfirmed)
        self.__wgnpSteamAccCtrl.statusEvents.unsubscribe(StatusTypes.ADDED, self._setEmailActionNeeded)
        self.__wgnpSteamAccCtrl.statusEvents.unsubscribe(StatusTypes.ADD_NEEDED, self._setEmailActionNeeded)
        demoAccUnsubscribe = self.__wgnpDemoAccCtrl.statusEvents.unsubscribe
        demoAccUnsubscribe(StatusTypes.ADD_NEEDED, self._showDemoAccountRenaming, context=NICKNAME_CONTEXT)
        demoAccUnsubscribe(StatusTypes.PROCESSING, self._showDemoAccountRenamingInProcess, context=NICKNAME_CONTEXT)
        demoAccUnsubscribe(StatusTypes.ADDED, self._hideDemoAccountRenaming, context=NICKNAME_CONTEXT)
        demoAccUnsubscribe(StatusTypes.UNDEFINED, self._hideDemoAccountRenaming, context=NICKNAME_CONTEXT)
        if self.__confirmationWindow is not None:
            self.__confirmationWindow.stopWaiting(DialogButtons.CANCEL)
            self.__confirmationWindow = None
        super(HeaderFeature, self).finalize()
        return

    def createToolTipContent(self, event, contentID):
        return self._tooltipModelFactories[contentID]() if contentID in self._tooltipModelFactories else None

    def _fillModel(self, model):
        submodel = model.header
        submodel.setUserName(BigWorld.player().name)
        submodel.setIsTeamKiller(self.__itemsCache.items.stats.isTeamKiller)
        self._updateClanInfo(model=model)
        self._updateBadges(model=model)
        submodel.setAccountInfoState(AccountInfoStateEnum.COMPLETED)
        submodel.setEmailButtonLabel(R.invalid())
        if self.__steamRegistrationCtrl.isSteamAccount:
            self.__askEmailStatus()
        else:
            self.__askDemoAccountRenameStatus()

    @replaceNoneKwargsModel
    def _setEmailConfirmed(self, status=None, model=None):
        submodel = model.header
        submodel.setEmailButtonLabel(R.invalid())
        submodel.setAccountInfoState(AccountInfoStateEnum.COMPLETED)
        self.__notConfirmedEmail = ''
        _logger.debug('User email confirmed.')

    @replaceNoneKwargsModel
    def _setEmailActionNeeded(self, status=None, model=None):
        submodel = model.header
        submodel.setAccountInfoState(AccountInfoStateEnum.EMAILPENDING)
        self.__notConfirmedEmail = status.email if status else ''
        if self.__notConfirmedEmail:
            submodel.setEmailButtonLabel(R.strings.badge.badgesPage.accountCompletion.button.confirmEmail())
        else:
            submodel.setEmailButtonLabel(R.strings.badge.badgesPage.accountCompletion.button.provideEmail())
        _logger.debug('User email: %s action needed.', self.__notConfirmedEmail)

    @replaceNoneKwargsModel
    def _showDemoAccountRenaming(self, status=None, model=None):
        submodel = model.header
        submodel.setAccountInfoState(AccountInfoStateEnum.RENAMEAVAILABLE)
        dispatcher = g_prbLoader.getDispatcher()
        if dispatcher is not None:
            queueType = dispatcher.getEntity().getQueueType()
            if queueType != QUEUE_TYPE.RANDOMS:
                submodel.setAccountInfoState(AccountInfoStateEnum.RENAMEDISABLED)
        _logger.debug('Demo account renaming needed.')
        return

    @replaceNoneKwargsModel
    def _showDemoAccountRenamingInProcess(self, status=None, model=None):
        submodel = model.header
        submodel.setAccountInfoState(AccountInfoStateEnum.RENAMEINPROGRESS)
        _logger.debug('Demo account renaming in process.')

    @replaceNoneKwargsModel
    def _hideDemoAccountRenaming(self, status=None, model=None):
        submodel = model.header
        submodel.setAccountInfoState(AccountInfoStateEnum.COMPLETED)
        _logger.debug('Hide demo account renaming.')

    @replaceNoneKwargsModel
    def _updateRenameButtonStatus(self, queueType, model=None):
        submodel = model.header
        if queueType != QUEUE_TYPE.RANDOMS and submodel.getAccountInfoState() in (AccountInfoStateEnum.RENAMEAVAILABLE, AccountInfoStateEnum.RENAMEINPROGRESS):
            submodel.setAccountInfoState(AccountInfoStateEnum.RENAMEDISABLED)

    @replaceNoneKwargsModel
    def _updateClanInfo(self, model=None):
        submodel = model.header
        clanProfile = self.__webCtrl.getAccountProfile()
        isInClan = clanProfile.isInClan()
        submodel.setIsInClan(isInClan)
        if isInClan:
            submodel.setClanAbbrev(clanProfile.getClanAbbrev())
            submodel.setRoleInClan(getClanRoleName(clanProfile.getRole()) or '')
            submodel.setClanDescription(clanProfile.getClanFullName())
            clanIcon = getClanEmblemURL(clanProfile.getClanDbID(), EmblemSize.SIZE_32)
            submodel.setClanIcon(clanIcon if clanIcon is not None else '')
        return

    @replaceNoneKwargsModel
    def _updateBadges(self, model=None):
        submodel = model.header
        self.__setBadge(submodel.setBadgeID, self.__badgesController.getPrefix())
        self.__setBadge(submodel.setSuffixBadgeID, self.__badgesController.getSuffix())

    def __createHangarTooltipView(self):
        _logger.debug('Show not confirmed email: %s tooltip.', self.__notConfirmedEmail)
        return HangarTooltipView(self.__notConfirmedEmail)

    def __onPreQueueJoined(self, queueType):
        self._updateRenameButtonStatus(queueType)

    def __onClanInfoChanged(self, _):
        self._updateClanInfo()

    def __onBadgesChanged(self):
        self._updateBadges()

    @staticmethod
    def __setBadge(setter, badge):
        setter(badge.getIconPostfix() if badge is not None and badge.isSelected else '')
        return

    @staticmethod
    def __onShowBadges():
        event_dispatcher.showBadges(backViewName=backport.text(R.strings.badge.badgesPage.header.backBtn.descrLabel()))

    def __onAccountInfoButtonClick(self):
        if self.__steamRegistrationCtrl.isSteamAccount:
            self.__onEmailButtonClicked()
        else:
            self.__onRenamingButtonClicked()

    def __onEmailButtonClicked(self):
        label = self._viewModel.header.getEmailButtonLabel()
        if label == R.strings.badge.badgesPage.accountCompletion.button.confirmEmail():
            _logger.debug('Show email confirmation overlay with email=%s.', self.__notConfirmedEmail)
            showSteamConfirmEmailOverlay(email=self.__notConfirmedEmail)
        elif label == R.strings.badge.badgesPage.accountCompletion.button.provideEmail():
            _logger.debug('Show add email overlay.')
            showSteamAddEmailOverlay()
        else:
            _logger.warning('Unknown email button label: %s. Action skipped.', label)

    def __onRenamingButtonClicked(self):
        _logger.debug('Show demo account renaming overlay.')
        if self.__platoonCtrl.isInPlatoon():
            self.__showLeaveSquadForRenamingDialog()
        else:
            showDemoAccRenamingOverlay()

    @wg_async
    def __askEmailStatus(self):
        if not self.__steamRegistrationCtrl.isSteamAccount:
            _logger.debug('Account completion disabled.')
            return
        _logger.debug('Sending email status request.')
        status = yield wg_await(self.__wgnpSteamAccCtrl.getEmailStatus())
        if status.isUndefined or self.__isDestroyed:
            _logger.warning('Can not get account email status.')
            return
        if status.typeIs(StatusTypes.ADD_NEEDED):
            self._setEmailActionNeeded()
        elif status.typeIs(StatusTypes.ADDED):
            self._setEmailActionNeeded(status=status)
        else:
            self._setEmailConfirmed()

    @wg_async
    def __askDemoAccountRenameStatus(self):
        if not self.__wgnpDemoAccCtrl.settings.isRenameApiEnabled():
            return
        status = yield wg_await(self.__wgnpDemoAccCtrl.getNicknameStatus())
        if status.isUndefined or self.__isDestroyed:
            return
        if status.typeIs(StatusTypes.ADD_NEEDED):
            self._showDemoAccountRenaming()
        elif status.typeIs(StatusTypes.PROCESSING):
            self._showDemoAccountRenamingInProcess()

    @wg_async
    def __showLeaveSquadForRenamingDialog(self):
        builder = ResDialogBuilder()
        builder.setMessagesAndButtons(R.strings.dialogs.accountCompletion.leaveSquad)
        self.__confirmationWindow = builder.build()
        result = yield wg_await(dialogs.show(self.__confirmationWindow))
        self.__confirmationWindow = None
        if result.result == DialogButtons.SUBMIT:
            self.__platoonCtrl.leavePlatoon(ignoreConfirmation=True)
            showDemoAccRenamingOverlay()
        return
