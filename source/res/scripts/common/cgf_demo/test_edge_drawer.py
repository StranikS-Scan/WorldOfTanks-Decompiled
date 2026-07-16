# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/common/cgf_demo/test_edge_drawer.py
from __future__ import absolute_import
import CGF
import Triggers
from cgf_demo.demo_category import DEMO_CATEGORY
from cgf_script.registration import registerComponent
from EdgeDrawer import EdgeHighlightComponent

class _Stage(object):
    Empty = 0
    Ally = 1
    Enemy = 2


@registerComponent
class TestEdgeDrawerComponent(object):
    group = DEMO_CATEGORY
    editorTitle = 'Test Edge Drawer'
    domain = CGF.Domain.ClientEditor

    def __init__(self):
        super(TestEdgeDrawerComponent, self).__init__()
        self.callbackID = None
        return


class TestEdgeDrawerComponentSystem(CGF.System):
    _ALLY_COLOR = 2
    _ENEMY_COLOR = 1
    EdgeDrawerActivated = CGF.ActivateReaction(CGF.ReactRw(TestEdgeDrawerComponent), CGF.Rw(Triggers.TimeTriggerComponent))
    EdgeDrawerDeactivated = CGF.DeactivateReaction(CGF.ReactRo(TestEdgeDrawerComponent), CGF.Rw(Triggers.TimeTriggerComponent))
    EdgeHighlightAccess = CGF.AccessReaction(CGF.Rw(EdgeHighlightComponent))
    Reactions = CGF.Reactions(EdgeDrawerActivated, EdgeDrawerDeactivated, EdgeHighlightAccess)

    def update(self):
        for testComponent, trigger in self.reaction(self.EdgeDrawerDeactivated):
            if testComponent.callbackID is not None:
                trigger.removeFireReaction(testComponent.callbackID)

        for testComponent, trigger in self.reaction(self.EdgeDrawerActivated):
            testComponent.callbackID = trigger.addFireReaction(self.__triggerReaction)

        return

    def __triggerReaction(self, gameObject):
        if not gameObject.valid:
            return
        else:
            stage = _Stage.Empty
            highlightAccess = self.reaction(self.EdgeHighlightAccess)
            highlighter = highlightAccess.find(gameObject)
            if highlighter is not None:
                if highlighter.colorIndex == self._ALLY_COLOR:
                    stage = _Stage.Ally
                elif highlighter.colorIndex == self._ENEMY_COLOR:
                    stage = _Stage.Enemy
                q = CGF.CommandQueue(self.gom)
                q.removeComponent(gameObject, EdgeHighlightComponent)
            self.__switchStage(stage, gameObject)
            return

    def __switchStage(self, prevStage, gameObject):
        q = CGF.CommandQueue(self.gom)
        if prevStage == _Stage.Empty:
            q.createComponent(gameObject, EdgeHighlightComponent, self._ALLY_COLOR, False, 0, False)
        elif prevStage == _Stage.Ally:
            q.createComponent(gameObject, EdgeHighlightComponent, self._ENEMY_COLOR, False, 0, False)
