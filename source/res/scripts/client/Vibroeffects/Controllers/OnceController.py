# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/Vibroeffects/Controllers/OnceController.py
from Vibroeffects import VibroManager

class OnceController:

    def __init__(self, effectName, gain=100):
        VibroManager.g_instance.launchQuickEffect(effectName, 1, gain)
