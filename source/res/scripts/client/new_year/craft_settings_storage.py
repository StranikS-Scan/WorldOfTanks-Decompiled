# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/new_year/craft_settings_storage.py
from skeletons.new_year import ICraftMachineSettingsStorage

class CraftMachineSettingsStorage(ICraftMachineSettingsStorage):

    def __init__(self):
        super(CraftMachineSettingsStorage, self).__init__()
        self.__settings = {}
        self.__isConnected = False

    def fini(self):
        self.resetSettings()

    def getValue(self, name, default=None):
        return default if name not in self.__settings else self.__settings[name]

    def setValue(self, name, value):
        if not self.__isConnected:
            return
        self.__settings[name] = value

    def resetSettings(self):
        self.__settings.clear()

    def onConnected(self):
        self.__isConnected = True

    def onDisconnected(self):
        self.resetSettings()
        self.__isConnected = False
