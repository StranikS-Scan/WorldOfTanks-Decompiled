# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: last_stand/scripts/client/last_stand/gui/impl/lobby/pre_battle_queue_view.py
from gui.Scaleform.daapi.settings.views import VIEW_ALIAS
from gui.Scaleform.framework.managers.containers import POP_UP_CRITERIA
from gui.Scaleform.framework.managers.loaders import SFViewLoadParams
from gui.app_loader import sf_lobby
from gui.hangar_cameras.hangar_camera_common import CameraRelatedEvents
from last_stand.gui.impl.lobby.base_view import BaseView
from last_stand.gui.ls_gui_constants import QUEUE_TYPE_TO_DIFFICULTY_LEVEL
from last_stand.gui.prb_control.entities.squad.entity import LastStandSquadEntity
from last_stand.gui.sounds import playSound
from last_stand.gui.sounds.sound_constants import PRE_QUEUE_EXIT, PRE_QUEUE_ENTER
from last_stand_common.last_stand_constants import CURRENT_QUEUE_TYPE_KEY
from helpers import dependency
from gui.impl.gen import R
from frameworks.wulf import ViewFlags, ViewSettings, WindowLayer
from gui.shared import g_eventBus, events, EVENT_BUS_SCOPE
from last_stand.gui.impl.gen.view_models.views.lobby.pre_battle_queue_view_model import PreBattleQueueViewModel
from last_stand.skeletons.difficulty_level_controller import IDifficultyLevelController
from skeletons.gui.app_loader import IAppLoader
_BACKGROUND_ALPHA = 0.0

class PreBattleQueueView(BaseView):
    _difficultyLevelCtrl = dependency.descriptor(IDifficultyLevelController)
    _appLoader = dependency.descriptor(IAppLoader)

    def __init__(self, layoutID=R.views.last_stand.mono.lobby.prebattle_queue_view(), startTime=None):
        settings = ViewSettings(layoutID)
        settings.flags = ViewFlags.LOBBY_SUB_VIEW
        settings.model = PreBattleQueueViewModel()
        self.__startTime = startTime
        super(PreBattleQueueView, self).__init__(settings)

    @property
    def viewModel(self):
        return super(PreBattleQueueView, self).getViewModel()

    def _onLoading(self, *args, **kwargs):
        super(PreBattleQueueView, self)._onLoading(*args, **kwargs)
        self._loadModel()
        app = self._appLoader.getApp()
        app.setBackgroundAlpha(_BACKGROUND_ALPHA)

    def _loadModel(self):
        with self.getViewModel().transaction() as model:
            model.setSelectedDifficultyLevel(self.__getSelectedDifficultyLevel())
            permissions = self.prbEntity.getPermissions()
            model.setIsExitButtonAvailable(permissions.canExitFromQueue())
            model.setTimerStartTime(self.__startTime)

    def _getEvents(self):
        return [(self.viewModel.onExitBattle, self.__onExitBattleButtonClick), (self.viewModel.onEscape, self.__onEscape), (self.viewModel.onMoveSpace, self.__onMoveSpace)]

    def _initialize(self, *args, **kwargs):
        super(PreBattleQueueView, self)._initialize()
        playSound(PRE_QUEUE_ENTER)

    def _finalize(self):
        playSound(PRE_QUEUE_EXIT)
        super(PreBattleQueueView, self)._finalize()

    def __onExitBattleButtonClick(self):
        self.prbEntity.exitFromQueue()

    @sf_lobby
    def __app(self):
        return None

    def __onEscape(self):
        dialogsContainer = self.__app.containerManager.getContainer(WindowLayer.TOP_WINDOW)
        if not dialogsContainer.getView(criteria={POP_UP_CRITERIA.VIEW_ALIAS: VIEW_ALIAS.LOBBY_MENU}):
            g_eventBus.handleEvent(events.LoadViewEvent(SFViewLoadParams(VIEW_ALIAS.LOBBY_MENU)), scope=EVENT_BUS_SCOPE.LOBBY)

    @staticmethod
    def __onMoveSpace(moveTypeArgs=None):
        if moveTypeArgs is None:
            return
        else:
            g_eventBus.handleEvent(CameraRelatedEvents(CameraRelatedEvents.LOBBY_VIEW_MOUSE_MOVE, ctx=moveTypeArgs), EVENT_BUS_SCOPE.GLOBAL)
            g_eventBus.handleEvent(events.LobbySimpleEvent(events.LobbySimpleEvent.NOTIFY_SPACE_MOVED, ctx=moveTypeArgs), EVENT_BUS_SCOPE.GLOBAL)
            return

    def __getSelectedDifficultyLevel(self):
        if isinstance(self.prbEntity, LastStandSquadEntity):
            _, unit = self.prbEntity.getUnit()
            if unit:
                queueType = unit._extras.get(CURRENT_QUEUE_TYPE_KEY)
                return QUEUE_TYPE_TO_DIFFICULTY_LEVEL[queueType].value
        return self._difficultyLevelCtrl.getSelectedLevel().value
