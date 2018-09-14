# Embedded file name: scripts/client/gui/customization_2_0/elements/qualifier.py
from gui.shared.gui_items.Vehicle import VEHICLE_CLASS_NAME
from helpers.i18n import makeString as _ms
from CurrentVehicle import g_currentVehicle as _g_currentVehicle
_ICONS = {'16x16': {'main_skill': '../maps/icons/customization/qualifiers/16x16/{0}.png',
           'camouflage': '../maps/icons/customization/qualifiers/16x16/camouflage.png'},
 '42x42': {'main_skill': '../maps/icons/customization/qualifiers/42x42/{0}.png',
           'camouflage': '../maps/icons/customization/qualifiers/42x42/camouflage.png'}}

class QUALIFIER_TYPE:
    ALL = 'all'
    RADIOMAN = 'radioman'
    COMMANDER = 'commander'
    DRIVER = 'driver'
    GUNNER = 'gunner'
    LOADER = 'loader'
    CAMOUFLAGE = 'camouflage'


QUALIFIER_TYPE_NAMES = dict([ (v, k) for k, v in QUALIFIER_TYPE.__dict__.iteritems() if not k.startswith('_') ])
_VEHICLE_CAMOUFLAGE_BONUS = {VEHICLE_CLASS_NAME.LIGHT_TANK: 3,
 VEHICLE_CLASS_NAME.MEDIUM_TANK: 3,
 VEHICLE_CLASS_NAME.HEAVY_TANK: 2,
 VEHICLE_CLASS_NAME.AT_SPG: 4,
 VEHICLE_CLASS_NAME.SPG: 2}

def getNameByType(qualifierType):
    return _ms('#customization:bonusName/{0}'.format(qualifierType))


def getIcon16x16ByType(qualifierType):
    if qualifierType == QUALIFIER_TYPE.CAMOUFLAGE:
        return _ICONS['16x16'][qualifierType]
    else:
        return _ICONS['16x16']['main_skill'].format(qualifierType)


def getIcon42x42ByType(qualifierType):
    if qualifierType == QUALIFIER_TYPE.CAMOUFLAGE:
        return _ICONS['42x42'][qualifierType]
    else:
        return _ICONS['42x42']['main_skill'].format(qualifierType)


class QualifierBase(object):
    __slots__ = ('__rawData',)

    def getIcon16x16(self):
        raise NotImplementedError

    def getDescription(self):
        raise NotImplementedError

    def getValue(self):
        raise NotImplementedError

    def getType(self):
        raise NotImplementedError

    def getName(self):
        raise NotImplementedError

    def getExtendedName(self):
        raise NotImplementedError

    def getIcon42x42(self):
        raise NotImplementedError

    def getFormattedValue(self):
        return '+{0}%'.format(self.getValue())


class CamouflageQualifier(QualifierBase):

    def __init__(self, camouflageType):
        super(CamouflageQualifier, self).__init__()
        self.__camouflageType = camouflageType
        self.__value = _VEHICLE_CAMOUFLAGE_BONUS[_g_currentVehicle.item.type]

    def getIcon16x16(self):
        return _ICONS['16x16']['camouflage']

    def getIcon42x42(self):
        return _ICONS['42x42']['camouflage']

    def getDescription(self):
        return _ms('#customization:qualifier/condition/map_kind_{0}'.format(self.__camouflageType))

    def getValue(self):
        return self.__value

    def getType(self):
        return 'camouflage'

    def getName(self):
        return _ms('#customization:bonusName/camouflage')

    def getExtendedName(self):
        return _ms('#customization:bonusName/extended/camouflage')


class Qualifier(QualifierBase):

    def __init__(self, rawData):
        self.__rawData = rawData

    def getIcon16x16(self):
        return _ICONS['16x16'][self.__rawData.qualifierType].format(self.__rawData.crewRole)

    def getIcon42x42(self):
        return _ICONS['42x42'][self.__rawData.qualifierType].format(self.__rawData.crewRole)

    def getDescription(self):
        if self.__rawData.conditionDescription:
            return _ms(self.__rawData.conditionDescription)
        else:
            return None
            return None

    def getValue(self):
        return self.__rawData.value

    def getType(self):
        return self.__rawData.crewRole

    def getName(self):
        return _ms('#customization:bonusName/{0}'.format(self.__rawData.crewRole))

    def getExtendedName(self):
        return _ms('#customization:bonusName/extended/{0}'.format(self.__rawData.crewRole))
