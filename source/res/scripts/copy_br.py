# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/copy_br.py
import os
import shutil
from itertools import chain
g_staticComponents = ['BattleRoyaleComponent']
g_dynamicComponents = ['ArenaLootComponent',
 'ArenaMinesComponent',
 'SpawnKeyPointController',
 'BattleXP',
 'ConeVisibility',
 'Radar',
 'InBattleUpgradeReadiness',
 'InBattleUpgrades',
 'VehicleLoot',
 'VehicleDeathZoneEffect',
 'InBattleUpgradesAvatar']
g_entities = ['Mine',
 'Loot',
 'Placement',
 'InfluenceZone',
 'BattleRoyaleRadio']
g_misc = ['vehicle_extras_battle_royale', 'vehicles/common/vehicle_battle_royale', 'vehicles/common/equipments/battle_royale_equipments']
g_all = g_staticComponents + g_dynamicComponents + g_entities + g_misc
ROOT_PATH = './'
EXT_PATH = '../wot_ext/battle_royale/'
g_folders = ['base',
 'cell',
 'client',
 'bot',
 'common',
 'entity_defs',
 'component_defs',
 'user_data_object_defs',
 'item_defs']
g_exts = ['.py', '.def', '.xml']
MODE = 'svn'
extensionXMLpattern = "\n<root>\n    <!-- Arbitrary and unique feature name. It can match <extension_dir> but doesn't have to -->\n    <FeatureName>\n        BattleRoyale\n    </FeatureName>\n    <Components>\n        <StaticComponents>\n            {staticComponents}\n        </StaticComponents>\n        <DynamicComponents>\n            {dynamicComponents}\n        </DynamicComponents>\n    </Components>\n\n    <IsEnabled>\n        True\n    </IsEnabled>\n\n    <Entities>\n        <!-- The list of client-server entities in this feature extension -->\n        <ClientServerEntities>\n            {entities}\n        </ClientServerEntities>\n        <!-- The list of server-only entities in this feature extension -->\n        <ServerOnlyEntities>\n        </ServerOnlyEntities>\n    </Entities>\n\n    <ExternalComponents>\n        <!-- The list of components defined externally -->\n    </ExternalComponents>\n</root>\n"

def mkdir(path):
    try:
        result = os.makedirs(path)
        os.system('svn add {}'.format(path))
        return result
    except OSError:
        if not os.path.isdir(path):
            raise


def makedirsRecursive(name, mode=511):
    head, tail = os.path.split(name)
    if not tail:
        head, tail = os.path.split(head)
    if head and tail and not os.path.exists(head):
        try:
            makedirsRecursive(head, mode)
        except OSError as e:
            if e.errno != os.errno.EEXIST:
                raise

        if tail == os.curdir:
            return
    try:
        os.mkdir(name, mode)
        os.system('svn add {}'.format(name))
    except OSError as e:
        if e.errno != os.errno.EEXIST:
            raise


mkdir = makedirsRecursive

def copyFile(file, ext, folders):
    filename = file + ext
    for folder in folders:
        fullPathFrom = '{}scripts/{}/{}'.format(ROOT_PATH, folder, filename)
        fullPathTo = '{}scripts/{}/{}'.format(EXT_PATH, folder, filename)
        if os.path.exists(fullPathFrom):
            mkdir(os.path.dirname(fullPathTo))
            if MODE == 'move':
                os.rename(fullPathFrom, fullPathTo)
            elif MODE == 'svn':
                os.system('svn move {} {}'.format(fullPathFrom, os.path.dirname(fullPathTo)))
            else:
                shutil.copyfile(fullPathFrom, fullPathTo)

    for xmlFile in ('entities.xml', 'components.xml', 'user_data_objects.xml'):
        with open('{}scripts/{}'.format(ROOT_PATH, xmlFile), 'r+') as f:
            old = f.read()
            f.seek(0)
            f.truncate()
            f.write(old.replace('<{}/>\n'.format(file), ''))


def copyExt(items, exts, folders):
    for file in items:
        for ext in exts:
            copyFile(file, ext, folders)


def generateXML(staticComponents, dynamicComponents, entities):
    magic = '\n\t\t\t'
    result = extensionXMLpattern.replace('{staticComponents}', magic.join([ '<{}/>'.format(name) for name in staticComponents ])).replace('{dynamicComponents}', magic.join([ '<{}/>'.format(name) for name in dynamicComponents ])).replace('{entities}', magic.join([ '<{}/>'.format(name) for name in entities ]))
    with open(EXT_PATH + 'extension.xml', 'w') as f:
        f.write(result)


mkdir(EXT_PATH + 'scripts')
copyExt(g_all, g_exts, g_folders)
generateXML(g_staticComponents, g_dynamicComponents, g_entities)
