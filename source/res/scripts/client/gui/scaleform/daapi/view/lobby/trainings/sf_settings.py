# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/trainings/sf_settings.py
from gui.Scaleform.framework.managers.loaders import PackageBusinessHandler
from gui.Scaleform.framework import ViewSettings, GroupedViewSettings, ViewTypes, ScopeTemplates
from gui.Scaleform.genConsts.PREBATTLE_ALIASES import PREBATTLE_ALIASES
from gui.shared import EVENT_BUS_SCOPE
from gui.shared.events import ShowWindowEvent, LoadEvent

def getViewSettings():
    from gui.Scaleform.daapi.view.lobby import trainings
    return [ViewSettings(PREBATTLE_ALIASES.TRAINING_LIST_VIEW_PY, trainings.Trainings, 'trainingForm.swf', ViewTypes.LOBBY_SUB, LoadEvent.LOAD_TRAININGS, ScopeTemplates.DEFAULT_SCOPE), ViewSettings(PREBATTLE_ALIASES.TRAINING_ROOM_VIEW_PY, trainings.TrainingRoom, 'trainingRoom.swf', ViewTypes.LOBBY_SUB, LoadEvent.LOAD_TRAINING_ROOM, ScopeTemplates.DEFAULT_SCOPE), GroupedViewSettings(PREBATTLE_ALIASES.TRAINING_SETTINGS_WINDOW_PY, trainings.TrainingSettingsWindow, 'trainingWindow.swf', ViewTypes.WINDOW, '', None, ScopeTemplates.DEFAULT_SCOPE)]


def getBusinessHandlers():
    return [_TrainingPackageBusinessHandler()]


class _TrainingPackageBusinessHandler(PackageBusinessHandler):

    def __init__(self):
        listeners = [(LoadEvent.LOAD_TRAININGS, self.__loadTrainingListView), (LoadEvent.LOAD_TRAINING_ROOM, self.__loadTrainingRoomView), (ShowWindowEvent.SHOW_TRAINING_SETTINGS_WINDOW, self.__showTrainingSettingsWindow)]
        super(_TrainingPackageBusinessHandler, self).__init__(listeners, EVENT_BUS_SCOPE.LOBBY)

    def __loadTrainingListView(self, _):
        self.app.loadView(PREBATTLE_ALIASES.TRAINING_LIST_VIEW_PY)

    def __loadTrainingRoomView(self, _):
        self.app.loadView(PREBATTLE_ALIASES.TRAINING_ROOM_VIEW_PY)

    def __showTrainingSettingsWindow(self, event):
        alias = name = PREBATTLE_ALIASES.TRAINING_SETTINGS_WINDOW_PY
        self.app.loadView(alias, name, event.ctx)
