# Embedded file name: scripts/client/Vibroeffects/Controllers/ReloadController.py
from OnceController import OnceController

class ReloadController(OnceController):

    def __init__(self):
        OnceController.__init__(self, 'shot_reload_veff')
