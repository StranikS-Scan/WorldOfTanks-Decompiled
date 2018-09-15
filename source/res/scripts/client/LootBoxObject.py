# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/LootBoxObject.py
import BigWorld
import SoundGroups
from debug_utils import LOG_DEBUG
from CustomizableNewYearSceneObject import CustomizableNewYearSceneObject
from functools import partial
from helpers.EffectsList import EffectsListPlayer
import LootBoxReader as lbr

class BoxStates:
    DEFAULT = 'DEFAULT'
    APPEAR = 'APPEAR'
    ON_SCENE = 'ON_SCENE'
    START_OPENING = 'START_OPENING'
    FINISH_OPENING = 'FINISH_OPENING'
    DONE = 'DONE'
    ALL = [DEFAULT,
     APPEAR,
     ON_SCENE,
     START_OPENING,
     FINISH_OPENING,
     DONE]


class LootBoxObject(CustomizableNewYearSceneObject):

    @staticmethod
    def create(position, direction, modelName, anchorName, selectionId, configPath, spaceID):
        entityID = BigWorld.createEntity('LootBoxObject', spaceID, 0, position, direction, {'modelName': modelName,
         'anchorName': anchorName,
         'selectionId': selectionId,
         'configPath': configPath,
         'isSelectable': True})
        return entityID

    @staticmethod
    def destroy(id):
        BigWorld.destroyEntity(id)

    @property
    def state(self):
        return self.__state

    def __init__(self):
        super(LootBoxObject, self).__init__()
        self.__state = None
        self.__states = {}
        self.__onStateChangedCallback = None
        self.__onLeaveWorldCallback = None
        self.__onClickCallBack = None
        self.__effectsPlayers = []
        self.__effectsTimeLine = {}
        return

    def prerequisites(self):
        root = lbr.getRoot(self.configPath)
        if root:
            self.__states = lbr.readStates(root)
            assert all((transition in self.__states for transition in BoxStates.ALL))
            self.__effectsTimeLine = lbr.readEffects(root)
        return super(LootBoxObject, self).prerequisites()

    def onEnterWorld(self, prereqs):
        super(LootBoxObject, self).onEnterWorld(prereqs)
        self.__changeState(BoxStates.DEFAULT)

    def onLeaveWorld(self):
        if self.__onLeaveWorldCallback:
            self.__onLeaveWorldCallback()
        for effect in self.__effectsPlayers:
            effect[1].stop()

        self.__effectsPlayers = None
        super(LootBoxObject, self).onLeaveWorld()
        return

    def onClicked(self):
        super(LootBoxObject, self).onClicked()
        if self.__onClickCallBack:
            self.__onClickCallBack()

    def setOnStateChangedCallback(self, callback):
        self.__onStateChangedCallback = callback

    def setOnLeaveWorldCallback(self, callback):
        self.__onLeaveWorldCallback = callback

    def setOnClickCallback(self, callback):
        self.__onClickCallBack = callback

    def startTransition(self, transition):
        if transition not in self.__states[self.__state].transitions:
            LOG_DEBUG("LootBox can't move from {} to {} state".format(self.__state, transition))
            return False
        animations = self.__states[transition].animation
        if animations:
            self.__playAnimations(animations)
        self.__changeState(transition)
        return True

    def __changeState(self, state):
        stateCfg = self.__states[state]
        self.enable(stateCfg.enable)
        self.model.visible = stateCfg.visible
        self.__playEffect(stateCfg.effects)
        self.__playSound(stateCfg.sound)
        if self.__onStateChangedCallback:
            self.__onStateChangedCallback(self.__state, state)
        self.__state = state

    def __playAnimations(self, animations):
        actionQueuer = self.model
        for animation in animations:
            action = actionQueuer.action(animation.action)
            if action:
                if animation.trigger:
                    callback = partial(self.__changeState, animation.trigger)
                    actionQueuer = action(0.0, callback)
                else:
                    actionQueuer = action()

    def __playEffect(self, effects):
        updatedEffects = []
        for effect in self.__effectsPlayers:
            if effect[0] in effects.keep:
                updatedEffects.append(effect)
            effect[1].stop()

        self.__effectsPlayers = updatedEffects
        newEffectName = effects.effect
        if not newEffectName:
            return
        effect = self.__effectsTimeLine[newEffectName]
        if effect:
            effectPlayer = EffectsListPlayer(effect.effectsList, effect.keyPoints)
            effectPlayer.play(self.model)
            self.__effectsPlayers.append((newEffectName, effectPlayer))

    def __playSound(self, sound):
        if sound:
            SoundGroups.g_instance.playSoundPos(sound, self.position)
