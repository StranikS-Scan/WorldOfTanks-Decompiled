# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/bwobsolete_tests/Fonts.py
import BigWorld
import ResMgr
import GUI
import math
fontTestGUIs = []

def removeAll():
    global fontTestGUIs
    for i in fontTestGUIs:
        GUI.delRoot(i)

    fontTestGUIs = []


def _showFont(fontName, pos=(-1, -1, 0.5), size=(2, 2)):
    import GUI
    s = GUI.Simple('')
    GUI.addRoot(s)
    fontTestGUIs.append(s)
    s.materialFX = 'BLEND'
    s.textureName = fontName.lower() + '.dds'
    s.position = pos
    s.verticalAnchor = 'BOTTOM'
    s.horizontalAnchor = 'LEFT'
    s.filterType = 'LINEAR'
    s.size = size
    s.label = GUI.Text(fontName.lower())
    s.label.verticalAnchor = 'TOP'
    s.label.horizontalAnchor = 'LEFT'
    s.label.font = 'system_small.font'
    s.label.materialFX = 'BLEND'
    s.label.colour = (255, 192, 128, 255)
    s.label.position = s.position + (0, size[1], -0.01)
    return s


def getAllFontNames():
    l = []
    all = ResMgr.openSection('system/fonts')
    for name, ds in all.items():
        if name.endswith('.font'):
            l.append(name)

    return l


def showAllFonts():
    removeAll()
    fonts = getAllFontNames()
    nFonts = len(fonts)
    nx = math.floor(math.sqrt(nFonts))
    ny = math.ceil(float(nFonts) / float(nx))
    dx = 2.0 / nx
    dy = 2.0 / ny
    z = 0.5
    idx = 0
    for y in xrange(0, ny):
        for x in xrange(0, nx):
            s = _showFont(fonts[idx], (-1.0 + x * dx, -1.0 + y * dy, z), (dx, dy))
            fontTestGUIs.append(s)
            idx += 1
            if idx == nFonts:
                break

    return s


def showFont(idx):
    removeAll()
    fonts = getAllFontNames()
    s = _showFont(fonts[idx % len(fonts)], (0, 0, 0.5), (0, 0))
    s.filterType = 'POINT'


def showFDFont():
    s = GUI.Simple('')
    s.position = (0, 0, 0)
    GUI.addRoot(s)
    s.materialFX = 'SOLID'
    s.textureName = 'fantasydemofont_20_font_rt'
    s.size = (2, 2)


def testResize1():
    t = GUI.Text('resize')
    t.font = 'resize.font'
    GUI.addRoot(t)
    fontTestGUIs.append(t)
    t.verticalAnchor = 'BOTTOM'
    _showFont('resize.font')
    return t


def testResize2():
    t2 = GUI.Text('resizebgman')
    t2.font = 'resize.font'
    GUI.addRoot(t2)
    t2.verticalAnchor = 'TOP'
    fontTestGUIs.append(t2)
    return t2


def testResize():
    removeAll()
    testResize1()
    BigWorld.callback(1, testResize2)
