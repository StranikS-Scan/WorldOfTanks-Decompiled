# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/battle_control/controllers/hit_direction_ctrl/__init__.py
from gui.battle_control.controllers.hit_direction_ctrl.base import HitType, IHitIndicator
from gui.battle_control.controllers.hit_direction_ctrl.ctrl import HitDirectionControllerPlayer, HitDirectionController
from gui.shared.system_factory import collectHitDirectionController
__all__ = ('HitType', 'IHitIndicator', 'createHitDirectionController')

def createHitDirectionController(setup):
    hitDirectionControllerType, hitDirectionControllerPlayerType = collectHitDirectionController(setup.arenaVisitor.gui.guiType, HitDirectionController, HitDirectionControllerPlayer)
    return hitDirectionControllerPlayerType(setup) if setup.isReplayPlaying else hitDirectionControllerType(setup)
