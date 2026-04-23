# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/achievements/achievements_summary_edit_mode_view.py
import typing
from PlayerEvents import g_playerEvents
from adisp import adisp_process
from frameworks.wulf import WindowFlags, WindowLayer
from gui.Scaleform.daapi.settings.views import VIEW_ALIAS
from gui.game_control.wot_plus.service_record_customization import ServiceRecordProcessor
from gui.impl.dialogs.dialogs import showServiceRecordCustomizationConfirmDialog
from gui.impl.gen.view_models.views.lobby.achievements.views.achievements_main_view_model import AchievementsViews
from gui.impl.lobby.achievements.achievements_main_view import AchievementsViewCtx, BaseAchievementView
from gui.impl.lobby.achievements.summary.summary_view import SummaryView
from gui.impl.pub.dialog_window import DialogButtons
from gui.impl.pub.lobby_window import LobbyWindow
from helpers import dependency
from renewable_subscription_common.schema import renewableSubscriptionsConfigSchema
from skeletons.gui.game_control import IWotPlusController
from wg_async import wg_async, wg_await
if typing.TYPE_CHECKING:
    from gui.impl.gen.view_models.views.lobby.achievements.views.summary.summary_view_model import SummaryViewModel

@adisp_process
def _storeNewCustomization(bg, ribbon):
    yield ServiceRecordProcessor(bg, ribbon).request()


class SummaryEditModeView(SummaryView):

    def initialize(self, *args, **kwargs):
        super(SummaryEditModeView, self).initialize(*args, **kwargs)
        self.__setInitialData()
        self.viewModel.setIsInCustomizationMode(True)

    def _getEvents(self):
        mainEvents = super(SummaryEditModeView, self)._getEvents()
        mainEvents.extend([(self.viewModel.onCustomizationConfirmed, self.__onCustomizationConfirmed),
         (self.viewModel.onCustomizationDiscard, self.__onCustomizationDiscard),
         (self.viewModel.onSetBackgroundDraft, self.__onSetBackgroundDraft),
         (self.viewModel.onSetRibbonDraft, self.__onSetRibbonDraft)])
        return mainEvents

    def _onSetIsInCustomizationMode(self, _):
        pass

    def __onCustomizationConfirmed(self, ctx):
        _storeNewCustomization(int(ctx.get('backgroundSlug')), int(ctx.get('ribbonSlug')))
        self.parentView.destroy()

    def __onCustomizationDiscard(self, _):
        self.__setInitialData()

    def __onSetBackgroundDraft(self, ctx):
        self.__setBackgroundDraftBySlug(slug=int(ctx.get('backgroundDraftSlug')))

    def __setInitialData(self):
        backgroundIndex, _, ribbonIndex, _ = self._getCustomizationData()
        self.__setBackgroundDraftBySlug(backgroundIndex)
        self.__setRibbonDraftBySlug(ribbonIndex)

    def __onSetRibbonDraft(self, ctx):
        self.__setRibbonDraftBySlug(slug=int(ctx.get('ribbonDraftSlug')))

    def __setRibbonDraftBySlug(self, slug):
        with self.viewModel.transaction() as model:
            ribbonImages = self._getServiceRecordRibbonOptions()
            for index, image, icon in ribbonImages:
                if slug == index:
                    model.ribbonDraft.setSlug(str(index))
                    model.ribbonDraft.setImage(image)
                    model.ribbonDraft.setIcon(icon)
                    break

    def __setBackgroundDraftBySlug(self, slug):
        with self.viewModel.transaction() as model:
            bgOptionsData = self._getServiceRecordBackgroundOptions()
            for index, image, label in bgOptionsData:
                if slug == index:
                    model.backgroundDraft.setSlug(str(index))
                    model.backgroundDraft.setImage(image)
                    model.backgroundDraft.setLabel(label)
                    break


class _AchievemetSummaryEditModeView(BaseAchievementView):
    __slots__ = ('_ctx', '__summaryViewPresenter')
    __wotPlusCtrl = dependency.descriptor(IWotPlusController)

    def __init__(self, userID, *args, **kwargs):
        super(_AchievemetSummaryEditModeView, self).__init__(ctx=AchievementsViewCtx(menuName=VIEW_ALIAS.PROFILE_TOTAL_PAGE, userID=userID, closeCallback=None), *args, **kwargs)
        self.__summaryViewPresenter = SummaryEditModeView(self.viewModel.summaryModel, self, userID)
        return

    def _onLoading(self, *args, **kwargs):
        super(_AchievemetSummaryEditModeView, self)._onLoading(*args, **kwargs)
        with self.viewModel.transaction() as tx:
            self.__summaryViewPresenter.initialize()
            tx.setViewType(AchievementsViews.SUMMARY)
            tx.setIsOtherPlayer(self._ctx.userID is not None)
        return

    def _getEvents(self):
        events = [(g_playerEvents.onRenewableSubscriptionStatusChanged, self.__onRenewableSubscriptionStatusChanged), (g_playerEvents.onConfigModelUpdated, self.__onConfigModelUpdated)]
        events.extend(super(_AchievemetSummaryEditModeView, self)._getEvents())
        return events

    def _finalize(self):
        self.currentPresenter.finalize()
        super(_AchievemetSummaryEditModeView, self)._finalize()
        self.__summaryViewPresenter = None
        return

    @property
    def currentPresenter(self):
        return self.__summaryViewPresenter

    @wg_async
    def _onClose(self):
        summaryViewModel = self.__summaryViewPresenter.viewModel
        bgNewVal = summaryViewModel.backgroundDraft.getSlug()
        ribbonNewVal = summaryViewModel.ribbonDraft.getSlug()
        if bgNewVal == summaryViewModel.background.getSlug() and ribbonNewVal == summaryViewModel.ribbon.getSlug():
            self.destroy()
            return
        else:
            result = yield wg_await(showServiceRecordCustomizationConfirmDialog())
            if result is None or result.busy or not result.result:
                return
            btnClicked = result.result.result
            if not btnClicked:
                return
            if btnClicked == DialogButtons.CANCEL:
                self.destroy()
                return
            _storeNewCustomization(int(bgNewVal), int(ribbonNewVal))
            self.destroy()
            return

    def __onRenewableSubscriptionStatusChanged(self):
        self.__destroyIfNotActual()

    def __onConfigModelUpdated(self, gpKey):
        if renewableSubscriptionsConfigSchema.gpKey == gpKey:
            self.__destroyIfNotActual()

    def __destroyIfNotActual(self):
        if not self.__wotPlusCtrl.getSettingsStorage().isServiceRecordCustomizationAvailable():
            self.destroy()


class AchievementSummaryViewEditModeWindow(LobbyWindow):

    def __init__(self, userID, parent):
        super(AchievementSummaryViewEditModeWindow, self).__init__(wndFlags=WindowFlags.WINDOW | WindowFlags.WINDOW_FULLSCREEN, content=_AchievemetSummaryEditModeView(userID), parent=parent, layer=WindowLayer.WINDOW)
