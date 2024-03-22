# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/battle_control/controllers/vse_hud_settings_ctrl/settings/secondary_objective.py


class SecondaryObjectiveClientModel(object):
    __slots__ = ('id', 'header', 'subheader', 'startSound', 'icon', 'countdownTimer', 'countdownSound', 'successSound', 'failureSound')

    def __init__(self, id, header, subheader, startSound, icon, countdownTimer, countdownSound, successSound, failureSound):
        super(SecondaryObjectiveClientModel, self).__init__()
        self.id = id
        self.header = header
        self.subheader = subheader
        self.startSound = startSound
        self.icon = icon
        self.countdownTimer = countdownTimer
        self.countdownSound = countdownSound
        self.successSound = successSound
        self.failureSound = failureSound

    def __repr__(self):
        return '<SecondaryObjectiveClientModel>: id=%s, header=%s, subheader=%s, startSound=%s, icon=%s, remindTimers=%s, countdownSound=%s, successSound=%s, failureSound=%s' % (self.id,
         self.header,
         self.subheader,
         self.startSound,
         self.icon,
         self.countdownTimer,
         self.countdownSound,
         self.successSound,
         self.failureSound)
