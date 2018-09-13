# Embedded file name: scripts/client/Vibroeffects/Controllers/OnceController.py
import BigWorld
from Vibroeffects import VibroManager
from debug_utils import *

class OnceController:

    def __init__(self, effectName, gain = 100):
        VibroManager.g_instance.launchQuickEffect(effectName, 1, gain)
