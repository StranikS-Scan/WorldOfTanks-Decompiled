# Python bytecode 2.6 (decompiled from Python 2.7)
# Embedded file name: scripts/client/FX/ClientCompatibility.py
# Compiled at: 2010-05-25 20:46:16
import BigWorld
if BigWorld.component == 'editor':

    def addMat(a, b):
        pass


    def delMat(a):
        pass


    BigWorld.addMat = addMat
    BigWorld.delMat = delMat

    def player():
        return None


    BigWorld.player = player
