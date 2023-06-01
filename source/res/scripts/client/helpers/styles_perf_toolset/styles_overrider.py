# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/helpers/styles_perf_toolset/styles_overrider.py
import logging
import ResMgr
from items.vehicles import makeIntCompactDescrByID, getItemByCompactDescr
from items.components.c11n_constants import CustomizationType, SeasonType

class StylesOverrider(object):

    def __init__(self):
        self.__stylesConfig = {}

    @property
    def stylesConfig(self):
        return self.__stylesConfig

    def loadStylesConfig(self, configPath):
        section = ResMgr.openSection(configPath, False)
        if section is None:
            logging.error('failed to open styles configuration file: %s', configPath)
            return
        else:
            for value in section.values():
                name = value.readString('name', '')
                style = value.readInt('style', -1)
                if name != '' and style != -1:
                    self.__stylesConfig[name] = style

            return

    def overrideStyleForVehicle(self, vehicleName):
        if vehicleName in self.__stylesConfig:
            style = self.__stylesConfig[vehicleName]
            styleItem = getItemByCompactDescr(makeIntCompactDescrByID('customizationItem', CustomizationType.STYLE, style))
            outfitDescr = styleItem.outfits[SeasonType.SUMMER].makeCompDescr()
            return outfitDescr
        else:
            return None
