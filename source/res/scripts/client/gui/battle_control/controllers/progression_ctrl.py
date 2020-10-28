# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/battle_control/controllers/progression_ctrl.py
import logging
import BigWorld
import Event
from adisp import process
from constants import UpgradeProhibitionReason
from debug_utils import LOG_ERROR, LOG_WARNING
from gui.Scaleform.genConsts.BATTLE_VIEW_ALIASES import BATTLE_VIEW_ALIASES
from gui.app_loader.decorators import sf_battle
from gui.battle_control import avatar_getter
from gui.battle_control.arena_info.interfaces import IProgressionController
from gui.battle_control.battle_constants import BATTLE_CTRL_ID
from gui.battle_control.view_components import ViewComponentsController
from gui.battle_control.battle_cache.cache_records import TmpBRProgressionCacheRecord, BRInitialModules
from gui.shared.gui_items import GUI_ITEM_TYPE
from gui.shared.gui_items.Vehicle import Vehicle
from items import getTypeOfCompactDescr
from helpers import dependency
from gui.shared.gui_items.processors.module import getPreviewInstallerProcessor
from items.battle_royale import ModulesInstaller
from skeletons.gui.battle_session import IBattleSessionProvider
from skeletons.gui.shared.gui_items import IGuiItemsFactory
from soft_exception import SoftException
_logger = logging.getLogger(__name__)
_MAX_PERCENT_AMOUNT = 100

def createGuiVehicle(strCD):
    return Vehicle(strCompactDescr=strCD)


class IProgressionListener(object):
    MAX_PERCENT_AMOUNT = _MAX_PERCENT_AMOUNT

    def setCurrentXP(self, xp, xpPercent):
        pass

    def setLevel(self, level, minXP, maxXP):
        pass

    def selectVehicleModule(self, index):
        pass

    def onMaxLvlAchieved(self):
        pass

    def setVehicleChanged(self, vehicle, newModuleIntCD, vehicleRecreated):
        pass

    def vehicleChangeRequestSent(self, intCD, successfullySent):
        pass

    def setVehicleChangeResponse(self, intCD, success):
        pass

    def setVehicleVisualChangingStarted(self, vehicleID):
        pass

    def setVehicleVisualChangingFinished(self, vehicleID):
        pass

    def setUpgradeDisabled(self, cooldownTime, reason):
        pass

    def setUpgradeEnabled(self):
        pass

    def setAverageBattleLevel(self, level):
        pass


class _SelectedModulesStorage(object):
    __slots__ = ('__selectedIntCDs',)

    def __init__(self):
        super(_SelectedModulesStorage, self).__init__()
        self.__selectedIntCDs = set([])

    def addIntCD(self, intCD):
        self.__selectedIntCDs.add(intCD)

    def removeIntCD(self, intCD):
        if intCD in self.__selectedIntCDs:
            self.__selectedIntCDs.remove(intCD)

    def isSelected(self, intCD):
        return intCD in self.__selectedIntCDs

    def dispose(self):
        self.__flush()
        self.__selectedIntCDs = None
        return

    def __flush(self):
        pass


class _UpgradesAvailability(object):
    __slots__ = ('__viewComponents', '__cbCooldownID', '__available', '__isStrategicMode')
    __STRATEGIC_MODES = ('mapcase', 'arcadeMapcase')

    def __init__(self, viewComponents):
        super(_UpgradesAvailability, self).__init__()
        self.__viewComponents = viewComponents
        self.__available = True
        self.__cbCooldownID = None
        self.__isStrategicMode = False
        return

    def destroy(self):
        self.__stopPreviousTimer()
        self.__viewComponents = None
        return

    def canUpgrade(self):
        return self.__available and self.__cbCooldownID is None

    def setCooldown(self, cooldownTime, reason):
        timeLeft = cooldownTime - BigWorld.serverTime()
        if timeLeft > 0:
            self.__stopPreviousTimer()
            for listener in self.__viewComponents:
                listener.setUpgradeDisabled(cooldownTime, reason)

            self.__cbCooldownID = BigWorld.callback(timeLeft, self.__checkAvailability)

    def onVehicleStatusChanged(self):
        avatar = BigWorld.player()
        reasons = (UpgradeProhibitionReason.OVERTURNED if avatar.isVehicleOverturned else -1, UpgradeProhibitionReason.DROWNING if avatar.isVehicleDrowning else -1, UpgradeProhibitionReason.COMBATING if self.__cbCooldownID is not None or self.__isStrategicMode else -1)
        reason = max(reasons)
        if reason < 0:
            self.__enableUpgrades()
        else:
            self.__disableUpgrades(reason)
        return

    def onCameraChanged(self, eMode):
        self.__isStrategicMode = eMode in self.__STRATEGIC_MODES
        self.onVehicleStatusChanged()

    def __enableUpgrades(self):
        self.__available = True
        for listener in self.__viewComponents:
            listener.setUpgradeEnabled()

    def __disableUpgrades(self, reason):
        self.__available = False
        for listener in self.__viewComponents:
            listener.setUpgradeDisabled(None, reason)

        return

    def __checkAvailability(self):
        self.__cbCooldownID = None
        self.onVehicleStatusChanged()
        return

    def __stopPreviousTimer(self):
        if self.__cbCooldownID is not None:
            BigWorld.cancelCallback(self.__cbCooldownID)
            self.__cbCooldownID = None
        return


class _ProgressionWindowCtrl(object):
    __slots__ = ('onTriggered', '__progressionWindow')

    def __init__(self):
        super(_ProgressionWindowCtrl, self).__init__()
        self.onTriggered = Event.Event()
        self.__progressionWindow = None
        if self.app:
            self.app.containerManager.onViewAddedToContainer += self.__onViewAddedToContainer
        return

    @sf_battle
    def app(self):
        return None

    def closeWindow(self):
        if self.__progressionWindow:
            self.__progressionWindow.destroy()

    def isWindowOpened(self):
        return self.__progressionWindow is not None

    def dispose(self):
        if self.app:
            self.app.containerManager.onViewAddedToContainer -= self.__onViewAddedToContainer
        self.__disposeProgressionWindow()

    def __onViewAddedToContainer(self, _, pyEntity):
        if pyEntity.getAlias() == BATTLE_VIEW_ALIASES.BATTLE_VEHICLE_CONFIGURATOR:
            self.__disposeProgressionWindow()
            self.__progressionWindow = pyEntity
            self.__progressionWindow.onDispose += self.__onProgressionWindowDisposed
            self.onTriggered(True)

    def __onProgressionWindowDisposed(self, _):
        self.__disposeProgressionWindow()
        self.onTriggered(False)

    def __disposeProgressionWindow(self):
        if self.__progressionWindow:
            self.__progressionWindow.onDispose -= self.__onProgressionWindowDisposed
            self.__progressionWindow = None
        return


class _VehicleHolder(object):
    __slots__ = ('__initialVehicle', '__vehicle', '__maxLevel', '__currentVehicleLevel', '__vehicleChangeCallback', '__modulesHolder')
    __sessionProvider = dependency.descriptor(IBattleSessionProvider)
    __itemsFactory = dependency.descriptor(IGuiItemsFactory)

    def __init__(self, vehicleChangeCallback, modulesHolder):
        super(_VehicleHolder, self).__init__()
        self.__vehicle = None
        self.__initialVehicle = None
        self.__modulesHolder = modulesHolder
        self.__vehicleChangeCallback = vehicleChangeCallback
        self.__maxLevel = 0
        self.__currentVehicleLevel = 0
        self.__initialize()
        return

    @property
    def maxLevel(self):
        return self.__maxLevel

    def installModule(self, module):
        moduleLevel = module.level
        if moduleLevel > self.__currentVehicleLevel:
            self.__processInstallModule(module)
            self.__currentVehicleLevel = moduleLevel
            self.__vehicleChangeCallback(newModuleIntCD=module.intCD)
        else:
            raise SoftException('Incorrect level! Current level=%s, module level=%s', str(self.__currentVehicleLevel), str(moduleLevel))

    @process
    def __processInstallModule(self, module):
        yield getPreviewInstallerProcessor(self.__vehicle, module).request()

    def recreateVehicle(self):
        self.__initialize()

    def setInitialModule(self, intCD):
        self.__initialVehicle.descriptor.installComponent(intCD)

    def setInitialTurret(self, turretCD, gunCD):
        self.__initialVehicle.descriptor.installTurret(turretCD, gunCD)

    def getInitialVehicle(self):
        return self.__initialVehicle

    def getVehicle(self):
        return self.__vehicle

    def getVehicleLevel(self):
        return self.__currentVehicleLevel

    def destroy(self):
        self.__vehicleChangeCallback = None
        self.__vehicle = None
        self.__initialVehicle = None
        self.__modulesHolder = None
        avatar = BigWorld.player()
        avatar.onVehicleEnterWorld -= self.__onVehicleEnterWorld
        return

    def __initialize(self):
        arenaDP = self.__sessionProvider.getArenaDP()
        strCD = arenaDP.getVehicleInfo().vehicleType.strCompactDescr
        if strCD:
            self.__initFromCD(strCD)
        else:
            avatar = BigWorld.player()
            pVehId = avatar_getter.getPlayerVehicleID()
            if pVehId != 0:
                vehicle = BigWorld.entities.get(pVehId)
                if vehicle:
                    self.__initFromCD(vehicle.typeDescriptor.makeCompactDescr())
                    return
            avatar.onVehicleEnterWorld += self.__onVehicleEnterWorld

    def __initFromCD(self, strCD):
        self.__initialVehicle = createGuiVehicle(strCD)
        self.__vehicle = createGuiVehicle(strCD)
        self.__currentVehicleLevel = self.__getCurrentLvl(self.__vehicle)
        if self.__maxLevel == 0:
            self.__maxLevel = self.__calculateMaxLevel(self.__vehicle)
        self.__vehicleChangeCallback(vehicleRecreated=True)

    def __calculateMaxLevel(self, vehicle):
        level = max((self.__modulesHolder.getModule(intCD).level for _, _, intCD, _ in vehicle.getUnlocksDescrs()))
        return level

    def __onVehicleEnterWorld(self, vehicle):
        avatar = BigWorld.player()
        pVehId = avatar_getter.getPlayerVehicleID()
        if vehicle.id == pVehId:
            avatar.onVehicleEnterWorld -= self.__onVehicleEnterWorld
            avatar = BigWorld.player()
            avatarVehicle = avatar.getVehicleAttached()
            if avatarVehicle:
                self.__initFromCD(avatarVehicle.typeDescriptor.makeCompactDescr())

    @staticmethod
    def __getCurrentLvl(vehicle):
        return max(vehicle.turret.level, vehicle.chassis.level, vehicle.engine.level, vehicle.radio.level, vehicle.gun.level)


class _VehicleModulesStorage(object):
    __itemsFactory = dependency.descriptor(IGuiItemsFactory)

    def __init__(self):
        self.__modules = {}

    def destroy(self):
        self.__modules = None
        return

    def getModule(self, intCD):
        return self.__registerItem(getTypeOfCompactDescr(intCD), intCD) if intCD not in self.__modules else self.__modules[intCD]

    def getInstalledOnVehicleAnalogByIntCD(self, intCD, vehicleDescriptor):
        targetModule = self.getModule(intCD)
        currModuleDescr, _ = vehicleDescriptor.getComponentsByType(targetModule.itemTypeName)
        installedModuleIntCD = currModuleDescr.compactDescr
        return self.__registerItem(currModuleDescr.typeID, installedModuleIntCD) if installedModuleIntCD not in self.__modules else self.__modules[installedModuleIntCD]

    def __registerItem(self, typeCD, moduleIntCD):
        self.__modules[moduleIntCD] = newM = self.__itemsFactory.createGuiItem(typeCD, intCompactDescr=moduleIntCD)
        return newM


class _ModuleChangeRequester(object):
    __slots__ = ('__awaitingResponse', '__intCDToUpgrade', '__vehicleInUpgrade')

    def __init__(self):
        super(_ModuleChangeRequester, self).__init__()
        self.__awaitingResponse = set([])
        self.__intCDToUpgrade = []
        self.__vehicleInUpgrade = False

    def destroy(self):
        pass

    def vehicleUpgradeStarted(self):
        self.__vehicleInUpgrade = True

    def vehicleUpgradeFinished(self):
        self.__vehicleInUpgrade = False
        if self.__intCDToUpgrade:
            intCD = self.__intCDToUpgrade.pop(0)
            self.__doRequest(intCD)

    def request(self, moduleItem, vehicle):
        canDoRequest, reason = self.mayInstallModule(moduleItem, vehicle)
        if not canDoRequest:
            _logger.info('%s "%s" could not be installed. %s', moduleItem.itemTypeName, moduleItem.name, reason)
            return False
        moduleIntCD = moduleItem.intCD
        if self.__vehicleInUpgrade:
            self.__intCDToUpgrade.append(moduleIntCD)
        elif self.__intCDToUpgrade:
            self.__intCDToUpgrade.append(moduleIntCD)
        return self.__doRequest(moduleIntCD)

    def mayInstallModule(self, moduleItem, vehicle):
        success, reason = moduleItem.mayInstall(vehicle)
        if success:
            success, reason = ModulesInstaller.checkModuleValidity(moduleItem.intCD, vehicle.descriptor)
        return (success, reason)

    def processResponse(self, intCD, isSuccessfull):
        if intCD not in self.__awaitingResponse:
            _logger.warning('Module %d is not in the waiting list!', intCD)
            return False
        self.__awaitingResponse.remove(intCD)
        return isSuccessfull

    def __doRequest(self, intCD):
        try:
            vehicle = BigWorld.player().getVehicleAttached()
            if vehicle is not None:
                vehicle.inBattleUpgrades.upgradeVehicle(intCD)
                self.__awaitingResponse.add(intCD)
                return True
        except AttributeError as e:
            _logger.exception('Failed to send vehicle upgrade request. %s', str(e))
            return False

        return False


class ProgressionController(IProgressionController, ViewComponentsController):
    __slots__ = ('__currentXP', '__currentXpPercents', 'onPageTriggered', '__progressionWindowCtrl', '__currentLevel', '_viewComponents', '__minXP', '__maxXP', '__modulesStorage', '__averageLevel', '__enemiesAmount', '__vehicleModulesStorage', '__enemyTeamsAmount', '__isStarted', '__upgradesAvailability', '__tmpProgressionRecord', 'onVehicleUpgradeStarted', 'onVehicleUpgradeFinished', '__vehicleHolder', '__moduleChangeReq', '__initialModulesRecord')
    __itemsFactory = dependency.descriptor(IGuiItemsFactory)

    def __init__(self):
        super(ProgressionController, self).__init__()
        self.__currentXP = 0
        self.__currentXpPercents = 0
        self.__currentLevel = 0
        self.__minXP = 0
        self.__maxXP = 0
        self.__modulesStorage = None
        self.__progressionWindowCtrl = None
        self.__upgradesAvailability = None
        self.__averageLevel = None
        self.__enemiesAmount = None
        self.__enemyTeamsAmount = None
        self.__isStarted = False
        self.__vehicleHolder = None
        self.__vehicleModulesStorage = None
        self.__moduleChangeReq = None
        self.__tmpProgressionRecord = TmpBRProgressionCacheRecord.get()
        self.__initialModulesRecord = BRInitialModules.get()
        self.onVehicleUpgradeStarted = Event.Event()
        self.onVehicleUpgradeFinished = Event.Event()
        return

    @property
    def maxLevel(self):
        return self.__vehicleHolder.maxLevel if self.__vehicleHolder else 0

    def getControllerID(self):
        return BATTLE_CTRL_ID.PROGRESSION_CTRL

    def getCurrentVehicle(self):
        return self.__vehicleHolder.getVehicle() if self.__vehicleHolder else None

    def getCurrentVehicleLevel(self):
        return self.__vehicleHolder.getVehicleLevel() if self.__vehicleHolder else None

    def mayInstallModule(self, moduleItem):
        if self.__vehicleHolder and self.__moduleChangeReq:
            success, _ = self.__moduleChangeReq.mayInstallModule(moduleItem, self.getCurrentVehicle())
            return success
        return False

    def mayInstallModuleOnVehicle(self, moduleItem, vehicle):
        if self.__moduleChangeReq:
            success, _ = self.__moduleChangeReq.mayInstallModule(moduleItem, vehicle)
            return success
        return False

    def startControl(self, battleCtx, arenaVisitor):
        self.__vehicleModulesStorage = _VehicleModulesStorage()
        self.__vehicleHolder = _VehicleHolder(self.__notifyVehicleChanged, self.__vehicleModulesStorage)
        pVehId = avatar_getter.getPlayerVehicleID()
        if pVehId != 0:
            vehicle = BigWorld.entities.get(pVehId)
            if vehicle:
                level, minXP, maxXP = vehicle.battleXP.battleXpLvlData
                self.updateLevel(level, minXP, maxXP)
                self.updateXP(vehicle.battleXP.battleXP)
                self.__isStarted = True
                return
        avatar = BigWorld.player()
        avatar.onVehicleEnterWorld += self.__onVehicleEnterWorld
        self.__modulesStorage = _SelectedModulesStorage()
        self.__moduleChangeReq = _ModuleChangeRequester()
        self.__loadCachedProgress()

    def stopControl(self):
        if self.__moduleChangeReq:
            self.__moduleChangeReq.destroy()
            self.__moduleChangeReq = None
        if self.__vehicleHolder:
            self.__vehicleHolder.destroy()
            self.__vehicleHolder = None
        if self.__vehicleModulesStorage:
            self.__vehicleModulesStorage.destroy()
            self.__vehicleModulesStorage = None
        if self.__progressionWindowCtrl:
            self.__progressionWindowCtrl.dispose()
            self.__progressionWindowCtrl = None
        if self.__modulesStorage:
            self.__modulesStorage.dispose()
        self.__modulesStorage = None
        if self.__upgradesAvailability:
            self.__upgradesAvailability.destroy()
        avatar = BigWorld.player()
        avatar.onVehicleEnterWorld -= self.__onVehicleEnterWorld
        if avatar.inputHandler is not None:
            avatar.inputHandler.onCameraChanged -= self.__onCameraChanged
        self.clearViewComponents()
        self.onVehicleUpgradeStarted.clear()
        self.onVehicleUpgradeFinished.clear()
        self.__tmpProgressionRecord = None
        self.__initialModulesRecord = None
        super(ProgressionController, self).stopControl()
        return

    def updateXP(self, xp):
        if self.__currentXP != xp:
            self.__currentXP = xp
            self.__updatePercents()
            for view in self._viewComponents:
                view.setCurrentXP(self.__currentXP, self.__currentXpPercents)

    def updateLevel(self, level, minXP, maxXP):
        if self.__currentLevel != level:
            self.__currentLevel = level
            self.__minXP = minXP
            self.__maxXP = maxXP
            self.__updatePercents()
            for view in self._viewComponents:
                view.setCurrentXP(self.__currentXP, self.__currentXpPercents)
                view.setLevel(self.__currentLevel, minXP, maxXP)
                if self.__currentLevel == self.__vehicleHolder.maxLevel:
                    view.onMaxLvlAchieved()

    def setViewComponents(self, *components):
        self.__progressionWindowCtrl = _ProgressionWindowCtrl()
        self._viewComponents = list(components)
        self.__upgradesAvailability = _UpgradesAvailability(self._viewComponents)
        avatar = BigWorld.player()
        if avatar.inputHandler is not None:
            avatar.inputHandler.onCameraChanged += self.__onCameraChanged
        return

    def addRuntimeView(self, view):
        if view in self._viewComponents:
            LOG_ERROR('View is already added! {}'.format(view))
        else:
            if self.__isStarted:
                view.setLevel(self.__currentLevel, self.__minXP, self.__maxXP)
                view.setCurrentXP(self.__currentXP, self.__currentXpPercents)
                if self.__currentLevel == self.__vehicleHolder.maxLevel:
                    view.onMaxLvlAchieved()
                if self.__averageLevel is not None:
                    view.setAverageBattleLevel(self.__averageLevel)
            self._viewComponents.append(view)
        return

    def removeRuntimeView(self, view):
        if view in self._viewComponents:
            self._viewComponents.remove(view)
        else:
            LOG_WARNING('View has not been found! {}'.format(view))

    def isModuleSelected(self, intCD):
        return self.__modulesStorage.isSelected(intCD)

    def getModule(self, intCD):
        return self.__vehicleModulesStorage.getModule(intCD)

    def getInstalledOnVehicleAnalogByIntCD(self, intCD):
        return self.__vehicleModulesStorage.getInstalledOnVehicleAnalogByIntCD(intCD, self.getCurrentVehicle().descriptor)

    def selectVehicleModule(self, index):
        if self.__upgradesAvailability is not None and self.__upgradesAvailability.canUpgrade():
            for view in self._viewComponents:
                view.selectVehicleModule(index)

        return

    def getWindowCtrl(self):
        return self.__progressionWindowCtrl

    def vehicleVisualChangingStarted(self, vehicleID):
        self.onVehicleUpgradeStarted(vehicleID)
        for view in self._viewComponents:
            view.setVehicleVisualChangingStarted(vehicleID)

        self.__moduleChangeReq.vehicleUpgradeStarted()

    def vehicleVisualChangingFinished(self, vehicleID):
        self.__moduleChangeReq.vehicleUpgradeFinished()
        for view in self._viewComponents:
            view.setVehicleVisualChangingFinished(vehicleID)

        self.onVehicleUpgradeFinished(vehicleID)

    def onVehicleStatusChanged(self):
        if self.__upgradesAvailability is not None:
            self.__upgradesAvailability.onVehicleStatusChanged()
        return

    def updateVehicleReadinessTime(self, cooldownTime, reason):
        if self.__upgradesAvailability is not None:
            self.__upgradesAvailability.setCooldown(cooldownTime, reason)
        return

    def isVehicleReady(self):
        canUpgrade = self.__upgradesAvailability is not None and self.__upgradesAvailability.canUpgrade()
        return canUpgrade and BigWorld.player().getVehicleAttached() is not None

    def vehicleUpgradeRequest(self, intCD=None, moduleItem=None):
        vehicle = self.getCurrentVehicle()
        moduleItem = moduleItem or self.getModule(intCD)
        successfullySent = self.__moduleChangeReq.request(moduleItem, vehicle)
        if successfullySent:
            intCD = intCD or moduleItem.intCD
            self.__vehicleHolder.installModule(moduleItem)
            self.__registerSelectedModule(intCD)
        for view in self._viewComponents:
            view.vehicleChangeRequestSent(intCD, successfullySent)

        return successfullySent

    def vehicleUpgradeResponse(self, intCD, successfullyProcessed):
        successfullyProcessed = self.__moduleChangeReq.processResponse(intCD, successfullyProcessed)
        if not successfullyProcessed:
            self.__unregisterSelectedModule(intCD)
            self.__vehicleHolder.recreateVehicle()
        for view in self._viewComponents:
            view.setVehicleChangeResponse(intCD, successfullyProcessed)

    def setAverageBattleLevel(self, level):
        self.__averageLevel = level
        for view in self._viewComponents:
            view.setAverageBattleLevel(level)

    def __registerSelectedModule(self, intCD):
        self.__modulesStorage.addIntCD(intCD)
        self.__cacheModule(self.__tmpProgressionRecord, intCD)

    def __cacheModule(self, cache, intCD):
        if cache.addModule(intCD):
            cache.save()

    def __loadCachedProgress(self):
        for module in self.__tmpProgressionRecord.getModules():
            self.__modulesStorage.addIntCD(module)

    def __unregisterSelectedModule(self, intCD):
        self.__modulesStorage.removeIntCD(intCD)

    def __updatePercents(self):
        total = self.__maxXP - self.__minXP
        if total > 0:
            self.__currentXpPercents = min(_MAX_PERCENT_AMOUNT * (self.__currentXP - self.__minXP) / total, _MAX_PERCENT_AMOUNT)
        else:
            self.__currentXpPercents = 0

    def __onVehicleEnterWorld(self, vehicle):
        avatar = BigWorld.player()
        pVehId = avatar_getter.getPlayerVehicleID()
        if vehicle.id == pVehId:
            self.updateLevel(*vehicle.battleXP.battleXpLvlData)
            self.updateXP(vehicle.battleXP.battleXP)
            avatar.onVehicleEnterWorld -= self.__onVehicleEnterWorld
            self.__installInitialModules()
            self.__cacheInitialModules(vehicle)
            self.__isStarted = True

    def getInitialVehicle(self):
        return self.__vehicleHolder.getInitialVehicle()

    def __installInitialModules(self):
        cachedModules = {getTypeOfCompactDescr(module):module for module in self.__initialModulesRecord.getModules()}
        for typeID, module in cachedModules.iteritems():
            if typeID != GUI_ITEM_TYPE.TURRET:
                self.__vehicleHolder.setInitialModule(module)
            self.__vehicleHolder.setInitialTurret(module, cachedModules[GUI_ITEM_TYPE.GUN])

    def __cacheInitialModules(self, vehicle):
        if self.__initialModulesRecord.getModules():
            return
        descriptors = (vehicle.typeDescriptor.chassis.compactDescr,
         vehicle.typeDescriptor.engine.compactDescr,
         vehicle.typeDescriptor.fuelTank.compactDescr,
         vehicle.typeDescriptor.gun.compactDescr,
         vehicle.typeDescriptor.radio.compactDescr,
         vehicle.typeDescriptor.turret.compactDescr)
        for descriptor in descriptors:
            self.__cacheModule(self.__initialModulesRecord, descriptor)

    def __onCameraChanged(self, eMode, _=None):
        if self.__upgradesAvailability is not None:
            self.__upgradesAvailability.onCameraChanged(eMode)
        return

    def __notifyVehicleChanged(self, newModuleIntCD=None, vehicleRecreated=False):
        for view in self._viewComponents:
            view.setVehicleChanged(self.getCurrentVehicle(), newModuleIntCD, vehicleRecreated)
