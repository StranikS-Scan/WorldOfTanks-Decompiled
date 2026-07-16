# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: last_stand/scripts/client/last_stand/gui/impl/lobby/difficulty_window_view.py
from __future__ import absolute_import
import WWISE
from frameworks.wulf import ViewSettings, WindowFlags
from gui.impl.backport import BackportTooltipWindow, createTooltipData
from gui.impl.gen import R
from gui.impl.lobby.common.tooltips.extended_text_tooltip import ExtendedTextTooltip
from helpers import dependency
from ids_generators import SequenceIDGenerator
from last_stand_common.last_stand_constants import DEFAULT_DIFFICULTY_MODIFIER
from last_stand.gui.impl.gen.view_models.views.lobby.difficulty_window_view_model import DifficultyWindowViewModel
from last_stand.gui.impl.lobby.base_view import BaseView, EventLobbyNotificationWindow
from last_stand.gui.impl.lobby.ls_helpers import fillRewards
from last_stand.gui.sounds import playSound
from last_stand.gui.sounds.sound_constants import DifficultyWindowState, DIFFICULTY_SCREEN
from last_stand.skeletons.ls_difficulty_missions_controller import ILSDifficultyMissionsController
_R_BACKPORT_TOOLTIP = R.views.common.tooltip_window.backport_tooltip_content.BackportTooltipContent()

class DifficultyWindowView(BaseView):
    layoutID = R.views.last_stand.mono.lobby.difficulty_congratulation_view()
    lsMissionsCtrl = dependency.descriptor(ILSDifficultyMissionsController)
    _MAX_BONUSES_IN_VIEW = 3

    def __init__(self, layoutID=None, difficultyLevel=None):
        settings = ViewSettings(layoutID or self.layoutID, model=DifficultyWindowViewModel())
        self._difficultyLevel = difficultyLevel
        self.__idGen = SequenceIDGenerator()
        super(DifficultyWindowView, self).__init__(settings)

    @property
    def viewModel(self):
        return super(DifficultyWindowView, self).getViewModel()

    def createToolTip(self, event):
        if event.contentID == _R_BACKPORT_TOOLTIP:
            tooltipId = event.getArgument('tooltipId')
            bonus = self.__bonusCache.get(tooltipId)
            if bonus:
                window = BackportTooltipWindow(createTooltipData(tooltip=bonus.tooltip, isSpecial=bonus.isSpecial, specialAlias=bonus.specialAlias, specialArgs=bonus.specialArgs, isWulfTooltip=bonus.isWulfTooltip), self.getParentWindow(), event=event)
                window.load()
                return window
        return super(DifficultyWindowView, self).createToolTip(event)

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

    def _onLoading(self, *args, **kwargs):
        super(DifficultyWindowView, self)._onLoading(*args, **kwargs)
        self._fillViewModel()

    def _fillViewModel(self):
        with self.viewModel.transaction() as model:
            model.setLevel(self._difficultyLevel)
            metaConfig = self.lsCtrl.getModeSettings().metaConfigs.get(self._difficultyLevel, {})
            model.setModifier(metaConfig.get('modifier', DEFAULT_DIFFICULTY_MODIFIER))
            if metaConfig.get('showMissionReward', False):
                self.__bonusCache = fillRewards(self.lsMissionsCtrl.getAggregatedMissionRewards(self._difficultyLevel), model.getRewards(), self._MAX_BONUSES_IN_VIEW, self.__idGen)

    def _getEvents(self):
        return [(self.viewModel.onClose, self._onClose), (self.lsCtrl.onSettingsUpdate, self._fillViewModel)]


class DifficultyWindow(EventLobbyNotificationWindow):

    def __init__(self, layoutID, difficultyLevel, parent=None):
        super(DifficultyWindow, self).__init__(wndFlags=WindowFlags.WINDOW_FULLSCREEN | WindowFlags.WINDOW, content=DifficultyWindowView(layoutID=layoutID, difficultyLevel=difficultyLevel), parent=parent)
        self._args = (layoutID, difficultyLevel)

    def isParamsEqual(self, *args):
        return self._args == args
