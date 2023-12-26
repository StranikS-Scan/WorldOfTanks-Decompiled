# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/web/web_client_api/seniority_awards/__init__.py
from helpers import dependency
from skeletons.gui.game_control import ISeniorityAwardsController
from gui.shared.event_dispatcher import showSeniorityRewardVehiclesWindow
from web.web_client_api import w2capi, w2c, W2CSchema

@w2capi(name='seniority_awards', key='action')
class SeniorityAwardsWebApi(object):
    __seniorityAwardsCtrl = dependency.descriptor(ISeniorityAwardsController)

    @w2c(W2CSchema, 'is_vehicle_selection_available')
    def isVehicleSelectionAvailable(self, _):
        return {'isVehicleSelectionAvailable': self.__seniorityAwardsCtrl.isVehicleSelectionAvailable}


class OpenSeniorityAwardsWebApi(object):

    @w2c(W2CSchema, 'seniority_vehicle_selection')
    def showSeniorityVehicleSelectionWindow(self, _):
        showSeniorityRewardVehiclesWindow()
