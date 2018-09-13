# Embedded file name: scripts/client/gui/Scaleform/managers/ColorSchemeManager.py
from debug_utils import LOG_ERROR, LOG_CURRENT_EXCEPTION
from gui.Scaleform.framework.entities.abstract.ColorSchemeManagerMeta import ColorSchemeManagerMeta
from gui.doc_loaders.GuiColorsLoader import GuiColorsLoader

class ColorSchemeManager(ColorSchemeManagerMeta):

    def __init__(self):
        super(ColorSchemeManager, self).__init__()
        self.colors = GuiColorsLoader()
        try:
            self.colors.load()
        except Exception:
            LOG_ERROR('There is error while loading colors xml data')
            LOG_CURRENT_EXCEPTION()

    def destroy(self):
        super(ColorSchemeManager, self).destroy()
        self.colors.clear()

    def __onAccountSettingsChange(self, diff):
        if 'isColorBlind' in diff:
            self.update()

    def _populate(self):
        super(ColorSchemeManager, self)._populate()
        from account_helpers.settings_core.SettingsCore import g_settingsCore
        g_settingsCore.onSettingsChanged += self.__onAccountSettingsChange

    def _dispose(self):
        from account_helpers.settings_core.SettingsCore import g_settingsCore
        g_settingsCore.onSettingsChanged -= self.__onAccountSettingsChange
        super(ColorSchemeManager, self)._dispose()

    @classmethod
    def _packRGB(cls, rgba):
        return (int(rgba[0]) << 16) + (int(rgba[1]) << 8) + (int(rgba[2]) << 0)

    @classmethod
    def _makeRGB(cls, subScheme):
        return cls._packRGB(subScheme.get('rgb', (0, 0, 0, 0)))

    @classmethod
    def _makeAdjustTuple(cls, subScheme):
        return subScheme['adjust']['offset']

    def getColorGroup(self):
        from account_helpers.settings_core.SettingsCore import g_settingsCore
        if g_settingsCore.getSetting('isColorBlind'):
            return 'color_blind'
        return 'default'

    def update(self):
        self.as_updateS()

    def getColorScheme(self, schemeName):
        scheme = self.colors.getSubScheme(schemeName, self.getColorGroup())
        return {'aliasColor': scheme['alias_color'],
         'rgb': self._packRGB(scheme['rgba']),
         'adjust': {'offset': scheme['adjust']['offset'].tuple()},
         'transform': {'mult': scheme['transform']['mult'].tuple(),
                       'offset': scheme['transform']['offset'].tuple()}}
