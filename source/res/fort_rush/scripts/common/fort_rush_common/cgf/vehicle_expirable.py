# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: fort_rush/scripts/common/fort_rush_common/cgf/vehicle_expirable.py
from __future__ import absolute_import
import CGF
from cgf_script.registration import ComponentProperty

class VehicleExpirableComponentDescriptor(object):
    category = 'Expirable'
    editorTitle = 'Vehicle Expirable Component'
    domain = CGF.Domain.All
    duration = ComponentProperty(CGF.PropertyType.Float, editorName='Duration', value=0.0)
