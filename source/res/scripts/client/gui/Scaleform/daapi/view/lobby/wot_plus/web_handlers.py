# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/wot_plus/web_handlers.py
import typing
from gui.shared.event_dispatcher import showVehicleRentalPage, showHangar
from gui.Scaleform.daapi.settings.views import VIEW_ALIAS
from web.web_client_api import Schema2Command, webApiCollection
from web.web_client_api.ui import OpenTabWebApi

class _OpenTabWebApi(OpenTabWebApi):

    def _getVehiclePreviewReturnAlias(self, cmd):
        return VIEW_ALIAS.WOT_PLUS_VEHICLE_PREVIEW

    def _getVehiclePreviewReturnCallback(self, cmd):
        return self.__getReturnCallback()

    def _getVehicleStylePreviewCallback(self, cmd):
        return self.__getReturnCallback()

    def __getReturnCallback(self):

        def _returnToVehicleRental():
            showHangar()
            showVehicleRentalPage()

        return _returnToVehicleRental


_NAME_TO_API_MAP = {'open_tab': _OpenTabWebApi}

def replaceHandlers(handlers):
    handlersToReplace = [ e for e in handlers if e.name in _NAME_TO_API_MAP.keys() ]
    for element in handlersToReplace:
        handlers.remove(element)

    newHandlers = webApiCollection(*_NAME_TO_API_MAP.values())
    handlers.extend(newHandlers)
