# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/poll/poll_browser_action.py
from debug_utils import LOG_WARNING, LOG_ERROR
from frameworks.wulf import ViewFlags
from gui.Scaleform.framework import ScopeTemplates
from gui.Scaleform.framework.managers.loaders import GuiImplViewLoadParams
from gui.impl.dialogs import dialogs
from gui.impl.dialogs.gf_builders import ResDialogBuilder
from gui.impl.gen.resources import R
from gui.impl.gen.view_models.views.lobby.poll.poll_view_model import PollViewType
from gui.impl.lobby.common.browser_view import BrowserView, makeSettings
from gui.impl.pub.dialog_window import DialogButtons
from gui.shared import g_eventBus
from gui.shared.events import LoadGuiImplViewEvent, SurveyEvent
from web.web_client_api import webApiCollection, ui as ui_web_api, sound as sound_web_api
from web.web_client_api.promo import PromoWebApi
from web.web_client_api.request import RequestWebApi
from web.web_client_api.survey import SurveyWebApi
from wg_async import wg_await, wg_async
from gui.wgnc import g_wgncProvider

class PollBrowserButtonHandler(object):

    @classmethod
    def invoke(cls, **kwargs):
        value = kwargs.get('value', None)
        if isinstance(value, dict):
            url = value.get('url', '')
            target = value.get('target', '')
            onExitCustomAction = value.get('on_exit_custom_action', '')
            notID = kwargs.get('notID', '')
        else:
            LOG_ERROR('{}: "value" should be dict'.format(cls.__name__))
            return
        if not url or not target or not notID:
            LOG_ERROR('{}: some items are not correct'.format(cls.__name__))
            return
        else:

            class PollBrowserView(BrowserView):

                def _initialize(self, *args, **kwargs):
                    super(PollBrowserView, self)._initialize(*args, **kwargs)
                    self.__isSurveyFinished = False
                    g_eventBus.addListener(SurveyEvent.SURVEY_FINISHED, self.__onFinishSurvey)

                def _finalize(self):
                    g_eventBus.removeListener(SurveyEvent.SURVEY_FINISHED, self.__onFinishSurvey)
                    super(PollBrowserView, self)._finalize()

                def __onFinishSurvey(self, _):
                    self.__isSurveyFinished = True

                @wg_async
                def onCloseView(self):
                    if self.__isSurveyFinished:
                        super(PollBrowserView, self).onCloseView()
                    else:
                        builder = ResDialogBuilder()
                        if target == PollViewType.SURVEY.value:
                            builder.setMessagesAndButtons(R.strings.dialogs.surveyQuit)
                        elif target == PollViewType.APPLICATION_FORM.value:
                            builder.setMessagesAndButtons(R.strings.dialogs.applicationQuit)
                        else:
                            LOG_WARNING('Not correct notification target "{}"'.format(target))
                        confirmationWindow = builder.build()
                        result = yield wg_await(dialogs.show(confirmationWindow))
                        if result.result == DialogButtons.CANCEL:
                            if onExitCustomAction and notID:
                                g_wgncProvider.doAction(notID, onExitCustomAction, target)
                            super(PollBrowserView, self).onCloseView()

            layoutID = R.views.lobby.common.BrowserView()
            webHandlers = webApiCollection(PromoWebApi, RequestWebApi, SurveyWebApi, ui_web_api.OpenWindowWebApi, ui_web_api.CloseWindowWebApi, ui_web_api.OpenTabWebApi, ui_web_api.NotificationWebApi, ui_web_api.ContextMenuWebApi, ui_web_api.UtilWebApi, sound_web_api.SoundWebApi, sound_web_api.HangarSoundWebApi)
            viewFlags = ViewFlags.LOBBY_TOP_SUB_VIEW
            g_eventBus.handleEvent(LoadGuiImplViewEvent(GuiImplViewLoadParams(layoutID, PollBrowserView, ScopeTemplates.LOBBY_SUB_SCOPE), settings=makeSettings(url=url, webHandlers=webHandlers, viewFlags=viewFlags, restoreBackground=True, isClosable=True)))
            return
