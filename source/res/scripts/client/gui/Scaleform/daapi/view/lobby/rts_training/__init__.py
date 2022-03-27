# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/rts_training/__init__.py
from frameworks.wulf import WindowLayer
from gui.Scaleform.framework import ViewSettings
from gui.Scaleform.framework import GroupedViewSettings, ScopeTemplates
from gui.Scaleform.framework.package_layout import PackageBusinessHandler
from gui.Scaleform.genConsts.PREBATTLE_ALIASES import PREBATTLE_ALIASES
from gui.app_loader import settings as app_settings
from gui.shared import EVENT_BUS_SCOPE

def getContextMenuHandlers():
    pass


def getViewSettings():
    from gui.Scaleform.daapi.view.lobby.rts_training.rts_trainings import RtsTrainings
    from gui.Scaleform.daapi.view.lobby.rts_training.rts_training_room import RtsTrainingRoom
    from gui.Scaleform.daapi.view.lobby.rts_training.rts_training_settings_window import RtsTrainingSettingsWindow
    return (ViewSettings(PREBATTLE_ALIASES.RTS_TRAINING_LIST_VIEW_PY, RtsTrainings, 'trainingForm.swf', WindowLayer.SUB_VIEW, PREBATTLE_ALIASES.RTS_TRAINING_LIST_VIEW_PY, ScopeTemplates.LOBBY_SUB_SCOPE, True), ViewSettings(PREBATTLE_ALIASES.RTS_TRAINING_ROOM_VIEW_PY, RtsTrainingRoom, 'trainingRoom.swf', WindowLayer.SUB_VIEW, PREBATTLE_ALIASES.RTS_TRAINING_ROOM_VIEW_PY, ScopeTemplates.DEFAULT_SCOPE, True), GroupedViewSettings(PREBATTLE_ALIASES.RTS_TRAINING_SETTINGS_WINDOW_PY, RtsTrainingSettingsWindow, 'trainingWindow.swf', WindowLayer.WINDOW, PREBATTLE_ALIASES.RTS_TRAINING_SETTINGS_WINDOW_PY, None, ScopeTemplates.DEFAULT_SCOPE, True))


def getBusinessHandlers():
    return (_RtsTrainingPackageBusinessHandler(),)


class _RtsTrainingPackageBusinessHandler(PackageBusinessHandler):

    def __init__(self):
        listeners = ((PREBATTLE_ALIASES.RTS_TRAINING_LIST_VIEW_PY, self.loadViewByCtxEvent), (PREBATTLE_ALIASES.RTS_TRAINING_ROOM_VIEW_PY, self.loadViewByCtxEvent), (PREBATTLE_ALIASES.RTS_TRAINING_SETTINGS_WINDOW_PY, self.loadViewByCtxEvent))
        super(_RtsTrainingPackageBusinessHandler, self).__init__(listeners, app_settings.APP_NAME_SPACE.SF_LOBBY, EVENT_BUS_SCOPE.LOBBY)
