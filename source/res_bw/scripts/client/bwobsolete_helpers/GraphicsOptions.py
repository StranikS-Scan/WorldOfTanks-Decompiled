# Python 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/bwobsolete_helpers/GraphicsOptions.py
import ResMgr
import sys
import BigWorld
tex_detail_levels = ResMgr.openSection('system/data/texture_detail_levels.xml')

def normalMapsCompressed():
    ns = tex_detail_levels.values()[0]
    if ns.readString('format') == 'A8R8G8B8':
        return False
    return True


def compressNormalMaps(state):
    ns = tex_detail_levels.values()[0]
    ns.writeString('format', 'A8R8G8B8')
    BigWorld.reloadTextures()


def optIncludeOptionEnabled(value):
    filename = '../../bigworld/res/shaders/std_effects/optinclude.fxh'
    try:
        f = open(filename, 'r')
    except IOError:
        print 'Failed to open %s' % (filename,)
        return

    output = []
    lines = f.readlines()
    changed = False
    found = False
    for line in lines:
        if value in line:
            found = True
            if '//' in line:
                return False
            return True

    return False


def enableOptincludeOption(value, enable):
    filename = '../../bigworld/res/shaders/std_effects/optinclude.fxh'
    try:
        f = open(filename, 'r')
    except IOError:
        print 'Failed to open %s' % (filename,)
        return

    output = []
    lines = f.readlines()
    changed = False
    found = False
    for line in lines:
        if value in line:
            found = True
            if '//' in line:
                if enable:
                    line = '#define ' + value + ' 1\n'
                    changed = True
            elif not enable:
                line = '//#define ' + value + ' 1\n'
                changed = True
        output.append(line)

    if enable and not found:
        output.append('#define ' + value + ' 1')
        changed = True
    f.close()
    if changed and len(output) > 0:
        f = open(filename, 'w+')
        if f == None:
            print 'Could not open %s for writing' % (filename,)
            return
        f.writelines(output)
        f.close()
    return
