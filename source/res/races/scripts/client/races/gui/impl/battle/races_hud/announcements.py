# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: races/scripts/client/races/gui/impl/battle/races_hud/announcements.py
import math
import typing
import BigWorld
from typing import TYPE_CHECKING
from races.gui.impl.gen.view_models.views.battle.races_hud.races_hud_view_model import AnnouncementTypeEnum, RacesHudViewModel
from helpers import dependency
from skeletons.gui.battle_session import IBattleSessionProvider
if typing.TYPE_CHECKING:
    from typing import Dict
if TYPE_CHECKING:
    from races.settings import Goal

def getAnnouncementType(hint, data):
    return AnnouncementGoal(hint, data)


class AnnouncementGoal(object):
    _sessionProvider = dependency.descriptor(IBattleSessionProvider)

    def __init__(self, hint, data):
        self._hint = hint
        self._showTimer = data.get('param2') == 'True'
        self._duration = int(data.get('param1', '0'))
        self._endTime = BigWorld.serverTime() + self.duration
        self._extraData = data.get('param3')
        self._playedSound = False
        self._ended = False

    @property
    def showTimer(self):
        return self._showTimer

    @property
    def duration(self):
        return self._duration

    @property
    def type(self):
        return self._hint.type

    @property
    def sound(self):
        return self._hint.sound

    @property
    def extraData(self):
        return self._extraData

    @property
    def ended(self):
        return self._ended

    def getRemainingTime(self):
        if self.type in (AnnouncementTypeEnum.PREBATTLE, AnnouncementTypeEnum.AWAITINGPLAYERS):
            periodCtrl = self._sessionProvider.shared.arenaPeriod
            return int(math.ceil(periodCtrl.getEndTime() - BigWorld.serverTime()))
        return int(math.ceil(self._endTime - BigWorld.serverTime()))

    def updateAnnouncement(self, transaction):
        if self._ended:
            return
        else:
            if self.type != transaction.getAnnouncementType():
                transaction.setAnnouncementType(self.type)
                if self.sound is not None:
                    self._playSound(self.sound)
            remTime = self.getRemainingTime()
            if remTime <= 0:
                self.onTimeElapsed(transaction)
            elif self.showTimer:
                transaction.setAnnouncementSecondsToEvent(self.getRemainingTime())
            return

    def onTimeElapsed(self, transaction):
        self.endAnnouncement(transaction)

    def endAnnouncement(self, transaction):
        self._ended = True
        self.clearAnnouncement(transaction)

    def clearAnnouncement(self, transaction):
        transaction.setAnnouncementType(AnnouncementTypeEnum.NONE)
        transaction.setAnnouncementSecondsToEvent(-1)

    def _playSound(self, sound):
        if self._playedSound:
            return
        self._playedSound = True
