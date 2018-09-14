# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/trainings/__init__.py
from gui.Scaleform.framework import ViewSettings, ViewTypes
from gui.Scaleform.framework import GroupedViewSettings, ScopeTemplates
from gui.Scaleform.framework.package_layout import PackageBusinessHandler
from gui.Scaleform.genConsts.PREBATTLE_ALIASES import PREBATTLE_ALIASES
from gui.app_loader.settings import APP_NAME_SPACE
from gui.shared import EVENT_BUS_SCOPE

def getViewSettings():
    from gui.Scaleform.daapi.view.lobby.trainings.Trainings import Trainings
    from gui.Scaleform.daapi.view.lobby.trainings.TrainingRoom import TrainingRoom
    from gui.Scaleform.daapi.view.lobby.trainings.TrainingSettingsWindow import TrainingSettingsWindow
    return (ViewSettings(PREBATTLE_ALIASES.TRAINING_LIST_VIEW_PY, Trainings, 'trainingForm.swf', ViewTypes.LOBBY_SUB, PREBATTLE_ALIASES.TRAINING_LIST_VIEW_PY, ScopeTemplates.DEFAULT_SCOPE, True), ViewSettings(PREBATTLE_ALIASES.TRAINING_ROOM_VIEW_PY, TrainingRoom, 'trainingRoom.swf', ViewTypes.LOBBY_SUB, PREBATTLE_ALIASES.TRAINING_ROOM_VIEW_PY, ScopeTemplates.DEFAULT_SCOPE, True), GroupedViewSettings(PREBATTLE_ALIASES.TRAINING_SETTINGS_WINDOW_PY, TrainingSettingsWindow, 'trainingWindow.swf', ViewTypes.WINDOW, PREBATTLE_ALIASES.TRAINING_SETTINGS_WINDOW_PY, None, ScopeTemplates.DEFAULT_SCOPE, True))


def getBusinessHandlers():
    return (_TrainingPackageBusinessHandler(),)


class _TrainingPackageBusinessHandler(PackageBusinessHandler):

    def __init__(self):
        listeners = ((PREBATTLE_ALIASES.TRAINING_LIST_VIEW_PY, self.loadViewByCtxEvent), (PREBATTLE_ALIASES.TRAINING_ROOM_VIEW_PY, self.loadViewByCtxEvent), (PREBATTLE_ALIASES.TRAINING_SETTINGS_WINDOW_PY, self.loadViewByCtxEvent))
        super(_TrainingPackageBusinessHandler, self).__init__(listeners, APP_NAME_SPACE.SF_LOBBY, EVENT_BUS_SCOPE.LOBBY)
