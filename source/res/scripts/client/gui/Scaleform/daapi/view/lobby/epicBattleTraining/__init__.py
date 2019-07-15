# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/epicBattleTraining/__init__.py
from gui.Scaleform.framework import ViewSettings, ViewTypes
from gui.Scaleform.framework import GroupedViewSettings, ScopeTemplates
from gui.Scaleform.framework.package_layout import PackageBusinessHandler
from gui.app_loader.settings import APP_NAME_SPACE
from gui.shared import EVENT_BUS_SCOPE
from gui.Scaleform.genConsts.PREBATTLE_ALIASES import PREBATTLE_ALIASES

def getContextMenuHandlers():
    pass


def getViewSettings():
    from gui.Scaleform.daapi.view.lobby.epicBattleTraining.epic_battles_list import EpicBattlesList
    from gui.Scaleform.daapi.view.lobby.epicBattleTraining.epic_battle_training_room import EpicBattleTrainingRoom
    from gui.Scaleform.daapi.view.lobby.trainings.TrainingSettingsWindow import TrainingSettingsWindow
    return [ViewSettings(PREBATTLE_ALIASES.EPICBATTLE_LIST_VIEW_PY, EpicBattlesList, 'trainingForm.swf', ViewTypes.LOBBY_SUB, PREBATTLE_ALIASES.EPICBATTLE_LIST_VIEW_PY, ScopeTemplates.DEFAULT_SCOPE, True), ViewSettings(PREBATTLE_ALIASES.EPIC_TRAINING_ROOM_VIEW_PY, EpicBattleTrainingRoom, 'EpicBattleTrainingRoom.swf', ViewTypes.LOBBY_SUB, PREBATTLE_ALIASES.EPIC_TRAINING_ROOM_VIEW_PY, ScopeTemplates.DEFAULT_SCOPE, True), GroupedViewSettings(PREBATTLE_ALIASES.EPIC_TRAINING_SETTINGS_WINDOW_PY, TrainingSettingsWindow, 'trainingWindow.swf', ViewTypes.WINDOW, PREBATTLE_ALIASES.EPIC_TRAINING_SETTINGS_WINDOW_PY, None, ScopeTemplates.DEFAULT_SCOPE, True)]


def getBusinessHandlers():
    return (_EpicBattlePackageBusinessHandler(),)


class _EpicBattlePackageBusinessHandler(PackageBusinessHandler):

    def __init__(self):
        listeners = ((PREBATTLE_ALIASES.EPICBATTLE_LIST_VIEW_PY, self.loadViewByCtxEvent), (PREBATTLE_ALIASES.EPIC_TRAINING_ROOM_VIEW_PY, self.loadViewByCtxEvent), (PREBATTLE_ALIASES.EPIC_TRAINING_SETTINGS_WINDOW_PY, self.loadViewByCtxEvent))
        super(_EpicBattlePackageBusinessHandler, self).__init__(listeners, APP_NAME_SPACE.SF_LOBBY, EVENT_BUS_SCOPE.LOBBY)
