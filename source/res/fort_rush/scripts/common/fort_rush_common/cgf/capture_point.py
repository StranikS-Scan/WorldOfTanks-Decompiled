# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: fort_rush/scripts/common/fort_rush_common/cgf/capture_point.py
from __future__ import absolute_import
import CGF
import Triggers
from GenericComponents import Sequence
from cgf_script.registration import ComponentProperty

class FortRushCapturePointComponentDescr(object):
    category = 'CapturePoint'
    domain = CGF.Domain.All
    editorTitle = 'Capture Point Component'
    trigger = ComponentProperty(type=CGF.PropertyType.Link, editorName='AreaTrigger', value=Triggers.AreaTriggerComponent)
    sequence = ComponentProperty(type=CGF.PropertyType.Link, editorName='SequenceComponent', value=Sequence)
    capturablePointName = ComponentProperty(type=CGF.PropertyType.String, editorName='capturablePointName')
