# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/new_year/fade_window.py
import BigWorld
import GUI
import _Scaleform

class FadeWindow(object):

    def __init__(self):
        movieDef = _Scaleform.MovieDef('gui/flash/fadeWindow.swf')
        movie = movieDef.createInstance()
        self.__component = GUI.Flash(movie)
        self.__component.position.z = 0.1
        self.__component.size = (2, 2)
        self.__component.focus = True
        self.__component.moveFocus = True
        self.__component.wg_inputKeyMode = 2

    def activate(self):
        GUI.addRoot(self.__component)
        GUI.reSort()

    def deactivate(self):
        GUI.delRoot(self.__component)

    def setAlpha(self, alpha):
        self.__component.movie.backgroundAlpha = alpha
