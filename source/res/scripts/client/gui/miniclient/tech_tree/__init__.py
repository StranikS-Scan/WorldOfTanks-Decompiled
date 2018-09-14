# Python 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/miniclient/tech_tree/__init__.py
import pointcuts as _pointcuts

def configure_pointcuts(config):
    _pointcuts.OnBuyVehicle(config)
    _pointcuts.OnTechTreePopulate()
