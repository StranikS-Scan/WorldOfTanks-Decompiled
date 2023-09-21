# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/battle_control/controllers/players_panel_ctrl.py
import logging
from gui.battle_control.arena_info.settings import VEHICLE_STATUS
from gui.battle_control.battle_constants import BATTLE_CTRL_ID
from gui.battle_control.arena_info.interfaces import IPlayersPanelController
from gui.battle_control.arena_info.arena_vos import EventKeys
from gui.shared.players_panel_items import PlayersPanelItems
from helpers import dependency
from gui.shared.gui_items.Vehicle import VEHICLE_TAGS
from gui.wt_event.wt_event_helpers import isBoss
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
    __slots__ = ('__processors', '__camps')
    __sessionProvider = dependency.descriptor(IBattleSessionProvider)

    def __init__(self):
        super(PlayersPanelController, self).__init__()
        self.__processors = {PlayersPanelItems.CAMP.name: self.__processCamp}
        self.__camps = {}

    def getControllerID(self):
        return BATTLE_CTRL_ID.PLAYERS_PANEL_CTRL

    def setViewComponents(self, *components):
        self._viewComponents = list(components)
        self.invalidateArenaInfo()

    def stopControl(self):
        if self.__processors is not None:
            self.__processors.clear()
            self.__processors = None
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
