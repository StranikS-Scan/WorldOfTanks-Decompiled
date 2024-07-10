# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/battle/comp7/status_notifications/panel.py
import logging
import BigWorld
import GUI
from arena_bonus_type_caps import ARENA_BONUS_TYPE_CAPS
from gui.Scaleform.daapi.view.battle.comp7.status_notifications import sn_items as comp7_sn_items
from gui.Scaleform.daapi.view.battle.shared.status_notifications import components
from gui.Scaleform.daapi.view.battle.shared.status_notifications import sn_items
from gui.Scaleform.daapi.view.battle.shared.status_notifications.panel import StatusNotificationTimerPanel
from gui.Scaleform.daapi.view.battle.shared.status_notifications.poi_sn_items import PoiNotificationsGroup
from gui.Scaleform.genConsts.BATTLE_NOTIFICATIONS_TIMER_COLORS import BATTLE_NOTIFICATIONS_TIMER_COLORS as _COLORS
from gui.Scaleform.genConsts.BATTLE_NOTIFICATIONS_TIMER_LINKAGES import BATTLE_NOTIFICATIONS_TIMER_LINKAGES as _LINKS
from gui.Scaleform.genConsts.BATTLE_NOTIFICATIONS_TIMER_TYPES import BATTLE_NOTIFICATIONS_TIMER_TYPES as _TYPES
from gui.Scaleform.locale.INGAME_GUI import INGAME_GUI
from gui.battle_control.battle_constants import CROSSHAIR_VIEW_ID
from gui.shared.items_parameters import isAutoReloadGun
from gui.shared.utils.MethodsRules import MethodsRules
from helpers import dependency
from skeletons.account_helpers.settings_core import ISettingsCore
_logger = logging.getLogger(__name__)

class Comp7BattleHighPriorityGroup(components.StatusNotificationsGroup):

    def __init__(self, updateCallback):
        super(Comp7BattleHighPriorityGroup, self).__init__((sn_items.DrownSN,
         sn_items.OverturnedSN,
         sn_items.HalfOverturnedSN,
         sn_items.UnderFireSN,
         sn_items.FireSN), updateCallback)


class Comp7StatusNotificationTimerPanel(StatusNotificationTimerPanel):
    _settingsCore = dependency.descriptor(ISettingsCore)
    _ARCADE_ADDITIONAL_MIN_SHIFT = 231
    _ARCADE_ADDITIONAL_MAX_SHIFT = 323
    _SNIPER_MIN_SHIFT = 135
    _SNIPER_MAX_SHIFT = 185
    _SNIPER_AUTOLOADER_MIN_SHIFT = 144
    _SNIPER_AUTOLOADER_MAX_SHIFT = 200
    _MIN_SCREEN_HEIGHT = 768
    _MAX_SCREEN_HEIGHT = 1200
    _ARCADE_DEFAULT_OFFSET = -0.15

    def _addListeners(self):
        super(Comp7StatusNotificationTimerPanel, self)._addListeners()
        self._settingsCore.interfaceScale.onScaleChanged += self.__onScaleFactorChanged

    def _removeListeners(self):
        super(Comp7StatusNotificationTimerPanel, self)._removeListeners()
        self._settingsCore.interfaceScale.onScaleChanged -= self.__onScaleFactorChanged

    def _getComponentClass(self):
        return components.Comp7StatusNotificationContainer

    def _generateItems(self):
        items = [Comp7BattleHighPriorityGroup,
         PoiNotificationsGroup,
         sn_items.StunSN,
         comp7_sn_items.AoeHealSN,
         comp7_sn_items.AoeInspireSN,
         comp7_sn_items.RiskyAttackBuffSN,
         comp7_sn_items.RiskyAttackHealSN,
         comp7_sn_items.Comp7HealingSN,
         comp7_sn_items.BerserkSN,
         comp7_sn_items.SniperSN,
         comp7_sn_items.AllySupportSN,
         comp7_sn_items.HunterSN,
         comp7_sn_items.JuggernautSN,
         comp7_sn_items.SureShotSN,
         comp7_sn_items.ConcentrationSN,
         comp7_sn_items.MarchSN,
         comp7_sn_items.AggressiveDetectionSN]
        return items

    def _generateNotificationTimerSettings(self):
        data = super(Comp7StatusNotificationTimerPanel, self)._generateNotificationTimerSettings()
        link = _LINKS.DESTROY_TIMER_UI
        self._addNotificationTimerSetting(data, _TYPES.DROWN, _LINKS.DROWN_ICON, link)
        if BigWorld.player().hasBonusCap(ARENA_BONUS_TYPE_CAPS.LIFT_OVER):
            overturnedIcon = _LINKS.OVERTURNED_GREEN_ICON
            overturnedColor = _COLORS.GREEN
            iconOffsetY = 1
        else:
            overturnedIcon = _LINKS.OVERTURNED_ICON
            overturnedColor = _COLORS.ORANGE
            iconOffsetY = 0
        self._addNotificationTimerSetting(data, _TYPES.OVERTURNED, overturnedIcon, link, color=overturnedColor, iconOffsetY=iconOffsetY)
        self._addNotificationTimerSetting(data, _TYPES.FIRE, _LINKS.FIRE_ICON, link)
        self._addNotificationTimerSetting(data, _TYPES.HALF_OVERTURNED, overturnedIcon, link, color=overturnedColor, iconOffsetY=iconOffsetY)
        self._addNotificationTimerSetting(data, _TYPES.UNDER_FIRE, _LINKS.UNDER_FIRE_ICON, link)
        self.__genPoiTimersSettings(data)
        link = _LINKS.SECONDARY_TIMER_UI
        self._addNotificationTimerSetting(data, _TYPES.STUN, _LINKS.STUN_ICON, link, _COLORS.ORANGE, noiseVisible=True, text=INGAME_GUI.STUN_INDICATOR)
        self.__gerRoleSkillsTimersSettings(data)
        return data

    def _calcVerticalOffset(self, vehicle):
        verticalOffset = self._DEFAULT_Y_SHIFT
        _, height = GUI.screenResolution()
        if self._viewID == CROSSHAIR_VIEW_ID.ARCADE:
            arcadeOffset = self._ARCADE_DEFAULT_OFFSET * height
            minTopOffset = arcadeOffset + self._ARCADE_ADDITIONAL_MIN_SHIFT
            maxTopOffset = arcadeOffset + self._ARCADE_ADDITIONAL_MAX_SHIFT
            verticalOffset = self.__calcOffset(height=height, minTopOffset=minTopOffset, maxTopOffset=maxTopOffset)
        elif self._viewID == CROSSHAIR_VIEW_ID.SNIPER:
            minTopOffset = self._SNIPER_MIN_SHIFT
            maxTopOffset = self._SNIPER_MAX_SHIFT
            vTypeDescr = vehicle.typeDescriptor
            hasAutoloaderInterface = vTypeDescr.isDualgunVehicle or isAutoReloadGun(vTypeDescr.gun)
            if hasAutoloaderInterface:
                minTopOffset = self._SNIPER_AUTOLOADER_MIN_SHIFT
                maxTopOffset = self._SNIPER_AUTOLOADER_MAX_SHIFT
            verticalOffset = self.__calcOffset(height=height, minTopOffset=minTopOffset, maxTopOffset=maxTopOffset)
        return verticalOffset

    @MethodsRules.delayable('_onVehicleControlling')
    def __onScaleFactorChanged(self, _):
        self._updatePanelPosition()

    def __calcOffset(self, height, minTopOffset, maxTopOffset):
        height = max(self._MIN_SCREEN_HEIGHT, min(self._MAX_SCREEN_HEIGHT, height))
        dH = self._MAX_SCREEN_HEIGHT - self._MIN_SCREEN_HEIGHT
        offset = minTopOffset + (maxTopOffset - minTopOffset) * (height - self._MIN_SCREEN_HEIGHT) / dH
        return offset

    def __genPoiTimersSettings(self, data):
        link = _LINKS.POI_TIMER_UI
        self._addNotificationTimerSetting(data, _TYPES.POI_CAPTURING, '', link, _COLORS.GREEN, countdownVisible=True)
        self._addNotificationTimerSetting(data, _TYPES.POI_COOLDOWN, '', link, _COLORS.ORANGE, countdownVisible=True)
        self._addNotificationTimerSetting(data, _TYPES.POI_BLOCKED_NOT_USED_ABILITY, '', link, _COLORS.ORANGE, countdownVisible=False)
        self._addNotificationTimerSetting(data, _TYPES.POI_CAPTURING_INTERRUPTED, '', link, _COLORS.ORANGE, countdownVisible=True, isReversedTimerDirection=True)
        self._addNotificationTimerSetting(data, _TYPES.POI_BLOCKED_NOT_INVADER, '', link, _COLORS.ORANGE, countdownVisible=False)
        self._addNotificationTimerSetting(data, _TYPES.POI_BLOCKED_OVERTURNED, '', link, _COLORS.ORANGE, countdownVisible=False)

    def __gerRoleSkillsTimersSettings(self, data):
        link = _LINKS.SECONDARY_TIMER_UI
        self._addNotificationTimerSetting(data, _TYPES.COMP7_ALLY_SUPPORT, _LINKS.COMP7_ALLY_SUPPORT_ICON, link, _COLORS.GREEN)
        self._addNotificationTimerSetting(data, _TYPES.COMP7_RISKY_ATTACK, _LINKS.COMP7_RISKY_ATTACK_ICON, link, _COLORS.GREEN)
        self._addNotificationTimerSetting(data, _TYPES.COMP7_RISKY_ATTACK_HEAL, _LINKS.COMP7_RISKY_ATTACK_HEAL_ICON, link, _COLORS.GREEN)
        self._addNotificationTimerSetting(data, _TYPES.COMP7_SNIPER, _LINKS.COMP7_SNIPER_ICON, link, _COLORS.GREEN, canBlink=True)
        self._addNotificationTimerSetting(data, _TYPES.COMP7_HUNTER, _LINKS.COMP7_HUNTER_ICON, link, _COLORS.GREEN)
        self._addNotificationTimerSetting(data, _TYPES.COMP7_BERSERK, _LINKS.COMP7_BERSERK_ICON, link, _COLORS.GREEN, canBlink=True)
        self._addNotificationTimerSetting(data, _TYPES.COMP7_JUGGERNAUT, _LINKS.COMP7_JUGGERNAUT_ICON, link, _COLORS.GREEN)
        self._addNotificationTimerSetting(data, _TYPES.COMP7_AOE_HEAL, _LINKS.COMP7_AOE_HEAL_ICON, link, _COLORS.GREEN)
        self._addNotificationTimerSetting(data, _TYPES.COMP7_AOE_INSPIRE, _LINKS.COMP7_AOE_INSPIRE_ICON, link, _COLORS.GREEN)
        self._addNotificationTimerSetting(data, _TYPES.COMP7_SURE_SHOT, _LINKS.COMP7_SURE_SHOT_ICON, link, _COLORS.GREEN)
        self._addNotificationTimerSetting(data, _TYPES.COMP7_CONCENTRATION, _LINKS.COMP7_CONCENTRATION_ICON, link, _COLORS.GREEN)
        self._addNotificationTimerSetting(data, _TYPES.COMP7_MARCH, _LINKS.COMP7_MARCH_ICON, link, _COLORS.GREEN)
        self._addNotificationTimerSetting(data, _TYPES.COMP7_AGGRESSIVE_DETECTION, _LINKS.COMP7_AGGRESSIVE_DETECTION_ICON, link, _COLORS.GREEN, canBlink=True)
