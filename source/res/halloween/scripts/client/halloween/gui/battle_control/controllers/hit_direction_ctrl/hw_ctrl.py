# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: halloween/scripts/client/halloween/gui/battle_control/controllers/hit_direction_ctrl/hw_ctrl.py
from __future__ import absolute_import
from gui.battle_control.controllers.hit_direction_ctrl.ctrl import HitDirectionController
from gui.battle_control.controllers.hit_direction_ctrl.hit_data import HitData
from gui.battle_control.controllers.hit_direction_ctrl.base import HitType
from halloween.gui.hw_vehicle_role_helper import getVehicleRole

class HWHitDirectionController(HitDirectionController):

    def addHit(self, hitDirYaw, attackerID, damage, isBlocked, critFlags, isHighExplosive, damagedID, attackReasonID):
        arenaDP = self._HitDirectionController__arenaDP
        atackerVehInfo = arenaDP.getVehicleInfo(attackerID)
        atackerVehType = atackerVehInfo.vehicleType
        atackerVehName = atackerVehType.shortNameWithPrefix
        isAlly = arenaDP.isAllyTeam(atackerVehInfo.team)
        playerVehType = arenaDP.getVehicleInfo(damagedID).vehicleType
        classTag = atackerVehType.classTag
        role = getVehicleRole(atackerVehType)
        if role:
            classTag = 'hw_' + role
        if atackerVehInfo.isEnemy():
            atackerVehName = atackerVehType.name
        hitData = HitData(yaw=hitDirYaw, attackerID=attackerID, isAlly=isAlly, damage=damage, attackerVehName=atackerVehName, isBlocked=isBlocked, attackerVehClassTag=classTag, critFlags=critFlags, playerVehMaxHP=playerVehType.maxHealth, isHighExplosive=isHighExplosive, attackReasonID=attackReasonID, friendlyFireMode=self._HitDirectionController__isFriendlyFireMode())
        uiHitComponents = self._HitDirectionController__uiHitComponents
        return uiHitComponents[HitType.HIT_DAMAGE].pull.addHit(hitData)


class HWHitDirectionControllerPlayer(HWHitDirectionController):

    def stopControl(self):
        self._hideAllHits()
        super(HWHitDirectionControllerPlayer, self).stopControl()
