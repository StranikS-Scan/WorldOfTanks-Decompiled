# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: cosmic_event/scripts/client/cosmic_event/settings.py
from collections import namedtuple
from cosmic_event.gui.impl.gen.view_models.views.battle.cosmic_hud.cosmic_hud_view_model import AnnouncementTypeEnum
from cosmic_sound import CosmicBattleSounds

class CosmicEventConfig(namedtuple('CosmicEventConfig', ('isEnabled', 'isBattleEnabled', 'peripheryIDs', 'primeTimes', 'seasons', 'cycleTimes', 'scoreSystem', 'eventVehicleCD', 'rewardSettings', 'vehicleRentQuestID', 'progressionFinishedToken'))):
    __slots__ = ()

    def __new__(cls, **kwargs):
        defaults = dict(isEnabled=False, isBattleEnabled=False, peripheryIDs={}, primeTimes={}, seasons={}, cycleTimes={}, scoreSystem={}, eventVehicleCD=None, rewardSettings={}, vehicleRentQuestID='', progressionFinishedToken='')
        defaults.update(kwargs)
        return super(CosmicEventConfig, cls).__new__(cls, **defaults)

    def asDict(self):
        return self._asdict()

    @classmethod
    def defaults(cls):
        return cls()


Goal = namedtuple('Goal', ['type', 'sound', 'endSound'])
HINTS = {AnnouncementTypeEnum.RESPAWN.value: Goal(type=AnnouncementTypeEnum.RESPAWN, sound=None, endSound=(CosmicBattleSounds.Announcements.FINISHED,)),
 AnnouncementTypeEnum.AWAITINGPLAYERS.value: Goal(type=AnnouncementTypeEnum.AWAITINGPLAYERS, sound=None, endSound=(CosmicBattleSounds.Announcements.FINISHED,)),
 AnnouncementTypeEnum.PREBATTLE.value: Goal(type=AnnouncementTypeEnum.PREBATTLE, sound=None, endSound=(CosmicBattleSounds.Announcements.FINISHED,)),
 AnnouncementTypeEnum.STARTBATTLE.value: Goal(type=AnnouncementTypeEnum.STARTBATTLE, sound=None, endSound=None),
 AnnouncementTypeEnum.PICKUPS.value: Goal(type=AnnouncementTypeEnum.PICKUPS, sound=None, endSound=(CosmicBattleSounds.Announcements.PICK_UP_ANNOUNCE_END, CosmicBattleSounds.Announcements.FINISHED, CosmicBattleSounds.Announcements.ABILITIES_SPAWNED)),
 AnnouncementTypeEnum.SCANAVAILABLE.value: Goal(type=AnnouncementTypeEnum.SCANAVAILABLE, sound=None, endSound=(CosmicBattleSounds.Announcements.FINISHED,)),
 AnnouncementTypeEnum.PREPARETOSCAN.value: Goal(type=AnnouncementTypeEnum.PREPARETOSCAN, sound=None, endSound=(CosmicBattleSounds.Announcements.FINISHED,)),
 AnnouncementTypeEnum.PREPARETOSCANFINAL.value: Goal(type=AnnouncementTypeEnum.PREPARETOSCANFINAL, sound=None, endSound=(CosmicBattleSounds.Announcements.FINISHED,)),
 AnnouncementTypeEnum.FINALSCANAVAILABLE.value: Goal(type=AnnouncementTypeEnum.FINALSCANAVAILABLE, sound=None, endSound=(CosmicBattleSounds.Announcements.FINISHED,)),
 AnnouncementTypeEnum.SCANNING.value: Goal(type=AnnouncementTypeEnum.SCANNING, sound=None, endSound=(CosmicBattleSounds.Announcements.FINISHED,))}
