# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/common/cgf_components_common/vehicle_mechanics/staged_jet_boosters.py
from __future__ import absolute_import
import CGF
from cgf_script.registration import ComponentProperty

class StagedJetBoostersControllerDescriptor(object):
    category = 'Vehicle Mechanics'
    editorTitle = 'Staged Jet Boosters Controller'
    domain = CGF.Domain.All
    left = ComponentProperty(CGF.PropertyType.Link, editorName='Left Rocket', value=CGF.GameObject)
    right = ComponentProperty(CGF.PropertyType.Link, editorName='Right Rocket', value=CGF.GameObject)
    stateController = ComponentProperty(CGF.PropertyType.Link, editorName='State Controller', value=CGF.GameObject)
