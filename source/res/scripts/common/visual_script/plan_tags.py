# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/common/visual_script/plan_tags.py
from constants import IS_CLIENT
if IS_CLIENT:
    import BattleReplay

class PlanTags(object):

    def __init__(self):
        self._tags = {'Load.NotInReplay': PlanTags.__notInReplay}

    @staticmethod
    def __notInReplay():
        return not BattleReplay.isPlaying() if IS_CLIENT else False

    def tagsAll(self):
        return list(self._tags.keys())

    def tags(self):
        return [ tag for tag, func in self._tags.iteritems() if func() ]
