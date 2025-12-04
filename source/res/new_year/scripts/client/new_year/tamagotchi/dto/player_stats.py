# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: new_year/scripts/client/new_year/tamagotchi/dto/player_stats.py
import typing
from new_year.tamagotchi.dto.base import BaseDto

class PlayerStats(BaseDto):

    class Dto(BaseDto):
        __slots__ = ('leaderboardPoint', 'weekStats')

        def __init__(self):
            super(PlayerStats.Dto, self).__init__()
            self.leaderboardPoint = 0.0
            self.weekStats = list()

    class WeekStat(BaseDto):

        class Dto(BaseDto):
            __slots__ = ('week', 'position', 'point', 'isRewarded', 'rewardedDate', 'rewards', 'deltaPoint')

            def __init__(self):
                super(PlayerStats.WeekStat.Dto, self).__init__()
                self.week = 0
                self.position = 0
                self.point = 0.0
                self.isRewarded = False
                self.rewardedDate = 0.0
                self.rewards = dict()
                self.deltaPoint = 0
