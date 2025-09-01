# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/personal_missions_30/camera_mover.py
import logging
from gui.subhangar.subhangar_state_groups import CameraMover
_logger = logging.getLogger(__name__)

class PersonalMissions3CameraMover(CameraMover):

    def __init__(self, callback=None):
        self.callback = callback

    def moveCamera(self, _, __):
        if self.callback:
            self.callback()
        else:
            _logger.error('PersonalMissions3CameraMover callback is None')
