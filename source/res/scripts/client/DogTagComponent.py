# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/DogTagComponent.py
import logging
import BigWorld
_logger = logging.getLogger(__name__)

class DogTagComponent(BigWorld.DynamicScriptComponent):

    def set_killerDogTag(self, old):
        _logger.info('DogTagComponent.set_killerDogTag: killerDogTag %s', str(self.killerDogTag))
        dogTagsCtrl = self.entity.guiSessionProvider.dynamic.dogTags
        if dogTagsCtrl is not None:
            dogTagsCtrl.setKillerDogTag(self.killerDogTag)
        return

    def setSlice_victimsDogTags(self, changePath, oldValue):
        _logger.info('DogTagComponent.setSlice_victimsDogTags: victimsDogTags %s, changePath %s', str(self.victimsDogTags), str(changePath))
        dogTagsCtrl = self.entity.guiSessionProvider.dynamic.dogTags
        if dogTagsCtrl is not None:
            begin, end = changePath[0]
            newVictimsDogTags = self.victimsDogTags[begin:end]
            dogTagsCtrl.setVictimsDogTags(newVictimsDogTags)
        return
