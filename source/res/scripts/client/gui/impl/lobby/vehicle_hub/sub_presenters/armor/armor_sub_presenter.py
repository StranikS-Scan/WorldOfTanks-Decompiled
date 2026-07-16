# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/vehicle_hub/sub_presenters/armor/armor_sub_presenter.py
from __future__ import absolute_import
import logging
from functools import partial
import typing
import BigWorld
import GUI
import Math
import math_utils
import armor_inspector
from AvatarInputHandler import cameras
from CurrentVehicle import g_currentPreviewVehicle
from account_helpers.settings_core import settings_constants
from constants import VehicleArmorTags
from frameworks.wulf import ViewStatus
from gui import g_mouseEventHandlers
from gui.Scaleform.genConsts.TOOLTIPS_CONSTANTS import TOOLTIPS_CONSTANTS
from gui.app_loader import app_getter
from gui.impl.backport import createTooltipData
from gui.impl.gen import R
from gui.impl.gen.view_models.views.lobby.vehicle_hub.views.sub_models.armor_model import Modes
from gui.impl.gen.view_models.views.lobby.vehicle_hub.views.sub_models.armor_vehicle_module import ArmorVehicleModule
from gui.impl.lobby.common.vehicle_model_helpers import fillVehicleModel
from gui.impl.lobby.common.view_wrappers import createBackportTooltipDecorator
from gui.impl.lobby.select_vehicle.select_vehicle import SelectVehicleWindow, SelectVehicleTitles
from gui.impl.lobby.vehicle_hub.sub_presenters.armor.armor_tooltip import ArmorTooltipWindow
from cgf_components.armor_inspector_component import ArmorInspectorComponent
from gui.impl.lobby.vehicle_hub.sub_presenters.armor.minor_tooltip import MinorTooltip
from gui.impl.lobby.vehicle_hub.sub_presenters.armor.minor_short_tooltip import MinorShortTooltip
from gui.impl.lobby.vehicle_hub.sub_presenters.armor.utils import fillArmorData, getCursorPositionInPixels, getMaxArmor, getModuleForTurretRotation, getArmorInspectorSetting, setArmorInspectorSetting, ArmorInspectorSettingsKeys, AttackerVehicleConfiguration, getArmorInspectorAttackerVehicleConfig, getDefaultAttackerVehicleConfigByCD, setArmorInspectorAttackerVehicleConfig, MINOR_SHORT_TOOLTIP_DATA, getCollisionsAtCursor
from gui.impl.lobby.vehicle_hub.sub_presenters.armor.penetration_utils import setShellParamsFromVehicle
from gui.impl.lobby.vehicle_hub.sub_presenters.sub_presenter_base import SubPresenterBase
from gui.shared.gui_items.Vehicle import Vehicle
from gui.shared.gui_items.vehicle_modules import ModulesIconNames
from gui.shared.sort_key import SortKey
from gun_rotation_shared import calcPitchLimitsFromDesc
from helpers import dependency
from skeletons.account_helpers.settings_core import ISettingsCore
from skeletons.gui.app_loader import IAppLoader
from skeletons.gui.shared import IItemsCache
from skeletons.gui.shared.utils import IHangarSpace
from uilogging.vehicle_hub.loggers import ArmorTabLogger
if typing.TYPE_CHECKING:
    import CGF
    from ClientSelectableCameraVehicle import ClientSelectableCameraVehicle
    from gui.Scaleform.framework.application import AppEntry
    from gui.impl.gen.view_models.views.lobby.vehicle_hub.views.sub_models.armor_model import ArmorModel
    from gui.impl.lobby.vehicle_hub.sub_presenters.armor.penetration_utils import ShellParams
_ROTATION_PER_PX = 0.0015
_logger = logging.getLogger(__name__)

class _ModeBase(object):
    __slots__ = ('isEntered', '_p', 'needsFadeDelay')

    def __init__(self, presenter):
        self.isEntered = False
        self._p = presenter
        self.needsFadeDelay = True

    def enter(self):
        self.isEntered = True

    def exit(self):
        self.isEntered = False


class _ArmorMode(_ModeBase):

    def enter(self):
        super(_ArmorMode, self).enter()
        gameObject = self._p.vehicleEntity.appearance.gameObject
        if not gameObject.hasComponent(ArmorInspectorComponent):
            comp = ArmorInspectorComponent()
            comp.showProbability = self._isShowProbability()
            gameObject.assignComponent(comp)

    def exit(self):
        super(_ArmorMode, self).exit()
        gameObject = self._p.vehicleEntity.appearance.gameObject
        comp = gameObject.findWrite(ArmorInspectorComponent)
        if comp:
            comp.fadeOnRemove = not self._p.isClosing
            gameObject.removeComponent(ArmorInspectorComponent)

    def _isShowProbability(self):
        return False


class _NominalMode(_ArmorMode):

    def enter(self):
        super(_NominalMode, self).enter()
        _logger.debug('Armor mode switched to nominal armor')

    def _isShowProbability(self):
        return False


class _PenetrationMode(_ArmorMode):

    def enter(self):
        super(_PenetrationMode, self).enter()
        _logger.debug('Armor mode switched to penetration chance')

    def _isShowProbability(self):
        return True


class _NoArmorMode(_ModeBase):

    def __init__(self, presenter):
        super(_NoArmorMode, self).__init__(presenter)
        self.needsFadeDelay = False

    def enter(self):
        super(_NoArmorMode, self).enter()
        _logger.debug('Armor mode switched to no_armor')


_MODE_CLASSES = {Modes.NOMINAL.value: _NominalMode,
 Modes.PENETRATION.value: _PenetrationMode,
 Modes.NO_ARMOR.value: _NoArmorMode}

class ArmorSubPresenter(SubPresenterBase):
    __slots__ = ('_isMouseOver', '_tooltip', '_level', '_normalArmorMax', '_spacedArmorMax', '_uiLogger', '_modes', '_currentModeId', '_currentMode', '_modulesMover', 'vehicleEntity', 'isClosing', '__weakref__', '_modulesSetup', '_attackerSetup', '_shellParams')
    _appLoader = dependency.descriptor(IAppLoader)
    _settingsCore = dependency.descriptor(ISettingsCore)
    _hangarSpace = dependency.descriptor(IHangarSpace)

    def __init__(self, model, parentView):
        super(ArmorSubPresenter, self).__init__(model, parentView)
        self._isMouseOver = False
        self._tooltip = None
        self._level = 0
        self._normalArmorMax, self._spacedArmorMax = (0, 0)
        self._uiLogger = None
        self._modes = None
        self._currentModeId = getArmorInspectorSetting(ArmorInspectorSettingsKeys.SELECTED_MODE)
        self._currentMode = None
        self._modulesMover = None
        self._modulesSetup = None
        self._attackerSetup = None
        self._shellParams = None
        self.vehicleEntity = None
        self.isClosing = False
        return

    @property
    def viewModel(self):
        return self.getViewModel()

    @property
    def vehicleLevel(self):
        return self._level

    def storeShellParams(self, shellParams):
        self._shellParams = shellParams

    @app_getter
    def app(self):
        pass

    def initialize(self, vhCtx, *args, **kwargs):
        super(ArmorSubPresenter, self).initialize(vhCtx, *args, **kwargs)
        self.vehicleEntity = self._hangarSpace.space.getVehicleEntity()
        self._level = self.vehicleEntity.typeDescriptor.level
        self._normalArmorMax, self._spacedArmorMax = getMaxArmor(self.vehicleEntity)
        g_mouseEventHandlers.add(self._handleMouseEvent)
        self._hangarSpace.lockVehicleSelectable(self)
        self._startUILogger()
        self.viewModel.setSelectedMode(self._currentModeId)
        self._attackerSetup = _AttackerSetup(getArmorInspectorAttackerVehicleConfig(self._level), self)
        self._fillArmorData()
        self._modulesSetup = _ModulesSetup(self.vehicleEntity, self.viewModel)
        self._setupModes()
        if self._hangarSpace.isModelLoaded:
            self._currentMode.enter()
        else:
            self._hangarSpace.onVehicleChanged += self._onVehicleChanged
        self._modulesMover = _ModulesMover(self.vehicleEntity, self.viewModel)

    def finalize(self):
        self.isClosing = True
        g_mouseEventHandlers.discard(self._handleMouseEvent)
        if self._modulesSetup is not None:
            self._modulesSetup.finalize(self.viewModel)
            self._modulesSetup = None
        self._hangarSpace.unlockVehicleSelectable(self)
        self._destroyTooltip()
        if self._uiLogger is not None:
            self._uiLogger.logClose()
            self._uiLogger = None
        if self._hangarSpace.spaceInited and self._currentMode is not None:
            self._currentMode.exit()
        self._currentMode = None
        self._modes = None
        if self._modulesMover is not None:
            self._modulesMover.finalize(self.viewModel)
            self._modulesMover = None
        if self._attackerSetup is not None:
            self._attackerSetup.finalize(self.viewModel)
            self._attackerSetup = None
        self.vehicleEntity = None
        self.isClosing = False
        self._shellParams = None
        super(ArmorSubPresenter, self).finalize()
        return

    @createBackportTooltipDecorator()
    def createToolTip(self, event):
        return super(ArmorSubPresenter, self).createToolTip(event)

    def getTooltipData(self, event):
        tooltipId = event.getArgument('tooltipId')
        if tooltipId == TOOLTIPS_CONSTANTS.CONTEXT_VEHICLE_MODULE:
            compactDescr = int(event.getArgument('compactDescr', 0))
            if tooltipId == TOOLTIPS_CONSTANTS.CONTEXT_VEHICLE_MODULE:
                isAttacker = bool(event.getArgument('isAttacker', False))
                specialArgs = (compactDescr, self._attackerSetup.vehicle if isAttacker else g_currentPreviewVehicle.item)
            else:
                specialArgs = (compactDescr,)
            return createTooltipData(isSpecial=True, specialAlias=tooltipId, specialArgs=specialArgs)
        elif tooltipId == TOOLTIPS_CONSTANTS.ARMOR_INSPECTOR_SHELL:
            index = int(event.getArgument('shellIndex', 0))
            compactDescr = self._attackerSetup.vehicle.descriptor.gun.shots[index].shell.compactDescr
            return createTooltipData(isSpecial=True, specialAlias=tooltipId, specialArgs=(compactDescr, self._attackerSetup.vehicle))
        else:
            return None

    def createToolTipContent(self, event, contentID):
        if contentID == R.views.mono.vehicle_hub.tooltips.minor_tooltip():
            return MinorTooltip()
        if contentID == R.views.mono.vehicle_hub.tooltips.minor_short_tooltip():
            tooltipType = event.getArgument('tooltipType')
            return MinorShortTooltip(**MINOR_SHORT_TOOLTIP_DATA[tooltipType])
        return super(ArmorSubPresenter, self).createToolTipContent(event, contentID)

    def _getEvents(self):
        return ((self.viewModel.onModeChanged, self._onModeChanged),
         (self._hangarSpace.onMouseEnter, self._onMouseEnter),
         (self._hangarSpace.onMouseExit, self._onMouseExit),
         (self._settingsCore.onSettingsChanged, self._onSettingsChanged),
         (g_currentPreviewVehicle.onComponentInstalled, self._onComponentInstalled))

    def _fillArmorData(self):
        fillArmorData(self.getViewModel(), self._level, self._normalArmorMax, self._spacedArmorMax, self._settingsCore.getSetting(settings_constants.GRAPHICS.COLOR_BLIND))

    def _onComponentInstalled(self, *_):
        if not self.isClosing:
            self._fillArmorData()
            self._modulesSetup.updateSelectedModules(self.viewModel)
            self._modulesSetup.tryRestoreOutfit()
            self._currentMode.exit()
            self.vehicleEntity.appearance.loadState.subscribe(self._onVehicleLoadFinished, self._onVehicleLoadStarted)

    def _onVehicleLoadStarted(self):
        pass

    def _onVehicleLoadFinished(self):
        self.vehicleEntity.appearance.loadState.unsubscribe(self._onVehicleLoadFinished, self._onVehicleLoadStarted)
        self._currentMode.enter()

    def _startUILogger(self):
        cd = self.vehicleEntity.typeDescriptor.type.compactDescr
        self._uiLogger = ArmorTabLogger(cd)
        self._uiLogger.logOpen()

    def _handleMouseEvent(self, _):
        isOverActive3DScene = GUI.mcursor().inWindow and GUI.mcursor().inFocus and self._hangarSpace.isCursorOver3DScene
        if isOverActive3DScene:
            if self._tooltip:
                self._updateTooltip()
            elif self._isMouseOver:
                self._createTooltip()
            self._modulesMover.onHover3DScene(self.viewModel)
        elif self._tooltip:
            self._destroyTooltip()

    def _onMouseEnter(self, entity):
        if self.vehicleEntity != entity:
            return
        self._isMouseOver = True

    def _onMouseExit(self, entity):
        if self.vehicleEntity != entity:
            return
        self._isMouseOver = False
        self._destroyTooltip()

    def _createTooltip(self):
        if self._tooltip is None and self._currentMode.isEntered:
            self._tooltip = ArmorTooltipWindow(self.vehicleEntity)
            self._tooltip.onStatusChanged += self.__onTooltipStatusChanged
            self._updateTooltip()
            self._tooltip.load()
            self._uiLogger.tooltipOpened()
            GUI.switchArmorInspectorCursor(True)
        return

    def _updateTooltip(self):
        if self._tooltip:
            x, y = self._applyScaleToPosition(getCursorPositionInPixels())
            self._tooltip.move(x, y)
            collisions = getCollisionsAtCursor(self.vehicleEntity)
            self._tooltip.update(self._currentModeId, self._shellParams, collisions)

    def _applyScaleToPosition(self, position):
        scale = self._settingsCore.interfaceScale.get()
        return (int(coord // scale) for coord in position) if scale != 1 else position

    def __onTooltipStatusChanged(self, status):
        if status == ViewStatus.DESTROYED:
            self._destroyTooltip()

    def _destroyTooltip(self):
        if self._tooltip is not None:
            self._tooltip.onStatusChanged -= self.__onTooltipStatusChanged
            self._tooltip.destroy()
            self._tooltip = None
            self._uiLogger.armorTooltipClosed()
            GUI.switchArmorInspectorCursor(False)
        return

    def _onVehicleChanged(self):
        self._hangarSpace.onVehicleChanged -= self._onVehicleChanged
        self._fillArmorData()
        if self._currentMode is not None:
            self._currentMode.enter()
        return

    def _onSettingsChanged(self, diff):
        if settings_constants.GRAPHICS.COLOR_BLIND in diff:
            self._fillArmorData()
            if self._tooltip is not None:
                self._updateTooltip()
        return

    def _onModeChanged(self, event):
        itemId = event.get('id', None)
        if itemId is not None:
            if itemId == self._currentModeId:
                return
            needsDelay = False
            if self._currentMode is not None:
                needsDelay = self._currentMode.needsFadeDelay
                self._currentMode.exit()
            self._currentModeId = itemId
            setArmorInspectorSetting(ArmorInspectorSettingsKeys.SELECTED_MODE, self._currentModeId)
            self.viewModel.setSelectedMode(itemId)
            self._currentMode = self._modes.get(itemId)
            if self._currentMode is not None:
                if needsDelay:
                    BigWorld.callback(armor_inspector.FADE_DURATION, self._currentMode.enter)
                else:
                    self._currentMode.enter()
        return

    def _setupModes(self):
        self._modes = {modeId:cls(self) for modeId, cls in _MODE_CLASSES.items()}
        self._currentMode = self._modes.get(self._currentModeId)


class _ModulesMover(object):
    __slots__ = ('_vehicleEntity', '_hoveredDistance', '_hoveredModule', '_dragModule', '_gunMultiplier', '_turretMultiplier')

    def __init__(self, vehicleEntity, viewModel):
        super(_ModulesMover, self).__init__()
        self._vehicleEntity = vehicleEntity
        self._hoveredModule = None
        self._hoveredDistance = None
        self._dragModule = None
        self._gunMultiplier = 1.0
        self._turretMultiplier = 1.0
        viewModel.onDragModule += self._onDragModule
        viewModel.onDragStateChanged += self._onDragStateChanged
        return

    def finalize(self, viewModel):
        viewModel.onDragModule -= self._onDragModule
        viewModel.onDragStateChanged -= self._onDragStateChanged
        self.resetModulesRotation()
        self._vehicleEntity = None
        return

    def resetModulesRotation(self):
        if hasattr(self._vehicleEntity, 'appearance') and self._vehicleEntity.appearance is not None:
            self._vehicleEntity.appearance.rotateTurretForAnchor(None, 0.0)
            self._vehicleEntity.appearance.rotateGunToDefault()
        return

    def onHover3DScene(self, viewModel):
        if self._dragModule is None:
            self._hoveredModule, self._hoveredDistance = getModuleForTurretRotation(self._vehicleEntity)
            gun = self._vehicleEntity.typeDescriptor.gun
            if self._hoveredModule == VehicleArmorTags.TURRET and gun.staticTurretYaw is None or self._hoveredModule in (VehicleArmorTags.GUN, VehicleArmorTags.GUN_MASK) and gun.staticPitch is None:
                viewModel.setDragModuleMode(True)
            else:
                viewModel.setDragModuleMode(False)
        return

    def _onDragStateChanged(self, args):
        if args is None:
            return
        else:
            if args.get('state', False):
                if self._hoveredModule in (VehicleArmorTags.TURRET, VehicleArmorTags.GUN, VehicleArmorTags.GUN_MASK):
                    self._dragModule = self._hoveredModule
                    self._updateInversion()
                    return
            self._dragModule = None
            return

    def _updateInversion(self):
        cursorPosition = GUI.mcursor().position
        ray, startPoint = cameras.getWorldRayAndPoint(cursorPosition.x, cursorPosition.y)
        ray.normalise()
        point = startPoint + ray.scale(self._hoveredDistance)
        typeDescriptor = self._vehicleEntity.typeDescriptor
        turretOffs = typeDescriptor.hull.turretPositions[0] + typeDescriptor.chassis.hullPosition
        if self._dragModule in (VehicleArmorTags.GUN, VehicleArmorTags.GUN_MASK):
            turretYaw = self._vehicleEntity.appearance.turretRotator.turretYaw
            gunPitch = self._vehicleEntity.appearance.getGunPitch()
            turretWorldMatrix = Math.Matrix()
            turretWorldMatrix.setRotateY(turretYaw)
            turretWorldMatrix.translation = turretOffs
            turretWorldMatrix.postMultiply(self._vehicleEntity.model.matrix)
            gunWorldMatrix = Math.Matrix()
            gunWorldMatrix.setRotateX(gunPitch)
            gunWorldMatrix.postMultiply(turretWorldMatrix)
            invGunWorldMatrix = Math.Matrix(gunWorldMatrix)
            invGunWorldMatrix.invert()
            gunLocalPoint = invGunWorldMatrix.applyPoint(point)
            self._gunMultiplier = -1.0 if gunLocalPoint.z < 0 else 1.0
        turretCenterPoint = self._vehicleEntity.model.position + turretOffs
        turretCenterPoint.y = point.y
        self._turretMultiplier = -1.0 if (turretCenterPoint - startPoint).length < self._hoveredDistance else 1.0

    def _onDragModule(self, args):
        if args is None or self._dragModule is None:
            return
        else:
            dx = args.get('dx')
            dy = args.get('dy')
            turretRotator = self._vehicleEntity.appearance.turretRotator
            turretYaw = turretRotator.turretYaw
            typeDescriptor = self._vehicleEntity.typeDescriptor
            gunPitch = self._vehicleEntity.appearance.getGunPitch()
            calcGunPitch = False
            if dx != 0.0 and self._dragModule == VehicleArmorTags.TURRET or self._dragModule in (VehicleArmorTags.GUN, VehicleArmorTags.GUN_MASK) and typeDescriptor.gun.staticTurretYaw is None:
                turretYaw = turretRotator.turretYaw - dx * _ROTATION_PER_PX * self._turretMultiplier
                turretYawLimits = typeDescriptor.gun.turretYawLimits
                if turretYawLimits is None:
                    turretYaw = math_utils.reduceTo2PI(turretYaw)
                else:
                    turretYaw = math_utils.clamp(turretYawLimits[0], turretYawLimits[1], turretYaw)
                turretRotator.start(turretYaw, 0.0)
                if self._dragModule == VehicleArmorTags.TURRET and typeDescriptor.gun.staticPitch is None:
                    calcGunPitch = True
            if dy != 0.0 and self._dragModule in (VehicleArmorTags.GUN, VehicleArmorTags.GUN_MASK) and typeDescriptor.gun.staticPitch is None:
                gunPitch = gunPitch + dy * _ROTATION_PER_PX * self._gunMultiplier
                calcGunPitch = True
            if calcGunPitch:
                pitchLimits = typeDescriptor.gun.pitchLimits
                minPitch, maxPitch = calcPitchLimitsFromDesc(turretYaw, pitchLimits, typeDescriptor.hull.turretPitches[0], typeDescriptor.turret.gunJointPitch)
                gunPitch = math_utils.clamp(minPitch, maxPitch, gunPitch)
                self._vehicleEntity.appearance.rotateGunForAngle(gunPitch)
            return


class _ModulesSetup(object):
    __slots__ = ('_vehicleEntity', '_initialVehicleCD', '_initialTurretCD', '_initialGunCD', '_initialOutfit')
    _itemsCache = dependency.descriptor(IItemsCache)
    _hangarSpace = dependency.descriptor(IHangarSpace)

    def __init__(self, vehicleEntity, viewModel):
        super(_ModulesSetup, self).__init__()
        self._vehicleEntity = vehicleEntity
        typeDescriptor = vehicleEntity.typeDescriptor
        self._initialVehicleCD = typeDescriptor.type.compactDescr
        self._initialTurretCD = typeDescriptor.turret.compactDescr
        self._initialGunCD = typeDescriptor.gun.compactDescr
        self._initialOutfit = vehicleEntity.appearance.outfit if vehicleEntity.appearance else None
        viewModel.onTurretItemClick += self._onTurretItemClick
        viewModel.onGunItemClick += self._onGunItemClick
        self._initModulesData(viewModel)
        return

    def finalize(self, viewModel):
        viewModel.onTurretItemClick -= self._onTurretItemClick
        viewModel.onGunItemClick -= self._onGunItemClick
        if self._initialVehicleCD is not None and g_currentPreviewVehicle.intCD == self._initialVehicleCD:
            turretChanged = self._vehicleEntity.typeDescriptor.turret.compactDescr != self._initialTurretCD
            gunChanged = self._vehicleEntity.typeDescriptor.gun.compactDescr != self._initialGunCD
            if turretChanged:
                g_currentPreviewVehicle.installComponent(self._initialTurretCD)
                g_currentPreviewVehicle.installComponent(self._initialGunCD)
            elif gunChanged:
                g_currentPreviewVehicle.installComponent(self._initialGunCD)
            if (turretChanged or gunChanged) and self._initialOutfit is not None:
                self._hangarSpace.updatePreviewVehicle(g_currentPreviewVehicle.item, self._initialOutfit)
        self._initialVehicleCD = None
        self._initialOutfit = None
        return

    def tryRestoreOutfit(self):
        if self._initialOutfit is None:
            return
        else:
            self._vehicleEntity.updateVehicleCustomization(self._initialOutfit)
            return

    def updateSelectedModules(self, viewModel):
        typeDescriptor = self._vehicleEntity.typeDescriptor
        currentTurret = typeDescriptor.turret
        currentGun = typeDescriptor.gun
        with viewModel.transaction() as model:
            vehicle = model.vehicle
            self._updateConfigurationTitle(vehicle)
            vehicle.setCurrentTurret(currentTurret.compactDescr)
            vehicle.setCurrentGun(currentGun.compactDescr)

    def _initModulesData(self, viewModel):
        typeDescriptor = self._vehicleEntity.typeDescriptor
        hasTurrets = len(typeDescriptor.hull.fakeTurrets['lobby']) != len(typeDescriptor.turrets)
        currentTurret = typeDescriptor.turret
        currentGun = typeDescriptor.gun
        vehicle = viewModel.vehicle
        self._updateConfigurationTitle(vehicle)
        vehicle.setCurrentTurret(currentTurret.compactDescr)
        vehicle.setCurrentGun(currentGun.compactDescr)
        turretsModel = vehicle.getTurrets()
        gunsModel = vehicle.getGuns()
        turretsModel.clear()
        gunsModel.clear()
        turrets = sorted(typeDescriptor.type.turrets[0], key=partial(_ModulesSortKey, typeDescriptor.type))
        if hasTurrets:
            for turret in turrets:
                turretModel = ArmorVehicleModule()
                turretModel.setLevel(turret.level)
                turretModel.setImage(ModulesIconNames.TURRET)
                turretModel.setCompactDescr(turret.compactDescr)
                turretDependencies = turretModel.getDependencies()
                for gun in turret.guns:
                    turretDependencies.addNumber(gun.compactDescr)

                turretsModel.addViewModel(turretModel)

        sortedGuns = _getSortedGuns(typeDescriptor.type)
        for gun in sortedGuns:
            gunModel = ArmorVehicleModule()
            gunModel.setLevel(gun.level)
            gunModel.setImage(ModulesIconNames.GUN)
            gunModel.setCompactDescr(gun.compactDescr)
            gunsModel.addViewModel(gunModel)
            gunItem = self._itemsCache.items.getItemByCD(gun.compactDescr)
            mechanics = gunModel.getMechanics()
            for m in gunItem.getModuleMechanicItems(typeDescriptor):
                if not m.isHidden:
                    mechanics.addString(m.guiName.value)

            gunDependencies = gunModel.getDependencies()
            for turret in turrets:
                if any((g.compactDescr == gun.compactDescr for g in turret.guns)):
                    gunDependencies.addNumber(turret.compactDescr)

    def _updateConfigurationTitle(self, vehicleModel):
        typeDescriptor = self._vehicleEntity.typeDescriptor
        vehicle = self._itemsCache.items.getItemByCD(typeDescriptor.type.compactDescr)
        currentTurret = typeDescriptor.turret
        currentGun = typeDescriptor.gun
        modulesAcc = R.strings.armor_inspector.modules
        if vehicle.isInInventory and currentTurret.compactDescr == vehicle.turret.intCD and currentGun.compactDescr == vehicle.gun.intCD:
            title = modulesAcc.current()
        else:
            turrets = typeDescriptor.type.turrets[0]
            isTurretTop = turrets[-1].compactDescr == currentTurret.compactDescr
            isTop = isTurretTop and turrets[-1].guns[-1].compactDescr == currentGun.compactDescr
            isTurretStock = len(turrets) == 1 or not isTurretTop and turrets[0].compactDescr == currentTurret.compactDescr
            isStock = isTurretStock and (len(turrets[0].guns) > 1 or len(turrets) > 1) and turrets[0].guns[0].compactDescr == currentGun.compactDescr
            if isTop:
                title = modulesAcc.top()
            elif isStock:
                title = modulesAcc.standard()
            else:
                title = modulesAcc.custom()
        vehicleModel.setConfigurationTitle(title)

    def _onTurretItemClick(self, args):
        if args is None:
            return
        else:
            compactDescr = int(args.get('compactDescr'))
            prevGunCD = self._vehicleEntity.typeDescriptor.gun.compactDescr
            g_currentPreviewVehicle.installComponent(compactDescr)
            self._installTopSupportedGun(prevGunCD, compactDescr)
            return

    def _onGunItemClick(self, args):
        if args is None:
            return
        else:
            compactDescr = int(args.get('compactDescr'))
            self._installSupportedTurret(compactDescr)
            g_currentPreviewVehicle.installComponent(compactDescr)
            return

    def _installSupportedTurret(self, gunCompactDescr):
        typeDescriptor = self._vehicleEntity.typeDescriptor
        currentTurret = typeDescriptor.turret
        if all((gun.compactDescr != gunCompactDescr for gun in currentTurret.guns)):
            turrets = typeDescriptor.type.turrets[0]
            for turret in reversed(turrets):
                for gun in turret.guns:
                    if gun.compactDescr == gunCompactDescr:
                        g_currentPreviewVehicle.installComponent(turret.compactDescr)
                        return

    def _installTopSupportedGun(self, prevGunCD, turretCompactDescr):
        typeDescriptor = self._vehicleEntity.typeDescriptor
        turret = next((turret for turret in typeDescriptor.type.turrets[0] if turret.compactDescr == turretCompactDescr), None)
        if turret and all((gun.compactDescr != prevGunCD for gun in turret.guns)):
            g_currentPreviewVehicle.installComponent(turret.guns[-1].compactDescr)
        return


class _AttackerSetup(object):
    __slots__ = ('_attackerVehicle', '_parent')
    _itemsCache = dependency.descriptor(IItemsCache)
    _hangarSpace = dependency.descriptor(IHangarSpace)

    def __init__(self, attackerConfig, parent):
        super(_AttackerSetup, self).__init__()
        self._attackerVehicle = Vehicle(typeCompDescr=attackerConfig.compactDescr)
        self._parent = parent
        viewModel = parent.viewModel
        viewModel.onAttackerClicked += self._onAttackerClicked
        viewModel.onAttackerGunItemClick += self._onAttackerGunItemClick
        viewModel.onAttackerShellItemClick += self._onAttackerShellItemClick
        self._update(viewModel.attacker, attackerConfig)

    @property
    def vehicle(self):
        return self._attackerVehicle

    def finalize(self, viewModel):
        viewModel.onAttackerClicked -= self._onAttackerClicked
        viewModel.onAttackerGunItemClick -= self._onAttackerGunItemClick
        viewModel.onAttackerShellItemClick -= self._onAttackerShellItemClick
        self._parent = None
        return

    def _update(self, attackerModel, attackerConfig):
        attackerDescr = self._attackerVehicle.descriptor
        topTurret = attackerDescr.type.turrets[0][-1]
        if attackerDescr.turret.compactDescr != topTurret.compactDescr:
            attackerDescr.installTurret(topTurret.compactDescr, topTurret.guns[-1].compactDescr)
        fillVehicleModel(attackerModel.vehicle, self._attackerVehicle)
        gunsModel = attackerModel.getGuns()
        gunsModel.clear()
        sortedGuns = _getSortedGuns(attackerDescr.type)
        for gun in sortedGuns:
            gunModel = ArmorVehicleModule()
            gunModel.setLevel(gun.level)
            gunModel.setImage(ModulesIconNames.GUN)
            gunModel.setCompactDescr(gun.compactDescr)
            mechanics = gunModel.getMechanics()
            gunItem = self._itemsCache.items.getItemByCD(gun.compactDescr)
            for m in gunItem.getModuleMechanicItems(attackerDescr):
                if not m.isHidden:
                    mechanics.addString(m.guiName.value)

            gunsModel.addViewModel(gunModel)

        gunsModel.invalidate()
        lastGunCD = sortedGuns[-1].compactDescr
        self._updateAttackerGun(attackerConfig.gunCompactDescr if attackerConfig.gunCompactDescr is not None else lastGunCD, attackerModel, attackerConfig.activeGunShotIndex)
        return

    def _updateAttackerGun(self, compactDescr, attackerModel, activeGunShotIndex=0):
        attackerDescr = self._attackerVehicle.descriptor
        for turret in reversed(attackerDescr.type.turrets[0]):
            for gun in turret.guns:
                if gun.compactDescr == compactDescr:
                    if attackerDescr.gun.compactDescr != gun.compactDescr:
                        attackerDescr.installComponent(gun.compactDescr)
                    attackerModel.setCurrentGun(gun.compactDescr)
                    attackerModel.setShells(','.join((shot.shell.iconName for shot in gun.shots)))

        self._updateAttackerShell(activeGunShotIndex, attackerModel)

    def _updateAttackerShell(self, index, attackerModel):
        attackerModel.setCurrentShell(index)
        self._attackerVehicle.descriptor.activeGunShotIndex = index
        shellParams = setShellParamsFromVehicle(self._attackerVehicle.descriptor.shot, self._hangarSpace.spaceID)
        self._parent.storeShellParams(shellParams)

    def _onAttackerGunItemClick(self, args):
        if args is None:
            return
        else:
            gunCompactDecscr = int(args.get('compactDescr'))
            setArmorInspectorAttackerVehicleConfig(self._parent.vehicleLevel, gunCompactDescr=gunCompactDecscr)
            with self._parent.viewModel.attacker.transaction() as attackerModel:
                self._updateAttackerGun(gunCompactDecscr, attackerModel)
            return

    def _onAttackerShellItemClick(self, args):
        if args is None:
            return
        else:
            activeGunShotIndex = int(args.get('index'))
            setArmorInspectorAttackerVehicleConfig(self._parent.vehicleLevel, activeGunShotIndex=activeGunShotIndex)
            with self._parent.viewModel.attacker.transaction() as attackerModel:
                self._updateAttackerShell(activeGunShotIndex, attackerModel)
            return

    def _onAttackerClicked(self):
        window = SelectVehicleWindow(SelectVehicleTitles.SELECT_ATTACKER, self._onSelectAttacker, self._attackerVehicle.descriptor.type.compactDescr)
        window.load()

    def _onSelectAttacker(self, vehicleCD):
        self._attackerVehicle = Vehicle(typeCompDescr=vehicleCD)
        setArmorInspectorAttackerVehicleConfig(self._parent.vehicleLevel, compactDescr=vehicleCD)
        with self._parent.viewModel.attacker.transaction() as attackerModel:
            self._update(attackerModel, getDefaultAttackerVehicleConfigByCD(vehicleCD))


class _ModulesSortKey(SortKey):
    __slots__ = ('vehType', 'item')

    def __init__(self, vehType, item):
        super(_ModulesSortKey, self).__init__()
        self.vehType = vehType
        self.item = item

    def _cmp(self, other):
        a = self.item
        b = other.item
        if a.unlocks:
            for unlockId in a.unlocks:
                unlock = self.vehType.unlocksDescrs[unlockId]
                if unlock[1] == b.compactDescr:
                    return -1

        if b.unlocks:
            for unlockId in b.unlocks:
                unlock = self.vehType.unlocksDescrs[unlockId]
                if unlock[1] == a.compactDescr:
                    return 1

        return a.level - b.level


def _getSortedGuns(vehType):
    turrets = sorted(vehType.turrets[0], key=partial(_ModulesSortKey, vehType))
    guns = []
    gunIds = []
    for turret in turrets:
        for gun in turret.guns:
            if gun.compactDescr in gunIds:
                continue
            guns.append(gun)
            gunIds.append(gun.compactDescr)

    return sorted(guns, key=partial(_ModulesSortKey, vehType))
