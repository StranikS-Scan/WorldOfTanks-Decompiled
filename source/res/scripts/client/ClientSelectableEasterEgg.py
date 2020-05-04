# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/ClientSelectableEasterEgg.py
import BigWorld
import AnimationSequence
from ClientSelectableObject import ClientSelectableObject
from gui import GUI_SETTINGS
from gui.Scaleform.daapi.settings.views import VIEW_ALIAS
from gui.shared import g_eventBus, events
from gui.shared.event_bus import EVENT_BUS_SCOPE
from helpers import dependency
from skeletons.gui.game_control import IBootcampController
from helpers import getClientLanguage
from vehicle_systems.stricted_loading import makeCallbackWeak

class ClientSelectableEasterEgg(ClientSelectableObject):
    bootcampController = dependency.descriptor(IBootcampController)

    def __init__(self):
        super(ClientSelectableEasterEgg, self).__init__()
        self.__animator = None
        if self.bootcampController.isInBootcamp() or not GUI_SETTINGS.easterEgg.enabled:
            self.setEnable(False)
        return

    @property
    def animator(self):
        return self.__animator

    def prerequisites(self):
        prereqs = super(ClientSelectableEasterEgg, self).prerequisites()
        if not prereqs:
            return []
        if self.outlineModelName:
            assembler = BigWorld.CompoundAssembler('outline_model', self.spaceID)
            assembler.addRootPart(self.outlineModelName, 'root')
            prereqs.append(assembler)
        return prereqs

    def _getCollisionModelsPrereqs(self):
        if self.outlineModelName:
            collisionModels = ((0, self.outlineModelName),)
            return collisionModels
        return super(ClientSelectableEasterEgg, self)._getCollisionModelsPrereqs()

    def onEnterWorld(self, prereqs):
        super(ClientSelectableEasterEgg, self).onEnterWorld(prereqs)
        if self.outlineModelName:
            compoundModel = prereqs['outline_model']
            compoundModel.matrix = self.matrix
            self.addModel(compoundModel)
        if self.animationSequence:
            self.__createAnimationSequence(self.animationSequence)

    def onLeaveWorld(self):
        super(ClientSelectableEasterEgg, self).onLeaveWorld()
        if self.__animator is not None:
            self.__animator.stop()
            self.__animator = None
        return

    def onMouseClick(self):
        super(ClientSelectableEasterEgg, self).onMouseClick()
        g_eventBus.handleEvent(events.LoadViewEvent(VIEW_ALIAS.IMAGE_VIEW, ctx={'img': self.__getImageName()}), EVENT_BUS_SCOPE.LOBBY)

    def __getImageName(self):
        nameParts = [self.imageName]
        if self.multiLanguageSupport:
            nameLocalizationSuffix = '_ru' if getClientLanguage() in GUI_SETTINGS.easterEgg.ruLangGroup else '_en'
            nameParts.append(nameLocalizationSuffix)
        nameParts.append('.png')
        return ''.join(nameParts)

    def __createAnimationSequence(self, resourceName):
        loader = AnimationSequence.Loader(resourceName, self.spaceID)
        BigWorld.loadResourceListBG((loader,), makeCallbackWeak(self.__onAnimatorLoaded, resourceName))

    def __onAnimatorLoaded(self, resourceName, resourceList):
        self.__animator = resourceList[resourceName]
        self.__animator.bindTo(AnimationSequence.ModelWrapperContainer(self.model, self.spaceID))
        self.__animator.start()
        self._onAnimatorReady()

    def _onAnimatorReady(self):
        pass

    def _addEdgeDetect(self):
        if self.outlineModelName and self.models:
            compoundModel = self.models[0]
            BigWorld.wgAddEdgeDetectCompoundModel(compoundModel, 0, self.edgeMode)
        else:
            super(ClientSelectableEasterEgg, self)._addEdgeDetect()

    def _delEdgeDetect(self):
        if self.outlineModelName and self.models:
            compoundModel = self.models[0]
            BigWorld.wgDelEdgeDetectCompoundModel(compoundModel)
        else:
            super(ClientSelectableEasterEgg, self)._delEdgeDetect()
