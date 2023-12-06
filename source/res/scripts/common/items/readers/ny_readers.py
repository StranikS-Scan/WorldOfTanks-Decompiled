# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/common/items/readers/ny_readers.py
import typing
import ResMgr
import contextlib
from ny_common.ny_exception import NYSoftException
from items.components.ny_components import SlotDescriptor, VariadicDiscountDescriptor, ToyTransformation, ToyModelOverride
from items.components.ny_constants import TOY_TYPES

@contextlib.contextmanager
def openSection(path):
    try:
        yield ResMgr.openSection(path)
    finally:
        ResMgr.purge(path)


def _readSlotSection(section):
    cfg = {'id': section.readInt('id')}
    cfg['type'] = slotType = section.readString('type')
    if slotType not in TOY_TYPES:
        raise NYSoftException("Wrong slot type '%s'" % slotType)
    return cfg


def readSlots(xmlPath):
    cache = None
    with openSection(xmlPath) as section:
        if section is None:
            raise NYSoftException("Can't open '%s'" % xmlPath)
        subsections = section['slots'].values()
        numSlots = len(subsections)
        cache = [None] * numSlots
        for slotSec in subsections:
            cfg = _readSlotSection(slotSec)
            slotID = cfg['id']
            if not 0 <= slotID < numSlots:
                raise NYSoftException('Wrong slotID {}, {}'.format(slotID, numSlots))
            if cache[slotID] is not None:
                raise NYSoftException("Repeated slotID '%d'" % slotID)
            cache[slotID] = SlotDescriptor(cfg)

    return cache


def _readToyTransformationNode(node):
    toyTransformation = ToyTransformation(transform=node.readMatrix('transform') if node.has_key('transform') else None, modelOverride=ToyModelOverride.createModel(node))
    return (node.readString('node'), node.readString('object'), toyTransformation)


def _readToyTransformationsSection(section):
    nodes = {}
    for subSection in section.values():
        if subSection.name == 'node':
            nodeName, objectName, transformation = _readToyTransformationNode(subSection)
            nodes[intern(objectName), intern(nodeName)] = transformation

    return (section.readString('name'), nodes)


def readToysTransformations(xmlPath):
    cache = {}
    with openSection(xmlPath) as section:
        if section is None:
            raise NYSoftException("Can't open '%s" % xmlPath)
        for subSection in section.values():
            modelName, nodes = _readToyTransformationsSection(subSection)
            cache[modelName] = nodes

    return cache


def buildVariadicDiscountsCache(xmlPath):
    section = ResMgr.openSection(xmlPath)
    if section is None:
        raise NYSoftException("Can't open '%s'" % xmlPath)
    cache = {}
    for vdSec in section.values():
        cfg = _readVariadicDiscount(vdSec)
        vdID = cfg['id']
        if vdID in cache:
            raise NYSoftException("Repeated variadic discount ID '%s'" % vdID)
        cache[vdID] = VariadicDiscountDescriptor(cfg['id'], cfg['firstGoodieId'], cfg['lastGoodieId'], cfg['level'])

    return cache


def _readVariadicDiscount(section):
    cfg = {}
    cfg['id'] = section.readString('id')
    cfg['firstGoodieId'] = section.readInt('firstGoodieId')
    cfg['lastGoodieId'] = section.readInt('lastGoodieId')
    cfg['level'] = section.readInt('level')
    return cfg
