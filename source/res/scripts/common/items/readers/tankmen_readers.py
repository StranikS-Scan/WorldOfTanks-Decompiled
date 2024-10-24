# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/common/items/readers/tankmen_readers.py
import typing
import ResMgr
from constants import IS_CLIENT, IS_WEB, IS_BOT
from items import _xml
from items.components import component_constants, skills_constants
from items.components import shared_components
from items.components import tankmen_components
if typing.TYPE_CHECKING:
    from typing import Dict, Callable, Optional, Tuple

def _parseName(xmlCtx, section):
    return shared_components.I18nString(_xml.readNonEmptyString(xmlCtx, section, component_constants.EMPTY_STRING)).value


def _parseIcon(xmlCtx, section):
    return _xml.readNonEmptyString(xmlCtx, section, component_constants.EMPTY_STRING)


def _readIDs(xmlCtx, subsections, accumulator, parser=None, optimizationNeeded=False, optimizationCache=None):
    res = set()
    strCache = optimizationCache if optimizationCache is not None else {}
    for sname, subsection in subsections:
        try:
            contentID = int(sname[1:])
        except ValueError:
            contentID = -1

        if sname[0] != '_' or not 0 <= contentID <= 65535:
            _xml.raiseWrongSection(xmlCtx, sname)
        if contentID in accumulator:
            _xml.raiseWrongXml(xmlCtx, sname, 'ID is not unique')
        if parser is not None:
            resultStr = parser((xmlCtx, sname), subsection)
        else:
            resultStr = component_constants.EMPTY_STRING
        if optimizationNeeded:
            resultStr = _searchAndUpdateStrInCache(resultStr, strCache)
        accumulator[contentID] = resultStr
        res.add(contentID)

    if not res:
        _xml.raiseWrongXml(xmlCtx, '', 'is empty')
    return res


def _searchAndUpdateStrInCache(value, strCache):
    strHash = hash(value)
    strInCache = strCache.get(strHash)
    if strInCache is not None:
        value = strInCache
    else:
        strCache[strHash] = value
    return value


def _readRanks(xmlCtx, subsections):
    ranks = tankmen_components.RanksSet()
    for sname, subsection in subsections:
        if ranks.getRankByName(sname) is not None:
            _xml.raiseWrongXml(xmlCtx, sname, 'is not unique')
        sname = intern(sname)
        ctx = (xmlCtx, sname)
        if IS_CLIENT or IS_WEB:
            i18n = shared_components.I18nString(_xml.readNonEmptyString(ctx, subsection, 'userString'))
            icon = _parseIcon((ctx, 'icon'), _xml.getSubsection(ctx, subsection, 'icon'))
            rank = tankmen_components.Rank(sname, i18n=i18n, icon=icon)
        else:
            rank = tankmen_components.Rank(sname)
        ranks.add(rank)

    return ranks


def _readRoleRanks(xmlCtx, section, ranks):
    roleRanks = tankmen_components.RoleRanks()
    for roleName in skills_constants.ROLES:
        rankIDs = []
        for rankName in _xml.readNonEmptyString(xmlCtx, section, roleName).split():
            rankIDs.append(ranks.getIDByName(rankName))

        roleRanks.setRanksIDs(roleName, tuple(rankIDs))

    return roleRanks


def _readGroupTags(xmlCtx, section, subsectionName):
    source = _xml.readStringOrNone(xmlCtx, section, subsectionName)
    if source is not None:
        from items import vehicles
        tags = source.split()
        restrictions = []
        for tag in tags:
            if not (tag in tankmen_components.GROUP_TAG.RANGE or vehicles.g_list.isVehicleExisting(tag)):
                _xml.raiseWrongXml(xmlCtx, subsectionName, 'unknown tag "{}"'.format(tag))
            if tag in tankmen_components.GROUP_TAG.RESTRICTIONS:
                restrictions.append(tag)

        if restrictions and tankmen_components.GROUP_TAG.PASSPORT_REPLACEMENT_FORBIDDEN not in restrictions:
            _xml.raiseWrongXml(xmlCtx, subsectionName, 'Group contains tags of restrictions {}, so tag "{}" is mandatory'.format(restrictions, tankmen_components.GROUP_TAG.PASSPORT_REPLACEMENT_FORBIDDEN))
    else:
        tags = []
    return frozenset(tags)


def _readGroupRoles(xmlCtx, section, subsectionName):
    source = _xml.readStringOrNone(xmlCtx, section, subsectionName)
    if source is not None:
        tags = source.split()
        roles = []
        for tag in tags:
            if tag not in skills_constants.ROLES:
                _xml.raiseWrongXml(xmlCtx, subsectionName, 'unknown tag "{}"'.format(tag))
            roles.append(intern(tag))

    else:
        tags = skills_constants.ROLES
    return frozenset(tags)


def _readTankmenGroup(xmlCtx, groupName, subsection, firstNames, lastNames, icons, optimizationCache=None):
    hasLocalizedName = IS_CLIENT or IS_WEB or IS_BOT
    if hasLocalizedName:
        parseName = _parseName
        parseIcon = _parseIcon
    else:
        parseName = parseIcon = None
    return tankmen_components.NationGroup(_xml.readNonNegativeInt(xmlCtx, subsection, 'groupID'), groupName, 'female' == _xml.readNonEmptyString(xmlCtx, subsection, 'sex'), subsection.readBool('notInShop', False), _readIDs((xmlCtx, 'firstNames'), _xml.getChildren(xmlCtx, subsection, 'firstNames'), firstNames, parseName, optimizationNeeded=hasLocalizedName, optimizationCache=optimizationCache), _readIDs((xmlCtx, 'lastNames'), _xml.getChildren(xmlCtx, subsection, 'lastNames'), lastNames, parseName, optimizationNeeded=hasLocalizedName, optimizationCache=optimizationCache), _readIDs((xmlCtx, 'icons'), _xml.getChildren(xmlCtx, subsection, 'icons'), icons, parseIcon), _xml.readNonNegativeFloat(xmlCtx, subsection, 'weight'), _readGroupTags((xmlCtx, 'tags'), subsection, 'tags'), _readGroupRoles((xmlCtx, 'roles'), subsection, 'roles'))


def _readNationConfigSection(xmlCtx, section):
    config = {}
    firstNames = {}
    lastNames = {}
    icons = {}
    optimizationCache = {}
    for kindName in component_constants.TANKMEN_GROUPS:
        groups = []
        totalWeight = 0.0
        groupIDs = set()
        for sname, subsection in _xml.getChildren(xmlCtx, section, kindName):
            ctx = (xmlCtx, kindName + '/' + sname)
            group = _readTankmenGroup(ctx, sname, subsection, firstNames, lastNames, icons, optimizationCache=optimizationCache)
            groupID = group.groupID
            if groupID in groupIDs:
                _xml.raiseWrongXml(xmlCtx, sname, 'duplicate groupID %d' % groupID)
            groupIDs.add(groupID)
            totalWeight += group.weight
            groups.append(group)

        totalWeight = max(0.001, totalWeight)
        for group in groups:
            group.weight /= totalWeight

        config[kindName] = {group.groupID:group for group in groups}

    ranks = _readRanks((xmlCtx, 'ranks'), _xml.getChildren(xmlCtx, section, 'ranks'))
    config['roleRanks'] = _readRoleRanks((xmlCtx, 'roleRanks'), _xml.getSubsection(xmlCtx, section, 'roleRanks'), ranks)
    if IS_CLIENT or IS_WEB or IS_BOT:
        config['firstNames'] = firstNames
        config['lastNames'] = lastNames
        config['icons'] = icons
        config['ranks'] = ranks
    else:
        config['firstNames'] = frozenset(firstNames)
        config['lastNames'] = frozenset(lastNames)
        config['icons'] = frozenset(icons)
    return tankmen_components.NationConfig(xmlCtx[1], **config)


def readNationConfig(xmlPath):
    section = ResMgr.openSection(xmlPath)
    if section is None:
        _xml.raiseWrongXml(None, xmlPath, 'can not open or read')
    config = _readNationConfigSection((None, xmlPath), section)
    ResMgr.purge(xmlPath, True)
    return config


def readLoreConfig(xmlPath):
    xmlCtx = (None, xmlPath)
    section = ResMgr.openSection(xmlPath)
    if section is None:
        _xml.raiseWrongXml(None, xmlPath, 'can not open or read')
    config = tankmen_components.LoreComponent()
    for partName, part in _xml.getChildren(xmlCtx, section, tankmen_components.LoreComponent.SECTION):
        config.addDescrForGroup(partName, part.asString)
        if part.has_key(tankmen_components.LoreComponent.NATION_SECTION):
            for itemName, item in _xml.getChildren(xmlCtx, part, tankmen_components.LoreComponent.NATION_SECTION):
                config.addNationDescrForGroup(partName, itemName, item.asString)

    return config
