# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: comp7/scripts/client/comp7/gui/impl/battle/vehicle_ban/ban_helpers.py
import typing
import BigWorld
import logging
from comp7.gui.impl.gen.view_models.views.battle.constants import Constants
from comp7.gui.impl.gen.view_models.views.battle.enums import BanState
from comp7_core_constants import ArenaPrebattlePhase
from constants import VEHICLE_SELECTION_BLOCK_DELAY
from gui.impl.lobby.common.vehicle_model_helpers import fillVehicleModel
from helpers import dependency
from skeletons.gui.battle_session import IBattleSessionProvider
from skeletons.gui.game_control import IComp7Controller
from skeletons.gui.shared import IItemsCache
if typing.TYPE_CHECKING:
    from typing import Optional
_logger = logging.getLogger(__name__)

def convertVehicleCD(vehicleCD):
    if vehicleCD is None:
        return Constants.NO_ANY_SELECTIONS_CD
    else:
        return Constants.NO_SELECTED_VEHICLE_CD if not vehicleCD else vehicleCD


@dependency.replace_none_kwargs(itemsCache=IItemsCache)
def fillComp7VehicleModel(model, vehicleCD, itemsCache=None):
    if not vehicleCD:
        model.setVehicleCD(convertVehicleCD(vehicleCD))
        return
    vehicleItem = itemsCache.items.getItemByCD(vehicleCD)
    fillVehicleModel(model, vehicleItem)
    model.setRoleSkill(_getRoleEquipmentKey(vehicleItem))
    model.setOriginalVehicleCD(_getOriginalVehicleCD(vehicleCD))


@dependency.replace_none_kwargs(comp7Controller=IComp7Controller)
def _getRoleEquipmentKey(vehicleItem, comp7Controller=None):
    return comp7Controller.getRoleEquipmentKey(vehicleItem.descriptor.type)


@dependency.replace_none_kwargs(comp7Controller=IComp7Controller)
def _getOriginalVehicleCD(vehicleCD, comp7Controller=None):
    vehicleCopiesInfo = comp7Controller.vehicleCopiesInfo
    originalCD = vehicleCD
    if originalCD in vehicleCopiesInfo:
        originalCD = vehicleCopiesInfo.getRoot(originalCD)
    return originalCD


@dependency.replace_none_kwargs(sessionProvider=IBattleSessionProvider)
def getOwnDatabaseID(sessionProvider=None):
    arenaDP = sessionProvider.getArenaDP()
    if arenaDP is None:
        return
    else:
        isObserver = arenaDP.getVehicleInfo().isObserver()
        if not isObserver:
            return arenaDP.getVehicleInfo().player.accountDBID
        attachedVehicleID = arenaDP.getAttachedVehicleID()
        return arenaDP.getVehicleInfo(attachedVehicleID).player.accountDBID


@dependency.replace_none_kwargs(comp7Controller=IComp7Controller, sessionProvider=IBattleSessionProvider)
def fillBanProgressionModel(model, vehicleBanCtrl, comp7Controller=None, sessionProvider=None):
    startTimestamp, endTimestamp = (0, 0)
    banPhase = vehicleBanCtrl.getArenaPrebattlePhase() if vehicleBanCtrl is not None else ArenaPrebattlePhase.NONE
    if banPhase == ArenaPrebattlePhase.NONE:
        model.setBanState(BanState.NONE)
    elif banPhase == ArenaPrebattlePhase.PREPICK:
        model.setBanState(BanState.PREPICK)
        startTimestamp = vehicleBanCtrl.vehiclePrepickEndTime - comp7Controller.bans.get('prepickPhaseDuration', 0)
        endTimestamp = vehicleBanCtrl.vehiclePrepickEndTime
    elif banPhase == ArenaPrebattlePhase.VOTING:
        model.setBanState(BanState.VOTING)
        startTimestamp = vehicleBanCtrl.vehiclePrepickEndTime
        endTimestamp = vehicleBanCtrl.vehicleBanEndTime
    else:
        model.setBanState(BanState.FINISHED)
        startTimestamp = vehicleBanCtrl.vehicleBanEndTime
        endTimestamp = sessionProvider.arenaVisitor.getArenaPeriodEndTime() - VEHICLE_SELECTION_BLOCK_DELAY
    startTimestamp = int(round(startTimestamp))
    endTimestamp = int(round(endTimestamp))
    if startTimestamp > endTimestamp:
        _logger.error('Incorrect timestamps range: startTimestamp=%d, endTimestamp=%d', startTimestamp, endTimestamp)
        return
    else:
        serverTimestamp = int(round(BigWorld.serverTime()))
        if serverTimestamp < startTimestamp or serverTimestamp > endTimestamp:
            serverTimestamp = startTimestamp
        model.setStartTimestamp(startTimestamp)
        model.setEndTimestamp(endTimestamp)
        model.setServerTimestamp(serverTimestamp)
        return
