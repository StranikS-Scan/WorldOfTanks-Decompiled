# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/extensions/football/client/FootballScoreboard.py
import BigWorld
from debug_utils import LOG_ERROR, LOG_CURRENT_EXCEPTION
from gui.battle_control.controllers.football_ctrl import IFootballView
from helpers import dependency
from skeletons.gui.battle_session import IBattleSessionProvider
BLUE_PANEL = 0
RED_PANEL = 1

class FootballScoreboard(BigWorld.Entity, IFootballView):
    sessionProvider = dependency.descriptor(IBattleSessionProvider)

    def __init__(self):
        super(FootballScoreboard, self).__init__(self)
        self.__scoreboardModel = None
        self.__numberPanels = []
        self.__score = {BLUE_PANEL: 0,
         RED_PANEL: 0}
        return

    def prerequisites(self):
        return [self.modelName, self.modelNameBlueDigitPanel, self.modelNameRedDigitPanel]

    def onEnterWorld(self, prereqs):
        try:
            self.__loadModels(prereqs)
        except Exception:
            LOG_CURRENT_EXCEPTION()

        self.__initScoreboard()
        self.sessionProvider.dynamic.footballCtrl.registerEntity(self)

    def onLeaveWorld(self):
        del self.__numberPanels[:]
        self.__scoreboardModel = None
        self.sessionProvider.dynamic.footballCtrl.unregisterEntity(self)
        return

    def updateScore(self, scores, scoreInfo):
        oldBlueScore = self.__score[BLUE_PANEL]
        newBlueScore = scores[1 - BLUE_PANEL]
        oldRedScore = self.__score[RED_PANEL]
        newRedScore = scores[1 - RED_PANEL]
        if oldBlueScore != newBlueScore:
            self.__playDigitAnimation(BLUE_PANEL, newBlueScore)
            self.__score[BLUE_PANEL] = newBlueScore
        if oldRedScore != newRedScore:
            self.__playDigitAnimation(RED_PANEL, newRedScore)
            self.__score[RED_PANEL] = newRedScore

    def __loadModels(self, prereqs):
        firstModel = True
        hpIndex = 0
        for modelName in prereqs.keys():
            if modelName in prereqs.failedIDs:
                LOG_ERROR('Failed to load football scoreboard model: %s' % modelName)
                continue
            model = prereqs[modelName]
            if firstModel:
                firstModel = False
                model.addMotor(BigWorld.Servo(self.matrix))
                model.castsShadow = False
                self.addModel(model)
                self.__scoreboardModel = model
            hardPoint = self.__scoreboardModel.node('HP_module_%d' % hpIndex)
            hardPoint.attach(model)
            hpIndex += 1
            self.__numberPanels.append(model)

    def __playDigitAnimation(self, panel, digitToSwitch):
        try:
            animAction = self.__numberPanels[panel].action('%d_Reveal' % digitToSwitch)
            animAction().action('%d_Displayed' % digitToSwitch)()
        except Exception:
            LOG_CURRENT_EXCEPTION()

    def __initScoreboard(self):
        self.__playDigitAnimation(RED_PANEL, self.__score[RED_PANEL])
        self.__playDigitAnimation(BLUE_PANEL, self.__score[BLUE_PANEL])
