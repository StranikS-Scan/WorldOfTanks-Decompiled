# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/battle/shared/indicators.py
import BigWorld
import GUI
import CommandMapping
from constants import VEHICLE_SIEGE_STATE as _SIEGE_STATE
from debug_utils import LOG_DEBUG, LOG_DEBUG_DEV
from gui import DEPTH_OF_Aim, GUI_SETTINGS, makeHtmlString
from helpers import dependency
from shared_utils import CONST_CONTAINER
from account_helpers.AccountSettings import AccountSettings
from account_helpers.settings_core.settings_constants import CONTROLS, SOUND, DAMAGE_INDICATOR, GRAPHICS
from gui.Scaleform import SCALEFORM_SWF_PATH_V3
from gui.Scaleform.Flash import Flash
from gui.Scaleform.daapi.view.battle.shared import siege_component
from gui.Scaleform.daapi.view.meta.SixthSenseMeta import SixthSenseMeta
from gui.Scaleform.daapi.view.meta.SiegeModeIndicatorMeta import SiegeModeIndicatorMeta
from gui.shared.crits_mask_parser import critsParserGenerator
from gui.shared.formatters import text_styles
from gui.shared.utils.key_mapping import getReadableKey
from gui.battle_control.battle_constants import HIT_INDICATOR_MAX_ON_SCREEN
from gui.battle_control.battle_constants import VEHICLE_VIEW_STATE
from gui.battle_control.battle_constants import DEVICE_STATES_RANGE
from gui.battle_control.controllers.hit_direction_ctrl import IHitIndicator
from gui.Scaleform.genConsts.DAMAGE_INDICATOR_ATLAS_ITEMS import DAMAGE_INDICATOR_ATLAS_ITEMS
from helpers import i18n
from gui.Scaleform.locale.INGAME_GUI import INGAME_GUI
import SoundGroups
from skeletons.account_helpers.settings_core import ISettingsCore
from skeletons.gui.battle_session import IBattleSessionProvider
_DAMAGE_INDICATOR_SWF = 'damageIndicator.swf'
_DAMAGE_INDICATOR_COMPONENT = 'WGHitIndicatorFlash'
_DAMAGE_INDICATOR_MC_NAME = '_root.dmgIndicator.hit_{0}'
_DAMAGE_INDICATOR_SWF_SIZE = (680, 680)
_DAMAGE_INDICATOR_TOTAL_FRAMES = 160
_BEGIN_ANIMATION_FRAMES = 11
_DAMAGE_INDICATOR_FRAME_RATE = 24
_BEGIN_ANIMATION_DURATION = _BEGIN_ANIMATION_FRAMES / float(_DAMAGE_INDICATOR_FRAME_RATE)
_DAMAGE_INDICATOR_ANIMATION_DURATION = _DAMAGE_INDICATOR_TOTAL_FRAMES / float(_DAMAGE_INDICATOR_FRAME_RATE)
_DIRECT_INDICATOR_SWF = 'directionIndicator.swf'
_DIRECT_INDICATOR_COMPONENT = 'WGDirectionIndicatorFlash'
_DIRECT_INDICATOR_MC_NAME = '_root.directionalIndicatorMc'
_DIRECT_INDICATOR_SWF_SIZE = (680, 680)
_MARKER_SMALL_SIZE_THRESHOLD = 0.1
_MARKER_LARGE_SIZE_THRESHOLD = 0.3

class _MARKER_TYPE(CONST_CONTAINER):
    """
    Types of damage indicator markers to be displayed on UI.
    """
    HP_DAMAGE = 0
    HP_ALLAY_DAMAGE = 1
    BLOCKED_DAMAGE = 2
    CRITICAL_DAMAGE = 3


class _MARKER_SIZE_TYPE(CONST_CONTAINER):
    """
    Types of sizes of extended damage indicator.
    """
    SMALL = 0
    MEDIUM = 1
    LARGE = 2


class DAMAGE_INDICATOR_TYPE(CONST_CONTAINER):
    """
    Types of damage indicator views. Note: values are correspond to possible settings
    (see DAMAGE_INDICATOR.TYPE setting)
    """
    STANDARD = 0
    EXTENDED = 1


_EXTENDED_MARKER_TYPE_TO_CIRCLE_BG = {_MARKER_TYPE.HP_DAMAGE: DAMAGE_INDICATOR_ATLAS_ITEMS.DAMAGE_CIRCLE,
 _MARKER_TYPE.HP_ALLAY_DAMAGE: DAMAGE_INDICATOR_ATLAS_ITEMS.DAMAGE_CIRCLE,
 _MARKER_TYPE.BLOCKED_DAMAGE: DAMAGE_INDICATOR_ATLAS_ITEMS.BLOCK_CIRCLE,
 _MARKER_TYPE.CRITICAL_DAMAGE: DAMAGE_INDICATOR_ATLAS_ITEMS.CRIT_CIRCLE}
_EXTENDED_BLIND_MARKER_TYPE_TO_CIRCLE_BG = {_MARKER_TYPE.HP_DAMAGE: DAMAGE_INDICATOR_ATLAS_ITEMS.DAMAGE_CIRCLE_BLIND,
 _MARKER_TYPE.HP_ALLAY_DAMAGE: DAMAGE_INDICATOR_ATLAS_ITEMS.DAMAGE_CIRCLE_BLIND,
 _MARKER_TYPE.BLOCKED_DAMAGE: DAMAGE_INDICATOR_ATLAS_ITEMS.BLOCK_CIRCLE,
 _MARKER_TYPE.CRITICAL_DAMAGE: DAMAGE_INDICATOR_ATLAS_ITEMS.CRIT_CIRCLE}
_CRITICAL_DAMAGE_TYPE_TO_CIRCLE_BG = {'engine': DAMAGE_INDICATOR_ATLAS_ITEMS.CRITS_ENGINE_CIRCLE,
 'ammoBay': DAMAGE_INDICATOR_ATLAS_ITEMS.CRITS_AMMO_CIRCLE,
 'fuelTank': DAMAGE_INDICATOR_ATLAS_ITEMS.CRITS_TANKS_CIRCLE,
 'radio': DAMAGE_INDICATOR_ATLAS_ITEMS.CRITS_RADIO_CIRCLE,
 'track': DAMAGE_INDICATOR_ATLAS_ITEMS.CRITS_TRACKS_CIRCLE,
 'gun': DAMAGE_INDICATOR_ATLAS_ITEMS.CRITS_GUN_CIRCLE,
 'turretRotator': DAMAGE_INDICATOR_ATLAS_ITEMS.CRITS_TURRET_CIRCLE,
 'surveyingDevice': DAMAGE_INDICATOR_ATLAS_ITEMS.CRITS_TRIPLEX_CIRCLE,
 'commander': DAMAGE_INDICATOR_ATLAS_ITEMS.CRITS_COMMANDER_CIRCLE,
 'driver': DAMAGE_INDICATOR_ATLAS_ITEMS.CRITS_DRIVER_CIRCLE,
 'radioman': DAMAGE_INDICATOR_ATLAS_ITEMS.CRITS_RADIOMAN_CIRCLE,
 'gunner': DAMAGE_INDICATOR_ATLAS_ITEMS.CRITS_GUNNER_CIRCLE,
 'loader': DAMAGE_INDICATOR_ATLAS_ITEMS.CRITS_RELOADER_CIRCLE,
 'ally_engine': DAMAGE_INDICATOR_ATLAS_ITEMS.CRITS_ENGINE_CIRCLE,
 'ally_ammoBay': DAMAGE_INDICATOR_ATLAS_ITEMS.CRITS_AMMO_CIRCLE,
 'ally_fuelTank': DAMAGE_INDICATOR_ATLAS_ITEMS.CRITS_TANKS_CIRCLE,
 'ally_radio': DAMAGE_INDICATOR_ATLAS_ITEMS.CRITS_RADIO_CIRCLE,
 'ally_track': DAMAGE_INDICATOR_ATLAS_ITEMS.CRITS_TRACKS_CIRCLE,
 'ally_gun': DAMAGE_INDICATOR_ATLAS_ITEMS.CRITS_GUN_CIRCLE,
 'ally_turretRotator': DAMAGE_INDICATOR_ATLAS_ITEMS.CRITS_TURRET_CIRCLE,
 'ally_surveyingDevice': DAMAGE_INDICATOR_ATLAS_ITEMS.CRITS_TRIPLEX_CIRCLE,
 'ally_commander': DAMAGE_INDICATOR_ATLAS_ITEMS.CRITS_COMMANDER_CIRCLE,
 'ally_driver': DAMAGE_INDICATOR_ATLAS_ITEMS.CRITS_DRIVER_CIRCLE,
 'ally_radioman': DAMAGE_INDICATOR_ATLAS_ITEMS.CRITS_RADIOMAN_CIRCLE,
 'ally_gunner': DAMAGE_INDICATOR_ATLAS_ITEMS.CRITS_GUNNER_CIRCLE,
 'ally_loader': DAMAGE_INDICATOR_ATLAS_ITEMS.CRITS_RELOADER_CIRCLE}
_STANDARD_MARKER_TYPE_TO_BG = {_MARKER_TYPE.HP_DAMAGE: DAMAGE_INDICATOR_ATLAS_ITEMS.DAMAGE_STANDARD,
 _MARKER_TYPE.HP_ALLAY_DAMAGE: DAMAGE_INDICATOR_ATLAS_ITEMS.DAMAGE_STANDARD,
 _MARKER_TYPE.BLOCKED_DAMAGE: DAMAGE_INDICATOR_ATLAS_ITEMS.BLOCKED_STANDARD,
 _MARKER_TYPE.CRITICAL_DAMAGE: DAMAGE_INDICATOR_ATLAS_ITEMS.DAMAGE_STANDARD}
_STANDARD_BLIND_MARKER_TYPE_TO_BG = {_MARKER_TYPE.HP_DAMAGE: DAMAGE_INDICATOR_ATLAS_ITEMS.DAMAGE_STANDARD_BLIND,
 _MARKER_TYPE.HP_ALLAY_DAMAGE: DAMAGE_INDICATOR_ATLAS_ITEMS.DAMAGE_STANDARD_BLIND,
 _MARKER_TYPE.BLOCKED_DAMAGE: DAMAGE_INDICATOR_ATLAS_ITEMS.BLOCKED_STANDARD,
 _MARKER_TYPE.CRITICAL_DAMAGE: DAMAGE_INDICATOR_ATLAS_ITEMS.DAMAGE_STANDARD_BLIND}
_EXTENDED_MARKER_TYPE_TO_BG = {_MARKER_TYPE.HP_DAMAGE: {_MARKER_SIZE_TYPE.SMALL: DAMAGE_INDICATOR_ATLAS_ITEMS.DAMAGE_SMALL,
                          _MARKER_SIZE_TYPE.MEDIUM: DAMAGE_INDICATOR_ATLAS_ITEMS.DAMAGE_MEDIUM,
                          _MARKER_SIZE_TYPE.LARGE: DAMAGE_INDICATOR_ATLAS_ITEMS.DAMAGE_BIG},
 _MARKER_TYPE.HP_ALLAY_DAMAGE: {_MARKER_SIZE_TYPE.SMALL: DAMAGE_INDICATOR_ATLAS_ITEMS.DAMAGE_SMALL,
                                _MARKER_SIZE_TYPE.MEDIUM: DAMAGE_INDICATOR_ATLAS_ITEMS.DAMAGE_MEDIUM,
                                _MARKER_SIZE_TYPE.LARGE: DAMAGE_INDICATOR_ATLAS_ITEMS.DAMAGE_BIG},
 _MARKER_TYPE.BLOCKED_DAMAGE: {_MARKER_SIZE_TYPE.SMALL: DAMAGE_INDICATOR_ATLAS_ITEMS.BLOCKED_SMALL,
                               _MARKER_SIZE_TYPE.MEDIUM: DAMAGE_INDICATOR_ATLAS_ITEMS.BLOCKED_MEDIUM,
                               _MARKER_SIZE_TYPE.LARGE: DAMAGE_INDICATOR_ATLAS_ITEMS.BLOCKED_BIG},
 _MARKER_TYPE.CRITICAL_DAMAGE: {_MARKER_SIZE_TYPE.SMALL: DAMAGE_INDICATOR_ATLAS_ITEMS.CRIT,
                                _MARKER_SIZE_TYPE.MEDIUM: DAMAGE_INDICATOR_ATLAS_ITEMS.CRIT,
                                _MARKER_SIZE_TYPE.LARGE: DAMAGE_INDICATOR_ATLAS_ITEMS.CRIT}}
_EXTENDED_BLIND_MARKER_TYPE_TO_BG = {_MARKER_TYPE.HP_DAMAGE: {_MARKER_SIZE_TYPE.SMALL: DAMAGE_INDICATOR_ATLAS_ITEMS.DAMAGE_SMALL_BLIND,
                          _MARKER_SIZE_TYPE.MEDIUM: DAMAGE_INDICATOR_ATLAS_ITEMS.DAMAGE_MEDIUM_BLIND,
                          _MARKER_SIZE_TYPE.LARGE: DAMAGE_INDICATOR_ATLAS_ITEMS.DAMAGE_BIG_BLIND},
 _MARKER_TYPE.HP_ALLAY_DAMAGE: {_MARKER_SIZE_TYPE.SMALL: DAMAGE_INDICATOR_ATLAS_ITEMS.DAMAGE_SMALL_BLIND,
                                _MARKER_SIZE_TYPE.MEDIUM: DAMAGE_INDICATOR_ATLAS_ITEMS.DAMAGE_MEDIUM_BLIND,
                                _MARKER_SIZE_TYPE.LARGE: DAMAGE_INDICATOR_ATLAS_ITEMS.DAMAGE_BIG_BLIND},
 _MARKER_TYPE.BLOCKED_DAMAGE: {_MARKER_SIZE_TYPE.SMALL: DAMAGE_INDICATOR_ATLAS_ITEMS.BLOCKED_SMALL,
                               _MARKER_SIZE_TYPE.MEDIUM: DAMAGE_INDICATOR_ATLAS_ITEMS.BLOCKED_MEDIUM,
                               _MARKER_SIZE_TYPE.LARGE: DAMAGE_INDICATOR_ATLAS_ITEMS.BLOCKED_BIG},
 _MARKER_TYPE.CRITICAL_DAMAGE: {_MARKER_SIZE_TYPE.SMALL: DAMAGE_INDICATOR_ATLAS_ITEMS.CRIT,
                                _MARKER_SIZE_TYPE.MEDIUM: DAMAGE_INDICATOR_ATLAS_ITEMS.CRIT,
                                _MARKER_SIZE_TYPE.LARGE: DAMAGE_INDICATOR_ATLAS_ITEMS.CRIT}}

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
            else:
                return _MARKER_TYPE.HP_DAMAGE
        else:
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
         'tankTypeStr': markerData.hitData.getAttackerVehicleClassTag(),
         'tankName': markerData.hitData.getAttackerVehicleName(),
         'damageValue': self._getDamageLabel(markerData)})
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

    def _getDamageLabel(self, markerData):
        return str(markerData.hitData.getDamage())

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
        if critsCount > 1:
            return i18n.makeString(INGAME_GUI.DAMAGEINDICATOR_MULTIPLIER, multiplier=str(critsCount))
        else:
            return ''

    @staticmethod
    def _getCritType(mask):
        """
        Returns type of critical hit. Type is represented by string (see VEHICLE_DEVICE_TYPE_NAMES
        and VEHICLE_TANKMAN_TYPE_NAMES, see critsParserGenerator description).
        Note that if the given crit mask has a few bits set, method returns first bit set according
        to priority rules (see critsParserGenerator description).
        
        :param mask: Crit bit mask: |destroyed tankmans|destroyed devices|critical devices|
        :return: string type (from VEHICLE_DEVICE_TYPE_NAMES or VEHICLE_TANKMAN_TYPE_NAMES) or ''
                 if mask is 0 or mask has unknown bit set
        """
        for _, critType in critsParserGenerator(mask):
            return critType

    @staticmethod
    def _makeCritType(mask, isAlly):
        """
        Makes and return critical damage type string.
        Also it checks if attacker is ally and adds prefix in this case
        :param mask: Crit bit mask: |destroyed tankmans|destroyed devices|critical devices|
        :param isAlly: boolean flag indicating was it ally shot
        :return: critical damage type string type
        """
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

    def __init__(self, swf, className, args, path):
        super(DamageIndicatorMeta, self).__init__(swf, className, args, path)
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
        return

    def as_updateSettingsS(self, isStandard, isWithTankInfo, isWithAnimation, isWithValue):
        return self._as_updateSettings(isStandard, isWithTankInfo, isWithAnimation, isWithValue)

    def as_showStandardS(self, itemIdx, bgStr, frame):
        return self._as_showStandard(itemIdx, bgStr, frame)

    def as_showExtendedS(self, itemIdx, bgStr, circleStr, frame, tankName, tankTypeStr, damageValue):
        return self._as_showExtended(itemIdx, bgStr, circleStr, frame, tankName, tankTypeStr, damageValue)

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
        names = tuple(map(lambda i: _DAMAGE_INDICATOR_MC_NAME.format(i), xrange(hitsCount)))
        super(_DamageIndicator, self).__init__(_DAMAGE_INDICATOR_SWF, _DAMAGE_INDICATOR_COMPONENT, (names,), SCALEFORM_SWF_PATH_V3)
        self.__voBuilderFactory = None
        self.__updateMethod = None
        self.component.wg_inputKeyMode = 2
        self.component.position.z = DEPTH_OF_Aim
        self.movie.backgroundAlpha = 0.0
        self.component.focus = False
        self.component.moveFocus = False
        self.component.heightMode = 'PIXEL'
        self.component.widthMode = 'PIXEL'
        self.movie.scaleMode = 'NoScale'
        self.__isBlind = bool(self.settingsCore.getSetting(GRAPHICS.COLOR_BLIND))
        self.__setUpVOBuilderFactoryAndUpdateMethod(_DEFAULT_DAMAGE_INDICATOR_TYPE)
        self.settingsCore.interfaceScale.onScaleChanged += self.__setMarkersScale
        ctrl = self.sessionProvider.shared.crosshair
        if ctrl is not None:
            ctrl.onCrosshairPositionChanged += self.__onCrosshairPositionChanged
            self.__onCrosshairPositionChanged(*ctrl.getPosition())
        self.__setMarkersScale()
        self.active(True)
        self.component.offsetRotationElementsInDegree(10.0, 10.0)
        return

    def __del__(self):
        LOG_DEBUG('DamageIndicator is deleted')

    def destroy(self):
        super(_DamageIndicator, self).destroy()
        self.settingsCore.interfaceScale.onScaleChanged -= self.__setMarkersScale
        ctrl = self.sessionProvider.shared.crosshair
        if ctrl is not None:
            ctrl.onCrosshairOffsetChanged -= self.__onCrosshairPositionChanged
        self.__updateMethod = None
        self.close()
        return

    def getDuration(self):
        return _DAMAGE_INDICATOR_ANIMATION_DURATION

    def getBeginAnimationDuration(self):
        return _BEGIN_ANIMATION_DURATION

    def setVisible(self, flag):
        self.component.visible = flag

    def invalidateSettings(self):
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


class SixthSenseIndicator(SixthSenseMeta):
    sessionProvider = dependency.descriptor(IBattleSessionProvider)
    settingsCore = dependency.descriptor(ISettingsCore)

    def __init__(self):
        super(SixthSenseIndicator, self).__init__()
        self.__callbackID = None
        self.__detectionSoundEventName = None
        self.__detectionSoundEvent = None
        return

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
        if self.__detectionSoundEvent is not None:
            if self.__detectionSoundEvent.isPlaying:
                self.__detectionSoundEvent.restart()
            else:
                self.__detectionSoundEvent.play()
        self.as_showS()
        self.__callbackID = BigWorld.callback(GUI_SETTINGS.sixthSenseDuration / 1000.0, self.__hide)
        return

    def __hide(self):
        self.__callbackID = None
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
                self.as_hideS()

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
    """ Class responsible for siege mode state indication (enabled, disabled,
    switching), displaying a special hint that helps players to understand how
    to switch between siege modes, and also displaying damaged engine or chassis
    (since siege mode mechanics depend on them).
    """
    sessionProvider = dependency.descriptor(IBattleSessionProvider)
    settingsCore = dependency.descriptor(ISettingsCore)

    def __init__(self):
        super(SiegeModeIndicator, self).__init__()
        self._isEnabled = False
        self._siegeState = _SIEGE_STATE.DISABLED
        self._devices = {'engine': 'normal',
         'leftTrack': 'normal',
         'rightTrack': 'normal'}
        self._switchTime = 0.0
        self._startTime = BigWorld.serverTime()
        self._switchTimeTable = {}
        self._hintsLeft = 0
        self._isHintShown = False
        self._isInPostmortem = False
        self._isObserver = False
        self._siegeComponent = None
        return

    def _populate(self):
        vStateCtrl = self.sessionProvider.shared.vehicleState
        crosshairCtrl = self.sessionProvider.shared.crosshair
        keyboardSetting = self.settingsCore.options.getSetting(CONTROLS.KEYBOARD)
        arenaDP = self.sessionProvider.getArenaDP()
        isReplayPlaying = self.sessionProvider.isReplayPlaying
        self._siegeComponent = siege_component.createSiegeComponent(self, isReplayPlaying)
        keyboardSetting.onKeyBindingsChanged += self.__onKeyBindingsChanged
        self._hintsLeft = AccountSettings.getSettings('siegeModeHintCounter')
        if arenaDP is not None:
            vInfo = arenaDP.getVehicleInfo()
            self._isObserver = vInfo.isObserver()
        else:
            self._isObserver = False
        if crosshairCtrl is not None:
            crosshairCtrl.onCrosshairPositionChanged += self.__onCrosshairPositionChanged
            crosshairCtrl.onCrosshairScaleChanged += self.__onCrosshairPositionChanged
        if vStateCtrl is not None:
            vStateCtrl.onVehicleStateUpdated += self.__onVehicleStateUpdated
            vStateCtrl.onVehicleControlling += self.__onVehicleControlling
            vStateCtrl.onPostMortemSwitched += self.__onPostMortemSwitched
            vehicle = vStateCtrl.getControllingVehicle()
            if vehicle is not None:
                self.__onVehicleControlling(vehicle)
        self.as_setVisibleS(self._isEnabled)
        return

    def _dispose(self):
        vStateCtrl = self.sessionProvider.shared.vehicleState
        crosshairCtrl = self.sessionProvider.shared.crosshair
        keyboardSetting = self.settingsCore.options.getSetting(CONTROLS.KEYBOARD)
        keyboardSetting.onKeyBindingsChanged -= self.__onKeyBindingsChanged
        if crosshairCtrl is not None:
            crosshairCtrl.onCrosshairPositionChanged -= self.__onCrosshairPositionChanged
            crosshairCtrl.onCrosshairScaleChanged -= self.__onCrosshairPositionChanged
        if vStateCtrl is not None:
            vStateCtrl.onVehicleStateUpdated -= self.__onVehicleStateUpdated
            vStateCtrl.onVehicleControlling -= self.__onVehicleControlling
            vStateCtrl.onPostMortemSwitched -= self.__onPostMortemSwitched
        self._switchTimeTable.clear()
        self._siegeComponent.clear()
        self._siegeComponent = None
        AccountSettings.setSettings('siegeModeHintCounter', self._hintsLeft)
        return

    def __updateIndicatorView(self, isSmooth=False):
        """ Update indicator according to current siege state (enabled, disabled or switching).
        
        :param isSmooth: flag indication whether animation should be smooth.
        """
        LOG_DEBUG('Updating siege mode: indicator')
        engineState = self._devices['engine']
        totalTime = self._switchTimeTable[self._siegeState][engineState]
        self._siegeComponent.invalidate(totalTime, self._switchTime, self._siegeState, engineState, isSmooth)
        self.__updateHintView()

    def __updateHintView(self):
        """ Update hint according to current siege state.
        """
        LOG_DEBUG('Updating siege mode: hint')
        if self._isInPostmortem or self._isObserver:
            return
        if self._siegeState not in _SIEGE_STATE.SWITCHING and self._hintsLeft:
            self.as_showHintS(*self.__getHint())
            self._isHintShown = True
        elif self._isHintShown:
            self.as_hideHintS()
            self._isHintShown = False

    def __updateDevicesView(self):
        """ Update devices according to current siege state.
        """
        LOG_DEBUG('Updating siege mode: devices')
        engine = self._devices['engine']
        leftTrack = self._devices['leftTrack']
        rightTrack = self._devices['rightTrack']
        if DEVICE_STATES_RANGE.index(leftTrack) > DEVICE_STATES_RANGE.index(rightTrack):
            chassis = leftTrack
        else:
            chassis = rightTrack
        if chassis == 'critical':
            chassis = 'normal'
        if DEVICE_STATES_RANGE.index(chassis) > DEVICE_STATES_RANGE.index(engine):
            deviceName, deviceState = 'chassis', chassis
        else:
            deviceName, deviceState = 'engine', engine
        self.as_updateDeviceStateS(deviceName, deviceState)

    def __onVehicleControlling(self, vehicle):
        vStateCtrl = self.sessionProvider.shared.vehicleState
        vTypeDesc = vehicle.typeDescriptor
        vType = vTypeDesc.type
        if vehicle.isAlive() and vTypeDesc.hasSiegeMode:
            siegeModeParams = vType.siegeModeParams
            self._switchTimeTable.update({_SIEGE_STATE.DISABLED: siegeModeParams[_SIEGE_STATE.SWITCHING_ON],
             _SIEGE_STATE.SWITCHING_ON: siegeModeParams[_SIEGE_STATE.SWITCHING_ON],
             _SIEGE_STATE.ENABLED: siegeModeParams[_SIEGE_STATE.SWITCHING_OFF],
             _SIEGE_STATE.SWITCHING_OFF: siegeModeParams[_SIEGE_STATE.SWITCHING_OFF]})
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
            self.__updateIndicatorView()
            self.__updateDevicesView()
        else:
            self._isEnabled = False
            for deviceName in self._devices:
                self._devices[deviceName] = 'normal'

        self.as_setVisibleS(self._isEnabled)
        return

    def __onVehicleStateUpdated(self, state, value):
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

    def __onPostMortemSwitched(self):
        self._isInPostmortem = True

    def __onCrosshairPositionChanged(self, *args):
        if not self._isEnabled:
            return
        crosshairCtrl = self.sessionProvider.shared.crosshair
        scaledPosition = crosshairCtrl.getScaledPosition()
        self.as_updateLayoutS(*scaledPosition)

    def __onKeyBindingsChanged(self):
        if not self._isEnabled:
            return
        self.__updateHintView()

    def __updateSiegeState(self, siegeState, switchTime):
        if siegeState == _SIEGE_STATE.SWITCHING_OFF:
            if not self._isObserver and not self._isInPostmortem:
                self._hintsLeft = max(0, self._hintsLeft - 1)
        if self._siegeState in _SIEGE_STATE.SWITCHING:
            isSmooth = siegeState not in _SIEGE_STATE.SWITCHING
        else:
            isSmooth = siegeState in _SIEGE_STATE.SWITCHING
        self._startTime = BigWorld.serverTime()
        self._siegeState = siegeState
        self._switchTime = switchTime
        self.__updateIndicatorView(isSmooth)

    def __updateDevicesState(self, deviceName, _, realState):
        if deviceName in ('engine', 'leftTrack', 'rightTrack'):
            self._devices[deviceName] = realState
            self.__updateDevicesView()

    def __updateDestroyed(self, _):
        self._isEnabled = False
        self.as_setVisibleS(False)

    def __getHint(self):
        keyName = getReadableKey(CommandMapping.CMD_CM_VEHICLE_SWITCH_AUTOROTATION)
        if keyName:
            pressText = text_styles.tutorial(INGAME_GUI.SIEGEMODE_HINT_PRESS)
            hintText = text_styles.tutorial(INGAME_GUI.siegeModeHint(self._siegeState))
            keyText = makeHtmlString('html_templates:battle/siegeMode', 'toggle', ctx={'key': keyName})
            return (keyText, pressText, hintText)
        else:
            return ('', '', text_styles.tutorial(INGAME_GUI.SIEGEMODE_HINT_NOBINDING))


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
        super(_DirectionIndicator, self).__init__(swf, _DIRECT_INDICATOR_COMPONENT, (_DIRECT_INDICATOR_MC_NAME,), SCALEFORM_SWF_PATH_V3)
        self.component.wg_inputKeyMode = 2
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
        if self._dObject:
            self._dObject.setDistance(distance)

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
