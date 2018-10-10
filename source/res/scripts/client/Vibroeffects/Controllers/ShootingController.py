# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/Vibroeffects/Controllers/ShootingController.py
from OnceController import OnceController

class ShootingController(object):

    def __init__(self, caliber):
        if caliber < 50:
            OnceController('shot_small_veff')
        elif caliber < 57:
            OnceController('shot_medium_veff')
        elif caliber < 107:
            OnceController('shot_large_veff')
        else:
            OnceController('shot_main_veff')
