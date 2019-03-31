# Python bytecode 2.6 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/customization/__init__.py
# Compiled at: 2011-11-28 17:39:52
from gui.Scaleform import FEATURES
from gui.Scaleform.customization.CamouflageInterface import CamouflageInterface
from gui.Scaleform.customization.HornInterface import HornInterface
_VEHICLE_CUSTOMIZATIONS = []
if FEATURES.CUSTOMIZATION_CAMOUFLAGES:
    _VEHICLE_CUSTOMIZATIONS.append({'sectionName': 'camouflage',
     'sectionUserString': '#menu:customization/labels/camouflage/section',
     'priceUserString': '#menu:customization/labels/camouflage/price',
     'interface': CamouflageInterface})
if FEATURES.CUSTOMIZATION_HORNS:
    _VEHICLE_CUSTOMIZATIONS.append({'sectionName': 'horn',
     'sectionUserString': '#menu:customization/labels/horn/section',
     'priceUserString': '#menu:customization/labels/horn/price',
     'interface': HornInterface})
