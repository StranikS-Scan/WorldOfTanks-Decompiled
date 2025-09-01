# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: last_stand/scripts/client/last_stand/gui/prb_control/entities/squad/actions_validator.py
from BWUtil import AsyncReturn
from CurrentVehicle import g_currentVehicle
from gui.prb_control.entities.base.squad.actions_handler import SquadActionsHandler
from gui.prb_control.entities.base.squad.actions_validator import SquadActionsValidator, SquadVehiclesValidator
from gui.prb_control.settings import UNIT_RESTRICTION
from gui.shared.gui_items.Vehicle import Vehicle
from last_stand.gui.prb_control.entities.squad.ctx import LastStandSquadSettingsCtx
from last_stand.gui.shared.event_dispatcher import showBattleResult
from last_stand_common.last_stand_constants import UNIT_LS_EXTRA_DATA_KEY, UNIT_DIFFICULTY_LEVELS_KEY, CURRENT_QUEUE_TYPE_KEY
from helpers import dependency
from gui.prb_control.items import ValidationResult
from last_stand.skeletons.ls_controller import ILSController
from shared_utils import findFirst
from skeletons.gui.game_control import IPlatoonController
from gui.prb_control.events_dispatcher import g_eventDispatcher
from wg_async import wg_async

class LastStandSquadActionsHandler(SquadActionsHandler):

    def _updateSquadCtx(self, ctx, squadCtx):
        if ctx is None:
            return
        else:
            initCtx = ctx.getInitCtx()
            if not isinstance(initCtx, LastStandSquadSettingsCtx):
                return
            arenaUniqueID = initCtx.getArenaUniqueID()
            if squadCtx is None:
                squadCtx = {}
            squadCtx.update({'arenaUniqueID': arenaUniqueID})
            return

    def _loadWindow(self, ctx):
        super(LastStandSquadActionsHandler, self)._loadWindow(ctx)
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
        raise AsyncReturn(True)


class LastStandStateValidator(SquadVehiclesValidator):
    lsCtrl = dependency.descriptor(ILSController)
    __platoonCtrl = dependency.descriptor(IPlatoonController)

    def _validate(self):
        if not self.lsCtrl.isBattlesEnabled():
            return ValidationResult(False, UNIT_RESTRICTION.MODE_NOT_AVAILABLE)
        else:
            _, unit = self._entity.getUnit()
            playerInfo = self.__platoonCtrl.getPlayerInfo()
            queueType = None
            if unit and playerInfo:
                queueType = unit._extras.get(CURRENT_QUEUE_TYPE_KEY)
                queueTypes = playerInfo.extraData.get(UNIT_LS_EXTRA_DATA_KEY, {}).get(UNIT_DIFFICULTY_LEVELS_KEY, [])
                if queueType not in queueTypes:
                    return ValidationResult(False, UNIT_RESTRICTION.UNIT_WRONG_DATA)
            vehicle = g_currentVehicle.item
            if vehicle:
                limits = self.lsCtrl.getVehiclesConfig()
                if vehicle.intCD not in limits.allowedVehicles:
                    if vehicle.level not in limits.allowedLevels or vehicle.intCD in limits.forbiddenVehicles or vehicle.type in limits.forbiddenClassTags:
                        return ValidationResult(False, UNIT_RESTRICTION.UNSUITABLE_VEHICLE)
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


class LastStandSquadActionsValidator(SquadActionsValidator):

    def _createVehiclesValidator(self, entity):
        return LastStandStateValidator(entity)
