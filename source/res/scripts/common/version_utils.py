# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/common/version_utils.py
from debug_utils import *
from soft_exception import SoftException
_VERSION_REGEXP = re.compile('^([a-z]{2,4}_)?(([0-9]+\\.){2,4}[0-9]+)(_[0-9]+)?[ ]{0,}#[ ]{0,}([0-9]+)$')

def parseVersion(version):
    result = _VERSION_REGEXP.search(version)
    if result is None:
        return
    else:
        realmCode, mainVersion, _, patchVersion, clientVersion = result.groups()
        if mainVersion:
            realmCode = realmCode.replace('_', '') if realmCode else ''
            patchVersion = int(patchVersion.replace('_', '')) if patchVersion else 0
            return (realmCode,
             mainVersion,
             patchVersion,
             int(clientVersion))
        return


def isValidClientVersion(clientVersion, serverVersion):
    if clientVersion != serverVersion:
        if clientVersion is None or serverVersion is None:
            return False
        clientParsedVersion = parseVersion(clientVersion)
        serverParsedVersion = parseVersion(serverVersion)
        if clientParsedVersion is None or serverParsedVersion is None:
            return False
        clientRealmCode, clientMainVersion, clientPatchVersion, clientClientVersion = clientParsedVersion
        serverRealmCode, serverMainVersion, serverPatchVersion, serverClientVersion = serverParsedVersion
        if clientRealmCode != serverRealmCode:
            return False
        if clientMainVersion != serverMainVersion:
            return False
        if clientPatchVersion < serverPatchVersion:
            return False
        if clientClientVersion < serverClientVersion:
            return False
    return True


def getClientMainVersion(clientVersionGetter):
    mainVersion = None
    try:
        _, clientVersion = readClientServerVersion(clientVersionGetter)
        _, mainVersion, _, _ = parseVersion(clientVersion)
    except SoftException:
        LOG_CURRENT_EXCEPTION()

    return mainVersion


__ATTR_NAME = None
__VERSION = None

def readClientServerVersion(clientVersionGetter):
    global __ATTR_NAME
    global __VERSION
    attrName = __ATTR_NAME
    version = __VERSION
    if attrName is None or version is None:
        import ResMgr
        fileName = 'scripts/entity_defs/interfaces/AccountVersion.def'
        section = ResMgr.openSection(fileName)
        if section is None:
            raise SoftException('Cannot open ' + fileName)
        for attrName, section in section['Properties'].items():
            if not attrName.startswith('requiredVersion_'):
                continue
            version = section.readString('Default')
            if not version:
                raise SoftException('Subsection AccountVersion.def/Properties/{}/Default is missing or empty'.format(attrName))
            ResMgr.purge(fileName)
            __ATTR_NAME = attrName
            __VERSION = version
            break

    if attrName is None:
        raise SoftException('Field AccountVersion.def/Properties/requiredVersion_* is not found')
    version = '{}#{}'.format(version, clientVersionGetter())
    return (attrName, version)
