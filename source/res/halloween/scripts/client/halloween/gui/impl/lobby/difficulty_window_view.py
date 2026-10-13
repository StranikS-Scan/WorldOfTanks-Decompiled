# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: halloween/scripts/client/halloween/gui/impl/lobby/difficulty_window_view.py
from __future__ import absolute_import
import WWISE
from frameworks.wulf import ViewSettings, WindowFlags
from gui.impl.gen import R
from gui.impl.lobby.common.tooltips.extended_text_tooltip import ExtendedTextTooltip
from halloween.gui.halloween_account_settings import AccountSettingsKeys, getSettings, setSettings
from halloween.gui.impl.gen.view_models.views.lobby.difficulty_window_view_model import DifficultyWindowViewModel
from halloween.gui.impl.lobby.base_view import BaseView, HWLobbyNotificationWindow
from halloween.gui.impl.lobby.hw_helpers.anomalies_helpers import isAnomaliesSystemAvailable
from halloween.gui.shared.event_dispatcher import showAnomaliesWindow
from halloween.gui.sounds import playSound
from halloween.gui.sounds.sound_constants import DifficultyWindowState, DIFFICULTY_SCREEN
from helpers import dependency
from skeletons.gui.shared import IItemsCache

class DifficultyWindowView(BaseView):
    __slots__ = ()
    itemsCache = dependency.descriptor(IItemsCache)
    layoutID = R.views.halloween.mono.lobby.difficulty_congrat()

    def __init__(self, layoutID=None, difficultyLevel=None):
        settings = ViewSettings(layoutID or self.layoutID, model=DifficultyWindowViewModel())
        self._difficultyLevel = difficultyLevel
        super(DifficultyWindowView, self).__init__(settings)

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
        super(DifficultyWindowView, self)._initialize(*args, **kwargs)
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
        with self.viewModel.transaction() as model:
            model.setLevel(self._difficultyLevel)
            model.setHasNewRecipes(self._hasNewRecipes)

    def _getEvents(self):
        return ((self.viewModel.onClose, self._onClose), (self.viewModel.onToAnomalies, self._onToAnomaliesClick))

    @property
    def _hasNewRecipes(self):
        needToShow = not getSettings(AccountSettingsKeys.ANOMALIES_SYSTEM_AVAILABLE)
        if needToShow:
            setSettings(AccountSettingsKeys.ANOMALIES_SYSTEM_AVAILABLE, True)
        return needToShow and isAnomaliesSystemAvailable()

    @staticmethod
    def _onToAnomaliesClick():
        showAnomaliesWindow()


class DifficultyWindow(HWLobbyNotificationWindow):

    def __init__(self, layoutID, difficultyLevel, parent=None):
        super(DifficultyWindow, self).__init__(wndFlags=WindowFlags.WINDOW_FULLSCREEN | WindowFlags.WINDOW, content=DifficultyWindowView(layoutID=layoutID, difficultyLevel=difficultyLevel), parent=parent)
        self._args = (layoutID, difficultyLevel)

    def isParamsEqual(self, *args):
        return self._args == args
