# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: halloween/scripts/client/halloween/gui/prb_control/entities/squad/actions_validator.py
from __future__ import absolute_import
from BWUtil import AsyncReturn
from CurrentVehicle import g_currentVehicle
from gui.prb_control.entities.base.squad.actions_handler import SquadActionsHandler
from gui.prb_control.entities.base.squad.actions_validator import SquadActionsValidator, SquadVehiclesValidator
from gui.prb_control.settings import UNIT_RESTRICTION
from gui.shared.gui_items.Vehicle import Vehicle
from halloween.gui.prb_control.entities import checkVehicleAbilitiesFull
from halloween.gui.prb_control.entities.squad.ctx import HalloweenSquadSettingsCtx
from halloween.gui.shared.event_dispatcher import showBattleResult
from halloween_common.halloween_constants import UNIT_HALLOWEEN_EXTRA_DATA_KEY, UNIT_DIFFICULTY_LEVELS_KEY, CURRENT_QUEUE_TYPE_KEY
from helpers import dependency
from gui.prb_control.items import ValidationResult
from halloween.skeletons.halloween_controller import IHalloweenController
from shared_utils import findFirst
from skeletons.gui.game_control import IPlatoonController
from gui.prb_control.events_dispatcher import g_eventDispatcher
from wg_async import await_callback, wg_async

class HalloweenSquadActionsHandler(SquadActionsHandler):

    def _updateSquadCtx(self, initCtx, squadCtx):
        if initCtx is None:
            return
        else:
            initCtxGeneral = initCtx.getInitCtx()
            if not isinstance(initCtxGeneral, HalloweenSquadSettingsCtx):
                return
            arenaUniqueID = initCtxGeneral.getArenaUniqueID()
            if squadCtx is None:
                squadCtx = {}
            squadCtx.update({'arenaUniqueID': arenaUniqueID})
            return

    def _loadWindow(self, ctx):
        super(HalloweenSquadActionsHandler, self)._loadWindow(ctx)
        arenaUniqueID = ctx.get('arenaUniqueID') if ctx else None
        if arenaUniqueID:
            showBattleResult(arenaUniqueID)
        return

    def setUnitChanged(self, loadHangar=False):
        flags = self._entity.getFlags()
        if self._entity.getPlayerInfo().isReady and flags.isInQueue():
            _, unit = self._entity.getUnit()
            pInfo = self._entity.getPlayerInfo()
            vInfos = unit.getMemberVehicles(pInfo.dbID)
            if vInfos is not None:
                g_currentVehicle.selectVehicle(vInfos[0].vehInvID)
            g_eventDispatcher.loadBattleQueue()
        elif loadHangar:
            g_eventDispatcher.loadHangar()
        return

    @wg_async
    def _checkVehicleAmmo(self, vehicle):
        result = True
        if not self._entity.getPlayerInfo().isReady:
            result = yield await_callback(checkVehicleAbilitiesFull)(vehicle)
        raise AsyncReturn(result)


class HalloweenStateValidator(SquadVehiclesValidator):
    __halloweenBattleCtrl = dependency.descriptor(IHalloweenController)
    __platoonCtrl = dependency.descriptor(IPlatoonController)

    def _validate(self):
        if not self.__halloweenBattleCtrl.isBattlesEnabled():
            return ValidationResult(False, UNIT_RESTRICTION.MODE_NOT_AVAILABLE)
        else:
            _, unit = self._entity.getUnit()
            playerInfo = self.__platoonCtrl.getPlayerInfo()
            if unit and playerInfo:
                queueType = unit._extras.get(CURRENT_QUEUE_TYPE_KEY)
                queueTypes = playerInfo.extraData.get(UNIT_HALLOWEEN_EXTRA_DATA_KEY, {}).get(UNIT_DIFFICULTY_LEVELS_KEY, [])
                if queueType not in queueTypes:
                    return ValidationResult(False, UNIT_RESTRICTION.UNIT_WRONG_DATA)
            vehicle = g_currentVehicle.item
            if vehicle and not self.__halloweenBattleCtrl.hasAccessToVehicle(vehicle.intCD):
                return ValidationResult(False, UNIT_RESTRICTION.VEHICLE_NOT_VALID)
            vInfos = self._getVehiclesInfo()
            if not findFirst(lambda v: not v.isEmpty(), vInfos, False):
                return ValidationResult(False, UNIT_RESTRICTION.VEHICLE_NOT_SELECTED)
            for vInfo in vInfos:
                vehicle = vInfo.getVehicle()
                if vehicle is not None:
                    if not vehicle.isReadyToPrebattle(checkForRent=self._isCheckForRent()):
                        if not vehicle.isCrewFull:
                            return ValidationResult(False, UNIT_RESTRICTION.VEHICLE_CREW_NOT_FULL)
                        if vehicle.isInBattle:
                            return ValidationResult(False, UNIT_RESTRICTION.VEHICLE_IS_IN_BATTLE)
                        return ValidationResult(False, UNIT_RESTRICTION.VEHICLE_NOT_VALID)
                    state, _ = vehicle.getState()
                    if state == Vehicle.VEHICLE_STATE.UNSUITABLE_TO_QUEUE:
                        return ValidationResult(False, UNIT_RESTRICTION.VEHICLE_WRONG_MODE)

            return


class HalloweenSquadActionsValidator(SquadActionsValidator):

    def _createVehiclesValidator(self, entity):
        return HalloweenStateValidator(entity)
