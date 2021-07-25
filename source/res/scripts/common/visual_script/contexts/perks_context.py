# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/common/visual_script/contexts/perks_context.py
import weakref
from constants import BASE_DAMAGE_MONITORING_DELAY
from VSPlanEvents import OnVehicleEquipmentActivated, OnInnerDeviceWasCrit, OnVehicleTotalDamageDealtIncrease, OnVehicleAssistIncrease, OnVehicleInRange, OnVehicleShotDamagedEnemyVehicle, OnVehicleRadioDistanceChange, OnWitnessEnemyDamaged
from visual_script.slot_types import SLOT_TYPE
from visual_script.context import VScriptContext, vse_get_property, vse_func_call, vse_forward_event

class PerkContext(VScriptContext):
    OnVehicleStartMoving = vse_forward_event('OnVehicleStartMoving', (), display_name='OnVehicleStartMoving', description='On vehicle start moving')
    OnVehicleStopMoving = vse_forward_event('OnVehicleStopMoving', (), display_name='OnVehicleStopMoving', description='On vehicle stop moving')
    OnVehicleStartFwdMoving = vse_forward_event('OnVehicleStartFwdMoving', (), display_name='OnVehicleStartFwdMoving', description='On vehicle start forward moving')
    OnVehicleStopFwdMoving = vse_forward_event('OnVehicleStopFwdMoving', (), display_name='OnVehicleStopFwdMoving', description='On vehicle stop forward moving')
    OnVehicleShoot = vse_forward_event('OnVehicleShoot', (), display_name='OnVehicleShoot', description='On vehicle shoot')
    OnVehicleStun = vse_forward_event('OnVehicleStun', (), display_name='OnVehicleStun', description='On vehicle stun')
    OnVehicleStunOff = vse_forward_event('OnVehicleStunOff', (), display_name='OnVehicleStunOff', description='On vehicle stun off')
    OnVehicleFireStarted = vse_forward_event('OnVehicleFireStarted', (), display_name='OnVehicleFireStarted', description='On vehicle fire started')
    OnVehicleFireStopped = vse_forward_event('OnVehicleFireStopped', (), display_name='OnVehicleFireStopped', description='On vehicle fire stopped')
    OnVehicleBlockDamage = vse_forward_event('OnVehicleBlockDamage', (), display_name='OnVehicleBlockDamage', description='On vehicle block damage')
    OnVehicleChangeHealth = vse_forward_event('OnVehicleChangeHealth', (), display_name='OnVehicleChangeHealth', description='On vehicle change health')
    OnVehicleDeviceWasCrit = vse_forward_event('OnVehicleDeviceWasCrit', (), display_name='OnVehicleDeviceWasCrit', description='On vehicle device was crit')
    OnVehicleTankmanWasCrit = vse_forward_event('OnVehicleTankmanWasCrit', (), display_name='OnVehicleTankmanWasCrit', description='On vehicle tankman was crit')
    OnVehicleTankmanHealed = vse_forward_event('OnVehicleTankmanHealed', (), display_name='OnVehicleTankmanHealed', description='On vehicle tankman healed')
    OnVehicleDeviceHealed = vse_forward_event('OnVehicleDeviceHealed', (), display_name='OnVehicleDeviceHealed', description='On vehicle device healed')
    OnVehicleGunReloadFinished = vse_forward_event('OnVehicleGunReloadFinished', (), display_name='OnVehicleGunReloadFinished', description='On vehicle gun reload finished')
    OnEnemyDetected = vse_forward_event('OnEnemyDetected', (), display_name='OnEnemyDetected', description='On enemy detected')
    OnVehicleSixthSenseActivate = vse_forward_event('OnVehicleSixthSenseActivate', (), display_name='OnVehicleSixthSenseActivate', description='On vehicle sixth sense activate')
    OnVehicleChangeShellsByClient = vse_forward_event('OnVehicleChangeShellsByClient', (), display_name='OnVehicleChangeShellsByClient', description='On vehicle change shells by client')
    OnVehicleOnTargetKilled = vse_forward_event('OnVehicleOnTargetKilled', (), display_name='OnVehicleOnTargetKilled', description='On vehicle on target killed')
    OnVehicleOnTargetCrit = vse_forward_event('OnVehicleOnTargetCrit', (), display_name='OnVehicleOnTargetCrit', description='On vehicle on target crit')
    OnInnerDeviceWasCrit = vse_forward_event(OnInnerDeviceWasCrit.__name__, zip(OnInnerDeviceWasCrit._fields, (SLOT_TYPE.INT,)), display_name='OnInnerDeviceWasCrit', description='On inner device was crit')
    OnVehicleEquipmentActivated = vse_forward_event(OnVehicleEquipmentActivated.__name__, zip(OnVehicleEquipmentActivated._fields, (SLOT_TYPE.INT, SLOT_TYPE.STR)), display_name='OnEquipmentActivated', description='On equipment activated')
    OnVehicleTotalDamageDealtIncrease = vse_forward_event(OnVehicleTotalDamageDealtIncrease.__name__, zip(OnVehicleTotalDamageDealtIncrease._fields, (SLOT_TYPE.INT,)), display_name='OnVehicleTotalDamageDealtIncrease', description='On vehicle total damage dealt increase')
    OnVehicleAssistIncrease = vse_forward_event(OnVehicleAssistIncrease.__name__, zip(OnVehicleAssistIncrease._fields, (SLOT_TYPE.INT,)), display_name='OnVehicleAssistIncrease', description='On vehicle assist increase')
    OnVehicleInRange = vse_forward_event(OnVehicleInRange.__name__, zip(OnVehicleInRange._fields, (SLOT_TYPE.INT, SLOT_TYPE.STR, SLOT_TYPE.BOOL)), display_name='OnVehicleInRange', description='On vehicle in range')
    OnVehicleShotDamagedEnemyVehicle = vse_forward_event(OnVehicleShotDamagedEnemyVehicle.__name__, zip(OnVehicleShotDamagedEnemyVehicle._fields, (SLOT_TYPE.INT,)), display_name='OnVehicleShotDamagedEnemyVehicle', description='On vehicle shot damaged enemy vehicle')
    OnWitnessEnemyDamaged = vse_forward_event(OnWitnessEnemyDamaged.__name__, zip(OnWitnessEnemyDamaged._fields, (SLOT_TYPE.INT,)), display_name='OnWitnessEnemyDamaged', description='Vehicle has been damage in our vision')
    OnVehicleRadioDistanceChange = vse_forward_event(OnVehicleRadioDistanceChange.__name__, zip(OnVehicleRadioDistanceChange._fields, (SLOT_TYPE.FLOAT,)), display_name='OnVehicleRadioDistanceChange', description='On vehicle radio distance change', display_group='Aura')
    OnPerkRestarted = vse_forward_event('OnPerkRestarted', (), display_name='onPerkRestarted', description='On perk restarted', display_group='Perk')

    def __init__(self, aspectImplClass, perksControllerWeakRef, perkID, perkLevel, scopeID):
        super(PerkContext, self).__init__(aspectImplClass.ASPECT)
        self._aspectImpl = aspectImplClass(perksControllerWeakRef, perkID, perkLevel, scopeID)

    @property
    def perkID(self):
        return self._aspectImpl.perkID

    @property
    def perkLevel(self):
        return self._aspectImpl.perkLevel

    @property
    def scopeID(self):
        return self._aspectImpl.scopeID

    @property
    def vehicleID(self):
        return self._aspectImpl.vehicleID

    @vse_get_property(SLOT_TYPE.PERK, display_name='Self', description='Perk reference', display_group='Perk')
    def getSelf(self):
        return weakref.proxy(self)

    @vse_get_property(SLOT_TYPE.VEHICLE, display_name='Vehicle', description='Vehicle entity', display_group='Perk')
    def getVehicle(self):
        return self._aspectImpl.vehicle

    @vse_get_property(SLOT_TYPE.INT, display_name='PerkID', description='Perk ID', display_group='Perk/Support')
    def getPerkID(self):
        return self._aspectImpl.perkID

    @vse_get_property(SLOT_TYPE.INT, display_name='Level', description='Perk level', display_group='Perk/Support')
    def getLevel(self):
        return self._aspectImpl.perkLevel

    @vse_get_property(SLOT_TYPE.INT, display_name='VehicleID', description='Vehicle ID', display_group='Perk/Support')
    def getVehicleID(self):
        return self._aspectImpl.vehicleID

    @vse_get_property(SLOT_TYPE.FLOAT, display_name='BaseDamageMonitoringDelay', description='Base value for time in crosshair before damage monitoring starts, reduced with perk levels', display_group='Perk_201')
    def getBaseDamageMonitoringDelay(self):
        return BASE_DAMAGE_MONITORING_DELAY

    @vse_func_call(None, (SLOT_TYPE.STR, SLOT_TYPE.FLOAT), display_name='AddFactorModifier', description='Adds a modifier for a specified factor', display_group='Perk')
    def addFactorModifier(self, factor, value):
        self._aspectImpl.addFactorModifier(factor, value)

    @vse_func_call(None, (SLOT_TYPE.STR, SLOT_TYPE.FLOAT), display_name='AddAuraModifier', description='Adds a modifier to aura scope', display_group='Aura')
    def addAuraModifier(self, factor, value):
        self._aspectImpl.addAuraModifier(factor, value)

    @vse_func_call(None, (SLOT_TYPE.INT, SLOT_TYPE.FLOAT, SLOT_TYPE.FLOAT), display_name='StartAura', descrption='Starts aura loop', display_group='Aura')
    def startAura(self, targetTeam, startRadius, interval):
        self._aspectImpl.startAura(targetTeam, startRadius, interval)

    @vse_func_call(None, (SLOT_TYPE.FLOAT,), display_name='SetAuraRange', description='Set range for aura', display_group='Aura')
    def setAuraRange(self, radius):
        self._aspectImpl.setAuraRange(radius)

    @vse_func_call(None, (SLOT_TYPE.STR, SLOT_TYPE.INT), display_name='RemoveFactorModifiers', description='Remove modifier by count', display_group='Perk')
    def removeFactorModifiers(self, factor, numMods):
        self._aspectImpl.removeFactorModifiers(factor, numMods)

    @vse_func_call(None, (), display_name='DropAllPerkModifiers', description='Reset all perk modifiers', display_group='Perk')
    def dropAllPerkModifiers(self):
        self._aspectImpl.dropAllPerkModifiers()

    @vse_func_call(None, (SLOT_TYPE.BOOL,), display_name='SetCanSeeDamagedDevices', description='Allows vehicle to see damaged/destroyed devices/crew of other vehicles', display_group='Perk')
    def setCanSeeDamagedDevices(self, enabled):
        self._aspectImpl.setCanSeeDamagedDevices(enabled)

    @vse_func_call(None, (), display_name='StartPerkNotify', description='Notify perk controller about the starting the plan', display_group='Perk')
    def startPerkNotify(self):
        self._aspectImpl.startPerkNotify()

    @vse_func_call(None, (SLOT_TYPE.INT, SLOT_TYPE.STR, SLOT_TYPE.FLOAT), display_name='NotifyOnClient', description='Notify client on perk state change to perks panel', display_group='Perk')
    def notifyOnClient(self, stacks, state, lifeTime):
        self._aspectImpl.notifyOnClient(stacks, state, lifeTime)

    @vse_func_call(None, (SLOT_TYPE.INT,), display_name='NotifyOnClientRibbon', description='Notify client on perk to ribbon panel', display_group='Perk')
    def notifyOnClientRibbon(self, stacks):
        self._aspectImpl.notifyOnClientRibbon(stacks)

    @vse_func_call(None, (SLOT_TYPE.FLOAT,), display_name='SetAmmoChangeFactorForVehicle', description='Set ammo change factor for vehicle (information only, does not change TTC)', display_group='Perk_303')
    def setAmmoChangeFactorForVehicle(self, factor):
        self._aspectImpl.setAmmoChangeFactorForVehicle(factor)

    def setPerkLevel(self, level):
        self._aspectImpl.perkLevel = level
