# Python bytecode 2.6 (decompiled from Python 2.7)
# Embedded file name: scripts/client/SoundGroups.py
# Compiled at: 2018-11-29 14:33:44
import BigWorld
import FMOD
import Settings
from debug_utils import *
g_instance = None

class SoundGroups(object):

    def __init__(self):
        self.__volumeByCategory = {}
        self.__masterVolume = 1.0
        self.__isWindowVisible = BigWorld.isWindowVisible()
        self.__groups = {'arena': ('/vehicles/tanks', '/hits/hits', '/hits/explosions', '/hits/tank_death', '/weapons/large_fire', '/weapons/medium_fire', '/weapons/small_fire', '/weapons/tracer', '/GUI/notifications_FX', '/ingame_voice/notifications_VO', '/objects/wire_barricade', '/objects/tent', '/objects/dog_house', '/objects/structures', '/objects/treefall', '/objects/wood_box_mid', '/objects/telegraph_pole', '/objects/buildings', '/objects/fuel_tank', '/objects/fence', '/objects/fuel_barrel', '/objects/fire', '/objects/hay_stack', '/objects/metall_pole_huge')}
        self.__categories = {'voice': ('ingame_voice',),
         'vehicles': ('vehicles',),
         'effects': ('hits', 'weapons', 'environment', 'battle_gui'),
         'gui': ('gui',),
         'music': ('music',),
         'ambient': ('ambient',),
         'masterVivox': (),
         'micVivox': (),
         'masterFadeVivox': ()}
        defMasterVolume = 0.5
        defCategoryVolumes = {'music': 0.5,
         'masterVivox': 0.7,
         'micVivox': 0.8}
        userPrefs = Settings.g_instance.userPrefs
        if not userPrefs.has_key(Settings.KEY_SOUND_PREFERENCES):
            userPrefs.write(Settings.KEY_SOUND_PREFERENCES, '')
            self.__masterVolume = defMasterVolume
            for categoryName in self.__categories.keys():
                self.__volumeByCategory[categoryName] = defCategoryVolumes.get(categoryName, 1.0)

            self.savePreferences()
        else:
            ds = userPrefs[Settings.KEY_SOUND_PREFERENCES]
            self.__masterVolume = ds.readFloat('masterVolume', defMasterVolume)
            for categoryName in self.__categories.keys():
                volume = ds.readFloat('volume_' + categoryName, defCategoryVolumes.get(categoryName, 1.0))
                self.__volumeByCategory[categoryName] = volume

        self.applyPreferences()
        self.__muteCallbackID = BigWorld.callback(0.25, self.__muteByWindowVisibility)

    def __del__(self):
        if self.__muteCallbackID is not None:
            BigWorld.cancelCallback(self.__muteCallbackID)
            self.__muteCallbackID = None
        return

    def loadSounds(self, groupName):
        for group in self.__groups[groupName]:
            try:
                FMOD.loadSoundGroup(group)
            except Exception:
                LOG_CURRENT_EXCEPTION()

    def unloadSounds(self, groupName):
        for group in self.__groups[groupName]:
            try:
                FMOD.unloadSoundGroup(group)
            except Exception:
                LOG_CURRENT_EXCEPTION()

    def enableLobbySounds(self, enable):
        for categoryName in ('ambient', 'gui'):
            volume = 0.0 if not enable else self.__volumeByCategory[categoryName]
            self.setVolume(categoryName, volume, False)

    def enableArenaSounds(self, enable):
        for categoryName in ('voice', 'vehicles', 'effects', 'ambient'):
            volume = 0.0 if not enable else self.__volumeByCategory[categoryName]
            self.setVolume(categoryName, volume, False)

    def setMasterVolume(self, volume):
        self.__masterVolume = volume
        FMOD.setMasterVolume(volume)
        self.savePreferences()

    def getMasterVolume(self):
        return self.__masterVolume

    def setVolume(self, categoryName, volume, updatePrefs=True):
        for category in self.__categories[categoryName]:
            try:
                BigWorld.wg_setCategoryVolume(category, volume)
            except Exception:
                LOG_CURRENT_EXCEPTION()

        if updatePrefs:
            self.__volumeByCategory[categoryName] = volume
            self.savePreferences()

    def getVolume(self, categoryName):
        return self.__volumeByCategory[categoryName]

    def savePreferences(self):
        ds = Settings.g_instance.userPrefs[Settings.KEY_SOUND_PREFERENCES]
        ds.writeFloat('masterVolume', self.__masterVolume)
        for categoryName in self.__volumeByCategory.keys():
            ds.writeFloat('volume_' + categoryName, self.__volumeByCategory[categoryName])

    def applyPreferences(self):
        if not self.__isWindowVisible:
            FMOD.setMasterVolume(0)
            return
        self.setMasterVolume(self.__masterVolume)
        for categoryName in self.__volumeByCategory.keys():
            self.setVolume(categoryName, self.__volumeByCategory[categoryName], updatePrefs=False)

    def __muteByWindowVisibility(self):
        isWindowVisible = BigWorld.isWindowVisible()
        if self.__isWindowVisible != isWindowVisible:
            self.__isWindowVisible = isWindowVisible
            self.applyPreferences()
        self.__muteCallbackID = BigWorld.callback(0.25, self.__muteByWindowVisibility)
