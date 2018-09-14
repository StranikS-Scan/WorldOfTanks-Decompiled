# Embedded file name: scripts/client/gui/miniclient/fortified_regions/__init__.py
import pointcuts as _pointcuts

def configure_pointcuts():
    _pointcuts.FortificationsViewSubscriptions()
    _pointcuts.OnFortifiedRegionsOpen()
    _pointcuts.OnFortRequirementsUpdate()
    _pointcuts.OnViewPopulate()
