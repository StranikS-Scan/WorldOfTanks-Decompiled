# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/account_completion/add_email_overlay_view.py
from constants import EMAIL_CONFIRMATION_QUEST_ID
from frameworks.wulf import WindowFlags, WindowLayer, ViewSettings
from gui.impl import backport
from gui.impl.gen import R
from gui.impl.gen.view_models.views.lobby.account_completion.common.field_model import FieldModel
from gui.impl.gen.view_models.views.lobby.account_completion.email_confirmation_curtain_model import EmailConfirmationCurtainModel
from gui.impl.lobby.account_completion.common import fillRewards, getBonuses
from gui.impl.lobby.account_completion.email_overlay_view import EmailOverlayView
from gui.impl.pub.lobby_window import LobbyWindow
from gui.platform.wgnp.controller import isEmailInvalid, isEmailRestrictedByCountry, isEmailAlreadyTaken, isEmailMinLength, isEmailMaxLength, isEmailForbidden, isEmailBannedInCountry
from gui.platform.wgnp.controller import isRequestLimitExceeded, getRequestRestrictedUntilTime
from gui.shared.event_dispatcher import showConfirmEmailOverlay
from helpers import dependency
from helpers.time_utils import getTimeDeltaFromNow
from skeletons.gui.server_events import IEventsCache
_RESTRICTED_REQUEST_MIN_TIME = 5

class AddEmailOverlayView(EmailOverlayView):
    __slots__ = ('_initialEmail', '_tooltipItems')
    _TITLE = R.strings.dialogs.accountCompletion.email.title()
    _SUBTITLE = R.strings.dialogs.accountCompletion.email.subTitle()
    _eventsCache = dependency.descriptor(IEventsCache)

    def __init__(self, settings, initialEmail='', fadeAnimation=False):
        super(AddEmailOverlayView, self).__init__(settings, fadeAnimation)
        self._initialEmail = initialEmail
        self._tooltipItems = {}

    @property
    def viewModel(self):
        return super(AddEmailOverlayView, self).getViewModel()

    def createToolTip(self, event):
        if event.contentID == R.views.common.tooltip_window.backport_tooltip_content.BackportTooltipContent():
            tooltipId = event.getArgument('tooltipId')
            if tooltipId:
                itemIndex = tooltipId.split(':').pop()
                tooltipData = self._tooltipItems.get(int(itemIndex))
                window = None
                if tooltipData is not None:
                    window = backport.BackportTooltipWindow(tooltipData, self.getParentWindow())
                    window.load()
                return window
        return super(AddEmailOverlayView, self).createToolTip(event)

    def _finalize(self):
        super(AddEmailOverlayView, self)._finalize()
        self._tooltipItems = None
        return

    def _addListeners(self):
        super(AddEmailOverlayView, self)._addListeners()
        self._eventsCache.onSyncCompleted += self._onSyncCompleted

    def _removeListeners(self):
        self._eventsCache.onSyncCompleted -= self._onSyncCompleted
        super(AddEmailOverlayView, self)._removeListeners()

    def _fillModel(self, model):
        super(AddEmailOverlayView, self)._fillModel(model)
        model.setQuestID(EMAIL_CONFIRMATION_QUEST_ID)
        self._fillRewards(model)
        self._fillField(model)

    def _fillField(self, model):
        emailField = model.field
        emailField.setValue(self._initialEmail)
        emailField.setName(R.strings.dialogs.accountCompletion.email.fieldName())
        emailField.setType(FieldModel.TYPE_EMAIL)
        emailField.setPlaceholder(R.strings.dialogs.accountCompletion.email.fieldPlaceholder())

    def _fillRewards(self, model):
        fillRewards(model, getBonuses(), self._tooltipItems)

    def _doRequest(self, value):
        return self._wgnpCtrl.addEmail(value)

    def _handleSuccess(self, value):
        self._setAnimation(isFade=True, isShow=False)
        showConfirmEmailOverlay(email=value, fadeAnimation=True)
        self.destroyWindow(offOverlay=False)

    def _handleError(self, email, response):
        if isRequestLimitExceeded(response):
            message = R.strings.dialogs.accountCompletion.emailOverlay.error.codeAlreadySent()
            restrictedUntil = getRequestRestrictedUntilTime(response)
            errorTime = max(_RESTRICTED_REQUEST_MIN_TIME, getTimeDeltaFromNow(restrictedUntil))
            with self.viewModel.transaction() as model:
                self._updateModel(model, errorMessage=message, errorTime=errorTime)
        else:
            super(AddEmailOverlayView, self)._handleError(email, response)

    def _getErrorMessage(self, response):
        if isEmailRestrictedByCountry(response):
            message = R.strings.dialogs.accountCompletion.emailRestrictedByCountry()
        elif isEmailBannedInCountry(response):
            message = R.strings.dialogs.accountCompletion.emailProviderBanned()
        elif isEmailInvalid(response):
            message = R.strings.dialogs.accountCompletion.errorIsWrong()
        elif isEmailForbidden(response):
            message = R.strings.dialogs.accountCompletion.emailForbidden()
        elif isEmailMinLength(response):
            message = R.strings.dialogs.accountCompletion.emailIsToShort()
        elif isEmailMaxLength(response):
            message = R.strings.dialogs.accountCompletion.emailIsToLong()
        elif isEmailAlreadyTaken(response):
            message = R.strings.dialogs.accountCompletion.emailAlreadyTaken()
        else:
            message = super(AddEmailOverlayView, self)._getErrorMessage(response)
        return message

    def _updateModel(self, model, value=None, isUnavailable=False, errorMessage=None, errorTime=0):
        super(AddEmailOverlayView, self)._updateModel(model, value, isUnavailable, errorMessage)
        model.field.setErrorTime(errorTime)

    def _onSyncCompleted(self, *args):
        with self.viewModel.transaction() as model:
            self._fillRewards(model)


class AddEmailOverlayWindow(LobbyWindow):

    def __init__(self, initialEmail='', fadeAnimation=False):
        settings = ViewSettings(R.views.lobby.account_completion.EmailConfirmationCurtainView())
        settings.model = EmailConfirmationCurtainModel()
        super(AddEmailOverlayWindow, self).__init__(wndFlags=WindowFlags.WINDOW_FULLSCREEN, content=AddEmailOverlayView(settings, initialEmail, fadeAnimation), layer=WindowLayer.TOP_WINDOW)
