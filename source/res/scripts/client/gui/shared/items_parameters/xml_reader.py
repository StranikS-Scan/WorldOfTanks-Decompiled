# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/shared/items_parameters/xml_reader.py
import resource_helper
SIMPLIFIED_COEFFICIENTS_PATH = 'gui/params_coefficients.xml'

def _getBonusTypesGenerator(bonusTypes):
    for bonusType, items in bonusTypes.items():
        for itemName in items:
            yield (itemName, bonusType)


def read():
    params = {}
    for item in resource_helper.root_iterator(SIMPLIFIED_COEFFICIENTS_PATH):
        params[item.name] = item.value

    coefficients = params.pop('coefficients')
    bonuses = params.pop('bonuses')
    for paramName, bonusTypes in bonuses.iteritems():
        bonuses[paramName] = tuple(_getBonusTypesGenerator(bonusTypes))

    return (coefficients, bonuses)
