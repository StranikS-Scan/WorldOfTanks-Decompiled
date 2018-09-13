# Embedded file name: scripts/client/Vibroeffects/Controllers/SwitchController.py
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
