# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/battle_control/controllers/hit_direction_ctrl/__init__.py
from gui.battle_control.controllers.hit_direction_ctrl.base import HitType, IHitIndicator
from gui.battle_control.controllers.hit_direction_ctrl.ctrl import HitDirectionControllerPlayer, HitDirectionController, EpicHitDirectionController
__all__ = ('HitType', 'IHitIndicator', 'createHitDirectionController')

def createHitDirectionController(setup):
    if setup.isReplayPlaying:
        return HitDirectionControllerPlayer(setup)
    guiVisitor = setup.arenaVisitor.gui
    return EpicHitDirectionController(setup) if guiVisitor.isInEpicRange() else HitDirectionController(setup)
