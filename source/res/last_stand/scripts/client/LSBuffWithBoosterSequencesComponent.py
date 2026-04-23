# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: last_stand/scripts/client/LSBuffWithBoosterSequencesComponent.py
from __future__ import absolute_import
from LSBuffSequencesComponent import LSBuffSequencesComponent
from dyn_components_groups import groupComponent
from xml_config_specs import StrParam, Vector3Param, ListParam, ObjParam, IntParam, BoolParam
_DEFAULTS = 'default'

@groupComponent(sequences=ListParam(valueParam=ObjParam(sequence=StrParam(), bindNode=StrParam(), offset=Vector3Param(), loopCount=IntParam(default=-1), autoStart=BoolParam(default=True), visibleTo=StrParam(default='all'), sniperModeVisibleTo=StrParam(default='all'), checkNodeExists=BoolParam(default=False), boosterFactors=StrParam(default=_DEFAULTS))))
class LSBuffWithBoosterSequencesComponent(LSBuffSequencesComponent):

    def __init__(self):
        super(LSBuffWithBoosterSequencesComponent, self).__init__()
        self._sequences = None
        return

    @property
    def _componentConfigs(self):
        if not self._sequences:
            matchedItems = []
            defaults = []
            factorSet = set(self.factors.split())
            for seq in self.groupComponentConfig.sequences:
                if seq.boosterFactors == _DEFAULTS:
                    defaults.append(seq)
                if not factorSet.isdisjoint(seq.boosterFactors.split()):
                    matchedItems.append(seq)

            self._sequences = matchedItems if matchedItems else defaults
        return self._sequences
