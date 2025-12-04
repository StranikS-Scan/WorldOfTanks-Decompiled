# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: new_year/scripts/client/new_year/tamagotchi/dto/leaderboard.py
import typing
from new_year.tamagotchi.dto.base import BaseDto

class Leaderboard(BaseDto):

    class Dto(BaseDto):
        __slots__ = ('updateTime', 'nextUpdateTime', 'isRecalcTime', 'user', 'page')

        def __init__(self):
            super(Leaderboard.Dto, self).__init__()
            self.updateTime = 0.0
            self.nextUpdateTime = 0.0
            self.isRecalcTime = False
            self.user = Leaderboard.User.Dto()
            self.page = Leaderboard.Page.Dto()

    class User(BaseDto):

        class Dto(BaseDto):
            __slots__ = ('position', 'points', 'pointsByNextPlayer', 'pointsByNextTop', 'rewardsPlaces', 'rewards')

            def __init__(self):
                super(Leaderboard.User.Dto, self).__init__()
                self.position = 0
                self.points = 0
                self.pointsByNextPlayer = 0
                self.pointsByNextTop = 0
                self.rewardsPlaces = 0
                self.rewards = dict()

    class Page(BaseDto):

        class Dto(BaseDto):
            __slots__ = ('totalPage', 'currentPage', 'leaderboard')

            def __init__(self):
                super(Leaderboard.Page.Dto, self).__init__()
                self.totalPage = 0
                self.currentPage = 0
                self.leaderboard = list()

        class Row(BaseDto):

            class Dto(BaseDto):
                __slots__ = ('spaId', 'position', 'point', 'nickname', 'upDown')

                def __init__(self):
                    super(Leaderboard.Page.Row.Dto, self).__init__()
                    self.spaId = 0
                    self.position = 0
                    self.point = 0
                    self.nickname = ''
                    self.upDown = 0
