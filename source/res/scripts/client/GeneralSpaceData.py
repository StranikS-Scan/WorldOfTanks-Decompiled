# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/GeneralSpaceData.py
import BigWorld

class GeneralSpaceData(BigWorld.Space):

    def set_environment(self, prev):
        name = self.environment
        if name:
            self.setEnvironment(name)
        else:
            self.resetEnvironment()
