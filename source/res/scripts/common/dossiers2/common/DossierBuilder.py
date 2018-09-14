# Python 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/common/dossiers2/common/DossierBuilder.py
import struct
from DossierDescr import DossierDescr

class DossierBuilder(object):

    def __init__(self, blockBuilders, versionFormat, blockSizeFormat, version, updaters, initializer):
        self.__blockBuilders = blockBuilders
        self.__versionFormat = versionFormat
        self.__headerFormat = '<' + versionFormat + blockSizeFormat * len(blockBuilders)
        self.__latestVersion = version
        self.__updaters = updaters
        self.__initializer = initializer
        self.__emptyCompDescr = struct.pack(self.__headerFormat, version, *([0] * len(blockBuilders)))

    def build(self, compDescr = ''):
        if compDescr == '':
            dossier = DossierDescr(self.__emptyCompDescr, self.__blockBuilders, self.__headerFormat)
            self.__initializer(dossier)
        else:
            version = struct.unpack_from(self.__versionFormat, compDescr)[0]
            while version != self.__latestVersion:
                version, compDescr = self.__updaters[version](compDescr)

            dossier = DossierDescr(compDescr, self.__blockBuilders, self.__headerFormat)
        return dossier
