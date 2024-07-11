# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: races/scripts/client/races/settings.py
from collections import namedtuple
from races.gui.impl.gen.view_models.views.battle.races_hud.races_hud_view_model import AnnouncementTypeEnum
Goal = namedtuple('Goal', ['type', 'sound', 'endSound'])
HINTS = {AnnouncementTypeEnum.AWAITINGPLAYERS.value: Goal(type=AnnouncementTypeEnum.AWAITINGPLAYERS, sound=None, endSound=None),
 AnnouncementTypeEnum.PREBATTLE.value: Goal(type=AnnouncementTypeEnum.PREBATTLE, sound=None, endSound=None),
 AnnouncementTypeEnum.STARTRACE.value: Goal(type=AnnouncementTypeEnum.STARTRACE, sound=None, endSound=None),
 AnnouncementTypeEnum.PICKUPS.value: Goal(type=AnnouncementTypeEnum.PICKUPS, sound=None, endSound=None)}
