# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/miniclient/lobby/strongholds/pointcuts.py
from helpers import aop
import aspects

class MakeStrongholdsUnavailable(aop.Pointcut):

    def __init__(self):
        aop.Pointcut.__init__(self, 'gui.Scaleform.daapi.view.lobby.header.LobbyHeader', 'LobbyHeader', '_updateStrongholdsSelector', aspects=(aspects.MakeStrongholdsUnavailable(),))
