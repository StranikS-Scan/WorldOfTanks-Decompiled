# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: new_year/scripts/client/new_year/tamagotchi/dto/config.py
import typing
from new_year.tamagotchi.dto.base import BaseDto

class Config(BaseDto):

    class Dto(BaseDto):
        __slots__ = ('startTime', 'endTime', 'gift', 'currentSeason', 'seasons', 'states', 'indicators')

        def __init__(self):
            super(Config.Dto, self).__init__()
            self.startTime = 0.0
            self.endTime = 0.0
            self.gift = Config.Gift.Dto()
            self.currentSeason = None
            self.seasons = list()
            self.states = dict()
            self.indicators = dict()
            return

    class Season(BaseDto):

        class Dto(BaseDto):
            __slots__ = ('id', 'startTime', 'endTime', 'rewardTime', 'topConfig', 'drawReward')

            def __init__(self):
                super(Config.Season.Dto, self).__init__()
                self.id = 0
                self.startTime = 0.0
                self.endTime = 0.0
                self.rewardTime = 0.0
                self.topConfig = list()
                self.drawReward = Config.Season.DrawReward.Dto()

        class TopConfig(BaseDto):

            class Dto(BaseDto):
                __slots__ = ('startPos', 'endPos', 'rewards')

                def __init__(self):
                    super(Config.Season.TopConfig.Dto, self).__init__()
                    self.startPos = 0
                    self.endPos = 0
                    self.rewards = dict()

        class DrawReward(BaseDto):

            class Dto(BaseDto):
                __slots__ = ('count', 'rewards')

                def __init__(self):
                    super(Config.Season.DrawReward.Dto, self).__init__()
                    self.count = 0
                    self.rewards = dict()

    class States(BaseDto):

        class Dto(BaseDto):
            __slots__ = ('min', 'max')

            def __init__(self):
                super(Config.States.Dto, self).__init__()
                self.min = 0
                self.max = 0

    class Gift(BaseDto):

        class Dto(BaseDto):
            __slots__ = ('baseInterval', 'product', 'secret')

            def __init__(self):
                super(Config.Gift.Dto, self).__init__()
                self.baseInterval = 0
                self.product = ''
                self.secret = Config.Gift.Secret.Dto()

        class Secret(BaseDto):

            class Dto(BaseDto):
                __slots__ = ('product', 'giftCount', 'chance')

                def __init__(self):
                    super(Config.Gift.Secret.Dto, self).__init__()
                    self.product = ''
                    self.giftCount = 0
                    self.chance = 0.0

    class Indicators(BaseDto):

        class Dto(BaseDto):
            __slots__ = ('giftCountUnlock', 'maxPoints', 'levels', 'item')

            def __init__(self):
                super(Config.Indicators.Dto, self).__init__()
                self.giftCountUnlock = 0
                self.maxPoints = 0
                self.levels = list()
                self.item = Config.Items.Dto()

        class Level(BaseDto):

            class Dto(BaseDto):
                __slots__ = ('giftSpeedFactor', 'debPercent', 'degradation', 'loyalty', 'points', 'state')

                def __init__(self):
                    super(Config.Indicators.Level.Dto, self).__init__()
                    self.giftSpeedFactor = 0.0
                    self.debPercent = 0.0
                    self.degradation = 0
                    self.loyalty = 0
                    self.points = 0
                    self.state = 0

    class Items(BaseDto):

        class Dto(BaseDto):
            __slots__ = ('id', 'leaderboardPoint', 'dynCurrencyCode', 'currency', 'price', 'scalePoint')

            def __init__(self):
                super(Config.Items.Dto, self).__init__()
                self.id = 0
                self.leaderboardPoint = 0
                self.dynCurrencyCode = ''
                self.currency = ''
                self.price = 0
                self.scalePoint = 0
