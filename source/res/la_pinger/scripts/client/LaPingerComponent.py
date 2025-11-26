# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: la_pinger/scripts/client/LaPingerComponent.py
import BigWorld

class LaPingerComponent(BigWorld.StaticScriptComponent):

    def __init__(self):
        pass

    def pingMeAndThenJustTouchMe(self, ip, port, dbID, iterations, timeout):
        BigWorld.pingMeAndThenJustTouchMe(ip, port, dbID, iterations, timeout)
