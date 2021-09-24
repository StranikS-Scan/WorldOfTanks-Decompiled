# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/create_component.py
import os
import shutil
ROOT_PATH = './'
g_pyFolders = ['cell/', 'client/']
g_defFolders = ['component_defs/']
componentDefPattern = '\n<root>\n    <Properties>\n{0}\n    </Properties>\n\n    <ofEntity>\n        <{1}/>\n    </ofEntity>\n\n    <DefaultKeyName> {2} </DefaultKeyName>\n</root>\n'[1:]
propertyPattern = '\n        <{0}>\n            <Type> {1} </Type>\n            <Flags> ALL_CLIENTS </Flags>\n        </{0}>\n'[1:-1]
componentPyPattern = '\nimport BigWorld\nfrom script_component.DynamicScriptComponent import DynamicScriptComponent\n\n\nclass {0}(DynamicScriptComponent):\n    def __init__(self):\n        super({0}, self).__init__()\n'[1:]

def generate(name, properties, host):
    with open(ROOT_PATH + 'components.xml', 'r+') as f:
        data = f.read()
        if '<{0}/>'.format(name) not in data:
            data = data.replace('</DynamicComponents>', '\t<{0}/>\n\t</DynamicComponents>'.format(name))
            f.seek(0)
            f.write(data)
            f.truncate()
    for folder in g_pyFolders:
        with open(ROOT_PATH + folder + name + '.py', 'w') as f:
            data = componentPyPattern.format(name)
            f.write(data)

    for folder in g_defFolders:
        with open(ROOT_PATH + folder + name + '.def', 'w') as f:
            data = componentDefPattern.format('\n'.join([ propertyPattern.format(n, t) for n, t in properties ]), host, name[0].capitalize().swapcase() + name[1:])
            f.write(data)


def delete(name):
    with open(ROOT_PATH + 'components.xml', 'r+') as f:
        data = f.read()
        if '<{0}/>'.format(name) in data:
            data = data.replace('\t\t<{0}/>\n'.format(name), '')
            f.seek(0)
            f.write(data)
            f.truncate()
    for folder in g_pyFolders:
        os.remove(ROOT_PATH + folder + name + '.py')

    for folder in g_defFolders:
        os.remove(ROOT_PATH + folder + name + '.def')


GENERATE = True
REMOVE = False
if GENERATE:
    generate('WTBoss', [('radius', 'FLOAT32')], 'Entity')
if REMOVE:
    delete('DurationComponent')
