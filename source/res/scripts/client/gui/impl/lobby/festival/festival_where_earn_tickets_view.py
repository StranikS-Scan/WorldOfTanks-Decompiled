# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/festival/festival_where_earn_tickets_view.py
from async import async, await
from BWUtil import AsyncReturn
from frameworks.wulf import ViewModel
from gui.impl.gen import R
from gui.impl.gen.view_models.windows.animated_dialog_window_model import AnimatedDialogWindowModel
from gui.impl.gen.view_models.windows.simple_dialog_window_model import SimpleDialogWindowModel
from gui.impl.pub.dialog_window import DialogContent, DialogButtons
from gui.impl.gen.view_models.constants.dialog_presets import DialogPresets
from gui.impl.pub.animated_dialog_window import AnimatedDialogWindow
from helpers import dependency
from skeletons.festival import IFestivalController

@async
@dependency.replace_none_kwargs(festivalController=IFestivalController)
def showFestivalWhereEarnTickets(parent=None, festivalController=None):
    result = yield _showComplexFestivalWhereEarnTickets(parent.parent, parent)
    raise AsyncReturn(result is not None)
    return


@async
def _showSimpleFestivalWhereEarnTickets(parent, parentWindow):
    window = FestivalWhereEarnTicketsSimpleWindow(parent=parent, parentDialogWindow=parentWindow)
    window.load()
    result = yield await(window.wait())
    window.destroy()
    raise AsyncReturn(result)


@async
def _showComplexFestivalWhereEarnTickets(parent, parentWindow):
    window = FestivalWhereEarnTicketsWindow(parent=parent, parentDialogWindow=parentWindow)
    window.load()
    result = yield await(window.wait())
    window.destroy()
    raise AsyncReturn(result)


class FestivalWhereEarnTicketsView(DialogContent):
    __slots__ = ()

    def __init__(self, *args, **kwargs):
        super(FestivalWhereEarnTicketsView, self).__init__(R.views.lobby.festival.festival_where_earn_tickets_view.FestivalWhereEarnTicketsView(), ViewModel, *args, **kwargs)


class FestivalWhereEarnTicketsWindow(AnimatedDialogWindow):
    __slots__ = ()

    def __init__(self, parent=None, parentDialogWindow=None):
        super(FestivalWhereEarnTicketsWindow, self).__init__(content=FestivalWhereEarnTicketsView(), parent=parent, parentDialogWindow=parentDialogWindow, enableBlur=False)

    def _initialize(self):
        super(FestivalWhereEarnTicketsWindow, self)._initialize()
        self.viewModel.setPreset(DialogPresets.FESTIVAL_RANDOM_GENERATOR)
        self.viewModel.setTitle(R.strings.festival.dogtagView.whereEarnTickets())
        self._addButton(DialogButtons.SUBMIT, R.strings.festival.dogtagView.submit(), isFocused=True, invalidateAll=True)

    def _onButtonClick(self, item):
        self.processAnimatedAction(AnimatedDialogWindowModel.ACTION_CLOSE, item)


class FestivalWhereEarnTicketsSimpleWindow(AnimatedDialogWindow):
    __slots__ = ()

    def __init__(self, parent=None, parentDialogWindow=None):
        super(FestivalWhereEarnTicketsSimpleWindow, self).__init__(content=DialogContent(R.views.common.dialog_view.simple_dialog_content.SimpleDialogContent(), SimpleDialogWindowModel), parent=parent, parentDialogWindow=parentDialogWindow, enableBlur=False)

    def _initialize(self):
        super(FestivalWhereEarnTicketsSimpleWindow, self)._initialize()
        self.viewModel.setPreset(DialogPresets.FESTIVAL_RANDOM_GENERATOR)
        self.viewModel.setTitle(R.strings.festival.dogtagView.whereEarnTicketsAnswer())
        self.contentViewModel.setMessage(R.strings.festival.dogtagView.whereEarnTickets.battleQuests.desc())
        self.viewModel.setIcon(R.images.gui.maps.icons.festival.onboard_battle_task())
        self._addButton(DialogButtons.SUBMIT, R.strings.festival.dogtagView.submit(), isFocused=True, invalidateAll=True)

    def _onButtonClick(self, item):
        self.processAnimatedAction(AnimatedDialogWindowModel.ACTION_CLOSE, item)
