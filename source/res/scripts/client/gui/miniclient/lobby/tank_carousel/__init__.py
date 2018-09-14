# Embedded file name: scripts/client/gui/miniclient/lobby/tank_carousel/__init__.py
import pointcuts as _pointcuts

def configure_pointcuts(config):
    _pointcuts.MakeTankUnavailableInCarousel(config)
    _pointcuts.VehicleTooltipStatus(config)
