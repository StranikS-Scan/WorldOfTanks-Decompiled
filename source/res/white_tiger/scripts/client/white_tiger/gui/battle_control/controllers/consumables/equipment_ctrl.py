# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: white_tiger/scripts/client/white_tiger/gui/battle_control/controllers/consumables/equipment_ctrl.py
import Event
from gui.battle_control.controllers.consumables.equipment_ctrl import EquipmentsReplayPlayer, EquipmentsController
from gui.shared.utils.MethodsRules import MethodsRules
from helpers import dependency
from skeletons.gui.battle_session import IBattleSessionProvider
from constants import ARENA_PERIOD
from white_tiger.gui.battle_control.controllers.consumables.equipment_items import WTRepairKit, WTMedKitItem, WTPassiveHeal, WTUnionStrength, WTInvisibilityModA, WTInvisibilityModB, WTHyperionModA, WTHyperionModB, WTTeleportModA, WTTeleportModB, WTStunArea, WTChargedShot, WTBarrier, WTNitro, WTDamageShield, WTExplosiveShot, WTImpulseModA, WTVampirism, WTDecreaseReloadTime, WTGroupRepair, WTCloneItem, WTMissile, WTSmokeScreen, WTPlasmaRetention, WTStunAreaModA, WTIncreaseDamage, WTExtractorShot, WTExplosiveDamageShield, WTDome
_EQ_TYPES = {'wt_repairkit': WTRepairKit,
 'wt_medkit': WTMedKitItem,
 'wt_passive_heal': WTPassiveHeal,
 'wt_union_strength': WTUnionStrength,
 'wt_invisibility_mod_a': WTInvisibilityModA,
 'wt_invisibility_mod_b': WTInvisibilityModB,
 'wt_hyperion_mod_a': WTHyperionModA,
 'wt_hyperion_mod_b': WTHyperionModB,
 'wt_teleport_mod_a': WTTeleportModA,
 'wt_teleport_mod_b': WTTeleportModB,
 'wt_stun_area': WTStunArea,
 'wt_charged_shot': WTChargedShot,
 'wt_nitro': WTNitro,
 'wt_barrier': WTBarrier,
 'wt_damage_shield': WTDamageShield,
 'wt_explosive_shot': WTExplosiveShot,
 'wt_impulse_mod_a': WTImpulseModA,
 'wt_vampirism': WTVampirism,
 'wt_decrease_reload_time': WTDecreaseReloadTime,
 'wt_group_repair': WTGroupRepair,
 'wt_clone': WTCloneItem,
 'wt_missile': WTMissile,
 'wt_smoke_screen': WTSmokeScreen,
 'wt_plasma_retention': WTPlasmaRetention,
 'wt_stun_area_mod_a': WTStunAreaModA,
 'wt_increase_damage': WTIncreaseDamage,
 'wt_extractor_shot': WTExtractorShot,
 'wt_explosive_damage_shield': WTExplosiveDamageShield,
 'wt_dome': WTDome}

class WhiteTigerEquipmentController(EquipmentsController):
    __sessionProvider = dependency.descriptor(IBattleSessionProvider)

    def __init__(self, setup):
        super(WhiteTigerEquipmentController, self).__init__(setup)
        self.onDebuffEquipmentChanged = Event.Event(self._eManager)

    @classmethod
    def createItem(cls, descriptor, quantity, stage, timeRemaining, totalTime):
        clazz = _EQ_TYPES.get(descriptor.name)
        if not clazz:
            return None
        else:
            item = clazz(descriptor, quantity, stage, timeRemaining, totalTime, descriptor.tags)
            return item

    @MethodsRules.delayable('notifyPlayerVehicleSet')
    def setEquipment(self, intCD, quantity, stage, timeRemaining, totalTime):
        super(WhiteTigerEquipmentController, self).setEquipment(intCD, quantity, stage, timeRemaining, totalTime)
        item = self.getEquipment(intCD)
        return None if item is None else None

    def getEquipment(self, intCD):
        periodCtrl = self.__sessionProvider.shared.arenaPeriod
        if periodCtrl and periodCtrl.getPeriod() <= ARENA_PERIOD.WAITING:
            return
        else:
            try:
                item = self._equipments[intCD]
            except KeyError:
                item = None

            return item

    def getItemIDx(self, intCD):
        return self._order.index(intCD) + 1


class WhiteTigerReplayConsumablesPanelMeta(EquipmentsReplayPlayer, WhiteTigerEquipmentController):
    pass
