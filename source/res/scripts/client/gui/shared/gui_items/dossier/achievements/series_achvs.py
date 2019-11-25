# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/shared/gui_items/dossier/achievements/series_achvs.py
from dossiers2.ui.achievements import ACHIEVEMENT_BLOCK as _AB
from abstract import SeriesAchievement
from abstract.mixins import Deprecated, Quest, NoProgressBar

class AimerAchievement(NoProgressBar, SeriesAchievement):

    def __init__(self, dossier, value=None):
        SeriesAchievement.__init__(self, 'aimer', _AB.SINGLE, dossier, value)

    def _getCounterRecordNames(self):
        return ((_AB.TOTAL, 'maxAimerSeries'), (_AB.TOTAL, 'maxAimerSeries'))


class ArmorPiercerAchievement(SeriesAchievement):
    __slots__ = ()

    def __init__(self, dossier, value=None):
        super(ArmorPiercerAchievement, self).__init__('armorPiercer', _AB.SINGLE, dossier, value)

    def _getCounterRecordNames(self):
        return ((_AB.TOTAL, 'piercingSeries'), (_AB.TOTAL, 'maxPiercingSeries'))


class DeathTrackAchievement(NoProgressBar, Quest, SeriesAchievement):

    def __init__(self, dossier, value=None):
        SeriesAchievement.__init__(self, 'deathTrack', _AB.SINGLE, dossier, value)

    def _getCounterRecordNames(self):
        return ((_AB.TOTAL, 'deathTrackWinSeries'), (_AB.TOTAL, 'maxDeathTrackWinSeries'))


class DiehardAchievement(SeriesAchievement):
    __slots__ = ()

    def __init__(self, dossier, value=None):
        super(DiehardAchievement, self).__init__('diehard', _AB.SINGLE, dossier, value)

    def _getCounterRecordNames(self):
        return ((_AB.TOTAL, 'diehardSeries'), (_AB.TOTAL, 'maxDiehardSeries'))


class EFC2016Achievement(Quest, SeriesAchievement):

    def __init__(self, dossier, value=None):
        SeriesAchievement.__init__(self, 'EFC2016', _AB.SINGLE, dossier, value)

    def _getCounterRecordNames(self):
        return ((_AB.TOTAL, 'EFC2016WinSeries'), (_AB.TOTAL, 'maxEFC2016WinSeries'))


class InvincibleAchievement(SeriesAchievement):
    __slots__ = ()

    def __init__(self, dossier, value=None):
        super(InvincibleAchievement, self).__init__('invincible', _AB.SINGLE, dossier, value)

    def _getCounterRecordNames(self):
        return ((_AB.TOTAL, 'invincibleSeries'), (_AB.TOTAL, 'maxInvincibleSeries'))


class HandOfDeathAchievement(SeriesAchievement):
    __slots__ = ()

    def __init__(self, dossier, value=None):
        super(HandOfDeathAchievement, self).__init__('handOfDeath', _AB.SINGLE, dossier, value)

    def _getCounterRecordNames(self):
        return ((_AB.TOTAL, 'killingSeries'), (_AB.TOTAL, 'maxKillingSeries'))


class RankedBattlesHeroAchievement(Quest, SeriesAchievement):

    def __init__(self, dossier, value=None):
        SeriesAchievement.__init__(self, 'rankedBattlesHero', _AB.SINGLE, dossier, value)

    def _getCounterRecordNames(self):
        return ((_AB.TOTAL, 'rankedBattlesHeroProgress'), (_AB.TOTAL, 'rankedBattlesHeroProgress'))


class TacticalBreakthroughAchievement(SeriesAchievement):
    __slots__ = ()

    def __init__(self, dossier, value=None):
        super(TacticalBreakthroughAchievement, self).__init__('tacticalBreakthrough', _AB.SINGLE, dossier, value)

    def _getCounterRecordNames(self):
        return ((_AB.TEAM_7X7, 'tacticalBreakthroughSeries'), (_AB.TEAM_7X7, 'maxTacticalBreakthroughSeries'))


class TitleSniperAchievement(SeriesAchievement):
    __slots__ = ()

    def __init__(self, dossier, value=None):
        super(TitleSniperAchievement, self).__init__('titleSniper', _AB.SINGLE, dossier, value)

    def _getCounterRecordNames(self):
        return ((_AB.TOTAL, 'sniperSeries'), (_AB.TOTAL, 'maxSniperSeries'))


class VictoryMarchAchievement(Deprecated, NoProgressBar, SeriesAchievement):

    def __init__(self, dossier, value=None):
        super(VictoryMarchAchievement, self).__init__('victoryMarch', _AB.SINGLE, dossier, value)

    def _getCounterRecordNames(self):
        return ((_AB.RATED_7X7, 'victoryMarchSeries'), (_AB.RATED_7X7, 'maxVictoryMarchSeries'))


class VictoryMarchClubAchievement(Deprecated, NoProgressBar, SeriesAchievement):

    def __init__(self, dossier, value=None):
        super(VictoryMarchClubAchievement, self).__init__('victoryMarch', _AB.SINGLE_7X7, dossier, value)

    def _getCounterRecordNames(self):
        return ((_AB.RATED_7X7, 'victoryMarchSeries'), (_AB.RATED_7X7, 'maxVictoryMarchSeries'))


class WFC2014Achievement(Quest, SeriesAchievement):

    def __init__(self, dossier, value=None):
        SeriesAchievement.__init__(self, 'WFC2014', _AB.SINGLE, dossier, value)

    def _getCounterRecordNames(self):
        return ((_AB.TOTAL, 'WFC2014WinSeries'), (_AB.TOTAL, 'maxWFC2014WinSeries'))
