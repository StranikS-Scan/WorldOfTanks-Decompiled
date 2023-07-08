# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: fun_random/scripts/client/fun_random/gui/feature/sub_systems/fun_hidden_vehicles.py
import typing
from account_helpers import AccountSettings
from account_helpers.AccountSettings import CURRENT_VEHICLE
from adisp import adisp_process
from CurrentVehicle import g_currentVehicle
from fun_random.gui.feature.util.fun_helpers import getVehicleComparisonKey
from fun_random.gui.fun_gui_constants import PREBATTLE_ACTION_NAME
from gui.prb_control.entities.base.ctx import PrbAction
from gui.prb_control.entities.listener import IPrbListener
from gui.shared import events, g_eventBus, EVENT_BUS_SCOPE
from helpers import dependency
from shared_utils import first
from skeletons.gui.game_control import IFunRandomController
from skeletons.gui.shared import IItemsCache
if typing.TYPE_CHECKING:
    from fun_random.gui.feature.sub_modes.base_sub_mode import IFunSubMode

class FunHiddenVehicles(IFunRandomController.IFunHiddenVehicles, IPrbListener):
    __itemsCache = dependency.descriptor(IItemsCache)

    def __init__(self, subModesHolder):
        super(FunHiddenVehicles, self).__init__()
        self.__subModes = subModesHolder

    def fini(self):
        self.__subModes = None
        return

    def startVehiclesListening(self):
        g_eventBus.addListener(events.HangarVehicleEvent.SELECT_VEHICLE_IN_HANGAR, self.__onSelectVehicleInHangar, scope=EVENT_BUS_SCOPE.LOBBY)

    def stopVehiclesListening(self):
        g_eventBus.removeListener(events.HangarVehicleEvent.SELECT_VEHICLE_IN_HANGAR, self.__onSelectVehicleInHangar, scope=EVENT_BUS_SCOPE.LOBBY)

    def updateCurrentVehicle(self, desiredSubMode):
        vehicle = self.__itemsCache.items.getVehicle(AccountSettings.getFavorites(CURRENT_VEHICLE))
        isModeHiddenVehicle = vehicle is not None and vehicle.isOnlyForFunRandomBattles and vehicle.isModeHidden
        isInFunRandom = desiredSubMode is not None
        if not isInFunRandom and isModeHiddenVehicle:
            AccountSettings.setFavorites(CURRENT_VEHICLE, 0)
            g_currentVehicle.selectNoVehicle()
        if isInFunRandom and (vehicle is None or desiredSubMode.isSuitableVehicle(vehicle) is not None):
            suitableVehicles = sorted(desiredSubMode.getSuitableVehicles().itervalues(), key=getVehicleComparisonKey)
            g_currentVehicle.selectGuiVehicle(first(suitableVehicles))
        return

    @adisp_process
    def __onSelectVehicleInHangar(self, event):
        prbDispatcher = self.prbDispatcher
        desiredSubMode = self.__subModes.getDesiredSubMode()
        if prbDispatcher is None or desiredSubMode is None:
            return
        else:
            baseModeCriteria = desiredSubMode.getCarouselBaseCriteria()
            vehicle = self.__itemsCache.items.getVehicle(event.ctx['vehicleInvID'])
            if vehicle is None or baseModeCriteria is None or baseModeCriteria(vehicle):
                return
            prevVehicleInvID = event.ctx['prevVehicleInvID']
            result = yield prbDispatcher.doSelectAction(PrbAction(PREBATTLE_ACTION_NAME.RANDOM))
            if not result and desiredSubMode.isEnabled():
                g_currentVehicle.selectVehicle(prevVehicleInvID)
            return
