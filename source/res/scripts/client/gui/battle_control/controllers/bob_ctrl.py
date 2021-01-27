# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/battle_control/controllers/bob_ctrl.py
import weakref
import Event
from constants import getArenaStartTime
from gui.battle_control.arena_info import vos_collections
from gui.battle_control.arena_info.interfaces import IArenaVehiclesController
from gui.battle_control.battle_constants import BATTLE_CTRL_ID
from helpers import dependency
from shared_utils import first
from skeletons.gui.game_control import IBobController

class BattleBobController(IArenaVehiclesController):
    bobCtrl = dependency.descriptor(IBobController)

    def __init__(self, setup):
        self.__arenaDP = weakref.proxy(setup.arenaDP)
        self.__arenaVisitor = None
        self.__allySkill = None
        self.__enemySkill = None
        self.__allyBloggerID = 0
        self.__enemyBloggerID = 0
        self.__isInited = False
        self.__eManager = Event.EventManager()
        self.onSkillUpdated = Event.Event(self.__eManager)
        self.onInited = Event.Event(self.__eManager)
        return

    def getControllerID(self):
        return BATTLE_CTRL_ID.BOB_CTRL

    def startControl(self, battleCtx, arenaVisitor):
        self.__arenaVisitor = arenaVisitor

    def stopControl(self):
        self.bobCtrl.teamSkillsRequester.onUpdated -= self.__skillUpdated
        self.__arenaVisitor = None
        self.__eManager.clear()
        return

    def invalidateArenaInfo(self):
        if not self.bobCtrl.teamSkillsRequester.getCache():
            self.bobCtrl.teamSkillsRequester.doForcedRequest(self.__getArenaStartTime())
            self.bobCtrl.teamSkillsRequester.onUpdated += self.__skillUpdated
        self.__makeInitIfNeed()

    def isInited(self):
        return self.__isInited

    def getAllyBloggerID(self):
        return self.__allyBloggerID

    def getEnemyBloggerID(self):
        return self.__enemyBloggerID

    def getAllySkill(self):
        return self.__allySkill

    def getEnemySkill(self):
        return self.__enemySkill

    def __skillUpdated(self):
        if self.__isInited:
            self.__setSkills()
            self.onSkillUpdated()

    def __makeInitIfNeed(self):
        if self.__isInited:
            return
        self.__setBloggerIDs()
        self.__setSkills()
        self.__isInited = True
        self.onInited()

    def __setBloggerIDs(self):
        arenaDP = self.__arenaDP
        self.__allyBloggerID = self.__getBloggerID(vos_collections.AllyItemsCollection().iterator(arenaDP))
        self.__enemyBloggerID = self.__getBloggerID(vos_collections.EnemyItemsCollection().iterator(arenaDP))

    def __getBloggerID(self, vehiclesIterator):
        vehicleVO = first(vehiclesIterator)
        return vehicleVO[0].bobInfo.bloggerID if vehicleVO and vehicleVO[0].bobInfo else 0

    def __setSkills(self):
        if not self.bobCtrl.teamSkillsRequester.getCache():
            return
        self.__allySkill = self.__getSkillByBloggerID(self.__allyBloggerID)
        self.__enemySkill = self.__getSkillByBloggerID(self.__enemyBloggerID)

    def __getSkillByBloggerID(self, bloggerID):
        arenaStartTime = self.__getArenaStartTime()
        skill = self.bobCtrl.teamSkillsRequester.getSkill(bloggerID)
        return skill.skill if skill is not None and skill.isActiveAt(arenaStartTime) else None

    def __getArenaStartTime(self):
        arenaUniqueID = self.__arenaVisitor.getArenaUniqueID()
        return getArenaStartTime(arenaUniqueID)
