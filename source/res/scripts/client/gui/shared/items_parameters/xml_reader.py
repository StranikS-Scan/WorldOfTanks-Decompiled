# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/shared/items_parameters/xml_reader.py
import ResMgr
import resource_helper
SIMPLIFIED_COEFFICIENTS_PATH = 'gui/params_coefficients.xml'

class ParamsXMLReader(object):

    def __init__(self):
        self.__params = {}
        for item in resource_helper.root_iterator(SIMPLIFIED_COEFFICIENTS_PATH):
            self.__params[item.name] = item.value

    def readSimplifiedParamsCoefficients(self):
        return self.__params['coefficients']

    def readBonuses(self):
        result = {}
        for paramName, bonusTypes in self.__params['bonuses'].iteritems():
            currBonuses = []
            for bonusType, items in bonusTypes.items():
                for itemName in items:
                    currBonuses.append((itemName, bonusType))

            result[paramName] = tuple(currBonuses)

        return result
