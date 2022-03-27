# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/rts/tutorial/rts_tutorial_helpers.py
from async import await, async
from frameworks.wulf import ViewSettings, ViewStatus
from gui.impl.dialogs.sub_views.common.simple_text import SimpleText
from gui.impl.gen import R
from gui.impl.gen.view_models.views.lobby.rts.tutorial_dialog_view_model import TutorialDialogViewModel
from gui.impl.dialogs.dialog_template import DialogTemplateView
from gui.impl.dialogs.dialog_template_button import ButtonPresenter
from gui.impl.dialogs.sub_views.title.simple_text_title import SimpleTextTitle
from gui.impl.dialogs import dialogs
from gui.impl.gen.view_models.views.dialogs.default_dialog_place_holders import DefaultDialogPlaceHolders
from gui.impl.gen.view_models.views.dialogs.dialog_template_button_view_model import ButtonType
from gui.impl.gen.view_models.views.lobby.rts.tutorial_dialog_view_model import State, Placeholder
from gui.impl.lobby.dialogs.full_screen_dialog_view import FullScreenDialogWindowWrapper
from gui.impl.pub import ViewImpl
from gui.impl.pub.dialog_window import DialogButtons, DialogResult
from helpers import dependency
from skeletons.gui.game_control import IRTSBattlesController
dialogStrings = R.strings.rts_battles.tutorial.dialog

def showLobbyMenu():
    from gui.Scaleform.daapi.settings.views import VIEW_ALIAS
    from gui.Scaleform.framework.managers.loaders import SFViewLoadParams
    from gui.shared import g_eventBus, EVENT_BUS_SCOPE
    from gui.shared.events import LoadViewEvent
    g_eventBus.handleEvent(LoadViewEvent(SFViewLoadParams(VIEW_ALIAS.LOBBY_MENU)), scope=EVENT_BUS_SCOPE.LOBBY)


@async
def showInvitationDialog():
    dialogTemplateView = DialogTemplateView(R.views.lobby.rts.Tutorial.TutorialDialog())
    dialogTemplateView.setSubView(Placeholder.HEADER.value, HeaderComponent(dialogStrings.header()))
    dialogTemplateView.setSubView(Placeholder.SUBHEADER.value, SubheaderComponent(dialogStrings.invitation.subheader()))
    dialogTemplateView.setSubView(DefaultDialogPlaceHolders.TITLE, SimpleTextTitle(dialogStrings.invitation.description.header()))
    dialogTemplateView.setSubView(DefaultDialogPlaceHolders.CONTENT, SimpleText(dialogStrings.invitation.description.content()))
    dialogTemplateView.setSubView(Placeholder.BACKGROUND.value, BackgroundComponent(State.INVITATION))
    dialogTemplateView.addButton(ButtonPresenter(dialogStrings.invitation.buttonText(), DialogButtons.SUBMIT))
    dialogTemplateView.onStatusChanged += _onInvitationDialogStatusChanged
    result = yield await(dialogs.show(FullScreenDialogWindowWrapper(dialogTemplateView, None, False)))
    if result.result == DialogButtons.SUBMIT:
        rtsController = dependency.instance(IRTSBattlesController)
        rtsController.runRTSBootcamp()
    return


def _onInvitationDialogStatusChanged(status):
    rtsController = dependency.instance(IRTSBattlesController)
    soundManager = rtsController.getSoundManager()
    if not soundManager:
        return
    if status == ViewStatus.LOADED:
        soundManager.onOpenPage()
    elif status == ViewStatus.DESTROYING:
        soundManager.onClosePage()


@async
def showVictoryDialog():
    dialogTemplateView = DialogTemplateView(R.views.lobby.rts.Tutorial.TutorialDialog())
    dialogTemplateView.setSubView(Placeholder.VICTORY_LAYER.value, VictoryLayerComponent())
    dialogTemplateView.setSubView(Placeholder.BACKGROUND.value, BackgroundComponent(State.VICTORY))
    dialogTemplateView.addButton(ButtonPresenter(dialogStrings.victory.buttonText(), DialogButtons.SUBMIT))
    dialogTemplateView.onStatusChanged += _onVictoryDialogStatusChanged
    yield await(dialogs.show(FullScreenDialogWindowWrapper(dialogTemplateView, None, False)))
    rtsController = dependency.instance(IRTSBattlesController)
    rtsController.updateRTSTutorialBanner()
    return


def _onVictoryDialogStatusChanged(status):
    rtsController = dependency.instance(IRTSBattlesController)
    soundManager = rtsController.getSoundManager()
    if not soundManager:
        return
    if status == ViewStatus.LOADED:
        soundManager.onOpenTutorialResultScreen(True)
    elif status == ViewStatus.DESTROYING:
        soundManager.onClosePage()


@async
def showDefeatDialog():
    dialogTemplateView = DialogTemplateView(R.views.lobby.rts.Tutorial.TutorialDialog())
    dialogTemplateView.setSubView(Placeholder.HEADER.value, HeaderComponent(dialogStrings.header()))
    dialogTemplateView.setSubView(Placeholder.SUBHEADER.value, SubheaderComponent(dialogStrings.defeat.subheader()))
    dialogTemplateView.setSubView(DefaultDialogPlaceHolders.TITLE, SimpleTextTitle(dialogStrings.defeat.description.header()))
    dialogTemplateView.setSubView(DefaultDialogPlaceHolders.CONTENT, SimpleText(dialogStrings.defeat.description.content()))
    dialogTemplateView.setSubView(Placeholder.BUTTONS_DESCRIPTION.value, ButtonsDescriptionComponent(dialogStrings.defeat.buttonsDescription()))
    dialogTemplateView.setSubView(Placeholder.BACKGROUND.value, BackgroundComponent(State.DEFEAT))
    dialogTemplateView.addButton(ButtonPresenter(dialogStrings.defeat.retryButtonText(), DialogButtons.SUBMIT))
    dialogTemplateView.addButton(ButtonPresenter(dialogStrings.defeat.cancelButtonText(), DialogButtons.CANCEL, ButtonType.SECONDARY))
    dialogTemplateView.onStatusChanged += _onDefeatDialogStatusChanged
    result = yield await(dialogs.show(FullScreenDialogWindowWrapper(dialogTemplateView, None, False)))
    rtsController = dependency.instance(IRTSBattlesController)
    if result.result == DialogButtons.SUBMIT:
        rtsController.runRTSBootcamp()
    else:
        rtsController.updateRTSTutorialBanner()
    return


def _onDefeatDialogStatusChanged(status):
    rtsController = dependency.instance(IRTSBattlesController)
    soundManager = rtsController.getSoundManager()
    if not soundManager:
        return
    if status == ViewStatus.LOADED:
        soundManager.onOpenTutorialResultScreen()
    elif status == ViewStatus.DESTROYING:
        soundManager.onClosePage()


class HeaderComponent(SimpleText):
    __slots__ = ()
    _LAYOUT_DYN_ACCESSOR = R.views.lobby.rts.Tutorial.sub_views.Header


class SubheaderComponent(SimpleText):
    __slots__ = ()
    _LAYOUT_DYN_ACCESSOR = R.views.lobby.rts.Tutorial.sub_views.Subheader


class ButtonsDescriptionComponent(SimpleText):
    __slots__ = ()
    _LAYOUT_DYN_ACCESSOR = R.views.lobby.rts.Tutorial.sub_views.ButtonsDescription


class VictoryLayerComponent(ViewImpl):
    __slots__ = ()

    def __init__(self):
        settings = ViewSettings(R.views.lobby.rts.Tutorial.sub_views.VictoryLayer())
        settings.model = TutorialDialogViewModel()
        super(VictoryLayerComponent, self).__init__(settings)


class BackgroundComponent(ViewImpl):

    def __init__(self, state=State.INVITATION):
        settings = ViewSettings(R.views.lobby.rts.Tutorial.sub_views.Background())
        settings.model = TutorialDialogViewModel()
        super(BackgroundComponent, self).__init__(settings)
        self.__state = state

    def _onLoading(self, *args, **kwargs):
        with self.getViewModel().transaction() as model:
            model.setState(self.__state)
