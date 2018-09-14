# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/AnimatedGiftBox.py
from ClientSelectableCameraObject import ClientSelectableCameraObject
from christmas_shared import CHRISTMAS_TOOLTIPS_IDS
from helpers.EffectsList import effectsFromSection, EffectsListPlayer
import ResMgr
import SoundGroups

class AnimatedGiftBox(ClientSelectableCameraObject):

    class BoxState:
        HIDDEN = 0
        APPEARANCE = 1
        ON_SCENE = 2
        WAITING_FOR_OPEN_RESPONSE = 3
        OPENING = 4
        DONE = 5

    def __init__(self):
        super(AnimatedGiftBox, self).__init__()
        self.__boxState = self.BoxState.HIDDEN
        self.__effectsTimeLine = None
        self.__effectsPlayers = []
        self.__readEffects()
        self.__appearanceFinishedCallback = None
        self.__openingFinishedCallback = None
        return

    def getState(self):
        return self.__boxState

    def tooltipID(self):
        return CHRISTMAS_TOOLTIPS_IDS.GIFT

    def __readEffects(self):
        self.__effectsTimeLine = dict()
        from ChristmassTree import _CHRISTMASS_CONFIG_FILE
        configSection = ResMgr.openSection(_CHRISTMASS_CONFIG_FILE)
        if configSection is not None:
            effects = configSection['boxEffects']
            if effects is not None:
                for effect in effects.values():
                    name = effect.name
                    self.__effectsTimeLine[name] = effectsFromSection(effect)

        return

    def __updateEffect(self, newEffectName, keepEffects=()):
        updatedEffects = []
        for effect in self.__effectsPlayers:
            if effect[0] in keepEffects:
                updatedEffects.append(effect)
            effect[1].stop()

        self.__effectsPlayers = updatedEffects
        if newEffectName is None:
            return
        else:
            effect = self.__effectsTimeLine[newEffectName]
            if effect is not None:
                effectPlayer = EffectsListPlayer(effect.effectsList, effect.keyPoints)
                effectPlayer.play(self.model)
                self.__effectsPlayers.append((newEffectName, effectPlayer))
            return

    def __playAnimationWithCallBack(self, actionName, callback=None):
        if actionName == '':
            return
        else:
            action = self.model.action(actionName)
            if action is not None:
                action(0, callback)
            return

    def onEnterWorld(self, prereqs):
        super(AnimatedGiftBox, self).onEnterWorld(prereqs)
        import ChristmassTreeManager
        ChristmassTreeManager.g_christMassManager.setPart(self, ChristmassTreeManager.GIFT)
        self.setState(self.__boxState)

    def onLeaveWorld(self):
        for effect in self.__effectsPlayers:
            effect[1].stop()

        self.__effectsPlayers = None
        super(AnimatedGiftBox, self).onLeaveWorld()
        import ChristmassTreeManager
        ChristmassTreeManager.g_christMassManager.removePart(ChristmassTreeManager.GIFT)
        return

    def setState(self, newState, callback=None):
        if newState == self.BoxState.HIDDEN:
            self.__hideAndDisable()
        elif newState == self.BoxState.APPEARANCE:
            self.__startAppearance(callback)
        elif newState == self.BoxState.ON_SCENE:
            self.__showAndEnable()
        elif newState == self.BoxState.WAITING_FOR_OPEN_RESPONSE:
            self.__startWaitForOpening()
        elif newState == self.BoxState.OPENING:
            self.__startOpening(callback)
        elif newState == self.BoxState.DONE:
            self.__startDone()
        self.__boxState = newState

    def __hideAndDisable(self):
        self.enable(False)
        self.model.visible = False
        self.__updateEffect(None)
        return

    def __showAndEnable(self):
        self.enable(True)
        self.model.visible = True
        self.__updateEffect(self.effect_on_scene)
        SoundGroups.g_instance.playSoundPos('ev_christmas_tree_giftBox_in_place', self.position)

    def __startAppearance(self, callback):
        self.enable(True)
        self.model.visible = True
        self.__appearanceFinishedCallback = callback
        self.__playAnimationWithCallBack(self.animation_appearance, self.__finishAppearance)
        self.__updateEffect(self.effect_appearance)
        SoundGroups.g_instance.playSoundPos('ev_christmas_tree_giftBox_appear', self.position)

    def __finishAppearance(self):
        if self.__boxState == self.BoxState.APPEARANCE:
            self.setState(self.BoxState.ON_SCENE)
            if self.__appearanceFinishedCallback is not None:
                self.__appearanceFinishedCallback()
        self.__appearanceFinishedCallback = None
        return

    def __startWaitForOpening(self):
        self.enable(False)
        self.model.visible = True
        self.__playAnimationWithCallBack(self.animation_wait)
        self.__updateEffect(self.effect_wait, (self.effect_on_scene,))
        SoundGroups.g_instance.playSoundPos('ev_christmas_tree_giftBox_open_click', self.position)

    def __startOpening(self, callback):
        self.enable(False)
        self.model.visible = True
        self.__openingFinishedCallback = callback
        self.__playAnimationWithCallBack(self.animation_opening, self.__finishOpening)
        self.__updateEffect(self.effect_opening, (self.effect_on_scene,))
        SoundGroups.g_instance.playSoundPos('ev_christmas_tree_giftBox_open', self.position)

    def __finishOpening(self):
        if self.__boxState == self.BoxState.OPENING:
            self.setState(self.BoxState.DONE)
            if self.__openingFinishedCallback is not None:
                self.__openingFinishedCallback()
        self.__openingFinishedCallback = None
        return

    def __startDone(self):
        self.enable(False)
        self.model.visible = True
        self.__playAnimationWithCallBack(self.animation_done)
        self.__updateEffect(None, (self.effect_on_scene, self.effect_opening))
        return

    def onSelect(self, callback=None):
        super(AnimatedGiftBox, self).onSelect(callback)
        self.enable(True)
