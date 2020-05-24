# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/common/material_kinds.py
import ResMgr
from soft_exception import SoftException
_MATERIAL_KINDS_FILE = 'system/data/material_kinds.xml'
_EFFECT_MATERIALS_FILE = 'system/data/effect_materials.xml'
IDS_BY_NAMES = None
EFFECT_MATERIALS = None
EFFECT_MATERIAL_INDEXES_BY_NAMES = None
EFFECT_MATERIAL_NAMES_BY_INDEXES = None
EFFECT_MATERIAL_INDEXES_BY_IDS = None
EFFECT_MATERIAL_IDS_BY_NAMES = None
NOT_GROUND_MATERIALS = None
EFFECT_MATERIAL_PROPERTIES = None

def _init():
    global IDS_BY_NAMES
    global EFFECT_MATERIAL_INDEXES_BY_IDS
    global EFFECT_MATERIALS
    global EFFECT_MATERIAL_NAMES_BY_INDEXES
    global EFFECT_MATERIAL_IDS_BY_NAMES
    global NOT_GROUND_MATERIALS
    global EFFECT_MATERIAL_INDEXES_BY_NAMES
    global EFFECT_MATERIAL_PROPERTIES
    IDS_BY_NAMES = {}
    EFFECT_MATERIALS = []
    EFFECT_MATERIAL_INDEXES_BY_NAMES = {}
    EFFECT_MATERIAL_NAMES_BY_INDEXES = {}
    EFFECT_MATERIAL_INDEXES_BY_IDS = {}
    EFFECT_MATERIAL_IDS_BY_NAMES = {'default': [0]}
    NOT_GROUND_MATERIALS = []
    EFFECT_MATERIAL_PROPERTIES = {}
    xmlPath = _MATERIAL_KINDS_FILE
    section = ResMgr.openSection(xmlPath)
    if section is None:
        _raiseWrongXml(xmlPath, 'can not open or read')
    ids = set()
    for s in section.values():
        id = s.readInt('id', -1)
        name = s.readString('desc')
        if not name or id in ids or name in IDS_BY_NAMES:
            _raiseWrongXml(xmlPath, "wrong or non-unique 'id' or 'desc' (%d, '%s')" % (id, name))
        ids.add(id)
        IDS_BY_NAMES[name] = id
        matName = s.readString('effect_material')
        if matName:
            matName = intern(matName)
            if matName not in EFFECT_MATERIALS:
                EFFECT_MATERIALS.append(matName)
            if EFFECT_MATERIAL_IDS_BY_NAMES.get(matName) is None:
                EFFECT_MATERIAL_IDS_BY_NAMES[matName] = []
            EFFECT_MATERIAL_IDS_BY_NAMES[matName].append(id)

    for ind, matName in enumerate(EFFECT_MATERIALS):
        EFFECT_MATERIAL_INDEXES_BY_NAMES[matName] = ind
        EFFECT_MATERIAL_NAMES_BY_INDEXES[ind] = matName
        for id in EFFECT_MATERIAL_IDS_BY_NAMES[matName]:
            EFFECT_MATERIAL_INDEXES_BY_IDS[id] = ind

    ResMgr.purge(xmlPath, True)
    xmlPath = _EFFECT_MATERIALS_FILE
    section = ResMgr.openSection(xmlPath)
    if section is None:
        _raiseWrongXml(xmlPath, 'can not open or read')
    for s in section.values():
        name = s.readString('name')
        if not name:
            _raiseWrongXml(xmlPath, "wrong 'name' ('%s')" % name)
        if EFFECT_MATERIAL_PROPERTIES.get(name) is not None:
            _raiseWrongXml(xmlPath, "name duplication ('%s')" % name)
        EFFECT_MATERIAL_PROPERTIES[name] = {}
        hardnessMap = s.readVector2('hardness_map')
        if hardnessMap:
            EFFECT_MATERIAL_PROPERTIES[name]['hardness_map'] = [hardnessMap[0], hardnessMap[1]]
        if s.readBool('not_ground_material'):
            NOT_GROUND_MATERIALS.append(name)

    ResMgr.purge(xmlPath, True)
    return


def _raiseWrongXml(fileName, msg):
    raise SoftException("error in '" + fileName + "': " + msg)


def getWaterMatKind():
    return EFFECT_MATERIAL_IDS_BY_NAMES['water'][0]


_init()
