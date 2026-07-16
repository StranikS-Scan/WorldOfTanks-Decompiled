# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/cgf_components/pbs_components.py
from __future__ import absolute_import
import CGF
import GenericComponents
from cgf_script.registration import registerComponent

@registerComponent
class PostBattleBoardComponent(object):
    editorTitle = 'Post-battle Board'
    serialName = 'PostBattleBoardComponent'
    domain = CGF.Domain.ClientEditor


class PostBattleSystem(CGF.System):
    PostBattleActivated = CGF.ActivateReaction(CGF.ReactRw(PostBattleBoardComponent), CGF.Rw(GenericComponents.DynamicModelComponent))
    PostBattleIterate = CGF.IterateReaction(CGF.ActiveOnly, CGF.Rw(GenericComponents.DynamicModelComponent), CGF.Has(PostBattleBoardComponent))
    Reactions = CGF.Reactions(PostBattleActivated, PostBattleIterate)

    def update(self):
        for _, dynamicComp in self.reaction(self.PostBattleActivated):
            self.onAdded(dynamicComp)

    def __init__(self, *args):
        super(PostBattleSystem, self).__init__(*args)
        self._lastWrittenMapImage = None
        return

    def onAdded(self, dynamicComp):
        if self._lastWrittenMapImage:
            dynamicComp.setMaterialDiffuseMap(self._lastWrittenMapImage)

    def applyArenaImage(self, mapImageName):
        self._lastWrittenMapImage = mapImageName
        postBattleIterate = self.reaction(self.PostBattleIterate)
        for dynamicComp in postBattleIterate:
            dynamicComp.setMaterialDiffuseMap(mapImageName)
