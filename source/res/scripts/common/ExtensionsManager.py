# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/common/ExtensionsManager.py
import BigWorld
import os
import ResMgr
from collections import namedtuple
Extension = namedtuple('Extension', ('path', 'name', 'isEnabled'))

class ExtensionsManager(object):

    def __init__(self):
        self.__extensions = {}
        for root, dirs, files in os.walk('../wot_ext'):
            if 'extension.xml' in files:
                extension = self.__readExtension(root)
                self.__extensions[extension.name] = extension
                print extension

    def __readExtension(self, root):
        section = ResMgr.openSection(root + '/extension.xml')
        return Extension(root + '/', section.readString('FeatureName'), section.readBool('IsEnabled'))

    @property
    def extensions(self):
        return self.__extensions.values()


g_extensionsManager = ExtensionsManager()
