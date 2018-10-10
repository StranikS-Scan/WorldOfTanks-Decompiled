# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/common/settings/color_settings_view.py
import BigWorld
from debug_utils import LOG_DEBUG
import GUI
from account_helpers.AccountSettings import AccountSettings, COLOR_SETTINGS_TAB_IDX, APPLIED_COLOR_SETTINGS
from account_helpers.settings_core import settings_constants
from account_helpers.settings_core.settings_constants import GRAPHICS
from gui.Scaleform.daapi.settings.views import VIEW_ALIAS
from gui.Scaleform.daapi.view.meta.ColorSettingsViewMeta import ColorSettingsViewMeta
from gui.Scaleform.genConsts.COLOR_SETTINGS import COLOR_SETTINGS
from gui.Scaleform.locale.RES_ICONS import RES_ICONS
from gui.Scaleform.locale.SETTINGS import SETTINGS
from gui.shared import EVENT_BUS_SCOPE, events
from gui.shared.events import GameEvent
from gui.shared.formatters import text_styles
from gui.shared.utils import flashObject2Dict, graphics
from gui.hangar_cameras.hangar_camera_common import CameraRelatedEvents
from helpers import dependency, i18n
from skeletons.account_helpers.settings_core import ISettingsCore

class TABS(object):
    DEFAULT = 0
    FILTERS = 1
    CUSTOM = 2


COLOR_GRADING_TECHNIQUE_DEFAULT = 0

class ColorSettingsView(ColorSettingsViewMeta):
    settingsCore = dependency.descriptor(ISettingsCore)

    def __init__(self, ctx=None):
        super(ColorSettingsView, self).__init__(ColorSettingsView)
        self.fireEvent(GameEvent(GameEvent.HIDE_EXTERNAL_COMPONENTS), scope=EVENT_BUS_SCOPE.GLOBAL)
        self.__selectedTabIdx = AccountSettings.getSettings(COLOR_SETTINGS_TAB_IDX)
        self.__componentWidth = 0
        self.__isColorPreviewFilterActive = False
        self.__initSettings = self.__getSettings()
        self.__tabsPreviewSettings = self.__getLastAppliedTabsSettings()
        if self.__selectedTabIdx == TABS.CUSTOM:
            self.__showColorPreviewFilter()

    def setViewWidth(self, width):
        self.__componentWidth = width
        if self.__isColorPreviewFilterActive:
            self.__showColorPreviewFilter()

    def moveSpace(self, dx, dy, dz):
        self.fireEvent(CameraRelatedEvents(CameraRelatedEvents.LOBBY_VIEW_MOUSE_MOVE, ctx={'dx': dx,
         'dy': dy,
         'dz': dz}))
        self.fireEvent(events.LobbySimpleEvent(events.LobbySimpleEvent.NOTIFY_SPACE_MOVED, ctx={'dx': dx,
         'dy': dy,
         'dz': dz}))

    def onSettingsChange(self, settingName, settingValue):
        settingValue = flashObject2Dict(settingValue)
        LOG_DEBUG('onSettingsChange', settingName, settingValue)
        self.settingsCore.previewSetting(settingName, settingValue)
        self.__tabsPreviewSettings[self.__selectedTabIdx][settingName] = settingValue

    def onApply(self, diff):
        diff = flashObject2Dict(diff)
        AccountSettings.setSettings(COLOR_SETTINGS_TAB_IDX, self.__selectedTabIdx)
        if self.__selectedTabIdx == TABS.CUSTOM:
            if self.__hasChangesInSettings(settings_constants.GRAPHICS.getCustomColorSettings(), diff):
                diff.update({settings_constants.GRAPHICS.COLOR_GRADING_TECHNIQUE: COLOR_GRADING_TECHNIQUE_DEFAULT})
            diff[COLOR_SETTINGS.COLOR_GRADING_TECHNIQUE] = 0
            diff[COLOR_SETTINGS.COLOR_FILTER_INTENSITY] = 25
        self.settingsCore.applySettings(diff)
        lastAppliedSettings = AccountSettings.getSettings(APPLIED_COLOR_SETTINGS)
        lastAppliedSettings[self.__selectedTabIdx] = diff
        AccountSettings.setSettings(APPLIED_COLOR_SETTINGS, lastAppliedSettings)
        BigWorld.commitPendingGraphicsSettings()
        self.destroy()

    def onTabSelected(self, selectedTab):
        savedTab = AccountSettings.getSettings(COLOR_SETTINGS_TAB_IDX)
        if savedTab == self.__selectedTabIdx and self.__selectedTabIdx == TABS.FILTERS and selectedTab == TABS.CUSTOM:
            prevSettings = self.__getLastAppliedTabsSettings()[TABS.FILTERS]
            self.__selectedTabIdx = selectedTab
            settings = self.__getCurrentTabSettings()
            prevFilter = prevSettings[settings_constants.GRAPHICS.COLOR_GRADING_TECHNIQUE]
            settings[settings_constants.GRAPHICS.COLOR_GRADING_TECHNIQUE] = prevFilter
            settings[COLOR_SETTINGS.COLOR_FILTER_INTENSITY] = prevSettings[COLOR_SETTINGS.COLOR_FILTER_INTENSITY]
        else:
            self.__selectedTabIdx = selectedTab
            settings = self.__getCurrentTabSettings()
        self.__previewSettings(settings)
        self.as_updateDataS(self.__selectedTabIdx, settings)
        if self.__selectedTabIdx == TABS.CUSTOM:
            self.__showColorPreviewFilter()
        else:
            self.__hideColorPreviewFilter()

    def onReset(self):
        settings = self.__getCurrentTabSettings()
        for settingName in settings_constants.GRAPHICS.getCustomColorSettings():
            setting = self.settingsCore.options.getSetting(settingName)
            defaultValue = setting.getDefaultValue()
            self.settingsCore.previewSetting(settingName, defaultValue)
            self.__tabsPreviewSettings[self.__selectedTabIdx][settingName] = defaultValue
            settings[settingName] = defaultValue

        self.as_updateDataS(self.__selectedTabIdx, settings)

    def onClose(self):
        self.settingsCore.options.revert(settings_constants.GRAPHICS.getColorSettings())
        self.destroy()

    def _populate(self):
        super(ColorSettingsView, self)._populate()
        if self.app is not None:
            self._savedBackgroundAlpha = self.app.getBackgroundAlpha()
            self.app.setBackgroundAlpha(0)
            self.addListener(GameEvent.ON_BACKGROUND_ALPHA_CHANGE, self.__onExternalBackgroundAlphaChange, EVENT_BUS_SCOPE.GLOBAL)
        self.as_initDataS({'header': text_styles.superPromoTitle(SETTINGS.COLORSETTINGS_VIEW_HEADER),
         'typesHeader': text_styles.highTitle(SETTINGS.COLORSETTINGS_VIEW_SUBTITLE),
         'typesDesc': text_styles.main(SETTINGS.COLORSETTINGS_VIEW_DESCRIPTION),
         'applyLabel': i18n.makeString(SETTINGS.APPLY_BUTTON),
         'cancelLabel': i18n.makeString(SETTINGS.CANCEL_BUTTON),
         'settingsTypes': self.__getTypes(),
         'closeLabel': i18n.makeString(SETTINGS.COLORSETTINGS_VIEW_CLOSEBTN),
         'beforeStr': text_styles.promoSubTitle(SETTINGS.COLORSETTINGS_VIEW_BEFORE),
         'afterStr': text_styles.promoSubTitle(SETTINGS.COLORSETTINGS_VIEW_AFTER),
         'filtersHeader': text_styles.highTitle(SETTINGS.COLORSETTINGS_TAB_FILTERS),
         'filterPowerLabel': i18n.makeString(SETTINGS.COLORSETTINGS_TAB_FILTERS_INTENSITY),
         'filtersTypes': self.__getFiltersTypes(),
         'manualHeader': text_styles.highTitle(SETTINGS.COLORSETTINGS_TAB_CUSTOMSETTINGS),
         'brightnessLabel': i18n.makeString(SETTINGS.COLORSETTINGS_TAB_CUSTOMSETTINGS_BRIGHTNESS),
         'contrastLabel': i18n.makeString(SETTINGS.COLORSETTINGS_TAB_CUSTOMSETTINGS_CONTRAST),
         'saturationLabel': i18n.makeString(SETTINGS.COLORSETTINGS_TAB_CUSTOMSETTINGS_SATURATION),
         'resetLabel': i18n.makeString(SETTINGS.COLORSETTINGS_VIEW_RESETBTN)})
        self.as_updateDataS(self.__selectedTabIdx, self.__initSettings)
        return

    def _dispose(self):
        self.__hideColorPreviewFilter()
        self.settingsCore.clearStorages()
        self.removeListener(GameEvent.ON_BACKGROUND_ALPHA_CHANGE, self.__onExternalBackgroundAlphaChange, EVENT_BUS_SCOPE.GLOBAL)
        if self.app is not None:
            self.app.setBackgroundAlpha(self._savedBackgroundAlpha)
            if hasattr(self.app, 'leaveGuiControlMode'):
                self.app.leaveGuiControlMode(VIEW_ALIAS.COLOR_SETTING)
        self.fireEvent(GameEvent(GameEvent.SHOW_EXTERNAL_COMPONENTS), scope=EVENT_BUS_SCOPE.GLOBAL)
        if self.__initSettings is not None:
            self.__initSettings.clear()
            self.__initSettings = None
        super(ColorSettingsView, self)._dispose()
        return

    def __getLastAppliedTabsSettings(self):
        lastAppliedSettings = AccountSettings.getSettings(APPLIED_COLOR_SETTINGS)
        filterTabsKeys = (GRAPHICS.COLOR_GRADING_TECHNIQUE, GRAPHICS.COLOR_FILTER_INTENSITY)
        return {TABS.DEFAULT: {},
         TABS.FILTERS: self.__getTabSettings(lastAppliedSettings, TABS.FILTERS, filterTabsKeys),
         TABS.CUSTOM: self.__getTabSettings(lastAppliedSettings, TABS.CUSTOM, GRAPHICS.getCustomColorSettings())}

    def __getTabSettings(self, lastAppliedSettings, tabIdx, settingKeys):
        tabSettings = lastAppliedSettings.get(tabIdx, {})
        settings = {}
        for key in settingKeys:
            settings[key] = tabSettings.get(key, self.__initSettings[key])

        return settings

    def __getTypes(self):
        return [{'id': TABS.DEFAULT,
          'label': text_styles.highlightText(SETTINGS.COLORSETTINGS_TAB_DEFAULT),
          'icon': RES_ICONS.MAPS_ICONS_SETTINGS_COLORSETTINGS_DEFAULT}, {'id': TABS.FILTERS,
          'label': text_styles.highlightText(SETTINGS.COLORSETTINGS_TAB_FILTERS),
          'icon': RES_ICONS.MAPS_ICONS_SETTINGS_COLORSETTINGS_FILTERS}, {'id': TABS.CUSTOM,
          'label': text_styles.highlightText(SETTINGS.COLORSETTINGS_TAB_CUSTOMSETTINGS),
          'icon': RES_ICONS.MAPS_ICONS_SETTINGS_COLORSETTINGS_MANUAL}]

    def __getFiltersTypes(self):
        result = []
        setting = self.settingsCore.options.getSetting(GRAPHICS.COLOR_GRADING_TECHNIQUE)
        images = graphics.getGraphicSettingColorSettingsFiletersImages()
        if setting is not None:
            for option in setting.getOptions():
                result.append({'id': option.get('data', COLOR_GRADING_TECHNIQUE_DEFAULT),
                 'label': text_styles.stats(option.get('label')),
                 'icon': images.get(option.get('data', COLOR_GRADING_TECHNIQUE_DEFAULT))})

            result = sorted(result, key=lambda k: k['id'])
        return result

    def __getSettings(self):
        settings = {}
        for setting in settings_constants.GRAPHICS.getColorSettings():
            settings[setting] = self.settingsCore.getSetting(setting)

        return settings

    def __showColorPreviewFilter(self):
        width, _ = GUI.screenResolution()[:2]
        witdthPrc = self.__componentWidth / width
        delimiterPrc = witdthPrc + (1 - witdthPrc) / 2
        BigWorld.setColorBCSSetup(1, delimiterPrc)
        self.__isColorPreviewFilterActive = True

    def __hideColorPreviewFilter(self):
        BigWorld.setColorBCSSetup(0, 0)
        self.__isColorPreviewFilterActive = False

    def __hasChangesInSettings(self, settingsNames, diff):
        for name in settingsNames:
            if self.__initSettings[name] != diff[name]:
                return True

        return False

    def __getCurrentTabSettings(self):
        settings = {}
        for settingName in settings_constants.GRAPHICS.getColorSettings():
            setting = self.settingsCore.options.getSetting(settingName)
            if settingName != settings_constants.GRAPHICS.COLOR_GRADING_TECHNIQUE:
                defaultValue = setting.getDefaultValue()
            else:
                defaultValue = COLOR_GRADING_TECHNIQUE_DEFAULT
            settings[settingName] = defaultValue

        settings.update(self.__tabsPreviewSettings[self.__selectedTabIdx])
        return settings

    def __previewSettings(self, settings):
        for settingName, value in settings.iteritems():
            self.settingsCore.applySetting(settingName, value)

    def __onExternalBackgroundAlphaChange(self, event):
        self._savedBackgroundAlpha = event.ctx['alpha']
        self.removeListener(GameEvent.ON_BACKGROUND_ALPHA_CHANGE, self.__onExternalBackgroundAlphaChange, EVENT_BUS_SCOPE.GLOBAL)
        self.app.setBackgroundAlpha(0)
        self.addListener(GameEvent.ON_BACKGROUND_ALPHA_CHANGE, self.__onExternalBackgroundAlphaChange, EVENT_BUS_SCOPE.GLOBAL)
