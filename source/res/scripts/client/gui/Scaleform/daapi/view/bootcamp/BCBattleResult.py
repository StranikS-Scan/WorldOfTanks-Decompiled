# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/bootcamp/BCBattleResult.py
from gui.Scaleform.daapi.view.meta.BCBattleResultMeta import BCBattleResultMeta
from gui.Scaleform.genConsts.BOOTCAMP_BATTLE_RESULT_CONSTANTS import BOOTCAMP_BATTLE_RESULT_CONSTANTS as AWARD
from gui.shared import event_bus_handlers, events, EVENT_BUS_SCOPE
from CurrentVehicle import g_currentVehicle
from helpers import dependency
from gui.sounds.ambients import BattleResultsEnv
import SoundGroups
from bootcamp.BootCampEvents import g_bootcampEvents
from gui.app_loader import settings as app_settings
from gui import GUI_CTRL_MODE_FLAG as _CTRL_FLAG
from skeletons.gui.app_loader import IAppLoader
from skeletons.gui.battle_results import IBattleResultsService
from bootcamp.statistic.decorators import loggerTarget, loggerEntry, simpleLog
from bootcamp.statistic.logging_constants import BC_LOG_ACTIONS, BC_LOG_KEYS, BC_AWARDS_MAP
_SNDID_ACHIEVEMENT = 'result_screen_achievements'
_SNDID_BONUS = 'result_screen_bonus'
_AMBIENT_SOUND = 'bc_result_screen_ambient'

@loggerTarget(logKey=BC_LOG_KEYS.BC_RESULT_SCREEN)
class BCBattleResult(BCBattleResultMeta):
    battleResults = dependency.descriptor(IBattleResultsService)
    appLoader = dependency.descriptor(IAppLoader)
    __sound_env__ = BattleResultsEnv
    __metaclass__ = event_bus_handlers.EventBusListener

    def __init__(self, ctx=None):
        super(BCBattleResult, self).__init__()
        if 'arenaUniqueID' not in ctx:
            raise UserWarning('Key "arenaUniqueID" is not found in context', ctx)
        if not ctx['arenaUniqueID']:
            raise UserWarning('Value of "arenaUniqueID" must be greater than 0')
        self.__arenaUniqueID = ctx['arenaUniqueID']
        self.__hasShowRewards = False
        self.__hasBonusInMedals = False
        self.__hasBonusInStats = False
        self.__awardSounds = []
        self.__music = None
        return

    def onWindowClose(self):
        self.destroy()

    def onFocusIn(self, alias):
        if self.__music is None:
            if self.alias == alias:
                self.__music = SoundGroups.g_instance.getSound2D(_AMBIENT_SOUND)
                self.__music.play()
        elif self.alias != alias:
            self.__music.stop()
            self.__music = None
        return

    def click(self):
        g_bootcampEvents.onResultScreenFinished()

    def onVideoButtonClick(self):
        g_bootcampEvents.onInterludeVideoStarted()
        for sound in self.__awardSounds:
            sound.stop()

    @event_bus_handlers.eventBusHandler(events.HideWindowEvent.HIDE_BATTLE_RESULT_WINDOW, EVENT_BUS_SCOPE.LOBBY)
    def selectVehicle(self, inventoryId):
        g_currentVehicle.selectVehicle(inventoryId)
        return g_currentVehicle.invID == inventoryId

    @simpleLog(argKey='rendererId', resetTime=False, logOnce=True, argMap=BC_AWARDS_MAP)
    def onToolTipShow(self, rendererId):
        pass

    def onAnimationAwardStart(self, id):
        if not self.battleResults.areResultsPosted(self.__arenaUniqueID):
            return
        else:
            soundid = _SNDID_ACHIEVEMENT if self.__hasShowRewards else None
            if id == AWARD.MEDAlS_LIST and self.__hasBonusInMedals:
                soundid = _SNDID_BONUS
            elif id == AWARD.STATS_LIST and self.__hasBonusInStats:
                soundid = _SNDID_BONUS
            if soundid is not None:
                sound = SoundGroups.g_instance.getSound2D(soundid)
                self.__awardSounds.append(sound)
                sound.play()
            return

    @loggerEntry
    def _populate(self):
        g_bootcampEvents.onResultScreenFinished += self.__onResultScreenFinished
        g_bootcampEvents.onInterludeVideoStarted += self.__onInterludeVideoStarted
        g_bootcampEvents.onInterludeVideoFinished += self.__onInterludeVideoFinished
        self.__music = SoundGroups.g_instance.getSound2D(_AMBIENT_SOUND)
        if self.__music is not None:
            self.__music.play()
        super(BCBattleResult, self)._populate()
        if self.battleResults.areResultsPosted(self.__arenaUniqueID):
            self.__setBattleResults()
        self.app.as_loadLibrariesS(['guiControlsLobbyBattleDynamic.swf', 'guiControlsLobbyDynamic.swf'])
        self.appLoader.attachCursor(app_settings.APP_NAME_SPACE.SF_LOBBY, _CTRL_FLAG.GUI_ENABLED)
        g_bootcampEvents.onResultScreenPopulated()
        return

    @simpleLog(action=BC_LOG_ACTIONS.CONTINUE_BUTTON_PRESSED)
    def _dispose(self):
        g_bootcampEvents.onResultScreenFinished -= self.__onResultScreenFinished
        g_bootcampEvents.onInterludeVideoStarted -= self.__onInterludeVideoStarted
        g_bootcampEvents.onInterludeVideoFinished -= self.__onInterludeVideoFinished
        for sound in self.__awardSounds:
            sound.stop()

        del self.__awardSounds[:]
        if self.__music is not None:
            self.__music.stop()
            self.__music = None
        super(BCBattleResult, self)._dispose()
        return

    def __setBattleResults(self):
        vo = self.battleResults.getResultsVO(self.__arenaUniqueID)
        self.as_setDataS(vo)
        self.__hasShowRewards = vo['showRewards']
        self.__hasBonusInMedals = vo['hasUnlocks']
        self.__hasBonusInStats = vo['xp']['value'] > 0 or vo['credits']['value'] > 0

    def __onResultScreenFinished(self):
        self.destroy()

    def __onInterludeVideoStarted(self):
        self.onFocusIn(alias='')

    def __onInterludeVideoFinished(self):
        self.onFocusIn(alias=self.alias)
