# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/bootcamp/BCBattleResult.py
from gui.Scaleform.daapi.view.meta.BCBattleResultMeta import BCBattleResultMeta
from gui.Scaleform.genConsts.BOOTCAMP_BATTLE_RESULT_CONSTANTS import BOOTCAMP_BATTLE_RESULT_CONSTANTS as AWARD
from gui.shared import event_bus_handlers, events, EVENT_BUS_SCOPE
from CurrentVehicle import g_currentVehicle
from helpers import dependency
from gui.sounds.ambients import BattleResultsEnv
import SoundGroups
from re import sub
from bootcamp.BootCampEvents import g_bootcampEvents
from gui.app_loader import g_appLoader
from gui.app_loader.settings import APP_NAME_SPACE
from gui import GUI_CTRL_MODE_FLAG as _CTRL_FLAG
from skeletons.gui.battle_results import IBattleResultsService
from bootcamp.BootcampConstants import BATTLE_STATS_TOOLTIPS_INDEXES as INDEXES, BATTLE_STATS_ICONS as ICONS
from helpers.i18n import makeString
from bootcamp.Bootcamp import g_bootcamp
from constants import BOOTCAMP_BATTLE_RESULT_MESSAGE as BATTLE_RESULT
from gui.battle_control.battle_constants import WinStatus
from copy import deepcopy
from gui.Scaleform.locale.BOOTCAMP import BOOTCAMP
from gui.Scaleform.locale.RES_ICONS import RES_ICONS
from skeletons.gui.game_control import IBootcampController
STATS_ICON_PATH = '../maps/icons/bootcamp/battle_result/{0}.png'
STATS_ICON_TOOLTIP_PATH = '../maps/icons/bootcamp/battle_result/tooltip/{0}.png'
BACKGROUNDS_FOLDER_PATH = '../maps/icons/bootcamp/battle_result/background/'
SNDID_ACHIEVEMENT = 'bc_result_screen_achievements'
SNDID_BONUS = 'bc_result_screen_bonus'

class BCBattleResult(BCBattleResultMeta):
    battleResults = dependency.descriptor(IBattleResultsService)
    bootcampController = dependency.descriptor(IBootcampController)
    __sound_env__ = BattleResultsEnv
    __metaclass__ = event_bus_handlers.EventBusListener

    def __init__(self, ctx=None):
        super(BCBattleResult, self).__init__()
        assert 'arenaUniqueID' in ctx
        assert ctx['arenaUniqueID'], 'arenaUniqueID must be greater than 0'
        self.__arenaUniqueID = ctx['arenaUniqueID']
        self.__populated = False
        self.__isResultsSet = False
        self.__hasBonusInMedals = False
        self.__hasBonusInStats = False
        self.__awardSounds = []
        SoundGroups.g_instance.setVolume('gui', SoundGroups.g_instance.getVolume('gui'), False)
        SoundGroups.g_instance.setVolume('ambient', SoundGroups.g_instance.getVolume('ambient'), False)
        SoundGroups.g_instance.setVolume('music', SoundGroups.g_instance.getVolume('music'), False)
        self.battleResults.onResultPosted += self.__handleBattleResultsPosted

    def onWindowClose(self):
        self.destroy()

    def setReward(self, rewardIndex):
        self.selectedReward = rewardIndex

    def click(self):
        g_bootcampEvents.onResultScreenFinished(self.selectedReward)
        self.destroy()

    def _populate(self):
        SoundGroups.g_instance.playSound2D('bc_result_screen_ambient')
        super(BCBattleResult, self)._populate()
        self.__populated = True
        if self.battleResults.areResultsPosted(self.__arenaUniqueID):
            self.__setBattleResults()
        if g_bootcamp.transitionFlash:
            g_bootcamp.transitionFlash.active(False)
            g_bootcamp.transitionFlash.close()
            g_bootcamp.transitionFlash = None
        return

    def _dispose(self):
        g_bootcampEvents.onResultScreenFinished -= self.onResultScreenFinished
        self.battleResults.onResultPosted -= self.__handleBattleResultsPosted
        for sound in self.__awardSounds:
            sound.stop()

        del self.__awardSounds[:]
        super(BCBattleResult, self)._dispose()

    def addBattleStatsData(self, statsData, battleResultsPersonal, name, id):
        value = battleResultsPersonal['statValues'][0][id]['value']
        value = sub('<.*?>', '', value)
        if value.find('/') != -1:
            value = value.split('/')[-1]
        statsData.append({'id': name,
         'label': makeString('#bootcamp:BATTLE_RESULT_{0}'.format(name.upper())),
         'description': makeString('#bootcamp:BATTLE_RESULT_DESCRIPTION_{0}'.format(name.upper())),
         'value': value,
         'icon': STATS_ICON_PATH.format(ICONS[name]),
         'iconTooltip': STATS_ICON_TOOLTIP_PATH.format(ICONS[name])})

    def getBattleStatsData(self, battleResultsStats):
        battleResultsPersonal = battleResultsStats['personal']
        statsData = []
        battleStats = g_bootcamp.getBattleStatsLesson()
        for statType in battleStats:
            self.addBattleStatsData(statsData, battleResultsPersonal, statType, INDEXES[statType])

        return statsData

    def __addPremiumData(self, listData):
        listData.append({'id': 'premium',
         'label': makeString(BOOTCAMP.RESULT_AWARD_PREMIUM_LABEL),
         'description': makeString(BOOTCAMP.RESULT_AWARD_PREMIUM_TEXT),
         'icon': RES_ICONS.MAPS_ICONS_BOOTCAMP_REWARDS_BCPREMIUM,
         'iconTooltip': RES_ICONS.MAPS_ICONS_BOOTCAMP_REWARDS_TOOLTIPS_BCPREMIUM})

    def __setBattleResults(self):
        if not self.__isResultsSet:
            self.__isResultsSet = True
            g_appLoader.attachCursor(APP_NAME_SPACE.SF_LOBBY, _CTRL_FLAG.GUI_ENABLED)
            g_bootcampEvents.onResultScreenFinished += self.onResultScreenFinished
            resultType, resultReason, resultTypeStr, resultReasonStr, reusableInfo = g_bootcamp.getBattleResults()
            assert reusableInfo is not None
            bgImagePath = self.__getBackgroundImagePath(resultType, g_bootcamp.getLessonNum() - 1)
            self.as_resultTypeHandlerS(resultTypeStr, bgImagePath)
            if resultType == BATTLE_RESULT.VICTORY:
                battleResultsExtra = deepcopy(g_bootcamp.getBattleResultsExtra(g_bootcamp.getLessonNum() - 1))
            else:
                battleResultsExtra = {'medals': [],
                 'stats': [],
                 'unlocks': []}
            battleResultsStats = self.battleResults.getResultsVO(self.__arenaUniqueID)
            showPremium = g_bootcamp.getLessonNum() == g_bootcamp.getContextIntParameter('lastLessonNum') and self.bootcampController.needAwarding()
            battleResultsExtra['showRewards'] = resultType == BATTLE_RESULT.VICTORY and g_bootcamp.getLessonNum() != 1
            if showPremium:
                self.__addPremiumData(battleResultsExtra['medals'])
            battleResultsExtra['stats'] = self.getBattleStatsData(battleResultsStats)
            self.as_setBootcampDataS(battleResultsExtra)
            self.as_setDataS(self.battleResults.getResultsVO(self.__arenaUniqueID))
            self.__hasBonusInMedals = bool(battleResultsExtra.get('unlocks', None))
            xp = reusableInfo.personal.getBaseXPRecords().getRecord('xp')
            credits = reusableInfo.personal.getBaseCreditsRecords().getRecord('credits')
            self.__hasBonusInStats = xp > 0 or credits > 0
        return

    def __handleBattleResultsPosted(self, reusableInfo, composer):
        if self.__arenaUniqueID == reusableInfo.arenaUniqueID and self.__populated:
            self.__setBattleResults()

    @event_bus_handlers.eventBusHandler(events.HideWindowEvent.HIDE_BATTLE_RESULT_WINDOW, EVENT_BUS_SCOPE.LOBBY)
    def selectVehicle(self, inventoryId):
        g_currentVehicle.selectVehicle(inventoryId)
        return g_currentVehicle.invID == inventoryId

    def onResultScreenFinished(self, reward):
        self.destroy()

    def onAnimationAwardStart(self, id):
        soundid = SNDID_ACHIEVEMENT
        if id == AWARD.MEDAlS_LIST and self.__hasBonusInMedals:
            soundid = SNDID_BONUS
        elif id == AWARD.STATS_LIST and self.__hasBonusInStats:
            soundid = SNDID_BONUS
        sound = SoundGroups.g_instance.getSound2D(soundid)
        sound.play()
        self.__awardSounds.append(sound)

    def __handleBattleResultsClose(self, _):
        self.destroy()

    def __getBackgroundImagePath(self, resultType, lessonId):
        if resultType == BATTLE_RESULT.VICTORY:
            name = 'bcVictoryBg_{0}.png'.format(lessonId)
        elif resultType == BATTLE_RESULT.DEFEAT:
            name = 'bcDefeat.png'
        else:
            name = 'bcDraw.png'
        return BACKGROUNDS_FOLDER_PATH + name
