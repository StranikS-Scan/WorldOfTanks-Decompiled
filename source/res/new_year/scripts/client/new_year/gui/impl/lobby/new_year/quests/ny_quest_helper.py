# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: new_year/scripts/client/new_year/gui/impl/lobby/new_year/quests/ny_quest_helper.py
from helpers import time_utils
from helpers.time_utils import ONE_DAY, ONE_WEEK
from account_helpers import AccountSettings
from account_helpers.AccountSettings import NY_GENERATION_TIME, NY_DAILY_VIDEO_VISITED_AT
from gui.impl.gen.view_models.common.missions.event_model import EventStatus
from gui.impl.auxiliary.bonus_type import ArenaBonusTypeLabel
from new_year_account_settings import getQuestsUpdatedAt, setQuestsUpdatedAt
from new_year.helpers.server_settings import getNewYearGeneralConfig
from new_year.gui.impl.new_year.new_year_bonus_packer import getNewYearBonusPacker
from gui.shared.missions.packers.events import BattleQuestUIDataPacker

def packNyQuestCardModel(quest, model):
    packer = BattleQuestUIDataPacker(quest, bonusPackerGetter=getNewYearBonusPacker)
    return packer.pack(model=model)


def updateBattleModes(quest, arenaBonusTypes):
    arenaBonusTypes.clear()
    bonusTypes = quest.preBattleCond.getConditions().find('bonusTypes').getValue()
    for bonusType in bonusTypes:
        if ArenaBonusTypeLabel.LABELS.get(bonusType):
            arenaBonusTypes.addString(ArenaBonusTypeLabel.LABELS.get(bonusType))

    arenaBonusTypes.invalidate()


def updateQuests(model, quest, questsArray, questModel, questFilterPrefix):
    config = getNewYearGeneralConfig()
    dailyPrefix = config.getDailyPrefix()
    weeklyPrefix = config.getWeeklyPrefix()
    if quest.isCompleted():
        questModel.setStatus(EventStatus.DONE)
    else:
        questModel.setStatus(EventStatus.ACTIVE)
    if questFilterPrefix == dailyPrefix:
        model.setResetDailyTimeLeft(quest.getFinishTimeLeft())
    if questFilterPrefix == weeklyPrefix:
        model.setResetWeeklyTimeLeft(quest.getFinishTimeLeft())
    questsArray.addViewModel(questModel)


def getDaysFromStart():
    return int(time_utils.getServerUTCTime() - getNewYearGeneralConfig().getNewYearStartDate()) / ONE_DAY


def getDaysFromGeneration():
    return int(time_utils.getServerUTCTime() - AccountSettings.getNewYear(NY_GENERATION_TIME)) / ONE_DAY


def getWeekFromStart():
    return int(time_utils.getServerUTCTime() - getNewYearGeneralConfig().getNewYearStartDate()) / ONE_WEEK


def getDaysFromVisitVideo():
    return int(time_utils.getServerUTCTime() - AccountSettings.getNewYear(NY_DAILY_VIDEO_VISITED_AT)) / ONE_DAY


def getDaysFromQuestsUpdate():
    updatedAt = getQuestsUpdatedAt() if getQuestsUpdatedAt() != 0 else getNewYearGeneralConfig().getNewYearStartDate()
    return int((time_utils.getServerUTCTime() - updatedAt) / ONE_DAY)


def updateQuestsUpdatedAt():
    updatedAt = getQuestsUpdatedAt() if getQuestsUpdatedAt() != 0 else getNewYearGeneralConfig().getNewYearStartDate()
    newValue = updatedAt + getDaysFromQuestsUpdate() * ONE_DAY
    setQuestsUpdatedAt(newValue)
