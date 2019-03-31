# Python bytecode 2.6 (decompiled from Python 2.7)
# Embedded file name: scripts/client/Vibroeffects/Controllers/SwitchController.py
# Compiled at: 2011-03-25 20:17:34
import BigWorld
from Vibroeffects import VibroManager
from debug_utils import *

class SwitchController:

    def __init__(self, effectName):
        self.__effect = VibroManager.g_instance.getEffect(effectName)

    def destroy(self):
        VibroManager.g_instance.stopEffect(self.__effect)
        self.__effect = None
        return

    def switch(self, turnOn):
        if turnOn:
            VibroManager.g_instance.startEffect(self.__effect)
        else:
            VibroManager.g_instance.stopEffect(self.__effect)
