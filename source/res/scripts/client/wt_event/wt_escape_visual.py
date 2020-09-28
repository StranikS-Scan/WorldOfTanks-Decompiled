# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/wt_event/wt_escape_visual.py
import AnimationSequence
import BigWorld
import SoundGroups
from helpers import dependency, newFakeModel
from skeletons.dynamic_objects_cache import IBattleDynamicObjectsCache
from skeletons.gui.battle_session import IBattleSessionProvider
from svarog_script.script_game_object import ScriptGameObject
from vehicle_systems.stricted_loading import makeCallbackWeak

class _ModelBoundEffect(ScriptGameObject):

    def __init__(self, worldID, entityID, modelAnimator, nodeName):
        super(_ModelBoundEffect, self).__init__(worldID)
        self.__animator = modelAnimator
        self.__nodeName = nodeName
        self.__entityID = entityID
        self.__model = newFakeModel()
        self.__animator.bindTo(AnimationSequence.ModelWrapperContainer(self.__model, worldID))
        self.__animator.loopCount = 1

    def activate(self):
        entity = BigWorld.entities.get(self.__entityID)
        if entity is not None:
            node = entity.model.node(self.__nodeName)
            if node is not None:
                node.attach(self.__model)
                self.__animator.subscribe(self.__handleEvent)
        self.__animator.setEnabled(True)
        self.__animator.start()
        super(_ModelBoundEffect, self).activate()
        return

    def deactivate(self):
        if self.__model is not None and self.__model.attached:
            entity = BigWorld.entities.get(self.__entityID)
            if entity is not None:
                node = entity.model.node(self.__nodeName)
                if node is not None:
                    node.detach(self.__model)
            self.__animator.unsubscribe(self.__handleEvent)
        self.__animator.stop()
        super(_ModelBoundEffect, self).deactivate()
        return

    def destroy(self):
        self.__animator = None
        self.__model = None
        super(_ModelBoundEffect, self).destroy()
        return

    def __handleEvent(self, eventName, _):
        if eventName == 'hidden':
            vehicle = BigWorld.entities.get(self.__entityID)
            if vehicle is not None:
                vehicle.show(False)
                vehicle.appearance.clearCustomAnimators()
        return


class WtEscapeComponent(ScriptGameObject):
    __dynObjectsCache = dependency.descriptor(IBattleDynamicObjectsCache)
    __sessionProvider = dependency.descriptor(IBattleSessionProvider)

    def __init__(self, worldID, entityID):
        super(WtEscapeComponent, self).__init__(worldID)
        self.__entityID = entityID
        self.__modelAnimators = {}
        effectDescr = self.__effectDescriptor()
        if effectDescr is not None:
            BigWorld.loadResourceListBG((AnimationSequence.Loader(effectDescr.turret.path, worldID), AnimationSequence.Loader(effectDescr.hull.path, worldID)), makeCallbackWeak(self.__onResourcesLoaded))
        return

    def destroy(self):
        self.__modelAnimators = None
        super(WtEscapeComponent, self).destroy()
        return

    def startVisual(self):
        self.__startVisual()

    def __onResourcesLoaded(self, resourceRefs):
        self.__prepareAnimator('turret', self.__effectDescriptor().turret.path, resourceRefs)
        self.__prepareAnimator('hull', self.__effectDescriptor().hull.path, resourceRefs)

    def __startVisual(self):
        self.__addComponent('turret')
        self.__addComponent('hull')
        vehicle = BigWorld.entities.get(self.__entityID)
        if vehicle is not None:
            if BigWorld.player().playerVehicleID == self.__entityID:
                SoundGroups.g_instance.playSoundPos('ev_white_tiger_wt_escape_pc', vehicle.position)
            else:
                SoundGroups.g_instance.playSoundPos('ev_white_tiger_wt_escape_npc', vehicle.position)
        return

    def __prepareAnimator(self, node, path, resourceRefs):
        if path not in resourceRefs.failedIDs:
            modelAnimator = resourceRefs[path]
            self.__modelAnimators[node] = modelAnimator
            modelAnimator.setEnabled(False)

    def __addComponent(self, nodeName):
        if nodeName not in self.__modelAnimators:
            return
        modelAnimator = self.__modelAnimators.pop(nodeName)
        wrapper = _ModelBoundEffect(self.worldID, self.__entityID, modelAnimator, nodeName)
        self.addComponent(wrapper)

    def __effectDescriptor(self):
        arenaGuiType = self.__sessionProvider.arenaVisitor.getArenaGuiType()
        return self.__dynObjectsCache.getConfig(arenaGuiType).escapeEffect
