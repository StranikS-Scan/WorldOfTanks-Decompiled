# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/ClientSelectableEasterEgg.py
import BigWorld
import AnimationSequence
import ResMgr
from ClientSelectableObject import ClientSelectableObject
from gui import GUI_SETTINGS
from gui.Scaleform.daapi.settings.views import VIEW_ALIAS
from gui.shared import g_eventBus, events
from gui.shared.event_bus import EVENT_BUS_SCOPE
from helpers import dependency
from skeletons.gui.game_control import IBootcampController
from helpers import getClientLanguage
from vehicle_systems.stricted_loading import makeCallbackWeak
_VIEW_SOUNDS_XML_PATH = 'scripts/item_defs/easter_egg_sound_config.xml'

class ClientSelectableEasterEgg(ClientSelectableObject):
    bootcampController = dependency.descriptor(IBootcampController)

    def __init__(self):
        super(ClientSelectableEasterEgg, self).__init__()
        self.__animator = None
        self.__viewSounds = None
        if self.bootcampController.isInBootcamp() or not GUI_SETTINGS.easterEgg.enabled:
            self.setEnable(False)
        return

    def prerequisites(self):
        self.__readViewSoundSettings()
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
        self.__viewSounds = None
        return

    def onMouseClick(self):
        super(ClientSelectableEasterEgg, self).onMouseClick()
        g_eventBus.handleEvent(events.LoadViewEvent(VIEW_ALIAS.IMAGE_VIEW, ctx={'img': self.__getImageName(),
         'soundConfig': self.__viewSounds}), EVENT_BUS_SCOPE.LOBBY)

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
        self.__animator.bindTo(AnimationSequence.ModelWrapperContainer(self.model))
        self.__animator.start()

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

    def __readViewSoundSettings(self):
        self.__viewSounds = {}
        if not self.viewSoundConfig:
            return
        else:
            section = ResMgr.openSection(_VIEW_SOUNDS_XML_PATH)
            if section is None or not section.has_key(self.viewSoundConfig):
                return
            for action, soundConfig in section[self.viewSoundConfig].items():
                self.__viewSounds[action] = {}
                for soundAction, value in soundConfig.items():
                    if soundAction == 'event':
                        self.__viewSounds[action][soundAction] = value.asString
                    if soundAction == 'state':
                        self.__viewSounds[action][soundAction] = [value.readString('group'), value.asString]

            return
