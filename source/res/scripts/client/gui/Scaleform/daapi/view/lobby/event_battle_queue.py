# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/event_battle_queue.py
from gui.Scaleform.daapi.view.meta.EventBattleQueueMeta import EventBattleQueueMeta
from gui.hangar_cameras.hangar_camera_common import CameraRelatedEvents
from SE20SelectableObjectTooltipController import SE20SelectableObjectTooltipController
from gui.impl import backport
from gui.impl.gen import R
from gui.shared import events
from gui.sounds.ambients import BattleQueueEnv
from helpers import dependency
from helpers.time_utils import ONE_MINUTE
from skeletons.gui.game_event_controller import IGameEventController
from skeletons.gui.shared.utils import IHangarSpace
from gui.Scaleform.daapi.view.lobby.LobbySelectableView import LobbySelectableView

class EventBattleQueue(LobbySelectableView, EventBattleQueueMeta, SE20SelectableObjectTooltipController):
    __sound_env__ = BattleQueueEnv
    __background_alpha__ = 0.0
    gameEventController = dependency.descriptor(IGameEventController)
    hangarSpace = dependency.descriptor(IHangarSpace)

    def __init__(self, _=None):
        super(EventBattleQueue, self).__init__()

    def onEscape(self):
        self.prbEntity.exitFromQueue()

    def moveSpace(self, dx, dy, dz):
        self.fireEvent(CameraRelatedEvents(CameraRelatedEvents.LOBBY_VIEW_MOUSE_MOVE, ctx={'dx': dx,
         'dy': dy,
         'dz': dz}))
        self.fireEvent(events.LobbySimpleEvent(events.LobbySimpleEvent.NOTIFY_SPACE_MOVED, ctx={'dx': dx,
         'dy': dy,
         'dz': dz}))

    def notifyCursorOver3dScene(self, isOver3dScene):
        self.fireEvent(events.LobbySimpleEvent(events.LobbySimpleEvent.NOTIFY_CURSOR_OVER_3DSCENE, ctx={'isOver3dScene': isOver3dScene}))
        self.hangarSpace.setVehicleSelectable(isOver3dScene)

    def notifyCursorDragging(self, isDragging):
        self.fireEvent(events.LobbySimpleEvent(events.LobbySimpleEvent.NOTIFY_CURSOR_DRAGGING, ctx={'isDragging': isDragging}))

    def onHighlight3DEntity(self, entity):
        self._onHighlight3DEntity(self.app.getToolTipMgr(), entity)

    def onFade3DEntity(self, entity):
        self._onFade3DEntity(self.app.getToolTipMgr(), entity)

    def _populate(self):
        super(EventBattleQueue, self)._populate()
        commander = self.gameEventController.getSelectedCommander()
        commanderName = backport.text(R.strings.event.unit.name.upper.num(commander.getID())())
        self.as_setSubdivisionNameS(commanderName)
        self._readInterfaceScale()
        self._settingsCore.interfaceScale.onScaleChanged += self._readInterfaceScale

    def _dispose(self):
        self._settingsCore.interfaceScale.onScaleChanged -= self._readInterfaceScale
        super(EventBattleQueue, self)._dispose()

    def _dispatchHeroTankMarkerEvent(self, isDisable):
        pass

    def _getTimerText(self):
        return backport.text(R.strings.menu.prebattle.timerLabel.event())

    def _getTimerLabel(self, time):
        if time >= self.gameEventController.getLongWaitTime():
            provider = self._getProvider()
            if provider.needAdditionalInfo():
                return backport.text(R.strings.menu.prebattle.timerLabelWarning.event(), qLenght=provider.qInfo.get('players', 0))
        return '%d:%02d' % divmod(time, ONE_MINUTE)
