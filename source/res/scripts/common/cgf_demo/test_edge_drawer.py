# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/common/cgf_demo/test_edge_drawer.py
import CGF
import Triggers
from cgf_demo.demo_category import DEMO_CATEGORY
from cgf_script.component_meta_class import ComponentProperty, CGFMetaTypes, registerComponent
from cgf_script.managers_registrator import onAddedQuery, onRemovedQuery, autoregister, onProcessQuery
from EdgeDrawer import HighlightComponent

class _Stage(object):
    Empty = 0
    Ally = 1
    Enemy = 2


@registerComponent
class TestEdgeDrawerComponent(object):
    category = DEMO_CATEGORY
    domain = CGF.DomainOption.DomainClient | CGF.DomainOption.DomainEditor

    def __init__(self):
        super(TestEdgeDrawerComponent, self).__init__()
        self.callbackID = None
        return


class TestEdgeDrawerComponentManager(CGF.ComponentManager):
    _ALLY_COLOR = 2
    _ENEMY_COLOR = 1

    @onAddedQuery(TestEdgeDrawerComponent, Triggers.TimeTriggerComponent)
    def onAdded(self, testComponent, trigger):
        testComponent.callbackID = trigger.addFireReaction(self.__triggerReaction)

    @onRemovedQuery(TestEdgeDrawerComponent, Triggers.TimeTriggerComponent)
    def onRemoved(self, testComponent, trigger):
        if testComponent.callbackID is not None:
            trigger.removeFireReaction(testComponent.callbackID)
        return

    def __triggerReaction(self, gameObject):
        if not gameObject.isValid():
            return
        else:
            stage = _Stage.Empty
            highlighter = gameObject.findComponentByType(HighlightComponent)
            if highlighter is not None:
                if highlighter.colorIndex == self._ALLY_COLOR:
                    stage = _Stage.Ally
                elif highlighter.colorIndex == self._ENEMY_COLOR:
                    stage = _Stage.Enemy
                gameObject.removeComponentByType(HighlightComponent)
            self.__switchStage(stage, gameObject)
            return

    def __switchStage(self, prevStage, gameObject):
        if prevStage == _Stage.Empty:
            gameObject.createComponent(HighlightComponent, self._ALLY_COLOR, 0, False, False)
        elif prevStage == _Stage.Ally:
            gameObject.createComponent(HighlightComponent, self._ENEMY_COLOR, 0, False, False)
