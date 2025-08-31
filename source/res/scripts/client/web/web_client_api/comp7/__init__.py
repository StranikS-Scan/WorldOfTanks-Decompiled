# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/web/web_client_api/comp7/__init__.py
from helpers import dependency
from skeletons.gui.game_control import IComp7Controller
from web.web_client_api import w2capi, w2c, W2CSchema

@w2capi(name='comp7', key='action')
class Comp7WebApi(W2CSchema):
    __comp7Controller = dependency.descriptor(IComp7Controller)

    @w2c(W2CSchema, name='get_gamemode_state')
    def getGamemodeState(self, _):
        return {'isEnabled': self.__comp7Controller.isEnabled()}
