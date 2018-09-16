# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/FlagModel.py
from collections import namedtuple
from Math import Matrix
import BigWorld
from debug_utils import LOG_WARNING
FlagSettings = namedtuple('FlagSettings', ['flagStaffModel',
 'flagModel',
 'flagStaffFlagHP',
 'flagAnim',
 'flagBackgroundTex',
 'flagEmblemTex',
 'flagEmblemTexCoords',
 'flagScale'])

class FlagModel(object):
    model = property(lambda self: self.__flagStaffModel)

    def __init__(self):
        self.__flagModel = None
        self.__flagFashion = None
        self.__flagScaleMatrix = Matrix()
        self.__flagStaffModel = None
        self.__flagStaffFashion = None
        return

    def setupFlag(self, position, flagSettings, color):
        self.__setupFlagStaff(flagSettings, position)
        self.__setupFlagModel(flagSettings, color)

    def changeFlagColor(self, color):
        if self.__flagFashion:
            self.__flagFashion.setColor(color)

    def startFlagAnimation(self):
        if self.__flagModel is not None:
            try:
                animAction = self.__flagModel.action(self.__flagSettings.flagAnim)
                animAction()
            except Exception:
                LOG_WARNING('Unable to start "%s" animation action for model' % self.__flagSettings.flagAnim)

        return

    def __setupFlagStaff(self, flagSettings, position):
        self.__flagStaffModel = flagSettings.flagStaffModel
        self.__flagStaffModel.position = position
        self.__flagStaffFashion = BigWorld.WGAlphaFadeFashion()
        self.__flagStaffModel.fashion = self.__flagStaffFashion

    def __setupFlagModel(self, flagSettings, color):
        self.__flagSettings = flagSettings
        self.__flagScaleMatrix = Matrix()
        self.__flagScaleMatrix.setScale(flagSettings.flagScale)
        flagNode = self.__flagStaffModel.node(flagSettings.flagStaffFlagHP, self.__flagScaleMatrix)
        if self.__flagModel is not None:
            flagNode.detach(self.__flagModel)
            self.__flagModel = None
        self.__flagModel = flagSettings.flagModel
        self.__flagFashion = BigWorld.WGFlagAlphaFadeFashion()
        self.__flagFashion.setColor(color)
        self.__flagFashion.setFlagBackgroundTexture(flagSettings.flagBackgroundTex)
        self.__flagFashion.setEmblemTexture(flagSettings.flagEmblemTex, flagSettings.flagEmblemTexCoords)
        self.__flagModel.fashion = self.__flagFashion
        if self.__flagModel is not None:
            flagNode.attach(self.__flagModel)
            self.__flagFashion.overridePosition(self.__flagStaffModel.matrix)
        return
