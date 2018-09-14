# Embedded file name: scripts/client/gui/game_control/IGR.py
import Event
import constants
from PlayerEvents import g_playerEvents
from gui.game_control.controllers import Controller

class IGRController(Controller):

    def __init__(self, proxy):
        super(IGRController, self).__init__(proxy)
        self.__xpFactor = 1.0
        self.__roomType = constants.IGR_TYPE.NONE
        self.onIgrTypeChanged = Event.Event()

    def init(self):
        g_playerEvents.onIGRTypeChanged += self.__onIGRTypeChanged

    def fini(self):
        g_playerEvents.onIGRTypeChanged -= self.__onIGRTypeChanged
        self.onIgrTypeChanged.clear()
        super(IGRController, self).fini()

    def onLobbyStarted(self, ctx = None):
        data = (ctx or {}).get('igrData', {})
        self.__roomType = data.get('roomType', constants.IGR_TYPE.NONE)
        self.__xpFactor = data.get('igrXPFactor', 1.0)
        self.onIgrTypeChanged(self.__roomType, self.__xpFactor)

    def onDisconnected(self):
        self.__xpFactor = 1.0
        self.__roomType = constants.IGR_TYPE.NONE

    def getXPFactor(self):
        return self.__xpFactor

    def getRoomType(self):
        return self.__roomType

    def __onIGRTypeChanged(self, roomType, xpFactor):
        if roomType is not None:
            self.__roomType = roomType
        if xpFactor is not None:
            self.__xpFactor = xpFactor
        self.onIgrTypeChanged(self.__roomType, self.__xpFactor)
        return
