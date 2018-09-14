# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/common/material_kinds.py
import ResMgr
IDS_BY_NAMES = None
GROUND_STRENGTHS_BY_IDS = None
EFFECT_MATERIALS = ('ground', 'stone', 'wood', 'metal', 'snow', 'sand', 'water')
EFFECT_MATERIAL_INDEXES_BY_NAMES = dict(((name, idx) for idx, name in enumerate(EFFECT_MATERIALS)))
EFFECT_MATERIAL_INDEXES_BY_IDS = None
EFFECT_MATERIAL_IDS_BY_NAMES = None
WATER_MATERIAL_KIND = -100

def _init():
    global IDS_BY_NAMES
    global EFFECT_MATERIAL_INDEXES_BY_NAMES
    global EFFECT_MATERIAL_INDEXES_BY_IDS
    global EFFECT_MATERIALS
    global GROUND_STRENGTHS_BY_IDS
    global EFFECT_MATERIAL_IDS_BY_NAMES
    IDS_BY_NAMES = {}
    GROUND_STRENGTHS_BY_IDS = {}
    EFFECT_MATERIAL_INDEXES_BY_IDS = {}
    EFFECT_MATERIAL_IDS_BY_NAMES = {'default': [0]}
    xmlPath = 'system/data/material_kinds.xml'
    section = ResMgr.openSection(xmlPath)
    if section is None:
        _raiseWrongXml(xmlPath, 'can not open or read')
    ids = set()
    for s in section.values():
        id = s.readInt('id', -1)
        name = s.readString('desc')
        if id < 0 or not name or id in ids or name in IDS_BY_NAMES:
            _raiseWrongXml(xmlPath, "wrong or non-unique 'id' or 'desc' (%d, '%s')" % (id, name))
        ids.add(id)
        IDS_BY_NAMES[name] = id
        groundStrength = s.readString('ground_strength')
        if groundStrength:
            groundStrength = intern(groundStrength)
            if groundStrength not in ('firm', 'medium', 'soft'):
                _raiseWrongXml(xmlPath, "wrong value of 'ground_strength' for '%s'" % groundStrength)
            GROUND_STRENGTHS_BY_IDS[id] = groundStrength
        matName = s.readString('effect_material')
        if matName:
            matName = intern(matName)
            if matName not in EFFECT_MATERIALS:
                _raiseWrongXml(xmlPath, "wrong value of 'effect_material' for '%s'" % matName)
            EFFECT_MATERIAL_INDEXES_BY_IDS[id] = EFFECT_MATERIAL_INDEXES_BY_NAMES[matName]
            if EFFECT_MATERIAL_IDS_BY_NAMES.get(matName) is None:
                EFFECT_MATERIAL_IDS_BY_NAMES[matName] = []
            EFFECT_MATERIAL_IDS_BY_NAMES[matName].append(id)

    IDS_BY_NAMES['water'] = WATER_MATERIAL_KIND
    EFFECT_MATERIAL_INDEXES_BY_IDS[WATER_MATERIAL_KIND] = EFFECT_MATERIAL_INDEXES_BY_NAMES['water']
    EFFECT_MATERIAL_IDS_BY_NAMES['water'] = []
    EFFECT_MATERIAL_IDS_BY_NAMES['water'].append(WATER_MATERIAL_KIND)
    return


def _raiseWrongXml(fileName, msg):
    raise Exception("error in '" + fileName + "': " + msg)


_init()
