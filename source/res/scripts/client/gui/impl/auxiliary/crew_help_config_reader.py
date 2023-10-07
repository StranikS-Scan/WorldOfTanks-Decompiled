# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/auxiliary/crew_help_config_reader.py
import resource_helper
from functools import reduce
from operator import attrgetter
from gui.impl.gen import R
GUI_CONFIG_PATH = 'gui/crew_help_layout.xml'
TYPE_ATTR = 'type'
config = []

def readResourceValue(ctx, node):
    item = resource_helper.readStringItem(ctx, node)
    parts = str(item.value).split('.')
    return reduce(lambda res, curr: res.dyn(curr), parts[2:], attrgetter(parts[1])(R))


def readStringValue(ctx, node):
    return str(resource_helper.readStringItem(ctx, node).value)


def readListSection(ctx, node):
    listSection = []
    for sectionCtx, sectionNode in resource_helper.getIterator(ctx, node):
        listItem = {}
        for sectionItemCtx, sectionItem in resource_helper.getIterator(sectionCtx, sectionNode):
            itemType = resource_helper.readItemAttr(sectionItemCtx, sectionItem, TYPE_ATTR)
            listItem[sectionItem.name] = resource_readers[itemType](sectionItemCtx, sectionItem)

        if listItem:
            listSection.append(listItem)

    return listSection


resource_readers = {'resource': readResourceValue,
 'string': readStringValue,
 'list': readListSection}

def getHelpViewConfig():
    global config
    if not config:
        with resource_helper.root_generator(GUI_CONFIG_PATH) as rootCtx, slides:
            config = readListSection(rootCtx, slides)
    return config
