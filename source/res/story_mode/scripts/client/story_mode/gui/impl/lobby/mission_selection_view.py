# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: story_mode/scripts/client/story_mode/gui/impl/lobby/mission_selection_view.py
from functools import partial
import typing
from gui.impl.gen import R
from story_mode.gui.impl.gen.view_models.views.lobby.mission_selection_view_model import MissionSelectionViewModel
from story_mode.gui.impl.lobby.base_prb_view import BasePrbView
from story_mode.gui.impl.lobby.mission_tooltip import MissionTooltip
from story_mode.gui.shared.event_dispatcher import sendViewLoadedEvent
from story_mode.gui.story_mode_gui_constants import STORY_MODE_SOUND_SPACE
from story_mode.uilogging.story_mode.consts import LogButtons
from story_mode.uilogging.story_mode.loggers import SelectMissionWindow
from story_mode_common.story_mode_constants import UNDEFINED_MISSION_ID

class MissionSelectionView(BasePrbView):
    LAYOUT_ID = R.views.story_mode.lobby.MissionSelectionView()
    MODEL_CLASS = MissionSelectionViewModel
    _COMMON_SOUND_SPACE = STORY_MODE_SOUND_SPACE

    def __init__(self, *args, **kwargs):
        super(MissionSelectionView, self).__init__(*args, **kwargs)
        self._uiLogger = SelectMissionWindow()

    def createToolTipContent(self, event, contentID):
        return MissionTooltip() if contentID == R.views.story_mode.lobby.MissionTooltip() else super(MissionSelectionView, self).createToolTipContent(event=event, contentID=contentID)

    def _onLoading(self, *args, **kwargs):
        super(MissionSelectionView, self)._onLoading(*args, **kwargs)
        model = self.getViewModel()
        self.__updateSelectedMission(model)
        self.__updateMissions(model, True)

    def _onLoaded(self, *args, **kwargs):
        super(MissionSelectionView, self)._onLoaded(*args, **kwargs)
        viewModel = self.getViewModel()
        self._uiLogger.logOpen(viewModel.getMissionId() if viewModel else UNDEFINED_MISSION_ID)

    def _finalize(self):
        self._uiLogger.logClose()
        super(MissionSelectionView, self)._finalize()

    def _getEvents(self):
        viewModel = self.getViewModel()
        return ((viewModel.onLoaded, partial(sendViewLoadedEvent, self.LAYOUT_ID)),
         (viewModel.onQuit, self._quit),
         (viewModel.onMissionSelect, self.__onMissionSelect),
         (self._storyModeCtrl.onSyncDataUpdated, self.__onSyncDataUpdated))

    def __onMissionSelect(self, args):
        self._storyModeCtrl.selectedMissionId = int(args.get('id'))
        with self.getViewModel().transaction() as model:
            isMissionChanged = self.__updateSelectedMission(model)
        model = self.getViewModel()
        if isMissionChanged and model:
            self._uiLogger.logMissionSelectClick(model.getMissionId())

    def __onSyncDataUpdated(self):
        with self.getViewModel().transaction() as model:
            isMissionChanged = self.__updateSelectedMission(model)
            self.__updateMissions(model, False)
        model = self.getViewModel()
        if isMissionChanged and model:
            self._uiLogger.logAutoSelect(model.getMissionId())

    def __updateSelectedMission(self, model):
        missionId = self._storyModeCtrl.selectedMissionId
        isMissionChanged = model.getMissionId() != missionId
        model.setMissionId(missionId)
        model.setIsTaskCompleted(self._storyModeCtrl.isMissionCompleted(missionId))
        return isMissionChanged

    def __updateMissions(self, model, fill):
        missionsModel = model.getMissions()
        for idx, mission in enumerate(self._storyModeCtrl.missions.missions):
            if fill:
                missionsModel.addBool(self._storyModeCtrl.isMissionCompleted(mission.missionId))
            missionsModel.setBool(idx, self._storyModeCtrl.isMissionCompleted(mission.missionId))

        missionsModel.invalidate()

    def _quit(self):
        self._uiLogger.logClick(LogButtons.CLOSE)
        super(MissionSelectionView, self)._quit()
