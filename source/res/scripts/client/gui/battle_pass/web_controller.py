# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/battle_pass/web_controller.py
from gui import GUI_SETTINGS
from gui.wgcg.web_controller import WebController
from helpers.server_settings import _Wgcg

class BattlePassWebController(WebController):

    def __init__(self):
        super(BattlePassWebController, self).__init__()
        url = GUI_SETTINGS.battlePass.get('webApiUrl')
        self.__config = _Wgcg(True, url, type='gateway', loginOnStart=False)

    def getRequesterConfig(self):
        return self.__config
