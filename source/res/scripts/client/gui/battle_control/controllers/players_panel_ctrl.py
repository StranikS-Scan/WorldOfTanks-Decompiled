# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/battle_control/controllers/players_panel_ctrl.py
import logging
import BigWorld
import Event
from gui.battle_control import avatar_getter
from gui.battle_control.arena_info.settings import VEHICLE_STATUS
from gui.battle_control.battle_constants import BATTLE_CTRL_ID
from gui.battle_control.arena_info.interfaces import IPlayersPanelController
from gui.battle_control.arena_info.arena_vos import EventKeys
from gui.shared.players_panel_items import PlayersPanelItems
from helpers import dependency
from gui.shared.gui_items.Vehicle import VEHICLE_TAGS
from gui.wt_event.wt_event_helpers import isBoss, getSpeed, isBossTeam
from skeletons.gui.battle_session import IBattleSessionProvider
_logger = logging.getLogger(__name__)

@dependency.replace_none_kwargs(battleSession=IBattleSessionProvider)
def isBossBot(vehicleID=0, vInfo=None, battleSession=None):
    if vInfo is None:
        arenaDP = battleSession.getArenaDP()
        vInfo = arenaDP.getVehicleInfo(vehicleID)
    tags = vInfo.vehicleType.tags
    return VEHICLE_TAGS.EVENT_BOT in tags and not isBoss(tags)


class IPlayersPanelListener(object):

    def updateCamp(self, campID, vehicles):
        pass

    def destroyCamp(self, campID):
        pass


class PlayersPanelController(IPlayersPanelController):
    __slots__ = ('__eManager', '__processors', '__camps')
    __sessionProvider = dependency.descriptor(IBattleSessionProvider)

    def __init__(self):
        super(PlayersPanelController, self).__init__()
        self.__processors = {PlayersPanelItems.CAMP.name: self.__processCamp,
         PlayersPanelItems.CAPTURED_BOMB.name: self.__processBomb,
         PlayersPanelItems.FREE_BOMB.name: self.__processBomb}
        self.__camps = {}
        self.__eManager = Event.EventManager()
        self.onBombUpdated = Event.Event(self.__eManager)

    def getControllerID(self):
        return BATTLE_CTRL_ID.PLAYERS_PANEL_CTRL

    def setViewComponents(self, *components):
        self._viewComponents = list(components)
        self.invalidateArenaInfo()

    def stopControl(self):
        if self.__processors is not None:
            self.__processors.clear()
            self.__processors = None
        if self.__eManager is not None:
            self.__eManager.clear()
            self.__eManager = None
        if self.__camps is not None:
            self.__camps.clear()
            self.__camps = None
        return

    def show(self, params):
        self.__process(params)

    def hide(self, params):
        self.__process(params)

    def processReplay(self, params):
        self.__process(params)

    def invalidateArenaInfo(self):
        self.invalidateVehiclesInfo(self.__sessionProvider.getArenaDP())

    def invalidateVehiclesInfo(self, arenaDP):
        arenaDP = self.__sessionProvider.getArenaDP()
        for vInfo in arenaDP.getVehiclesInfoIterator():
            self.addVehicleInfo(vInfo, arenaDP)

    def addVehicleInfo(self, vInfo, arenaDP):
        if not isBossBot(vInfo=vInfo):
            return
        campUdo = vInfo.gameModeSpecific.getValue(EventKeys.CAMP.value)
        if campUdo in self.__camps and vInfo.vehicleStatus & VEHICLE_STATUS.IS_ALIVE:
            for component in self._viewComponents:
                component.updateCamp(self.__camps[campUdo], [vInfo])

    def updateStressTimer(self, timerID):
        entity = BigWorld.entities.get(timerID)
        if entity is None:
            return
        else:
            panelComponent = entity.dynamicComponents.get('playersPanelComponent')
            if panelComponent is None:
                return
            bombTimerParams = panelComponent.guiComponent
            if bombTimerParams is not None:
                bombTimerParams.setValuesOnCreate(entity)
                self.__updateBomb(entity, bombTimerParams)
            return

    def __process(self, params):
        if params is None:
            return
        else:
            itemType = params.getType()
            processor = self.__processors.get(itemType)
            if processor is not None:
                processor(params)
            return

    def __processCamp(self, params):
        campUdo = params.campUdo
        campId = params.campId
        if params.isAlive:
            arenaDP = self.__sessionProvider.getArenaDP()
            vInfos = [ vInfo for vInfo in arenaDP.getVehiclesInfoIterator() if isBossBot(vInfo=vInfo) and vInfo.gameModeSpecific.getValue(EventKeys.CAMP.value) == campUdo and vInfo.vehicleStatus & VEHICLE_STATUS.IS_ALIVE ]
            for component in self._viewComponents:
                component.updateCamp(campId, vInfos)

            self.__camps[campUdo] = campId
        else:
            self.__camps.pop(campUdo)
            for component in self._viewComponents:
                component.destroyCamp(campId)

    def __processBomb(self, params):
        entity = BigWorld.entities.get(params.timerID)
        if entity is None:
            return
        else:
            self.__updateBomb(entity, params)
            return

    def __updateBomb(self, entity, params):
        vehicleID = self.__findFollowee(entity) if params.leftTime > 0 else None
        arena = avatar_getter.getArena()
        arenaDP = self.__sessionProvider.getArenaDP()
        if arena is not None:
            if vehicleID:
                arena.onGameModeSpecifcStats(True, {vehicleID: self.__getBombData(params)})
            else:
                for vInfo in arenaDP.getVehiclesInfoIterator():
                    if not isBossTeam(vInfo.team):
                        if params.timerID == vInfo.gameModeSpecific.getValue(EventKeys.BOMB_INDEX.value):
                            arena.onGameModeSpecifcStats(True, {vInfo.vehicleID: self.__getBombData(None)})

        self.onBombUpdated(vehicleID, params)
        return

    @staticmethod
    def __findFollowee(entity):
        followerComponent = entity.dynamicComponents.get('follower')
        return followerComponent.followeeID if followerComponent else None

    @staticmethod
    def __getBombData(params):
        return {EventKeys.BOMB_INDEX.value: params.timerID if params else 0,
         EventKeys.BOMB_GUI_INDEX.value: params.timerGUID if params else 0,
         EventKeys.BOMB_TIME_LEFT.value: params.leftTime if params else 0,
         EventKeys.BOMB_TIME_TOTAL.value: params.totalTime if params else 0,
         EventKeys.IS_BOMB_ON_PAUSE.value: params.isPaused if params else False,
         EventKeys.SPEED.value: getSpeed() * params.factor if params else getSpeed()}
