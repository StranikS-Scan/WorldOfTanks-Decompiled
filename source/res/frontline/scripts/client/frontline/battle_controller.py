# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: frontline/scripts/client/frontline/battle_controller.py
import typing
import BigWorld
import Event
from constants import QUEST_PROGRESS_STATE as STATE
from epic_constants import SECTORS, EPIC_BATTLE_TEAM_ID
from helpers import dependency
from skeletons.gui.battle_session import IBattleSessionProvider
from skeletons.gui.game_control import IEpicBattleController, IEpicBattleMetaGameController
_DEFAULT_VALUE = 0
_DEFAULT_STATE = STATE.NOT_STARTED

class EpicBattleController(IEpicBattleController):
    __metaController = dependency.descriptor(IEpicBattleMetaGameController)
    __sessionProvider = dependency.descriptor(IBattleSessionProvider)

    def __init__(self):
        super(EpicBattleController, self).__init__()
        self.__eventManager = Event.EventManager()
        self.onQuestChanged = Event.Event(self.__eventManager)
        self.onQuestProgressChanged = Event.Event(self.__eventManager)
        self.onCurrentSectorChanged = Event.Event(self.__eventManager)
        self.onOwnSectorsChanged = Event.Event(self.__eventManager)
        self.onSectorProgressionChanged = Event.Event(self.__eventManager)
        self.onProgressionModelChanged = Event.Event(self.__eventManager)
        self.onSupplyActivated = Event.Event(self.__eventManager)
        self.onAirshipCome = Event.Event(self.__eventManager)
        self.__progress = None
        self.__ownSectors = None
        self.__currentSectorID = None
        self.__questName = None
        self.__sectorProgression = (-1, -1)
        return

    def init(self):
        self.reset()

    def fini(self):
        self.__eventManager.clear()

    def setQuest(self, questName):
        self.__questName = questName
        self.onQuestChanged(questName)

    def setOwnSectors(self, sectors):
        self.__ownSectors = sectors
        self.onOwnSectorsChanged(sectors)

    def setCurrentSector(self, sectorID):
        self.__currentSectorID = sectorID
        self.onCurrentSectorChanged(sectorID)

    def getCurrentSector(self):
        return self.__currentSectorID

    def getQuest(self):
        return self.__questName

    def getQuestProgress(self):
        return self.__progress

    def getOwnSectors(self):
        return self.__ownSectors

    def getAimSector(self):
        componentSystem = self.__sessionProvider.arenaVisitor.getComponentSystem()
        sectorBaseComp = getattr(componentSystem, 'sectorBaseComponent', None)
        if sectorBaseComp is None or not self.__ownSectors:
            return -1
        else:
            lane = self.__ownSectors[0]
            sectorIDs = sectorBaseComp.getNonCapturedSectorBaseIdsByLane(lane)
            return sectorIDs[0] if sectorIDs else -1

    def updateQuestProgress(self, questName, progressesInfo):
        if questName == self.__questName:
            self.__updateProgress(progressesInfo)
            self.onQuestProgressChanged(*self.__progress)

    def reset(self):
        self.__progress = (_DEFAULT_VALUE, _DEFAULT_STATE)
        self.__ownSectors = ()
        self.__currentSectorID = 0
        self.__questName = ''

    def setSectorProgression(self, progression):
        self.__sectorProgression = progression
        self.onSectorProgressionChanged(progression)
        self.__updateProgressionModel()

    def getSectorProgression(self):
        return self.__sectorProgression

    def isOnOwnSector(self):
        return self.__currentSectorID in self.__ownSectors

    def getSectorName(self, sectorID):
        return SECTORS[sectorID - 1] if sectorID and len(SECTORS) >= sectorID else ''

    def __updateProgress(self, progressesInfo):
        for data in progressesInfo.itervalues():
            state = data.get('state', _DEFAULT_STATE)
            value = _DEFAULT_VALUE
            if 'value' in data:
                value = data['value']
            elif 'counter' in data:
                value = len(data['counter'])
            self.__progress = (value, state)
            return

    def __updateProgressionModel(self):
        sectorID, points = self.__sectorProgression
        teamsConfig = self.__metaController.getSectorsProgression().getConfig(sectorID)
        sectorName = self.getSectorName(sectorID)
        if not teamsConfig:
            self.onProgressionModelChanged('', [])
            return
        else:
            progression = []
            isAttacker = BigWorld.player().team == EPIC_BATTLE_TEAM_ID.TEAM_ATTACKER
            cfg = teamsConfig.attackersCfg if isAttacker else teamsConfig.defendersCfg
            prevMilestone = None
            for milestone in cfg.milestones:
                progression.append((milestone.getSupplyTag(), self.getSupplyPercent(prevMilestone, milestone, points)))
                prevMilestone = milestone

            self.onProgressionModelChanged(sectorName, progression)
            return

    @classmethod
    def getPercent(cls, points, goalPoints):
        return min(int(round(float(points) / goalPoints * 100.0)), 100) if goalPoints else 100

    @classmethod
    def getSupplyPercent(cls, prevMilestone, currentMilestone, points):
        if prevMilestone is None:
            return cls.getPercent(points, currentMilestone.points)
        elif points >= prevMilestone.points:
            currentPoints = points - prevMilestone.points
            goalPoints = currentMilestone.points - prevMilestone.points
            return cls.getPercent(currentPoints, goalPoints)
        else:
            return 0
