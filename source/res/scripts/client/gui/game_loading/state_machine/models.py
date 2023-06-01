# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/game_loading/state_machine/models.py
from gui.game_loading.resources.consts import Milestones
from gui.game_loading.resources.models import StatusTextModel
from gui.game_loading.state_machine.const import ContentState

class ImageViewSettingsModel(object):
    __slots__ = ('showVfx', 'contentState', 'ageRatingPath', 'info')

    def __init__(self, showVfx=True, contentState=ContentState.INVISIBLE, ageRatingPath='', info=''):
        self.showVfx = showVfx
        self.contentState = contentState
        self.ageRatingPath = ageRatingPath
        self.info = info

    def __repr__(self):
        return '<ImageViewSettingsModel(vfx={}, contentState={}, ageRatingPath={}, info={})>'.format(self.showVfx, self.contentState, self.ageRatingPath, self.info)


class ProgressSettingsModel(object):
    __slots__ = ('startPercent', 'limitPercent', 'ticksInProgress', 'minTickTimeSec')

    def __init__(self, startPercent, limitPercent, ticksInProgress, minTickTimeSec):
        self.startPercent = startPercent
        self.limitPercent = limitPercent
        self.ticksInProgress = ticksInProgress
        self.minTickTimeSec = minTickTimeSec

    def __repr__(self):
        return '<ProgressBarSettingsModel(start={}, limit={}, ticks={}, minTickTimeSec={})>'.format(self.startPercent, self.limitPercent, self.ticksInProgress, self.minTickTimeSec)


class LoadingMilestoneModel(object):
    __slots__ = ('name', 'percent', 'forceApply', 'status')

    def __init__(self, name, percent, forceApply, status):
        self.name = name
        self.percent = percent
        self.forceApply = forceApply
        self.status = status

    def __repr__(self):
        return '<LoadingMilestoneModel(name={}, percent={}, forceApply={}, status={}>'.format(self.name, self.percent, self.forceApply, self.status)
