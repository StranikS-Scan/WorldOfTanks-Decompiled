# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: halloween/scripts/client/HWLootVisualComponent.py
from __future__ import absolute_import
from HWBuffSequencesComponent import HWBuffSequencesComponent
from dyn_components_groups import groupComponent
from xml_config_specs import StrParam

@groupComponent(stateParam=StrParam(default='state'))
class HWLootVisualComponent(HWBuffSequencesComponent):

    def __init__(self, stateParam='state'):
        super(HWLootVisualComponent, self).__init__()
        self._stateParam = stateParam

    def set_lootState(self, prev):
        self._onChangeLootState()

    def _onAvatarReady(self):
        super(HWLootVisualComponent, self)._onAvatarReady()
        self._onChangeLootState()

    def _onChangeLootState(self):
        for animator in self._animators:
            animator.setFloatParam(self._stateParam, self.lootState)
