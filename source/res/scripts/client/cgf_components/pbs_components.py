# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/cgf_components/pbs_components.py
import CGF
import GenericComponents
from cgf_script.component_meta_class import registerComponent
from cgf_script.managers_registrator import registerManager, onAddedQuery, registerRule, Rule

@registerComponent
class PostBattleBoardComponent(object):
    editorTitle = 'Post-battle Board Component'
    serialName = 'PostBattleBoardComponent'
    domain = CGF.DomainOption.DomainClient | CGF.DomainOption.DomainEditor


class PostBattleManager(CGF.ComponentManager):
    _boardQuery = CGF.QueryConfig(PostBattleBoardComponent, GenericComponents.DynamicModelComponent)

    def __init__(self, *args):
        super(PostBattleManager, self).__init__(*args)
        self._lastWrittenMapImage = None
        return

    @onAddedQuery(PostBattleBoardComponent, GenericComponents.DynamicModelComponent)
    def onAdded(self, _, dynamicComp):
        if self._lastWrittenMapImage:
            dynamicComp.setMaterialDiffuseMap(self._lastWrittenMapImage)

    def applyArenaImage(self, mapImageName):
        for _, dynamicComp in self._boardQuery:
            dynamicComp.setMaterialDiffuseMap(mapImageName)
            self._lastWrittenMapImage = mapImageName


@registerRule
class PostBattleRule(Rule):
    category = 'Hangar rules'
    domain = CGF.DomainOption.DomainClient

    @registerManager(PostBattleManager)
    def reg1(self):
        return None
