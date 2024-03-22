# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/battle_control/controllers/vse_hud_settings_ctrl/settings/primary_objective.py
from typing import List

class PrimaryObjectiveClientModel(object):
    __slots__ = ('id', 'header', 'subheader', 'startSound', 'remindTimers', 'remindSound', 'countdownTimer', 'countdownSound', 'success', 'successIcon', 'successSound', 'failure', 'failureIcon', 'failureSound')

    def __init__(self, id, header, subheader, startSound, remindTimers, remindSound, countdownTimer, countdownSound, success, successIcon, successSound, failure, failureIcon, failureSound):
        super(PrimaryObjectiveClientModel, self).__init__()
        self.id = id
        self.header = header
        self.subheader = subheader
        self.startSound = startSound
        self.remindTimers = sorted(remindTimers, reverse=True)
        self.remindSound = remindSound
        self.countdownTimer = countdownTimer
        self.countdownSound = countdownSound
        self.success = success
        self.successIcon = successIcon
        self.successSound = successSound
        self.failure = failure
        self.failureIcon = failureIcon
        self.failureSound = failureSound

    def __repr__(self):
        return '<PrimaryObjectiveClientModel>: id=%s, header=%s, subheader=%s, startSound=%s, remindTimers=%s, remindSound=%s, countdownTimer=%s, countdownSound=%s, success=%s, successIcon=%s, successSound=%s, failure=%s, failureIcon=%s, failureSound=%s' % (self.id,
         self.header,
         self.subheader,
         self.startSound,
         self.remindTimers,
         self.remindSound,
         self.countdownTimer,
         self.countdownSound,
         self.success,
         self.successIcon,
         self.successSound,
         self.failure,
         self.failureIcon,
         self.failureSound)
