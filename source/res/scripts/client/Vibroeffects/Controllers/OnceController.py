# Python bytecode 2.6 (decompiled from Python 2.7)
# Embedded file name: scripts/client/Vibroeffects/Controllers/OnceController.py
# Compiled at: 2011-03-25 20:17:34
import BigWorld
from Vibroeffects import VibroManager
from debug_utils import *

class OnceController:

    def __init__(self, effectName, gain=100):
        VibroManager.g_instance.launchQuickEffect(effectName, 1, gain)
