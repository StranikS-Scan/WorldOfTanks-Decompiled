# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/tutorial/data/chapter.py
import operator
from tutorial.data.has_id import HasID, HasTargetID, HasIDAndTarget

class VAR_FINDER_TYPE(object):
    GAME_ATTRIBUTE = 1


class Chapter(HasID):

    def __init__(self, entityID, bonus, forcedLoading, filePath, sharedScene, predefinedVars=None):
        super(Chapter, self).__init__(entityID=entityID)
        self.__bonus = bonus
        self.__forcedLoading = forcedLoading
        self.__filePath = filePath
        self.__sharedScenePath = sharedScene
        self.__initialSceneID = None
        self.__defaultSceneID = None
        self.__scenes = []
        self.__sceneMap = {}
        self.__flags = []
        self.__hasID = {}
        self.__triggers = {}
        self.__varSets = []
        self.__predefinedVars = predefinedVars or []
        self.__effectsPostScene = []
        self.__effectsPreScene = []
        self.__valid = False
        return

    def getBonus(self):
        return self.__bonus

    def getBonusID(self):
        return self.__bonus.getID()

    def hasBonus(self):
        return self.__bonus.getID() > -1

    def ignoreBonus(self, bonusCompleted):
        return not self.hasBonus() or self.__forcedLoading != -1 and self.__forcedLoading & bonusCompleted != 0

    def getBonusMessage(self):
        return self.__bonus.getMessage()

    def isBonusReceived(self, bonusCompleted):
        return 1 << self.__bonus.getID() & bonusCompleted != 0

    def getFilePath(self):
        return self.__filePath

    def getSharedScenePath(self):
        return self.__sharedScenePath

    def setInitialSceneID(self, initialSceneID):
        self.__initialSceneID = initialSceneID

    def setDefaultSceneID(self, defaultSceneID):
        self.__defaultSceneID = defaultSceneID

    def getFlags(self):
        return self.__flags[:]

    def setFlags(self, flags):
        self.__flags = flags

    def addScene(self, scene):
        self.__sceneMap[scene.getID()] = len(self.__scenes)
        self.__scenes.append(scene)

    def getScene(self, sceneID):
        scene = None
        if sceneID in self.__sceneMap:
            scene = self.__scenes[self.__sceneMap[sceneID]]
        elif self.__defaultSceneID in self.__sceneMap:
            scene = self.__scenes[self.__sceneMap[self.__defaultSceneID]]
            scene.setID(sceneID)
        return scene

    def getInitialScene(self):
        initialScene = None
        if self.__initialSceneID in self.__sceneMap:
            initialScene = self.__scenes[self.__sceneMap[self.__initialSceneID]]
        if initialScene is None and self.__scenes:
            initialScene = self.__scenes[0]
        return initialScene

    def isInScene(self, scene, nextSceneID):
        sceneID = scene.getID()
        return True if self.__defaultSceneID is not None and self.__initialSceneID is not None and self.__defaultSceneID == self.__initialSceneID and nextSceneID not in self.__sceneMap else sceneID == nextSceneID

    def addHasIDEntity(self, entity):
        self.__hasID[entity.getID()] = entity

    def getHasIDEntity(self, entityID):
        return self.__hasID.get(entityID)

    def addTrigger(self, trigger):
        self.__triggers[trigger.getID()] = trigger

    def getTrigger(self, triggerID):
        return self.__triggers.get(triggerID)

    def addVarSet(self, varSet):
        self.__varSets.append(varSet)

    def getVarSets(self):
        return self.__varSets + self.__predefinedVars

    def addGlobalEffect(self, effect, isPostScene):
        self.__getEffectsList(isPostScene).append(effect)

    def getGlobalEffects(self, isPostScene):
        return self.__getEffectsList(isPostScene)[:]

    def clear(self):
        self.__valid = False
        self.__flags = []
        self.__varSets = []
        self.__effectsPostScene = []
        self.__effectsPreScene = []
        self.__sceneMap.clear()
        while self.__scenes:
            self.__scenes.pop().clear()

        while self.__hasID:
            _, item = self.__hasID.popitem()
            item.clear()

        while self.__triggers:
            _, item = self.__triggers.popitem()
            item.clear()

    def isValid(self):
        return self.__valid

    def setValid(self, flag):
        self.__valid = flag

    def __getEffectsList(self, isPostScene):
        return self.__effectsPostScene if isPostScene else self.__effectsPreScene


class Scene(HasID):

    def __init__(self, entityID=None):
        super(Scene, self).__init__(entityID=entityID)
        self.__postEffects = []
        self.__effects = []
        self.__guiItems = {}

    def addPostEffect(self, postEffect, front=-1):
        if front > -1:
            self.__postEffects.insert(front, postEffect)
        else:
            self.__postEffects.append(postEffect)

    def getPostEffects(self):
        return self.__postEffects[:]

    def addEffect(self, effect, front=-1):
        if front > -1:
            self.__effects.insert(front, effect)
        else:
            self.__effects.append(effect)

    def getEffects(self):
        return self.__effects[:]

    def addGuiItem(self, item):
        self.__guiItems[item.getTargetID()] = item

    def getGuiItems(self):
        return self.__guiItems.values()

    def getGuiItem(self, targetID):
        if targetID in self.__guiItems:
            item = self.__guiItems[targetID]
        else:
            item = None
        return item

    def clear(self):
        while self.__postEffects:
            self.__postEffects.pop().clear()

        while self.__effects:
            self.__effects.pop().clear()

        while self.__guiItems:
            _, item = self.__guiItems.popitem()
            item.clear()


class Bonus(HasID):

    def __init__(self, entityID, message, values, altValues, conditions):
        super(Bonus, self).__init__(entityID=entityID)
        self.__message = message
        self.__values = values
        self.__altValues = altValues
        self.__altBonusValuesConditions = conditions

    def getMessage(self):
        return self.__message

    def getValues(self):
        return self.__values

    def getAltValues(self):
        return self.__altValues

    def getAltBonusValuesConditions(self):
        return self.__altBonusValuesConditions

    def clear(self):
        self.__altBonusValuesConditions.clear()
        self.__altValues = None
        self.__values = None
        return


class HasIDConditions(HasID):

    def __init__(self, entityID, conditions):
        super(HasIDConditions, self).__init__(entityID=entityID)
        self.__conditions = conditions

    def __repr__(self):
        return 'HasIDConditions({0:s}): {1!r:s}, {2!r:s}'.format(self._id, self.__conditions[:], self.__conditions.eitherBlocks())

    def __iter__(self):
        return iter(self.__conditions)

    def __len__(self):
        return len(self.__conditions)

    def appendEitherBlock(self, block):
        self.__conditions.appendEitherBlock(block)

    def eitherBlocks(self):
        return self.__conditions.eitherBlocks()

    def clear(self):
        self.__conditions.clear()


class Exit(HasID):

    def __init__(self, entityID, nextChapter=None, nextDelay=0, finishDelay=0, isSpeakOver=False):
        super(Exit, self).__init__(entityID=entityID)
        self.__nextChapter = nextChapter
        self.__nextDelay = nextDelay
        self.__finishDelay = finishDelay
        self.__isSpeakOver = isSpeakOver

    def getNextChapter(self):
        return self.__nextChapter

    def getNextDelay(self):
        return self.__nextDelay

    def getFinishDelay(self):
        return self.__finishDelay

    def isSpeakOver(self):
        return self.__isSpeakOver


class Action(HasIDAndTarget):

    def __init__(self, eventType, targetID):
        super(Action, self).__init__(targetID=targetID, entityType=eventType)
        self.__effects = []

    def addEffect(self, effect):
        self.__effects.append(effect)

    def getEffects(self):
        return self.__effects[:]

    def clear(self):
        while self.__effects:
            self.__effects.pop().clear()


class ActionsHolder(HasID):

    def __init__(self, entityID=None, **kwargs):
        super(ActionsHolder, self).__init__(entityID, **kwargs)
        self.__actions = {}

    def addAction(self, action):
        self.__actions[action.getType(), action.getTargetID()] = action

    def removeAction(self, action):
        self.__actions.pop((action.getType(), action.getTargetID()), None)
        return

    def getAction(self, event):
        key = event.getActionCriteria()
        return self.__actions[key] if key in self.__actions else None

    def getActionTypes(self):
        return map(operator.itemgetter(0), self.__actions.keys())

    def getActions(self):
        return self.__actions.values()

    def setActions(self, actions):
        self.__actions = dict((((action.getType(), action.getTargetID()), action) for action in actions))

    def clear(self):
        self.__actions.clear()


class Message(HasID):

    def __init__(self, entityID, guiType, text):
        super(Message, self).__init__(entityID=entityID)
        self.__guiType = guiType
        self.__text = text

    def getGuiType(self):
        return self.__guiType

    def getText(self):
        return self.__text


class SimpleImagePath(HasID):

    def __init__(self, entityID=None, image=''):
        super(SimpleImagePath, self).__init__(entityID=entityID)
        self._image = image

    def getImagePaths(self, varSummary):
        return (self._image, '')


class ChainHint(ActionsHolder, HasTargetID):

    def __init__(self, entityID, targetID, text, hasBox=None, arrow=None, padding=None, hideImmediately=False):
        super(ChainHint, self).__init__(entityID=entityID, targetID=targetID)
        self.__text = text
        self.__hasBox = hasBox
        self.__arrow = arrow
        self.__padding = padding
        self.__hideImmediately = hideImmediately

    def getText(self):
        return self.__text

    def hasBox(self):
        return self.__hasBox

    def getArrow(self):
        return self.__arrow

    def getPadding(self):
        return self.__padding

    def getHideImmediately(self):
        return self.__hideImmediately


class PopUp(ActionsHolder):

    def __init__(self, entityID, popUpType, content, varRef=None, forcedQuery=False):
        super(PopUp, self).__init__(entityID=entityID, entityType=popUpType)
        self.__content = content
        self.__varRef = varRef
        self.__forcedQuery = forcedQuery

    def getContent(self):
        return self.__content.copy()

    def getVarRef(self):
        return self.__varRef

    def isContentFull(self):
        return self.__varRef is None and not self.__forcedQuery


class GuiItemRef(HasTargetID):

    def __init__(self, targetID, conditions=None):
        super(GuiItemRef, self).__init__(targetID=targetID)
        self.__conditions = conditions
        self.__notOnSceneEffects = []
        self.__onSceneEffects = []

    def getConditions(self):
        return self.__conditions

    def addNotOnSceneEffect(self, effect):
        self.__notOnSceneEffects.append(effect)

    def getNotOnSceneEffects(self):
        return self.__notOnSceneEffects[:]

    def addOnSceneEffect(self, effect):
        self.__onSceneEffects.append(effect)

    def getOnSceneEffects(self):
        return self.__onSceneEffects[:]

    def clear(self):
        if self.__conditions is not None:
            self.__conditions.clear()
        while self.__notOnSceneEffects:
            self.__notOnSceneEffects.pop().clear()

        while self.__onSceneEffects:
            self.__onSceneEffects.pop().clear()

        return


class GuiItemCriteria(HasIDAndTarget):

    def __init__(self, entityID, targetID, value):
        super(GuiItemCriteria, self).__init__(entityID=entityID, targetID=targetID)
        self.__value = value

    def getValue(self):
        return self.__value


class GuiItemViewCriteria(HasID):

    def __init__(self, entityID, componentIDs, value):
        super(GuiItemViewCriteria, self).__init__(entityID=entityID)
        self.__componentIDs = componentIDs
        self.__value = value

    def getComponentIDs(self):
        return self.__componentIDs

    def getValue(self):
        return self.__value


class VarSet(HasID):

    def __init__(self, entityID, varSet):
        super(VarSet, self).__init__(entityID=entityID)
        self.__varSet = varSet

    def __iter__(self):
        return iter(self.__varSet)


class GameAttribute(HasIDAndTarget):

    def __init__(self, entityID, name, varID, args=None):
        super(GameAttribute, self).__init__(entityID=entityID, targetID=varID, entityType=VAR_FINDER_TYPE.GAME_ATTRIBUTE)
        self.__name = name
        self.__args = args or ()

    def getName(self):
        return self.__name

    def getArgs(self):
        return self.__args


class LoadViewData(HasID):

    def __init__(self, entityID, alias, scope, ctx):
        super(LoadViewData, self).__init__(entityID=entityID)
        self.__alias = alias
        self.__scope = scope
        self.__ctx = ctx

    def getAlias(self):
        return self.__alias

    def getScope(self):
        return self.__scope

    def getCtx(self):
        return self.__ctx
