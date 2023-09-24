# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/bootcamp/bootcamp_cm_handlers.py
from gui.Scaleform.daapi.view.lobby.techtree.research_cm_handlers import ResearchVehicleContextMenuHandler
from gui.Scaleform.daapi.view.lobby.techtree.research_cm_handlers import ResearchItemContextMenuHandler
from gui.Scaleform.daapi.view.lobby.hangar.hangar_cm_handlers import VehicleContextMenuHandler
from gui.Scaleform.daapi.view.lobby.hangar.hangar_cm_handlers import TechnicalMaintenanceCMHandler

def _disableContextMenuItem(item):
    if item['initData'] is None:
        item['initData'] = {}
    item['initData'].update({'enabled': False})
    return


def _disableAllContextMenuItems(options, exceptions=()):
    for item in options:
        if item['id'] not in exceptions:
            _disableContextMenuItem(item)


class BCResearchVehicleContextMenuHandler(ResearchVehicleContextMenuHandler):

    def _generateOptions(self, ctx=None):
        options = super(BCResearchVehicleContextMenuHandler, self)._generateOptions(ctx)
        _disableAllContextMenuItems(options)
        return options


class BCResearchItemContextMenuHandler(ResearchItemContextMenuHandler):

    def _generateOptions(self, ctx=None):
        options = super(BCResearchItemContextMenuHandler, self)._generateOptions(ctx)
        _disableAllContextMenuItems(options)
        return options


class BCVehicleContextMenuHandler(VehicleContextMenuHandler):

    def _generateOptions(self, ctx=None):
        options = super(BCVehicleContextMenuHandler, self)._generateOptions(ctx)
        _disableAllContextMenuItems(options)
        return options


class BCTechnicalMaintenanceCMHandler(TechnicalMaintenanceCMHandler):

    def _generateOptions(self, ctx=None):
        options = super(BCTechnicalMaintenanceCMHandler, self)._generateOptions(ctx)
        _disableAllContextMenuItems(options)
        return options
