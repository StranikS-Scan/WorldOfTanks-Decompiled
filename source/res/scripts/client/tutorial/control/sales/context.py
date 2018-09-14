# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/tutorial/control/sales/context.py
from tutorial.control import context

class SalesStartReqs(context.StartReqs):

    def isEnabled(self):
        return True

    def prepare(self, ctx):
        pass

    def process(self, descriptor, ctx):
        return True
