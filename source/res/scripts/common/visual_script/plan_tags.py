# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/common/visual_script/plan_tags.py
from __future__ import absolute_import
from future.utils import viewitems
from arena_bonus_type_caps import ARENA_BONUS_TYPE_CAPS as BONUS_CAPS, ALLOWED_ARENA_BONUS_TYPE_CAPS
from constants import IS_CLIENT, IS_DEVELOPMENT
if IS_CLIENT:
    import BattleReplay

def bonusCapToTag(cap):
    return 'Load.BonusCaps.' + cap


def notInReplay():
    return not BattleReplay.isPlaying() if IS_CLIENT else True


class PlanTags(object):
    _tags = {'Load.NotInReplay': notInReplay,
     'Load.Development': lambda : IS_DEVELOPMENT}
    EXTRA_TAGS = ['Load.Cache']

    def __init__(self, arenaBonusType=0):
        self._tagsList = [ tag for tag, func in viewitems(PlanTags._tags) if func() ]
        if arenaBonusType != 0:
            self._tagsList.extend((bonusCapToTag(cap) for cap in BONUS_CAPS.get(arenaBonusType)))

    @property
    def tags(self):
        return self._tagsList


def getAllTags():
    tagsAll = list(PlanTags._tags)
    tagsAll.extend((bonusCapToTag(cap) for cap in ALLOWED_ARENA_BONUS_TYPE_CAPS))
    tagsAll.extend(PlanTags.EXTRA_TAGS)
    return tagsAll
