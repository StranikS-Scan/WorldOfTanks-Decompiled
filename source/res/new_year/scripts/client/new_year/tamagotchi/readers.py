# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: new_year/scripts/client/new_year/tamagotchi/readers.py
import time
import typing
from helpers.time_utils import ONE_MINUTE, getServerUTCTime
from new_year.ny_constants import TamagotchiState
from new_year.tamagotchi.dto.leaderboard import Leaderboard
from new_year.tamagotchi.dto.config import Config
from new_year.tamagotchi.dto.player_info import PlayerInfo
from new_year.tamagotchi.dto.player_stats import PlayerStats

def readTamagotchiConfig(rawData):
    result = Config.Dto()
    result.startTime = rawData['start_time']
    result.endTime = rawData['end_time']
    result.currentSeason = None
    for seasonId, season in enumerate(rawData['leaderboards']['seasons'], start=1):
        seasonDto = Config.Season.Dto()
        seasonDto.id = int(seasonId)
        seasonDto.rewardTime = season['reward_time']
        seasonDto.startTime = season['start_time']
        seasonDto.endTime = season['end_time']
        for top in season['rewards_to_position']:
            topDto = Config.Season.TopConfig.Dto()
            topDto.startPos = top['start_pos']
            topDto.endPos = top['end_pos']
            topDto.rewards = top.get('rewards', dict())
            seasonDto.topConfig.append(topDto)

        giftReward = season['gift_reward']
        if giftReward is not None:
            drawRewardDto = seasonDto.drawReward
            drawRewardDto.count = giftReward['count']
            drawRewardDto.rewards = giftReward.get('rewards', dict())
        if seasonDto.startTime <= time.time() <= seasonDto.endTime:
            result.currentSeason = seasonDto
        result.seasons.append(seasonDto)

    for attrName, value in rawData['states'].iteritems():
        state = Config.States.Dto()
        state.min = value['scale_sum_level_min']
        state.max = value['scale_sum_level_max']
        result.states[attrName] = state

    gift = rawData['gift']
    giftDto = result.gift = Config.Gift.Dto()
    giftDto.baseInterval = gift['baseInterval']
    giftDto.product = gift['product']
    secret = gift['secret']
    secretDto = giftDto.secret = Config.Gift.Secret.Dto()
    secretDto.product = secret['product']
    secretDto.giftCount = secret['guaranteed_gift_count']
    secretDto.chance = secret['chance']
    for attrName, value in rawData['indicators'].iteritems():
        indicator = Config.Indicators.Dto()
        indicator.giftCountUnlock = value['giftCountUnlock']
        indicator.maxPoints = value['maxPoint']
        result.indicators[attrName] = indicator
        for state, level in enumerate(value['levels']):
            levelDto = Config.Indicators.Level.Dto()
            levelDto.giftSpeedFactor = level['giftSpeedFactor']
            levelDto.debPercent = level['debPercent']
            levelDto.degradation = level['degradation']
            levelDto.loyalty = level['loyalty']
            levelDto.points = level['point']
            levelDto.state = state
            indicator.levels.append(levelDto)

    for item in rawData['items']:
        itemDto = result.indicators[item['type']].item
        itemDto.id = item['id']
        itemDto.dynCurrencyCode = item['currency_code']
        itemDto.leaderboardPoint = item['leaderboard_point']
        itemDto.currency = item['price']['currency']
        itemDto.price = item['price']['amount']
        itemDto.scalePoint = item['scale_point']

    return result


def readTamagotchiLeaderboard(rawData):
    result = Leaderboard.Dto()
    result.updateTime = rawData.get('update_time')
    if result.updateTime is None:
        result.updateTime = getServerUTCTime()
    result.nextUpdateTime = rawData.get('next_update_time')
    if result.nextUpdateTime is None:
        result.nextUpdateTime = result.updateTime + ONE_MINUTE * 5
    result.isRecalcTime = rawData.get('is_recalc_time', False)
    pageData = rawData['page_data']
    pageDto = result.page
    pageDto.totalPage = pageData['total_page']
    pageDto.currentPage = pageData['current_page']
    for row in pageData['leaderboard']:
        rowDto = Leaderboard.Page.Row.Dto()
        rowDto.spaId = row['spa_id']
        rowDto.position = row['position']
        rowDto.point = row['point']
        rowDto.nickname = row['nickname']
        rowDto.upDown = row['up_down']
        pageDto.leaderboard.append(rowDto)

    userDto = result.user
    userData = rawData['user_data']
    userDto.position = userData['position']
    userDto.points = userData['points']
    userDto.pointsByNextPlayer = userData['points_by_next_player']
    userDto.pointsByNextTop = userData['points_by_next_top']
    userDto.rewardsPlaces = userData['rewards_places']
    userDto.rewards = userData['rewards']
    return result


def readTamagotchiPlayerInfo(rawData):
    result = PlayerInfo.Dto()
    result.state = TamagotchiState.SAD.value
    result.leaderboardPoint = rawData['leaderboard_point']
    result.lastUpdateTime = rawData['last_update']
    result.giftTime = rawData['gift_time']
    result.giftCount = rawData['gift_count']
    result.giftCollected = rawData['gift_collected']
    result.indicators = rawData['indicators']
    for rawDebHist in rawData['deb_history']:
        hist = PlayerInfo.DebHistory.Dto()
        hist.value = rawDebHist['value']
        hist.expirationTime = rawDebHist['expired_date']
        result.debHistory.append(hist)

    return result


def readTamagotchiPlayerStats(rawData):
    result = PlayerStats.Dto()
    result.leaderboardPoint = rawData['leaderboard_point']
    for rawWeekStat in rawData['week_stats']:
        weekStat = PlayerStats.WeekStat.Dto()
        weekStat.week = rawWeekStat['week'] + 1
        weekStat.position = rawWeekStat['position']
        weekStat.point = rawWeekStat['point']
        weekStat.isRewarded = rawWeekStat['isRewarded']
        weekStat.rewardedDate = rawWeekStat['rewarded_date']
        weekStat.rewards = rawWeekStat['rewards']
        weekStat.deltaPoint = rawWeekStat['delta_point']
        result.weekStats.append(weekStat)

    return result
