# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/battle_control/controllers/event_mark1/__init__.py
from gui.battle_control.controllers.event_mark1 import bonus_ctrl
from gui.battle_control.controllers.event_mark1 import events_ctrl

def createBonusCtrl(setup):
    return bonus_ctrl.Mark1BonusController(setup)


def createEventsCtrl(setup, bonusCtrl):
    return events_ctrl.Mark1EventNotificationController(setup, bonusCtrl)


__all__ = ('createBonusCtrl', 'createEventsCtrl')
