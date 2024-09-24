# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/common/extension_utils.py
import importlib
from soft_exception import SoftException
from ExtensionsManager import g_extensionsManager
from constants import IS_CLIENT, IS_EDITOR, IS_BOT
from debug_utils import LOG_CURRENT_EXCEPTION
from extension_rules import isExtXML, READ_METHOD
if IS_CLIENT or IS_EDITOR:
    import ResMgr as rmgr

    def getRealmFilePath(filepath):
        return filepath


else:
    from realm_utils import ResMgr as rmgr
    from realm_utils import getRealmFilePath
_ROOT_TAG = 'root'
_XML_NAMESPACE = ' xmlns:xmlref="http://bwt/xmlref"'
_MERGE_TAG = 'xmlref:merge'
_CONTENT_TAG = 'xmlref:content'
_INCLUDE_TAG = 'xmlref:include'
_INCLUDE_BY_PATH_TAG = 'xmlref:includeByPath'

def importClass(classPath, defaultMod):
    modPath, _, className = classPath.rpartition('.')
    try:
        mod = importlib.import_module(modPath or defaultMod)
    except ImportError:
        LOG_CURRENT_EXCEPTION()
        return

    try:
        return getattr(mod, className)
    except AttributeError:
        LOG_CURRENT_EXCEPTION()
        return


class _MergeExtensionFile(object):

    @classmethod
    def makeMergeXMLString(cls, xmlPaths, mergeType, params):
        if not xmlPaths:
            return ''
        else:
            genString = cls._openTag('{} {}'.format(_ROOT_TAG, _XML_NAMESPACE))
            operationTag = None
            if mergeType == READ_METHOD.MERGE:
                operationTag = _MERGE_TAG
            elif mergeType == READ_METHOD.INCLUDE_BY_PATH:
                operationTag = _INCLUDE_BY_PATH_TAG
            if operationTag:
                attribs = None if params is None else [('params', params)]
                genString += cls._openTag(operationTag, attribs)
            for path in xmlPaths:
                if operationTag:
                    genString += cls._openTag(_CONTENT_TAG)
                genString += cls._attributeTag(_INCLUDE_TAG, 'href', path)
                if operationTag:
                    genString += cls._closeTag(_CONTENT_TAG)

            if operationTag:
                genString += cls._closeTag(operationTag)
            genString += cls._closeTag(_ROOT_TAG)
            return genString

    @classmethod
    def openSection(cls, xmlPath, mergeType, params):
        xmlPaths = [ ext.path + xmlPath for ext in g_extensionsManager.activeExtensions if rmgr.isFile(ext.path + xmlPath) ]
        if not xmlPaths:
            return rmgr.openSection(xmlPath)
        if rmgr.isFile(xmlPath):
            xmlPaths = [xmlPath] + xmlPaths
        elif len(xmlPaths) > 1 and mergeType != READ_METHOD.INCLUDE:
            raise SoftException('The operation of merging files for files which are not present in the core is prohibited for the merge type: {t}. File: {f} may be present in different extensions!'.format(t=mergeType, f=xmlPath))
        if len(xmlPaths) == 1:
            return rmgr.openSection(xmlPaths[0])
        if not (IS_CLIENT or IS_EDITOR):
            xmlPaths = [ (getRealmFilePath(xmlPath) if rmgr.isFile(getRealmFilePath(xmlPath)) else xmlPath) for xmlPath in xmlPaths ]
        section = rmgr.DataSection('root')
        section.createSectionFromString(cls.makeMergeXMLString(xmlPaths, mergeType, params))
        section = section.child(0)
        return section

    @classmethod
    def _openTag(cls, tag, attributes=None):
        text = '<' + tag
        if attributes:
            for name, value in attributes:
                text = '{} {}="{}"'.format(text, name, value)

        text = text + '>\n'
        return text

    @classmethod
    def _closeTag(cls, tag):
        return '</' + tag + '>\n'

    @classmethod
    def _attributeTag(cls, tag, attrName, attrValue):
        return '<{} {}="{}"/>\n'.format(tag, attrName, attrValue)


def mergeSection(xmlPath, mergeType, params):
    return _MergeExtensionFile.openSection(xmlPath, mergeType, params)


def makeMergeXMLString(xmlPaths, mergeType, params):
    return _MergeExtensionFile.makeMergeXMLString(xmlPaths, mergeType, params)


class ResMgr(object):

    class __metaclass__(type):

        def __getattr__(self, item):
            return getattr(rmgr, item) if IS_CLIENT or IS_EDITOR or IS_BOT else getattr(self if item in ('openSection', 'addToCache') else rmgr, item)

    @classmethod
    def openSection(cls, filepath, createIfMissing=False):
        if (IS_CLIENT or IS_EDITOR or IS_BOT) and getattr(rmgr, 'IS_PY_SCRIPT', True):
            return rmgr.openSection(filepath, createIfMissing)
        if cls.isInCache(filepath):
            return rmgr.openSection(filepath, createIfMissing)
        readExtXML, readMethod, params = isExtXML(filepath)
        return rmgr.openSection(filepath, createIfMissing) if not readExtXML else mergeSection(filepath, readMethod, params)

    @staticmethod
    def addToCache(ftPath, xml):
        extensions = g_extensionsManager.activeExtensions
        extPaths = [ ext.path + ftPath for ext in extensions if rmgr.isFile(ext.path + ftPath) ]
        corePath = [ftPath] if rmgr.isFile(ftPath) else []
        xmlPaths = corePath + extPaths
        if not xmlPaths:
            return rmgr.addToCache(ftPath, xml)
        mergeRequired, mergeType, _ = isExtXML(ftPath)
        if len(xmlPaths) > 1 and not mergeRequired:
            raise SoftException('Multiple standalone resources for one relative path found: %s', ftPath)
        if len(xmlPaths) > 1 and not corePath and mergeType != READ_METHOD.INCLUDE:
            raise SoftException('The operation of merging files for files which are not present in the core is prohibited for the merge type: {t}. File: {f} may be present in different extensions!'.format(t=mergeType, f=ftPath))
        cachedPath = next(iter(xmlPaths))
        return rmgr.addToCache(cachedPath, xml)

    @staticmethod
    def isInCache(filePath):
        func = getattr(rmgr, 'isInCache', None)
        return func(getRealmFilePath(filePath)) or func(filePath) if func is not None else False
