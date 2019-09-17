# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/common/festival_race/FestivalRaceSettings.py
import ResMgr
from constants import ITEM_DEFS_PATH
from Singleton import Singleton
from items import _xml
from typing import Dict
_DEFAULT_XML_PATH = ITEM_DEFS_PATH + 'festival_race.xml'

class FestivalRaceSettings(Singleton):

    def _singleton_init(self, xmlPath=_DEFAULT_XML_PATH):
        self.reload(xmlPath)

    def reload(self, xmlPath=_DEFAULT_XML_PATH):
        self.__clean()
        self.__readSettings(xmlPath)

    @property
    def vehicleRammingDamageFactor(self):
        return self.__vehicleRammingDamageFactor

    @property
    def vehicleRammingDamageMax(self):
        return self.__vehicleRammingDamageMax

    @property
    def enemyCamoPaletteIdx(self):
        return self.__enemyCamoPaletteIdx

    @property
    def vsePlans(self):
        return self.__plans

    def __clean(self):
        self.__vehicleRammingDamageFactor = 1.0
        self.__vehicleRammingDamageMax = float('inf')
        self.__enemyCamoPalette = -1
        self.__plans = {}

    def __readSettings(self, xmlPath):
        configXml = ResMgr.openSection(xmlPath)
        if configXml is None:
            _xml.raiseWrongXml(None, xmlPath, 'can not open or read')
        self.__readVehicleRamming(configXml['vehicleRamming'])
        self.__readTeamColors(configXml['teamColors'])
        self.__readVsePlans(configXml['vsePlans'])
        ResMgr.purge(xmlPath, True)
        return

    def __readVehicleRamming(self, vehicleRamming):
        if vehicleRamming is None:
            return
        else:
            self.__vehicleRammingDamageFactor = vehicleRamming.readFloat('damageFactor', self.__vehicleRammingDamageFactor)
            self.__vehicleRammingDamageMax = vehicleRamming.readFloat('damageMax', self.__vehicleRammingDamageMax)
            return

    def __readTeamColors(self, section):
        if section is None:
            return
        else:
            self.__enemyCamoPaletteIdx = section.readInt('enemyCamoPaletteIdx', -1)
            return

    def __readVsePlans(self, section):
        if section is None:
            return
        else:
            for name, sec in section.items():
                planId = sec.readString('id')
                planName = sec.readString('name')
                self.__plans[planId] = planName

            return
