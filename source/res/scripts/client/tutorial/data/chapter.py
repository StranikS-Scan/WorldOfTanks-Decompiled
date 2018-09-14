# Embedded file name: scripts/client/tutorial/data/chapter.py
import types
from TriggersManager import TRIGGER_TYPE
from tutorial.data import HasID, HasTargetID, HasIDAndTarget

class Chapter(HasID):

    def __init__(self, entityID, title, descriptions, bonus, forcedLoading, filePaths, sharedScene):
        super(Chapter, self).__init__(entityID=entityID)
        self.__title = title
        self.__descriptions = descriptions
        self.__bonus = bonus
        self.__forcedLoading = forcedLoading
        self.__filePaths = filePaths
        self.__sharedScenePath = sharedScene
        self.__initialSceneID = None
        self.__defaultSceneID = None
        self.__scenes = []
        self.__sceneMap = {}
        self.__flags = []
        self.__hasID = {}
        self.__triggers = {}
        self.__varSets = []
        self.__valid = False
        return

    def getTitle(self):
        return self.__title

    def getDescription(self, afterBattle = False):
        return self.__descriptions[1 if afterBattle else 0]

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

    def getFilePath(self, afterBattle = False):
        return self.__filePaths[1 if afterBattle else 0]

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
        if initialScene is None and len(self.__scenes):
            initialScene = self.__scenes[0]
        return initialScene

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
        return self.__varSets[:]

    def clear(self):
        self.__valid = False
        self.__flags = []
        self.__varSets = []
        self.__sceneMap.clear()
        while len(self.__scenes):
            self.__scenes.pop().clear()

        while len(self.__hasID):
            _, item = self.__hasID.popitem()
            item.clear()

        while len(self.__triggers):
            _, item = self.__triggers.popitem()
            item.clear()

    def isValid(self):
        return self.__valid

    def setValid(self, flag):
        self.__valid = flag


class Scene(HasID):

    def __init__(self, entityID = None):
        super(Scene, self).__init__(entityID=entityID)
        self.__postEffects = []
        self.__guiItems = []
        self.__effects = []

    def addPostEffect(self, postEffect, front = -1):
        if front > -1:
            self.__postEffects.insert(front, postEffect)
        else:
            self.__postEffects.append(postEffect)

    def getPostEffects(self):
        return self.__postEffects[:]

    def addEffect(self, effect, front = -1):
        if front > -1:
            self.__effects.insert(front, effect)
        else:
            self.__effects.append(effect)

    def getEffects(self):
        return self.__effects[:]

    def addGuiItem(self, item):
        self.__guiItems.append(item)

    def getGuiItems(self):
        return self.__guiItems[:]

    def clear(self):
        while len(self.__postEffects):
            self.__postEffects.pop().clear()

        while len(self.__guiItems):
            self.__guiItems.pop().clear()

        while len(self.__effects):
            self.__effects.pop().clear()


class Bonus(HasID):

    def __init__(self, entityID, message, values):
        super(Bonus, self).__init__(entityID=entityID)
        self.__message = message
        self.__values = values

    def getMessage(self):
        return self.__message

    def getValues(self):
        return self.__values


class Effect(object):
    ACTIVATE, DEACTIVATE, GLOBAL_ACTIVATE, GLOBAL_DEACTIVATE, SHOW_HINT, CLOSE_HINT, SHOW_DIALOG, SHOW_WINDOW, CLOSE_WINDOW, SHOW_GREETING, REFUSE_TRAINING, NEXT_CHAPTER, RUN_TRIGGER, REQUEST_BONUS, REQUEST_ALL_BONUSES, SET_ITEM_PROPS, FINISH_TRAINING, DEFINE_GUI_ITEM, INVOKE_GUI_CMD, SET_FILTER, SHOW_MESSAGE, SHOW_MARKER, REMOVE_MARKER, NEXT_TASK, INVOKE_PLAYER_CMD, TELEPORT, ENTER_QUEUE, EXIT_QUEUE, ENABLE_CAMERA_ZOOM, DISABLE_CAMERA_ZOOM, PLAY_MUSIC, OPEN_INTERNAL_BROWSER = range(0, 32)

    def __init__(self, conditions = None, **kwargs):
        super(Effect, self).__init__(**kwargs)
        self.__conditions = conditions

    def getType(self):
        raise NotImplementedError, 'Effect.getType not implemented'

    def getConditions(self):
        return self.__conditions

    def clear(self):
        if self.__conditions is not None:
            self.__conditions.clear()
        self.__conditions = None
        return


EFFECT_TYPE_NAMES = dict([ (v, k) for k, v in Effect.__dict__.iteritems() if k.isupper() ])

class SimpleEffect(Effect):

    def __init__(self, effectType, conditions = None, **kwargs):
        super(SimpleEffect, self).__init__(conditions=conditions, **kwargs)
        self.__type = effectType

    def __repr__(self):
        return 'SimpleEffect(type = {0!r:s})'.format(EFFECT_TYPE_NAMES.get(self.__type))

    def getType(self):
        return self.__type


class HasTargetEffect(SimpleEffect, HasTargetID):

    def __init__(self, targetID, effectType, conditions = None):
        super(HasTargetEffect, self).__init__(effectType, conditions=conditions, targetID=targetID)

    def __repr__(self):
        return 'HasTargetEffect(type = {0!r:s}, targetID = {1:>s})'.format(EFFECT_TYPE_NAMES.get(self.getType()), self.getTargetID())


class DefineGuiItemEffect(HasTargetEffect):

    def __init__(self, targetID, effectType, parentRef, extraRef, conditions = None):
        super(DefineGuiItemEffect, self).__init__(targetID, effectType, conditions=conditions)
        self.__parentRef = parentRef
        self.__extraRef = extraRef

    def __repr__(self):
        return ('HasTargetEffect(type = {0!r:s}, targetID = {1:>s}, ' + 'parent = {2:>s}, extra-ref = {3:>s}').format(EFFECT_TYPE_NAMES.get(self.getType()), self.getTargetID(), self.__parentRef, self.__extraRef)

    def getParentReference(self):
        return self.__parentRef

    def getExtraReference(self):
        return self.__extraRef


class SetGuiItemProperty(HasTargetEffect):

    def __init__(self, targetID, props, conditions = None, revert = False):
        super(SetGuiItemProperty, self).__init__(targetID, Effect.SET_ITEM_PROPS, conditions=conditions)
        self.__props = props
        self.__revert = revert

    def getProps(self):
        return self.__props.copy()

    def isRevert(self):
        return self.__revert

    def clear(self):
        super(SetGuiItemProperty, self).clear()
        self.__props.clear()


class SetFilter(HasTargetEffect):

    def __init__(self, targetID, value, conditions = None):
        super(SetFilter, self).__init__(targetID, Effect.SET_FILTER, conditions=conditions)
        self.__value = value

    def getValue(self):
        return self.__value[:]


class Conditions(list):

    def __init__(self, *args):
        list.__init__(self, *args)
        self._eitherBlocks = []

    def __repr__(self):
        return 'Conditions({0:s}): {1!r:s}, {2!r:s}'.format(hex(id(self)), self[:], self._eitherBlocks)

    def appendEitherBlock(self, block):
        self._eitherBlocks.append(block)

    def eitherBlocks(self):
        return self._eitherBlocks[:]

    def clear(self):
        while len(self._eitherBlocks):
            self._eitherBlocks.pop()

        while len(self):
            self.pop()


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


class Condition(HasID):
    FLAG_CONDITION = 0
    GLOBAL_FLAG_CONDITION = 1
    WINDOW_ON_SCENE_CONDITION = 2
    VEHICLE_CONDITION = 3

    def __init__(self, condType, entityID):
        super(Condition, self).__init__(entityID=entityID)
        self._type = condType

    def getType(self):
        return self._type


class FlagCondition(Condition):
    FLAG_ACTIVE = 0
    FLAG_INACTIVE = 1

    def __init__(self, entityID, state = 0, condType = Condition.FLAG_CONDITION):
        super(FlagCondition, self).__init__(condType, entityID)
        self._state = state

    def isActiveState(self):
        return self._state == FlagCondition.FLAG_ACTIVE

    def isInactiveState(self):
        return self._state == FlagCondition.FLAG_INACTIVE


class VehicleCondition(Condition):
    CV_TYPE_NAME = 0

    def __init__(self, varID, value):
        super(VehicleCondition, self).__init__(Condition.VEHICLE_CONDITION, varID)
        self._value = value

    def isValueEqual(self, other):
        return self._value == other


class Exit(HasID):

    def __init__(self, entityID, nextChapter = None, nextDelay = 0, finishDelay = 0, isSpeakOver = False):
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


class Message(HasID):

    def __init__(self, entityID, guiType, text):
        super(Message, self).__init__(entityID=entityID)
        self.__guiType = guiType
        self.__text = text

    def getGuiType(self):
        return self.__guiType

    def getText(self):
        return self.__text


class Query(HasID):

    def __init__(self, entityID, queryType, varRef, extra = None):
        super(Query, self).__init__(entityID=entityID)
        self.__type = queryType
        self.__varRef = varRef
        self.__extra = extra

    def getType(self):
        return self.__type

    def getVarRef(self):
        return self.__varRef

    def getExtra(self):
        return self.__extra


class SimpleImagePath(HasID):

    def __init__(self, entityID = None, image = ''):
        super(SimpleImagePath, self).__init__(entityID=entityID)
        self._image = image

    def getImagePaths(self, varSummary):
        return (self._image, '')


class VehicleImagePath(SimpleImagePath):

    def __init__(self, entityID, image, path, default):
        super(VehicleImagePath, self).__init__(entityID=entityID, image=image)
        self._pathRef = path
        self._defaultRef = default

    def getImagePaths(self, varSummary):
        path = varSummary.get(self._pathRef)
        originPath = []
        altPath = []
        if path and len(path):
            originPath.append(path)
            altPath.append(path)
        else:
            return (self._image, self._image)
        default = varSummary.get(self._defaultRef)
        if default and len(default):
            from tutorial.control.context import GLOBAL_VAR, GlobalStorage
            vehTypeName = GlobalStorage(GLOBAL_VAR.PLAYER_VEHICLE_NAME, default).value()
            if vehTypeName and default != vehTypeName:
                originPath.append(vehTypeName.replace(':', '_'))
        originPath.append(self._image)
        altPath.append(self._image)
        if originPath != altPath:
            result = ('/'.join(originPath), '/'.join(altPath))
        else:
            result = ('/'.join(originPath), '')
        return result


class SimpleHint(HasID):

    def __init__(self, entityID, text, image, speakID = None):
        super(SimpleHint, self).__init__(entityID=entityID)
        self.__text = text
        self.__image = image
        self.__speakID = speakID

    def getText(self):
        return self.__text

    def getImage(self):
        return self.__image

    def hasImageRef(self):
        return type(self.__image) is types.StringType

    def getSpeakID(self):
        return self.__speakID


class Greeting(HasID):

    def __init__(self, entityID, title, text, speakID = None):
        super(Greeting, self).__init__(entityID=entityID)
        self.__title = title
        self.__text = text
        self.__speakID = speakID

    def getData(self):
        return [self._id, self.__title, self.__text]

    def getSpeakID(self):
        return self.__speakID


class ItemHint(HasIDAndTarget):

    def __init__(self, entityID, targetID, containerID, position, text, inPin, outPin, line, topmostLevel):
        super(ItemHint, self).__init__(entityID=entityID, targetID=targetID)
        self.__containerID = containerID
        self.__position = position
        self.__text = text
        self.__inPin = inPin
        self.__outPin = outPin
        self.__line = line
        self.__topmostLevel = topmostLevel

    def getContainerID(self):
        return self.__containerID

    def setContainerID(self, containerID):
        self.__containerID = containerID

    def getData(self):
        return [self._id,
         self.__position[0],
         self.__position[1],
         self.__text,
         self.__inPin,
         self.__outPin,
         self.__line,
         self.__topmostLevel]


class PopUp(HasID):

    def __init__(self, entityID, popUpType, content):
        super(PopUp, self).__init__(entityID=entityID)
        self.__type = popUpType
        self.__content = content
        self.__actions = {}

    def getType(self):
        return self.__type

    def getContent(self):
        return self.__content.copy()

    def isContentFull(self):
        return True

    def addAction(self, action):
        self.__actions[action.getTargetID()] = action

    def getAction(self, targetID):
        return self.__actions.get(targetID)

    def getActions(self):
        return self.__actions.values()

    def setActions(self, actions):
        self.__actions = dict(map(lambda action: (action.getTargetID(), action), actions))

    def clear(self):
        while len(self.__actions):
            _, action = self.__actions.popitem()
            action.clear()


class VarRefPopUp(PopUp):

    def __init__(self, entityID, popUpType, content, varRef):
        super(VarRefPopUp, self).__init__(entityID, popUpType, content)
        self.__varRef = varRef

    def getVarRef(self):
        return self.__varRef

    def isContentFull(self):
        return False


class Action(HasTargetID):
    PRESS = 0
    CLICK = 1
    CLICK_POINT = 2
    CLOSE = 3
    CHANGE = 4
    CLICK_ITEM = 5
    PRESS_ITEM = 6
    CHANGE_TEXT = 7

    def __init__(self, actionType, targetID):
        super(Action, self).__init__(targetID=targetID)
        self.__type = actionType
        self.__effects = []

    def getType(self):
        return self.__type

    def addEffect(self, effect):
        self.__effects.append(effect)

    def getEffects(self):
        return self.__effects[:]

    def clear(self):
        while len(self.__effects):
            self.__effects.pop().clear()


class GuiItemRef(HasTargetID):
    LIFE_CYCLE_PERMANENT = 0
    LIFE_CYCLE_DYNAMIC = 1

    def __init__(self, targetID, props, conditions = None):
        super(GuiItemRef, self).__init__(targetID=targetID)
        self.__props = props
        self.__conditions = conditions

    def getProps(self):
        return self.__props.copy()

    def getLifeCycle(self):
        raise NotImplementedError, 'GuiItemRef.getLifeCycle not implemented'

    def getConditions(self):
        return self.__conditions

    def clear(self):
        self.__props.clear()
        if self.__conditions is not None:
            self.__conditions.clear()
        self.__conditions = None
        return


class PermanentGuiItemRef(GuiItemRef):

    def getLifeCycle(self):
        return GuiItemRef.LIFE_CYCLE_PERMANENT


class DynamicGuiItemRef(GuiItemRef):

    def __init__(self, targetID, props, conditions = None):
        super(DynamicGuiItemRef, self).__init__(targetID, props, conditions)
        self.__findCriteria = None
        self.__notOnSceneEffects = []
        self.__onSceneEffects = []
        return

    def getLifeCycle(self):
        return GuiItemRef.LIFE_CYCLE_DYNAMIC

    def addNotOnSceneEffect(self, effect):
        self.__notOnSceneEffects.append(effect)

    def getNotOnSceneEffects(self):
        return self.__notOnSceneEffects[:]

    def addOnSceneEffect(self, effect):
        self.__onSceneEffects.append(effect)

    def getOnSceneEffects(self):
        return self.__onSceneEffects[:]

    def setFindCriteria(self, criteria):
        self.__findCriteria = criteria

    def getFindCriteria(self):
        if self.__findCriteria:
            return self.__findCriteria[:]
        else:
            return None

    def clear(self):
        super(DynamicGuiItemRef, self).clear()
        self.__findCriteria = None
        while len(self.__notOnSceneEffects):
            self.__notOnSceneEffects.pop().clear()

        while len(self.__onSceneEffects):
            self.__onSceneEffects.pop().clear()

        return


class PlayerCommand(HasID):

    def __init__(self, entityID, name, cmdArgs = None, cmdKwargs = None):
        super(PlayerCommand, self).__init__(entityID=entityID)
        self.__name = name
        if cmdArgs is None:
            cmdArgs = tuple()
        self.__args = cmdArgs
        if cmdKwargs is None:
            cmdKwargs = {}
        self.__kwargs = cmdKwargs
        return

    def getName(self):
        return self.__name

    def args(self):
        return self.__args[:]

    def kwargs(self):
        return self.__kwargs.copy()


class EntityMarker(HasID):

    def __init__(self, entityID, varRef, createInd = True):
        super(EntityMarker, self).__init__(entityID=entityID)
        self.__varRef = varRef
        self.__createInd = createInd

    def getTypeID(self):
        raise NotImplementedError, 'EntityMarker.getTypeID not implemented'

    def getVarRef(self):
        return self.__varRef

    def isIndicatorCreate(self):
        return self.__createInd


class AimMarker(EntityMarker):

    def __init__(self, entityID, varRef, modelData, worldData, createInd = True):
        super(AimMarker, self).__init__(entityID, varRef, createInd=createInd)
        self.__modelData = modelData
        self.__worldData = worldData

    def getTypeID(self):
        return TRIGGER_TYPE.AIM

    def getModelData(self):
        return self.__modelData

    def getWorldData(self):
        return self.__worldData


class AreaMarker(AimMarker):

    def __init__(self, entityID, varRef, modelData, groundData, worldData, minimapData, createInd = True):
        super(AreaMarker, self).__init__(entityID, varRef, modelData, worldData, createInd=createInd)
        self.__groundData = groundData
        self.__minimapData = minimapData

    def getTypeID(self):
        return TRIGGER_TYPE.AREA

    def getGroundData(self):
        return self.__groundData

    def getMinimapData(self):
        return self.__minimapData


class VehicleMarker(EntityMarker):

    def __init__(self, entityID, varRef, period, createInd = True):
        super(VehicleMarker, self).__init__(entityID, varRef, createInd=createInd)
        self.__period = period

    def getTypeID(self):
        return TRIGGER_TYPE.AIM_AT_VEHICLE

    def getPeriod(self):
        return self.__period


class ChapterTask(HasID):

    def __init__(self, entityID, text, flagID = None):
        super(ChapterTask, self).__init__(entityID=entityID)
        self.__text = text
        self.__flagID = flagID

    def getText(self):
        return self.__text

    def getFlagID(self):
        return self.__flagID


class ChapterProgress(HasID):
    PROGRESS_FLAG_UNDEFINED = 0
    PROGRESS_FLAG_FAILED = 1
    PROGRESS_FLAG_COMPLETED = 3

    def __init__(self, entityID, conditions):
        super(ChapterProgress, self).__init__(entityID=entityID)
        self.__conditions = conditions

    def __iter__(self):
        return iter(self.__conditions)


class VarSet(HasID):

    def __init__(self, entityID, varSet):
        super(VarSet, self).__init__(entityID=entityID)
        self.__varSet = varSet

    def __iter__(self):
        return iter(self.__varSet)
