# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/battle/shared/indicators.py
import typing
import BigWorld
import GUI
import SoundGroups
from account_helpers.settings_core.settings_constants import SOUND, DAMAGE_INDICATOR, GRAPHICS
from constants import VEHICLE_SIEGE_STATE as _SIEGE_STATE
from debug_utils import LOG_DEBUG, LOG_DEBUG_DEV
from gui import DEPTH_OF_Aim, GUI_SETTINGS
from gui.Scaleform.flash_wrapper import Flash, InputKeyMode
from gui.Scaleform.daapi.view.battle.shared.vehicles import siege_component
from gui.Scaleform.daapi.view.meta.SiegeModeIndicatorMeta import SiegeModeIndicatorMeta
from gui.Scaleform.daapi.view.meta.SixthSenseMeta import SixthSenseMeta
from gui.Scaleform.genConsts.DAMAGEINDICATOR import DAMAGEINDICATOR
from gui.Scaleform.genConsts.SIEGE_MODE_CONSTS import SIEGE_MODE_CONSTS
from gui.Scaleform.locale.INGAME_GUI import INGAME_GUI
from gui.battle_control.battle_constants import DEVICE_STATES_RANGE, DEVICE_STATE_NORMAL, DEVICE_STATE_CRITICAL, VEHICLE_DEVICE_IN_COMPLEX_ITEM
from gui.battle_control.battle_constants import HIT_INDICATOR_MAX_ON_SCREEN
from gui.battle_control.battle_constants import PREDICTION_INDICATOR_MAX_ON_SCREEN
from gui.battle_control.battle_constants import VEHICLE_VIEW_STATE, CROSSHAIR_VIEW_ID
from gui.battle_control.controllers.hit_direction_ctrl import IHitIndicator, HitType
from gui.shared.crits_mask_parser import critsParserGenerator
from helpers import dependency
from helpers import i18n
from gui.impl import backport
from gui.impl.gen import R
from shared_utils import CONST_CONTAINER
from skeletons.account_helpers.settings_core import ISettingsCore
from skeletons.gui.battle_session import IBattleSessionProvider
from soft_exception import SoftException
if typing.TYPE_CHECKING:
    from items.vehicles import VehicleDescriptor
_PREDICTION_INDICATOR_SWF = 'battlePredictionIndicatorApp.swf'
_PREDICTION_INDICATOR_COMPONENT = 'WGPredictionIndicatorFlash'
_PREDICTION_INDICATOR_MC_NAME = '_root.predictionIndicator.hit_{0}'
_PREDICTION_INDICATOR_SWF_SIZE = (680, 680)
_PREDICTION_INDICATOR_MAX_DUR = 20
_DAMAGE_INDICATOR_SWF = 'battleDamageIndicatorApp.swf'
_DAMAGE_INDICATOR_COMPONENT = 'WGHitIndicatorFlash'
_DAMAGE_INDICATOR_MC_NAME = '_root.dmgIndicator.hit_{0}'
_DAMAGE_INDICATOR_SWF_SIZE = (680, 680)
_DAMAGE_INDICATOR_TOTAL_FRAMES = 160
_BEGIN_ANIMATION_FRAMES = 11
_DAMAGE_INDICATOR_FRAME_RATE = 24
_BEGIN_ANIMATION_DURATION = _BEGIN_ANIMATION_FRAMES / float(_DAMAGE_INDICATOR_FRAME_RATE)
_DAMAGE_INDICATOR_ANIMATION_DURATION = _DAMAGE_INDICATOR_TOTAL_FRAMES / float(_DAMAGE_INDICATOR_FRAME_RATE)
_DIRECT_INDICATOR_SWF = 'battleDirectionIndicatorApp.swf'
_DIRECT_INDICATOR_COMPONENT = 'WGDirectionIndicatorFlash'
_DIRECT_INDICATOR_MC_NAME = '_root.directionalIndicatorMc'
_DIRECT_ARTY_INDICATOR_MC_NAME = '_root.artyDirectionalIndicatorMc'
_DIRECT_INDICATOR_SWF_SIZE = (680, 680)
_MARKER_SMALL_SIZE_THRESHOLD = 0.1
_MARKER_LARGE_SIZE_THRESHOLD = 0.3
_VIEWS_WITH_INV_CAMERA_ORIENTATION = (CROSSHAIR_VIEW_ID.STRATEGIC,)

class _MARKER_TYPE(CONST_CONTAINER):
    HP_DAMAGE = 0
    HP_ALLAY_DAMAGE = 1
    BLOCKED_DAMAGE = 2
    CRITICAL_DAMAGE = 3


class _MARKER_SIZE_TYPE(CONST_CONTAINER):
    SMALL = 0
    MEDIUM = 1
    LARGE = 2


class DAMAGE_INDICATOR_TYPE(CONST_CONTAINER):
    STANDARD = 0
    EXTENDED = 1


_EXTENDED_MARKER_TYPE_TO_CIRCLE_BG = {_MARKER_TYPE.HP_DAMAGE: DAMAGEINDICATOR.DAMAGE_CIRCLE,
 _MARKER_TYPE.HP_ALLAY_DAMAGE: DAMAGEINDICATOR.DAMAGE_CIRCLE,
 _MARKER_TYPE.BLOCKED_DAMAGE: DAMAGEINDICATOR.BLOCK_CIRCLE,
 _MARKER_TYPE.CRITICAL_DAMAGE: DAMAGEINDICATOR.CRIT_CIRCLE}
_EXTENDED_BLIND_MARKER_TYPE_TO_CIRCLE_BG = {_MARKER_TYPE.HP_DAMAGE: DAMAGEINDICATOR.DAMAGE_CIRCLE_BLIND,
 _MARKER_TYPE.HP_ALLAY_DAMAGE: DAMAGEINDICATOR.DAMAGE_CIRCLE_BLIND,
 _MARKER_TYPE.BLOCKED_DAMAGE: DAMAGEINDICATOR.BLOCK_CIRCLE,
 _MARKER_TYPE.CRITICAL_DAMAGE: DAMAGEINDICATOR.CRIT_CIRCLE_BLIND}
_CRITICAL_DAMAGE_TYPE_TO_CIRCLE_BG = {'engine': DAMAGEINDICATOR.ENGINE_CIRCLE,
 'ammoBay': DAMAGEINDICATOR.AMMO_CIRCLE,
 'fuelTank': DAMAGEINDICATOR.TANKS_CIRCLE,
 'radio': DAMAGEINDICATOR.RADIO_CIRCLE,
 'track': DAMAGEINDICATOR.TRACKS_CIRCLE,
 'wheel': DAMAGEINDICATOR.WHEEL_CIRCLE,
 'gun': DAMAGEINDICATOR.GUN_CIRCLE,
 'turretRotator': DAMAGEINDICATOR.TURRET_CIRCLE,
 'surveyingDevice': DAMAGEINDICATOR.TRIPLEX_CIRCLE,
 'commander': DAMAGEINDICATOR.COMMANDER_CIRCLE,
 'driver': DAMAGEINDICATOR.DRIVER_CIRCLE,
 'radioman': DAMAGEINDICATOR.RADIOMAN_CIRCLE,
 'gunner': DAMAGEINDICATOR.GUNNER_CIRCLE,
 'loader': DAMAGEINDICATOR.RELOADER_CIRCLE,
 'ally_engine': DAMAGEINDICATOR.ENGINE_CIRCLE,
 'ally_ammoBay': DAMAGEINDICATOR.AMMO_CIRCLE,
 'ally_fuelTank': DAMAGEINDICATOR.TANKS_CIRCLE,
 'ally_radio': DAMAGEINDICATOR.RADIO_CIRCLE,
 'ally_track': DAMAGEINDICATOR.TRACKS_CIRCLE,
 'ally_wheel': DAMAGEINDICATOR.WHEEL_CIRCLE,
 'ally_gun': DAMAGEINDICATOR.GUN_CIRCLE,
 'ally_turretRotator': DAMAGEINDICATOR.TURRET_CIRCLE,
 'ally_surveyingDevice': DAMAGEINDICATOR.TRIPLEX_CIRCLE,
 'ally_commander': DAMAGEINDICATOR.COMMANDER_CIRCLE,
 'ally_driver': DAMAGEINDICATOR.DRIVER_CIRCLE,
 'ally_radioman': DAMAGEINDICATOR.RADIOMAN_CIRCLE,
 'ally_gunner': DAMAGEINDICATOR.GUNNER_CIRCLE,
 'ally_loader': DAMAGEINDICATOR.RELOADER_CIRCLE}
_STANDARD_MARKER_TYPE_TO_BG = {_MARKER_TYPE.HP_DAMAGE: DAMAGEINDICATOR.DAMAGE_STANDARD,
 _MARKER_TYPE.HP_ALLAY_DAMAGE: DAMAGEINDICATOR.DAMAGE_STANDARD,
 _MARKER_TYPE.BLOCKED_DAMAGE: DAMAGEINDICATOR.BLOCKED_STANDARD,
 _MARKER_TYPE.CRITICAL_DAMAGE: DAMAGEINDICATOR.DAMAGE_STANDARD}
_STANDARD_BLIND_MARKER_TYPE_TO_BG = {_MARKER_TYPE.HP_DAMAGE: DAMAGEINDICATOR.DAMAGE_STANDARD_BLIND,
 _MARKER_TYPE.HP_ALLAY_DAMAGE: DAMAGEINDICATOR.DAMAGE_STANDARD_BLIND,
 _MARKER_TYPE.BLOCKED_DAMAGE: DAMAGEINDICATOR.BLOCKED_STANDARD,
 _MARKER_TYPE.CRITICAL_DAMAGE: DAMAGEINDICATOR.DAMAGE_STANDARD_BLIND}
_EXTENDED_MARKER_TYPE_TO_BG = {_MARKER_TYPE.HP_DAMAGE: {_MARKER_SIZE_TYPE.SMALL: DAMAGEINDICATOR.DAMAGE_SMALL,
                          _MARKER_SIZE_TYPE.MEDIUM: DAMAGEINDICATOR.DAMAGE_MEDIUM,
                          _MARKER_SIZE_TYPE.LARGE: DAMAGEINDICATOR.DAMAGE_BIG},
 _MARKER_TYPE.HP_ALLAY_DAMAGE: {_MARKER_SIZE_TYPE.SMALL: DAMAGEINDICATOR.DAMAGE_SMALL,
                                _MARKER_SIZE_TYPE.MEDIUM: DAMAGEINDICATOR.DAMAGE_MEDIUM,
                                _MARKER_SIZE_TYPE.LARGE: DAMAGEINDICATOR.DAMAGE_BIG},
 _MARKER_TYPE.BLOCKED_DAMAGE: {_MARKER_SIZE_TYPE.SMALL: DAMAGEINDICATOR.BLOCKED_SMALL,
                               _MARKER_SIZE_TYPE.MEDIUM: DAMAGEINDICATOR.BLOCKED_MEDIUM,
                               _MARKER_SIZE_TYPE.LARGE: DAMAGEINDICATOR.BLOCKED_BIG},
 _MARKER_TYPE.CRITICAL_DAMAGE: {_MARKER_SIZE_TYPE.SMALL: DAMAGEINDICATOR.CRIT,
                                _MARKER_SIZE_TYPE.MEDIUM: DAMAGEINDICATOR.CRIT,
                                _MARKER_SIZE_TYPE.LARGE: DAMAGEINDICATOR.CRIT}}
_EXTENDED_BLIND_MARKER_TYPE_TO_BG = {_MARKER_TYPE.HP_DAMAGE: {_MARKER_SIZE_TYPE.SMALL: DAMAGEINDICATOR.DAMAGE_SMALL_BLIND,
                          _MARKER_SIZE_TYPE.MEDIUM: DAMAGEINDICATOR.DAMAGE_MEDIUM_BLIND,
                          _MARKER_SIZE_TYPE.LARGE: DAMAGEINDICATOR.DAMAGE_BIG_BLIND},
 _MARKER_TYPE.HP_ALLAY_DAMAGE: {_MARKER_SIZE_TYPE.SMALL: DAMAGEINDICATOR.DAMAGE_SMALL_BLIND,
                                _MARKER_SIZE_TYPE.MEDIUM: DAMAGEINDICATOR.DAMAGE_MEDIUM_BLIND,
                                _MARKER_SIZE_TYPE.LARGE: DAMAGEINDICATOR.DAMAGE_BIG_BLIND},
 _MARKER_TYPE.BLOCKED_DAMAGE: {_MARKER_SIZE_TYPE.SMALL: DAMAGEINDICATOR.BLOCKED_SMALL,
                               _MARKER_SIZE_TYPE.MEDIUM: DAMAGEINDICATOR.BLOCKED_MEDIUM,
                               _MARKER_SIZE_TYPE.LARGE: DAMAGEINDICATOR.BLOCKED_BIG},
 _MARKER_TYPE.CRITICAL_DAMAGE: {_MARKER_SIZE_TYPE.SMALL: DAMAGEINDICATOR.CRIT_BLIND,
                                _MARKER_SIZE_TYPE.MEDIUM: DAMAGEINDICATOR.CRIT_BLIND,
                                _MARKER_SIZE_TYPE.LARGE: DAMAGEINDICATOR.CRIT_BLIND}}

class _MarkerData(object):

    def __init__(self, idx, timeLeft, hitData, isBlind=False):
        super(_MarkerData, self).__init__()
        self.idx = idx
        self.timeLeft = timeLeft
        self.hitData = hitData
        self.markerType = self.__getMarkerType(hitData)
        self.isBlind = isBlind

    @staticmethod
    def __getMarkerType(hitData):
        if hitData.isBlocked():
            return _MARKER_TYPE.BLOCKED_DAMAGE
        if hitData.getDamage() > 0:
            if hitData.isAttackerAlly():
                return _MARKER_TYPE.HP_ALLAY_DAMAGE
            return _MARKER_TYPE.HP_DAMAGE
        return _MARKER_TYPE.CRITICAL_DAMAGE


class _MarkerVOBuilder(object):

    def buildVO(self, markerData):
        return {'itemIdx': markerData.idx,
         'frame': markerData.timeLeft * self._getIndicatorFrameRate(),
         'bgStr': self._getBackground(markerData)}

    def _getIndicatorFrameRate(self):
        return _DAMAGE_INDICATOR_FRAME_RATE

    def _getBackground(self, markerData):
        pass


class _StandardMarkerVOBuilder(_MarkerVOBuilder):

    def _getBackground(self, markerData):
        return _STANDARD_BLIND_MARKER_TYPE_TO_BG[markerData.markerType] if markerData.isBlind else _STANDARD_MARKER_TYPE_TO_BG[markerData.markerType]


class _ExtendedMarkerVOBuilder(_MarkerVOBuilder):

    def __init__(self, dynamicIndicatorSize):
        super(_ExtendedMarkerVOBuilder, self).__init__()
        self.__dynamicIndicatorSize = dynamicIndicatorSize

    def buildVO(self, markerData):
        vo = super(_ExtendedMarkerVOBuilder, self).buildVO(markerData)
        vo.update({'circleStr': self._getCircleBackground(markerData),
         'tankTypeStr': self._getTankType(markerData),
         'tankName': markerData.hitData.getAttackerVehicleName(),
         'damageValue': self._getDamageLabel(markerData),
         'isFriendlyFire': markerData.hitData.isFriendlyFire()})
        return vo

    def _getBackground(self, markerData):
        sizeType = self._getSizeType(markerData.hitData.getPlayerVehicleMaxHP(), markerData.hitData.getDamage())
        if markerData.isBlind:
            bgMap = _EXTENDED_BLIND_MARKER_TYPE_TO_BG
        else:
            bgMap = _EXTENDED_MARKER_TYPE_TO_BG
        return bgMap[markerData.markerType][sizeType]

    def _getCircleBackground(self, markerData):
        return _EXTENDED_BLIND_MARKER_TYPE_TO_CIRCLE_BG[markerData.markerType] if markerData.isBlind else _EXTENDED_MARKER_TYPE_TO_CIRCLE_BG[markerData.markerType]

    def _getTankType(self, markerData):
        tankTypeStr = markerData.hitData.getAttackerVehicleClassTag()
        if markerData.hitData.isFriendlyFire():
            tankTypeStr = 'ally_' + tankTypeStr
        return tankTypeStr

    def _getDamageLabel(self, markerData):
        return backport.text(R.strings.ingame_gui.damageIndicator.friendlyFire.noDamageLabel()) if markerData.hitData.isFriendlyFire() else str(markerData.hitData.getDamage())

    def _getSizeType(self, hp, damage):
        sizeType = _MARKER_SIZE_TYPE.SMALL
        if self.__dynamicIndicatorSize and hp > 0:
            ratio = float(damage) / hp
            if ratio <= _MARKER_SMALL_SIZE_THRESHOLD:
                sizeType = _MARKER_SIZE_TYPE.SMALL
            elif ratio <= _MARKER_LARGE_SIZE_THRESHOLD:
                sizeType = _MARKER_SIZE_TYPE.MEDIUM
            else:
                sizeType = _MARKER_SIZE_TYPE.LARGE
        return sizeType


class _ExtendedCriticalMarkerVOBuilder(_ExtendedMarkerVOBuilder):

    def _getCircleBackground(self, markerData):
        if markerData.hitData.getCritsCount() == 1:
            mask = markerData.hitData.getCriticalFlags()
            critType = self._makeCritType(mask, markerData.hitData.isAttackerAlly())
            if critType in _CRITICAL_DAMAGE_TYPE_TO_CIRCLE_BG:
                return _CRITICAL_DAMAGE_TYPE_TO_CIRCLE_BG[critType]
        return super(_ExtendedCriticalMarkerVOBuilder, self)._getCircleBackground(markerData)

    def _getDamageLabel(self, markerData):
        critsCount = markerData.hitData.getCritsCount()
        return i18n.makeString(INGAME_GUI.DAMAGEINDICATOR_MULTIPLIER, multiplier=str(critsCount)) if critsCount > 1 else ''

    @staticmethod
    def _getCritType(mask):
        for _, critType in critsParserGenerator(mask):
            return critType

    @staticmethod
    def _makeCritType(mask, isAlly):
        critType = _ExtendedCriticalMarkerVOBuilder._getCritType(mask)
        if critType and isAlly:
            critType = 'ally_' + critType
        return critType


class _AbstractMarkerVOBuilderFactory(object):

    def getVOBuilder(self, markerData):
        raise NotImplementedError

    def buildMarkerVO(self, markerData):
        builder = self.getVOBuilder(markerData)
        return builder.buildVO(markerData)


class _ExtendedMarkerVOBuilderFactory(_AbstractMarkerVOBuilderFactory):

    def __init__(self, isIndicatorSizeDynamic):
        super(_ExtendedMarkerVOBuilderFactory, self).__init__()
        self.__isIndicatorSizeDynamic = isIndicatorSizeDynamic

    def getVOBuilder(self, markerData):
        return _ExtendedCriticalMarkerVOBuilder(self.__isIndicatorSizeDynamic) if markerData.markerType == _MARKER_TYPE.CRITICAL_DAMAGE else _ExtendedMarkerVOBuilder(self.__isIndicatorSizeDynamic)


class _StandardMarkerVOBuilderFactory(_AbstractMarkerVOBuilderFactory):

    def getVOBuilder(self, markerData):
        return _StandardMarkerVOBuilder()


_DEFAULT_DAMAGE_INDICATOR_TYPE = DAMAGE_INDICATOR_TYPE.EXTENDED

class DamageIndicatorMeta(Flash):

    def __init__(self, swf, className, args):
        super(DamageIndicatorMeta, self).__init__(swf, className, args)
        root = self.movie.root.dmgIndicator
        self._as_updateSettings = root.as_updateSettings
        self._as_showStandard = root.as_showStandard
        self._as_showExtended = root.as_showExtended
        self._as_setYaw = root.as_setYaw
        self._as_hide = root.as_hide
        self._as_setScreenSettings = root.as_setScreenSettings
        self._as_setPosition = root.as_setPosition

    def destroy(self):
        self._as_updateSettings = None
        self._as_showStandard = None
        self._as_showExtended = None
        self._as_setYaw = None
        self._as_hide = None
        self._as_setScreenSettings = None
        self._as_setPosition = None
        self.movie.root.dmgIndicator.dispose()
        return

    def as_updateSettingsS(self, isStandard, isWithTankInfo, isWithAnimation, isWithValue):
        return self._as_updateSettings(isStandard, isWithTankInfo, isWithAnimation, isWithValue)

    def as_showStandardS(self, itemIdx, bgStr, frame):
        return self._as_showStandard(itemIdx, bgStr, frame)

    def as_showExtendedS(self, itemIdx, bgStr, circleStr, frame, tankName, tankTypeStr, damageValue, isFriendlyFire):
        return self._as_showExtended(itemIdx, bgStr, circleStr, frame, tankName, tankTypeStr, damageValue, isFriendlyFire)

    def as_hideS(self, itemIdx):
        return self._as_hide(itemIdx)

    def as_setYawS(self, itemIdx, yaw):
        return self._as_setYaw(itemIdx, yaw)

    def as_setScreenSettingsS(self, scale, screenWidth, screenHeight):
        return self._as_setScreenSettings(scale, screenWidth, screenHeight)

    def as_setPosition(self, posX, posY):
        self._as_setPosition(posX, posY)


class _DamageIndicator(DamageIndicatorMeta, IHitIndicator):
    sessionProvider = dependency.descriptor(IBattleSessionProvider)
    settingsCore = dependency.descriptor(ISettingsCore)

    def __init__(self, hitsCount):
        names = tuple((_DAMAGE_INDICATOR_MC_NAME.format(x) for x in xrange(hitsCount)))
        super(_DamageIndicator, self).__init__(_DAMAGE_INDICATOR_SWF, _DAMAGE_INDICATOR_COMPONENT, (names,))
        self.__voBuilderFactory = None
        self.__updateMethod = None
        self.component.wg_inputKeyMode = InputKeyMode.NO_HANDLE
        self.component.position.z = DEPTH_OF_Aim
        self.movie.backgroundAlpha = 0.0
        self.component.focus = False
        self.component.moveFocus = False
        self.component.heightMode = 'PIXEL'
        self.component.widthMode = 'PIXEL'
        self.movie.scaleMode = 'NoScale'
        self.component.useInvertCameraView = False
        self.__isBlind = bool(self.settingsCore.getSetting(GRAPHICS.COLOR_BLIND))
        self.__setUpVOBuilderFactoryAndUpdateMethod(_DEFAULT_DAMAGE_INDICATOR_TYPE)
        self.settingsCore.interfaceScale.onScaleChanged += self.__setMarkersScale
        ctrl = self.sessionProvider.shared.crosshair
        if ctrl is not None:
            ctrl.onCrosshairPositionChanged += self.__onCrosshairPositionChanged
            ctrl.onCrosshairViewChanged += self.__onCrosshairViewChanged
            self.__onCrosshairPositionChanged(*ctrl.getPosition())
            self.__onCrosshairViewChanged(ctrl.getViewID())
        self.__setMarkersScale()
        self.active(True)
        self.component.offsetRotationElementsInDegree(10.0, 10.0)
        return

    def __del__(self):
        LOG_DEBUG('DamageIndicator is deleted')

    def getHitType(self):
        return HitType.HIT_DAMAGE

    def destroy(self):
        super(_DamageIndicator, self).destroy()
        self.settingsCore.interfaceScale.onScaleChanged -= self.__setMarkersScale
        ctrl = self.sessionProvider.shared.crosshair
        if ctrl is not None:
            ctrl.onCrosshairOffsetChanged -= self.__onCrosshairPositionChanged
            ctrl.onCrosshairViewChanged -= self.__onCrosshairViewChanged
        self.__updateMethod = None
        self.close()
        return

    def getDuration(self):
        return _DAMAGE_INDICATOR_ANIMATION_DURATION

    def getBeginAnimationDuration(self):
        return _BEGIN_ANIMATION_DURATION

    def invalidateSettings(self, diff=None):
        getter = self.settingsCore.getSetting
        self.__isBlind = bool(getter(GRAPHICS.COLOR_BLIND))
        indicatorType = getter(DAMAGE_INDICATOR.TYPE)
        self.__setUpVOBuilderFactoryAndUpdateMethod(indicatorType)
        self.as_updateSettingsS(isStandard=indicatorType == DAMAGE_INDICATOR_TYPE.STANDARD, isWithTankInfo=bool(getter(DAMAGE_INDICATOR.VEHICLE_INFO)), isWithAnimation=bool(getter(DAMAGE_INDICATOR.ANIMATION)), isWithValue=bool(getter(DAMAGE_INDICATOR.DAMAGE_VALUE)))

    def showHitDirection(self, idx, hitData, timeLeft):
        self.as_setYawS(idx, hitData.getYaw())
        markerData = _MarkerData(idx=idx, timeLeft=timeLeft, hitData=hitData, isBlind=self.__isBlind)
        vo = self.__voBuilderFactory.buildMarkerVO(markerData)
        LOG_DEBUG_DEV('showHitDirection hit={}, vo={}'.format(hitData, vo))
        self.__updateMethod(**vo)

    def hideHitDirection(self, idx):
        self.as_hideS(idx)

    def __onCrosshairPositionChanged(self, posX, posY):
        self.as_setPosition(posX, posY)

    def __setUpVOBuilderFactoryAndUpdateMethod(self, indicatorType):
        if indicatorType == DAMAGE_INDICATOR_TYPE.EXTENDED:
            isIndicatorSizeDynamic = bool(self.settingsCore.getSetting(DAMAGE_INDICATOR.DYNAMIC_INDICATOR))
            self.__voBuilderFactory = _ExtendedMarkerVOBuilderFactory(isIndicatorSizeDynamic)
            self.__updateMethod = self.as_showExtendedS
        else:
            self.__voBuilderFactory = _StandardMarkerVOBuilderFactory()
            self.__updateMethod = self.as_showStandardS

    def __setMarkersScale(self, scale=None):
        if scale is None:
            scale = self.settingsCore.interfaceScale.get()
        width, height = GUI.screenResolution()
        self.as_setScreenSettingsS(scale, width, height)
        return

    def __onCrosshairViewChanged(self, viewID):
        self.component.useInvertCameraView = viewID in _VIEWS_WITH_INV_CAMERA_ORIENTATION


class SixthSenseIndicator(SixthSenseMeta):
    sessionProvider = dependency.descriptor(IBattleSessionProvider)
    settingsCore = dependency.descriptor(ISettingsCore)

    def __init__(self):
        super(SixthSenseIndicator, self).__init__()
        self.__callbackID = None
        self.__detectionSoundEventName = None
        self.__detectionSoundEvent = None
        self.__enabled = True
        return

    @property
    def enabled(self):
        return self.__enabled

    @enabled.setter
    def enabled(self, enabled):
        self.__enabled = enabled

    def show(self):
        self.as_showS()

    def hide(self):
        self.as_hideS()

    def _populate(self):
        super(SixthSenseIndicator, self)._populate()
        detectionAlertSetting = self.settingsCore.options.getSetting(SOUND.DETECTION_ALERT_SOUND)
        self.__setDetectionSoundEvent(detectionAlertSetting.getEventName())
        self.settingsCore.onSettingsChanged += self.__onSettingsChanged
        ctrl = self.sessionProvider.shared.vehicleState
        if ctrl is not None:
            ctrl.onVehicleStateUpdated += self.__onVehicleStateUpdated
        return

    def _dispose(self):
        self.__cancelCallback()
        ctrl = self.sessionProvider.shared.vehicleState
        if ctrl is not None:
            ctrl.onVehicleStateUpdated -= self.__onVehicleStateUpdated
        self.settingsCore.onSettingsChanged -= self.__onSettingsChanged
        super(SixthSenseIndicator, self)._dispose()
        return

    def __show(self):
        if not self.__enabled:
            return
        else:
            if self.__detectionSoundEvent is not None:
                if self.__detectionSoundEvent.isPlaying:
                    self.__detectionSoundEvent.restart()
                else:
                    if self.__detectionSoundEvent.name in SoundGroups.CUSTOM_MP3_EVENTS:
                        SoundGroups.g_instance.prepareMP3(self.__detectionSoundEvent.name)
                    self.__detectionSoundEvent.play()
                self.sessionProvider.shared.optionalDevices.soundManager.playLightbulbEffect()
            self.as_showS()
            self.__callbackID = BigWorld.callback(GUI_SETTINGS.sixthSenseDuration / 1000.0, self.__hide)
            return

    def __hide(self):
        self.__callbackID = None
        if not self.__enabled:
            return
        else:
            self.as_hideS()
            return

    def __cancelCallback(self):
        if self.__callbackID is not None:
            BigWorld.cancelCallback(self.__callbackID)
            self.__callbackID = None
        return

    def __onVehicleStateUpdated(self, state, value):
        if state == VEHICLE_VIEW_STATE.OBSERVED_BY_ENEMY:
            if value:
                self.__cancelCallback()
                self.__show()
            else:
                self.__cancelCallback()
                self.__hide()

    def __onSettingsChanged(self, diff):
        key = SOUND.DETECTION_ALERT_SOUND
        if key in diff:
            detectionAlertSetting = self.settingsCore.options.getSetting(key)
            self.__setDetectionSoundEvent(detectionAlertSetting.getEventName())

    def __setDetectionSoundEvent(self, soundEventName):
        if self.__detectionSoundEventName != soundEventName:
            self.__detectionSoundEventName = soundEventName
            self.__detectionSoundEvent = SoundGroups.g_instance.getSound2D(self.__detectionSoundEventName)


class SiegeModeIndicator(SiegeModeIndicatorMeta):
    sessionProvider = dependency.descriptor(IBattleSessionProvider)
    settingsCore = dependency.descriptor(ISettingsCore)

    def __init__(self):
        super(SiegeModeIndicator, self).__init__()
        self._isEnabled = False
        self._siegeState = _SIEGE_STATE.DISABLED
        self._devices = {}
        self._switchTime = 0.0
        self._startTime = BigWorld.serverTime()
        self._switchTimeTable = {}
        self._siegeComponent = None
        self._deviceStateConverter = lambda s, dn: s
        return

    def _populate(self):
        vStateCtrl = self.sessionProvider.shared.vehicleState
        crosshairCtrl = self.sessionProvider.shared.crosshair
        isReplayPlaying = self.sessionProvider.isReplayPlaying
        self._siegeComponent = siege_component.createSiegeComponent(self, isReplayPlaying)
        if crosshairCtrl is not None:
            crosshairCtrl.onCrosshairPositionChanged += self.__onCrosshairPositionChanged
            crosshairCtrl.onCrosshairScaleChanged += self.__onCrosshairPositionChanged
            crosshairCtrl.onCrosshairViewChanged += self.__onCrosshairViewChanged
        if vStateCtrl is not None:
            vStateCtrl.onVehicleStateUpdated += self.__onVehicleStateUpdated
            vStateCtrl.onVehicleControlling += self.__onVehicleControlling
            vehicle = vStateCtrl.getControllingVehicle()
            if vehicle is not None:
                self.__onVehicleControlling(vehicle)
        self.as_setVisibleS(self._isEnabled)
        return

    def _dispose(self):
        vStateCtrl = self.sessionProvider.shared.vehicleState
        crosshairCtrl = self.sessionProvider.shared.crosshair
        if crosshairCtrl is not None:
            crosshairCtrl.onCrosshairPositionChanged -= self.__onCrosshairPositionChanged
            crosshairCtrl.onCrosshairScaleChanged -= self.__onCrosshairPositionChanged
            crosshairCtrl.onCrosshairViewChanged -= self.__onCrosshairViewChanged
        if vStateCtrl is not None:
            vStateCtrl.onVehicleStateUpdated -= self.__onVehicleStateUpdated
            vStateCtrl.onVehicleControlling -= self.__onVehicleControlling
        self._switchTimeTable.clear()
        self._siegeComponent.clear()
        self._siegeComponent = None
        return

    def __updateIndicatorView(self, isSmooth=False):
        LOG_DEBUG('Updating siege mode: indicator')
        engineState = self._devices.get('engine', DEVICE_STATE_NORMAL)
        totalTime = self._switchTimeTable[self._siegeState][engineState]
        self._siegeComponent.invalidate(totalTime, self._switchTime, self._siegeState, engineState, isSmooth)

    def __updateDevicesView(self):
        if self._siegeComponent.staticMode or not self._devices:
            return
        LOG_DEBUG('Updating siege mode: devices')
        device = max(self._devices.items(), key=self.__getDeviceStateLevel)
        deviceName, deviceState = device
        if deviceName in VEHICLE_DEVICE_IN_COMPLEX_ITEM:
            deviceName = VEHICLE_DEVICE_IN_COMPLEX_ITEM[deviceName]
        self.as_updateDeviceStateS(deviceName, deviceState)

    def __onVehicleControlling(self, vehicle):
        vStateCtrl = self.sessionProvider.shared.vehicleState
        vTypeDesc = vehicle.typeDescriptor
        vType = vTypeDesc.type
        self.__resetDevices()
        self.__updateDevicesView()
        if vehicle.isAlive() and vTypeDesc.hasSiegeMode and (vTypeDesc.hasTurboshaftEngine or vTypeDesc.hasHydraulicChassis or vTypeDesc.hasAutoSiegeMode):
            siegeModeParams = vType.siegeModeParams
            uiType = self.__getUIType(vTypeDesc)
            self.as_setSiegeModeTypeS(uiType)
            self._siegeComponent.staticMode = vTypeDesc.hasAutoSiegeMode
            self._switchTimeTable.update({_SIEGE_STATE.DISABLED: siegeModeParams[_SIEGE_STATE.SWITCHING_ON],
             _SIEGE_STATE.SWITCHING_ON: siegeModeParams[_SIEGE_STATE.SWITCHING_ON],
             _SIEGE_STATE.ENABLED: siegeModeParams[_SIEGE_STATE.SWITCHING_OFF],
             _SIEGE_STATE.SWITCHING_OFF: siegeModeParams[_SIEGE_STATE.SWITCHING_OFF]})
            self._devices = self.__createDevicesMap(vTypeDesc)
            self._deviceStateConverter = self.__getDeviceStateConverter(vTypeDesc)
            self._isEnabled = True
            for stateID in (VEHICLE_VIEW_STATE.DEVICES, VEHICLE_VIEW_STATE.SIEGE_MODE):
                value = vStateCtrl.getStateValue(stateID)
                if value is not None:
                    if stateID == VEHICLE_VIEW_STATE.DEVICES:
                        for v in value:
                            self.__onVehicleStateUpdated(stateID, v)

                    else:
                        self.__onVehicleStateUpdated(stateID, value)

            self.__onCrosshairPositionChanged()
            self.__updateDevicesView()
        else:
            self._siegeState = _SIEGE_STATE.DISABLED
            self._isEnabled = False
        self.as_setVisibleS(self._isEnabled)
        return

    def __onVehicleStateUpdated(self, state, value):
        if state == VEHICLE_VIEW_STATE.SWITCHING:
            self.__resetDevices()
            if not value:
                self._isEnabled = False
                self.as_setVisibleS(self._isEnabled)
        else:
            if not self._isEnabled:
                return
            if state == VEHICLE_VIEW_STATE.SIEGE_MODE:
                self.__updateSiegeState(*value)
            elif state == VEHICLE_VIEW_STATE.DEVICES:
                self.__updateDevicesState(*value)
            elif state == VEHICLE_VIEW_STATE.DESTROYED:
                self.__updateDestroyed(value)
            elif state == VEHICLE_VIEW_STATE.CREW_DEACTIVATED:
                self.__updateDestroyed(value)

    def __onCrosshairPositionChanged(self, *args):
        if not self._isEnabled:
            return
        crosshairCtrl = self.sessionProvider.shared.crosshair
        scaledPosition = crosshairCtrl.getScaledPosition()
        self.as_updateLayoutS(*scaledPosition)

    def __onCrosshairViewChanged(self, viewID):
        if viewID == CROSSHAIR_VIEW_ID.UNDEFINED:
            self.as_setVisibleS(False)
        else:
            self.as_setVisibleS(self._isEnabled)

    def __updateSiegeState(self, siegeState, switchTime):
        if self._siegeState in _SIEGE_STATE.SWITCHING:
            isSmooth = siegeState not in _SIEGE_STATE.SWITCHING
        else:
            isSmooth = siegeState in _SIEGE_STATE.SWITCHING
        self._startTime = BigWorld.serverTime()
        self._siegeState = siegeState
        self._switchTime = switchTime
        self.__updateIndicatorView(isSmooth)

    def __updateDevicesState(self, deviceName, _, realState):
        if deviceName in self._devices:
            self._devices[deviceName] = self._deviceStateConverter(deviceName, realState)
            self.__updateDevicesView()

    def __updateDestroyed(self, _):
        self._isEnabled = False
        self.as_setVisibleS(False)

    def __resetDevices(self):
        for deviceName in self._devices:
            self._devices[deviceName] = DEVICE_STATE_NORMAL

    @classmethod
    def __getDeviceStateConverter(cls, vTypeDesc):
        if vTypeDesc.hasHydraulicChassis or vTypeDesc.hasAutoSiegeMode:
            return cls.__hydraulicDeviceStateConverter
        if vTypeDesc.hasTurboshaftEngine:
            return cls.__turboshaftDeviceStateConverter
        raise SoftException("Can't get device state converter for siege mode")

    @staticmethod
    def __hydraulicDeviceStateConverter(deviceName, state):
        return DEVICE_STATE_NORMAL if state == DEVICE_STATE_CRITICAL and deviceName in ('leftTrack0', 'rightTrack0') else state

    @staticmethod
    def __turboshaftDeviceStateConverter(deviceName, state):
        return DEVICE_STATE_NORMAL if state == DEVICE_STATE_CRITICAL and deviceName == 'engine' else state

    @staticmethod
    def __getUIType(vTypeDesc):
        if vTypeDesc.hasHydraulicChassis or vTypeDesc.hasAutoSiegeMode:
            return SIEGE_MODE_CONSTS.HYDRAULIC_CHASSIS_TYPE
        if vTypeDesc.hasTurboshaftEngine:
            return SIEGE_MODE_CONSTS.TURBOSHAFT_ENGINE_TYPE
        raise SoftException("Can't get UI siege mode type")

    @staticmethod
    def __createDevicesMap(vTypeDesc):
        if vTypeDesc.hasHydraulicChassis or vTypeDesc.hasAutoSiegeMode:
            deviceNames = ('engine', 'leftTrack0', 'rightTrack0')
        elif vTypeDesc.hasTurboshaftEngine:
            deviceNames = ('engine',)
        else:
            raise SoftException("Can't create updatable devices")
        return {name:DEVICE_STATE_NORMAL for name in deviceNames}

    @staticmethod
    def __getDeviceStateLevel(device):
        return DEVICE_STATES_RANGE.index(device[1])


class IDirectionIndicator(object):

    def track(self, position):
        pass

    def setShape(self, shape):
        pass

    def setDistance(self, distance):
        pass

    def setPosition(self, position):
        pass

    def remove(self):
        pass


class _DirectionIndicator(Flash, IDirectionIndicator):

    def __init__(self, swf):
        super(_DirectionIndicator, self).__init__(swf, _DIRECT_INDICATOR_COMPONENT, (_DIRECT_INDICATOR_MC_NAME,))
        self.component.wg_inputKeyMode = InputKeyMode.NO_HANDLE
        self.component.position.z = DEPTH_OF_Aim
        self.movie.backgroundAlpha = 0.0
        self.movie.scaleMode = 'NoScale'
        self.component.focus = False
        self.component.moveFocus = False
        self.component.heightMode = 'PIXEL'
        self.component.widthMode = 'PIXEL'
        self.flashSize = _DIRECT_INDICATOR_SWF_SIZE
        self.__isVisible = True
        self.component.relativeRadius = 0.5
        self._dObject = getattr(self.movie, _DIRECT_INDICATOR_MC_NAME, None)
        return

    def __del__(self):
        LOG_DEBUG('DirectionIndicator deleted')

    def setShape(self, shape):
        if self._dObject:
            self._dObject.setShape(shape)

    def setDistance(self, distance):
        distanceFormat = '{}' + i18n.makeString(INGAME_GUI.MARKER_METERS)
        if self._dObject:
            self._dObject.setDistance(distanceFormat.format(distance))

    def setPosition(self, position):
        self.component.position3D = position

    def track(self, position):
        self.active(True)
        self.component.visible = True
        self.component.position3D = position

    def remove(self):
        self._dObject = None
        self.close()
        return

    def setVisibility(self, isVisible):
        if not self.__isVisible == isVisible:
            self.__isVisible = isVisible
            self.component.visible = isVisible


class _DirectionIndicatorMessage(_DirectionIndicator):

    def setMessage(self, message):
        if self._dObject:
            self._dObject.setMessage(message)


def createDirectIndicator():
    return _DirectionIndicator(_DIRECT_INDICATOR_SWF)


def createDamageIndicator():
    return _DamageIndicator(HIT_INDICATOR_MAX_ON_SCREEN)


def createPredictionIndicator():
    return _PredictionIndicator(PREDICTION_INDICATOR_MAX_ON_SCREEN)


class _ArtyDirectionIndicator(Flash, IDirectionIndicator):

    def __init__(self, swf):
        super(_ArtyDirectionIndicator, self).__init__(swf, _DIRECT_INDICATOR_COMPONENT, (_DIRECT_ARTY_INDICATOR_MC_NAME,))
        self.component.wg_inputKeyMode = InputKeyMode.NO_HANDLE
        self.component.position.z = DEPTH_OF_Aim
        self.movie.backgroundAlpha = 0.0
        self.movie.scaleMode = 'NoScale'
        self.component.focus = False
        self.component.moveFocus = False
        self.component.heightMode = 'PIXEL'
        self.component.widthMode = 'PIXEL'
        self.flashSize = _DIRECT_INDICATOR_SWF_SIZE
        self.__isVisible = True
        self.component.relativeRadius = 0.5
        self._dObject = getattr(self.movie, _DIRECT_ARTY_INDICATOR_MC_NAME, None)
        return

    def __del__(self):
        LOG_DEBUG('StunDirectionIndicator deleted')

    def setShape(self, shape):
        if self._dObject:
            self._dObject.setShape(shape)

    def setPosition(self, position):
        self.component.position3D = position

    def track(self, position):
        self.active(True)
        self.component.visible = True
        self.component.position3D = position

    def remove(self):
        self._dObject = None
        self.close()
        return

    def setVisibility(self, isVisible):
        if not self.__isVisible == isVisible:
            self.__isVisible = isVisible
            self.component.visible = isVisible


class PredictionIndicatorMeta(Flash):

    def __init__(self, swf, className, args):
        super(PredictionIndicatorMeta, self).__init__(swf, className, args)
        root = self.movie.root.predictionIndicator
        self._as_show = root.as_show
        self._as_setYaw = root.as_setYaw
        self._as_hide = root.as_hide
        self._as_setPosition = root.as_setPosition
        self._as_setScreenSettings = root.as_setScreenSettings

    def destroy(self):
        self._as_show = None
        self._as_setYaw = None
        self._as_hide = None
        self._as_setPosition = None
        self._as_setScreenSettings = None
        self.movie.root.predictionIndicator.dispose()
        return

    def as_showS(self, itemIdx):
        return self._as_show(itemIdx)

    def as_hideS(self, itemIdx):
        return self._as_hide(itemIdx)

    def as_setYawS(self, itemIdx, yaw):
        return self._as_setYaw(itemIdx, yaw)

    def as_setPosition(self, posX, posY):
        self._as_setPosition(posX, posY)

    def as_setScreenSettingsS(self, scale, screenWidth, screenHeight):
        return self._as_setScreenSettings(scale, screenWidth, screenHeight)


class _PredictionIndicator(PredictionIndicatorMeta, IHitIndicator):
    sessionProvider = dependency.descriptor(IBattleSessionProvider)
    settingsCore = dependency.descriptor(ISettingsCore)

    def __init__(self, hitsCount):
        names = tuple((_PREDICTION_INDICATOR_MC_NAME.format(x) for x in xrange(hitsCount)))
        super(_PredictionIndicator, self).__init__(_PREDICTION_INDICATOR_SWF, _PREDICTION_INDICATOR_COMPONENT, (names,))
        self.component.wg_inputKeyMode = InputKeyMode.NO_HANDLE
        self.component.position.z = DEPTH_OF_Aim
        self.movie.backgroundAlpha = 0.0
        self.component.focus = False
        self.component.moveFocus = False
        self.component.heightMode = 'PIXEL'
        self.component.widthMode = 'PIXEL'
        self.movie.scaleMode = 'NoScale'
        self.component.useInvertCameraView = False
        self.settingsCore.interfaceScale.onScaleChanged += self.__setMarkersScale
        ctrl = self.sessionProvider.shared.crosshair
        if ctrl is not None:
            ctrl.onCrosshairPositionChanged += self.__onCrosshairPositionChanged
            ctrl.onCrosshairViewChanged += self.__onCrosshairViewChanged
            self.__onCrosshairPositionChanged(*ctrl.getPosition())
            self.__onCrosshairViewChanged(ctrl.getViewID())
        self.__setMarkersScale()
        self.active(True)
        return

    def __del__(self):
        LOG_DEBUG('PredictionIndicator is deleted')

    def getHitType(self):
        return HitType.ARTY_HIT_PREDICTION

    def destroy(self):
        super(_PredictionIndicator, self).destroy()
        self.settingsCore.interfaceScale.onScaleChanged -= self.__setMarkersScale
        ctrl = self.sessionProvider.shared.crosshair
        if ctrl is not None:
            ctrl.onCrosshairOffsetChanged -= self.__onCrosshairPositionChanged
            ctrl.onCrosshairViewChanged -= self.__onCrosshairViewChanged
        self.close()
        return

    def getDuration(self):
        return _PREDICTION_INDICATOR_MAX_DUR

    def getBeginAnimationDuration(self):
        pass

    def showHitDirection(self, idx, hitData, timeLeft):
        self.as_setYawS(idx, hitData.getYaw())
        self.as_showS(itemIdx=idx)

    def hideHitDirection(self, idx):
        self.as_hideS(idx)

    def __onCrosshairPositionChanged(self, posX, posY):
        self.as_setPosition(posX, posY)

    def __onCrosshairViewChanged(self, viewID):
        self.component.useInvertCameraView = viewID in _VIEWS_WITH_INV_CAMERA_ORIENTATION

    def __setMarkersScale(self, scale=None):
        if scale is None:
            scale = self.settingsCore.interfaceScale.get()
        width, height = GUI.screenResolution()
        self.as_setScreenSettingsS(scale, width, height)
        return
