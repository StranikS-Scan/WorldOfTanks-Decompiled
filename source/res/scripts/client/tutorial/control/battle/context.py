# Embedded file name: scripts/client/tutorial/control/battle/context.py
from collections import namedtuple
import struct
import BigWorld
import SoundGroups
from constants import ARENA_GUI_TYPE
from gui.battle_control import arena_info
from tutorial.control import context
from tutorial.control.context import ClientCtx, GlobalStorage
from tutorial.logger import LOG_DEBUG, LOG_ERROR, LOG_WARNING
import FMOD
BATTLE_RECORDS = ('completed', 'failed', 'accCompleted', 'startedAt', 'chapterIdx')
EXTENDED_BATTLE_RECORDS = ('playerTeam', 'winnerTeam', 'finishReason', 'vTypeCD', 'arenaTypeID', 'arenaUniqueID')
ALL_BATTLE_RECORDS = BATTLE_RECORDS + EXTENDED_BATTLE_RECORDS
BATTLE_RECORDS_FORMAT = '3ifh'
ALL_BATTLE_RECORDS_FORMAT = '3if4h2iQ'

class TRAINING_RESULT_KEY:
    FINISHED = 'finished'
    FAILED = 'failed'


class TRAINING_FINISH_REASON_KEY:
    FINISHED = 'finished'
    FAILED = 'failed'
    TIMEOUT = 'timeout'
    EXTERMINATION = 'extermination'


class BattleClientCtx(ClientCtx, namedtuple('BattleClientCtx', BATTLE_RECORDS)):

    @classmethod
    def _makeDefault(cls):
        return cls.__new__(cls, 0, -1, -1, 0.0, -1)

    @classmethod
    def makeCtx(cls, record):
        result = cls._makeDefault()
        if record is not None and len(record):
            try:
                result = cls._make(struct.unpack(BATTLE_RECORDS_FORMAT, record))
            except struct.error:
                LOG_ERROR('Client ctx is not valid', record)

        return result

    @classmethod
    def fetch(cls, *args):
        player = BigWorld.player()
        if player is None or not hasattr(player, 'clientCtx'):
            LOG_DEBUG('Avatar.clientCtx not found', player)
            result = cls._makeDefault()
        else:
            result = cls.makeCtx(player.clientCtx)
        return result

    def _store(self):
        record = self.makeRecord()
        player = BigWorld.player()
        if player is None or not hasattr(player, 'storeClientCtx'):
            LOG_DEBUG('Avatar.storeClientCtx not found', player)
            return False
        else:
            player.storeClientCtx(record)
            return True

    def makeRecord(self):
        return struct.pack(BATTLE_RECORDS_FORMAT, *self)

    def addMask(self, mask, done = True):
        completed = self.completed
        failed = self.failed
        if done:
            completed |= mask
        else:
            failed |= mask
        newCtx = self._replace(completed=completed, failed=failed)
        if newCtx._store():
            return newCtx
        return self

    def setChapterIdx(self, chapterIdx):
        newCtx = self._replace(chapterIdx=chapterIdx)
        if newCtx._store():
            return newCtx
        return self

    def setAccCompleted(self, accCompleted):
        newCtx = self._replace(accCompleted=accCompleted)
        if newCtx._store():
            return newCtx
        return self

    def setStartedAt(self, time):
        newCtx = self._replace(startedAt=time)
        if newCtx._store():
            return newCtx
        return self


class ExtendedBattleClientCtx(ClientCtx, namedtuple('ExtendedBattleClientCtx', ALL_BATTLE_RECORDS)):

    @classmethod
    def _makeDefault(cls):
        return cls.__new__(cls, 0, -1, -1, 0.0, -1, 1, 2, -1, -1, -1, -1)

    @classmethod
    def makeCtx(cls, record):
        result = cls._makeDefault()
        if record is not None and len(record):
            try:
                result = cls._make(struct.unpack(ALL_BATTLE_RECORDS_FORMAT, record))
            except struct.error:
                LOG_ERROR('Client ctx is not valid', record)

        return result

    @classmethod
    def fetch(cls, *args):
        params = ExtendedBattleClientCtx._makeDefault()._asdict()
        player = BigWorld.player()
        params.update(BattleClientCtx.fetch()._asdict())
        arena = getattr(player, 'arena', None)
        if arena is not None:
            info = arena.periodAdditionalInfo
            if info is not None and len(info) > 1:
                params['winnerTeam'] = info[0]
                params['finishReason'] = info[1]
            params['arenaUniqueID'] = arena.arenaUniqueID
            arenaType = arena.arenaType
            if arenaType is not None:
                params['arenaTypeID'] = arenaType.id
            pVehID = getattr(player, 'playerVehicleID', None)
            vehicles = arena.vehicles
            if pVehID in vehicles:
                vDescriptor = vehicles[pVehID]['vehicleType']
                if vDescriptor is not None:
                    params['vTypeCD'] = vDescriptor.type.compactDescr
        params['playerTeam'] = getattr(player, 'team', 1)
        LOG_DEBUG('All records in context', params)
        return ExtendedBattleClientCtx(**params)

    def makeRecord(self):
        try:
            record = struct.pack(ALL_BATTLE_RECORDS_FORMAT, *self)
        except struct.error as error:
            LOG_ERROR('Can not pack client context', error.message, self)
            record = ''

        return record


class BattleStartReqs(context.StartReqs):

    def isEnabled(self):
        return arena_info.getArenaGuiType() == ARENA_GUI_TYPE.TUTORIAL

    def prepare(self, ctx):
        clientCtx = BattleClientCtx.fetch()
        ctx.bonusCompleted = clientCtx.completed
        GlobalStorage.clearVars()

    def process(self, descriptor, ctx):
        return True


class BattleBonusesRequester(context.BonusesRequester):

    def request(self, chapterID = None):
        chapter = self.getChapter(chapterID=chapterID)
        if chapter is None:
            LOG_ERROR('Chapter not found', chapterID)
            return
        elif not chapter.hasBonus():
            LOG_ERROR('Chapter has not bonus', chapter.getID())
            return
        else:
            bonusID = chapter.getBonusID()
            mask = 1 << bonusID
            localCtx = BattleClientCtx.fetch().addMask(mask)
            if chapter.isBonusReceived(self._completed):
                LOG_DEBUG('Bonus already received', chapter.getID(), self._completed)
                self._isReceived = True
                return
            LOG_DEBUG('Received bonus', bonusID)
            self._completed |= mask
            self._gui.setTrainingProgress(self._descriptor.getProgress(localCtx.completed))
            return


class BattleSoundPlayer(context.SoundPlayer):
    if FMOD.enabled:
        __guiSounds = {context.SOUND_EVENT.TASK_FAILED: '/GUI/notifications_FX/task_new',
         context.SOUND_EVENT.TASK_COMPLETED: '/GUI/notifications_FX/task_complete',
         context.SOUND_EVENT.NEXT_CHAPTER: '/GUI/notifications_FX/task_part_complete'}

    def __init__(self):
        super(BattleSoundPlayer, self).__init__()
        self.__ignoreNext = False
        self.__speakSnd = None
        self.__nextSpeakID = None
        self.__prevSpeaks = set()
        return

    def play(self, event, sndID = None):
        if self.isMuted():
            return
        if event in self.__guiSounds.keys():
            self._playGUI(event)
        elif event is context.SOUND_EVENT.SPEAKING:
            self._speak(sndID)
        else:
            LOG_WARNING('Sound event is not supported', event)

    def stop(self):
        self._clear()
        self.__ignoreNext = False
        self.__nextSpeakID = None
        self.__prevSpeaks.clear()
        return

    def isPlaying(self, event, sndID = None):
        result = False
        if event is context.SOUND_EVENT.SPEAKING:
            if self.__speakSnd is not None:
                if sndID is not None:
                    result = len(self.__prevSpeaks) and list(self.__prevSpeaks)[-1] == sndID
                else:
                    result = True
        else:
            LOG_WARNING('Sound event is not supported', event)
        return result

    def goToNextChapter(self):
        self.__prevSpeaks.clear()

    def _playGUI(self, event):
        if self.__ignoreNext:
            self.__ignoreNext = False
            return
        if event is context.SOUND_EVENT.NEXT_CHAPTER:
            self.__ignoreNext = True
        sndID = self.__guiSounds[event]
        SoundGroups.g_instance.playSound2D(sndID)

    def _clear(self):
        if self.__speakSnd is not None:
            if FMOD.enabled:
                self.__speakSnd.setCallback('EVENTFINISHED', None)
            self.__speakSnd.stop()
            self.__speakSnd = None
        return

    def _speak(self, sndID):
        if sndID is None:
            LOG_WARNING('Sound ID for speaking is not defined')
            return
        elif sndID in self.__prevSpeaks:
            LOG_DEBUG('Speaking played, ignore', sndID)
            return
        elif self.__speakSnd is not None:
            self.__nextSndID = sndID
            return
        else:
            sound = SoundGroups.g_instance.getSound2D(sndID)
            if not sound:
                LOG_ERROR('Sound not found', sndID)
                return
            self.__nextSndID = None
            self.__speakSnd = sound
            self.__prevSpeaks.add(sndID)
            if FMOD.enabled:
                sound.setCallback('EVENTFINISHED', self.__onSpeakingStop)
            sound.play()
            return

    def __onSpeakingStop(self, sound):
        LOG_DEBUG('Stop playing sound by event', sound)
        self._clear()
        if self.__nextSndID is not None:
            self._speak(self.__nextSndID)
        return
