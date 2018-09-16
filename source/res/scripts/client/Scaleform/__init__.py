# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/Scaleform/__init__.py
AVAILABLE = False
try:
    from _Scaleform import *
    AVAILABLE = True
except ImportError:
    print 'There is no module named _Scaleform.  The most likely cause of this \tis the client was built without Scaleform support.  Please check the \tdocumentation for further details on enabling Scaleform support.'

def showCursor():
    import GUI
    import BigWorld
    c = GUI.mcursor()
    c.visible = 1
    BigWorld.setCursor(c)


def exampleFSCommandHandler(cmd, s2):
    print 'FSCommand - ', cmd, s2


def exampleExternalInterfaceHandler(cmd, *args):
    print 'External Interface command - ', cmd, args


def createMovieInstance(file='scaleform/d3d9guide.swf'):
    mv = None
    mvDef = MovieDef(file)
    mv = mvDef.createInstance()
    mv.backgroundAlpha = 0.0
    mv.setFSCommandCallback(exampleFSCommandHandler)
    mv.setExternalInterfaceCallback(exampleExternalInterfaceHandler)
    mv.setFocussed()
    return (mv, mvDef)


def create3DDemo():
    file = 'scaleform/dogfight.swf'
    return createMovieInstance(file)


def createMovieGUI(file='scaleform/d3d9guide.swf'):
    m, d = createMovieInstance(file)
    import GUI
    for i in GUI.roots():
        i.position[2] = max(i.position[2], 0.1)

    f = GUI.Flash(m)
    f.position = (0, 0, 0)
    f.focus = True
    f.moveFocus = True
    GUI.addRoot(f)
    showCursor()
    return f


def createIMEFontsMovie():
    file = 'scaleform/fonts_all.swf'
    m, d = createMovieInstance(file)
    d.setAsFontMovie()
    d.addToFontLibrary()


def createIME():
    mapFont('$IMECandidateListFont', 'SimSun')
    mapFont('$IMELanguageBar', 'SimSun')
    mapFont('$IMESample', 'SimSun')
    createIMEFontsMovie()
    showCursor()


def createIMEMovie():
    file = 'scaleform/IMESample.swf'
    return createMovieInstance(file)


def createFontMovie(file='scaleform/drawtext_fonts.swf'):
    m, d = createMovieInstance(file)
    d.setAsFontMovie()
    d.addToFontLibrary()


def createAllFontsMovie():
    file = 'scaleform/fonts_all.swf'
    m, d = createMovieInstance(file)
    d.setAsFontMovie()
    d.addToFontLibrary()


def createFlashText(fontName='Slate Mobile'):
    import GUI
    g = GUI.FlashText(u'some label', fontName)
    g.size = (2, 2)
    g.position = (0, 0, 0)
    return g
