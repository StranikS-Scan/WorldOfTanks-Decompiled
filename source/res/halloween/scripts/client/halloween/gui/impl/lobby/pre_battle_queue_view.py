# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: halloween/scripts/client/halloween/gui/impl/lobby/pre_battle_queue_view.py
from __future__ import absolute_import
import random
from CurrentVehicle import g_currentVehicle
from gui.Scaleform.daapi.settings.views import VIEW_ALIAS
from gui.Scaleform.framework.managers.containers import POP_UP_CRITERIA
from gui.Scaleform.framework.managers.loaders import SFViewLoadParams
from gui.app_loader import sf_lobby
from gui.hangar_cameras.hangar_camera_common import CameraRelatedEvents
from gui.impl import backport
from halloween.gui.impl.lobby.base_view import BaseView
from halloween.gui.halloween_gui_constants import QUEUE_TYPE_TO_DIFFICULTY_LEVEL
from halloween.gui.prb_control.entities.squad.entity import HalloweenSquadEntity
from halloween.gui.sounds import playSound
from halloween.gui.sounds.sound_constants import PRE_QUEUE_EXIT, PRE_QUEUE_ENTER
from halloween.skeletons.halloween_controller import IHalloweenController
from halloween_common.halloween_constants import CURRENT_QUEUE_TYPE_KEY
from helpers import dependency
from gui.impl.gen import R
from frameworks.wulf import ViewFlags, ViewSettings, WindowLayer
from gui.shared import g_eventBus, events, EVENT_BUS_SCOPE
from halloween.gui.impl.gen.view_models.views.lobby.pre_battle_queue_view_model import PreBattleQueueViewModel
from halloween.skeletons.difficulty_level_controller import IDifficultyLevelController
from helpers.CallbackDelayer import CallbackDelayer
from skeletons.gui.app_loader import IAppLoader
_BACKGROUND_ALPHA = 0.0

class PreBattleQueueView(BaseView):
    _difficultyLevelCtrl = dependency.descriptor(IDifficultyLevelController)
    _appLoader = dependency.descriptor(IAppLoader)
    _halloweenCtrl = dependency.descriptor(IHalloweenController)

    def __init__(self, layoutID=R.views.halloween.mono.lobby.pre_battle_queue_view(), startTime=None):
        settings = ViewSettings(layoutID)
        settings.flags = ViewFlags.LOBBY_SUB_VIEW
        settings.model = PreBattleQueueViewModel()
        super(PreBattleQueueView, self).__init__(settings)
        self.__startTime = startTime
        self.__callbackDelayer = CallbackDelayer()

    @property
    def viewModel(self):
        return super(PreBattleQueueView, self).getViewModel()

    def _onLoading(self, *args, **kwargs):
        super(PreBattleQueueView, self)._onLoading(*args, **kwargs)
        self._loadModel()
        self._initTipDelayer()
        app = self._appLoader.getApp()
        app.setBackgroundAlpha(_BACKGROUND_ALPHA)

    def _loadModel(self):
        with self.viewModel.transaction() as vm:
            vm.setSelectedDifficultyLevel(self.__getSelectedDifficultyLevel())
            permissions = self.prbEntity.getPermissions()
            vm.setIsExitButtonAvailable(permissions.canExitFromQueue())
            if g_currentVehicle.item is not None:
                vm.setVehicleName(g_currentVehicle.item.userName)
                vm.setVehicleType(g_currentVehicle.item.type)
            vm.setTimerStartTime(self.__startTime)
            vm.setTip(backport.text(R.strings.halloween_lobby.preBattle.mainTip()))
            vm.setIsFirstTip(True)
        return

    def _getEvents(self):
        return [(self.viewModel.onExitBattle, self.__onExitBattleButtonClick), (self.viewModel.onEscape, self.__onEscape), (self.viewModel.onMoveSpace, self.__onMoveSpace)]

    def _initTipDelayer(self):
        tipDelay = self._getTipDelay()
        if tipDelay:
            self.__callbackDelayer.delayCallback(tipDelay, self.__updateTip)

    def _getTipDelay(self):
        return self._halloweenCtrl.getModeSettings().battleQueue.get('tipDelay', 0)

    def _initialize(self, *args, **kwargs):
        super(PreBattleQueueView, self)._initialize(*args, **kwargs)
        playSound(PRE_QUEUE_ENTER)

    def _finalizeTipDelayer(self):
        if self.__callbackDelayer:
            self.__callbackDelayer.destroy()
            self.__callbackDelayer = None
        return

    def _finalize(self):
        playSound(PRE_QUEUE_EXIT)
        self._finalizeTipDelayer()
        super(PreBattleQueueView, self)._finalize()

    def __updateTip(self):
        with self.viewModel.transaction() as vm:
            vm.setTip(backport.text(random.choice(list(R.strings.halloween_lobby.preBattle.tips.values()))()))
            vm.setIsFirstTip(False)
        self._finalizeTipDelayer()

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
        if isinstance(self.prbEntity, HalloweenSquadEntity):
            _, unit = self.prbEntity.getUnit()
            if unit:
                queueType = unit._extras.get(CURRENT_QUEUE_TYPE_KEY)
                return QUEUE_TYPE_TO_DIFFICULTY_LEVEL[queueType].value
        return self._difficultyLevelCtrl.getSelectedLevel().value
