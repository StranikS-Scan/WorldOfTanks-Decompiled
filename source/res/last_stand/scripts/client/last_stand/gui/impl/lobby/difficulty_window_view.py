# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: last_stand/scripts/client/last_stand/gui/impl/lobby/difficulty_window_view.py
import WWISE
from helpers import dependency
from frameworks.wulf import ViewSettings, WindowFlags
from gui.impl.gen import R
from gui.impl.lobby.common.tooltips.extended_text_tooltip import ExtendedTextTooltip
from last_stand.gui.impl.gen.view_models.views.lobby.difficulty_window_view_model import DifficultyWindowViewModel
from last_stand.gui.impl.lobby.base_view import BaseView, EventLobbyNotificationWindow
from last_stand.gui.impl.lobby.gsw_cards.quests_card_presenter import QuestsCardPresenter
from last_stand.gui.sounds import playSound
from last_stand.gui.sounds.sound_constants import DifficultyWindowState, DIFFICULTY_SCREEN
from skeletons.gui.server_events import IEventsCache

class DifficultyWindowView(BaseView):
    __slots__ = ()
    layoutID = R.views.last_stand.mono.lobby.difficulty_congratulation_view()
    eventsCache = dependency.descriptor(IEventsCache)

    def __init__(self, layoutID=None, difficultyLevel=None, showDailyWidget=False):
        settings = ViewSettings(layoutID or self.layoutID, model=DifficultyWindowViewModel())
        self._difficultyLevel = difficultyLevel
        self._showDailyWidget = showDailyWidget
        self._questWidget = None
        super(DifficultyWindowView, self).__init__(settings)
        return

    @property
    def viewModel(self):
        return super(DifficultyWindowView, self).getViewModel()

    def createToolTipContent(self, event, contentID):
        if contentID == R.views.lobby.common.tooltips.ExtendedTextTooltip():
            text = event.getArgument('text', '')
            stringifyKwargs = event.getArgument('stringifyKwargs', '')
            return ExtendedTextTooltip(text, stringifyKwargs)
        return super(DifficultyWindowView, self).createToolTipContent(event, contentID)

    def _initialize(self, *args, **kwargs):
        super(DifficultyWindowView, self)._initialize()
        WWISE.WW_setState(DifficultyWindowState.GROUP, DifficultyWindowState.OPEN)
        soundKey = DIFFICULTY_SCREEN.get(self._difficultyLevel, None)
        if soundKey is not None:
            playSound(soundKey)
        return

    def _finalize(self):
        WWISE.WW_setState(DifficultyWindowState.GROUP, DifficultyWindowState.CLOSE)
        super(DifficultyWindowView, self)._finalize()

    def _onLoading(self):
        super(DifficultyWindowView, self)._onLoading()
        self._questWidget = QuestsCardPresenter()
        self.setChildView(resourceID=R.aliases.last_stand.shared.Quests(), view=self._questWidget)
        with self.viewModel.transaction() as model:
            model.setLevel(self._difficultyLevel)
            model.setShowDaily(self._showDailyWidget and not self._questWidget.isBadgeWidget)

    def _subscribe(self):
        super(DifficultyWindowView, self)._subscribe()
        self.viewModel.onClose += self._onClose

    def _unsubscribe(self):
        super(DifficultyWindowView, self)._unsubscribe()
        self.viewModel.onClose -= self._onClose


class DifficultyWindow(EventLobbyNotificationWindow):

    def __init__(self, layoutID, difficultyLevel, showDailyWidget, parent=None):
        super(DifficultyWindow, self).__init__(wndFlags=WindowFlags.WINDOW_FULLSCREEN | WindowFlags.WINDOW, content=DifficultyWindowView(layoutID=layoutID, difficultyLevel=difficultyLevel, showDailyWidget=showDailyWidget), parent=parent)
        self._args = (layoutID, difficultyLevel)

    def isParamsEqual(self, *args):
        return self._args == args
