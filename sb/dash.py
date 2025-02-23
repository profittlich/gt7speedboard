from PyQt6.QtGui import *
from PyQt6.QtWidgets import *
from PyQt6.QtCore import *

from sb.helpers import logPrint

import sb.components.tyretemps
import sb.components.fuelandmessages
import sb.components.lapheader
import sb.components.mapce
import sb.components.lapcompare
import sb.components.stats
import sb.components.help
import sb.components.pedals
import sb.components.brakeboard
import sb.components.mapopt
import sb.components.mapopting
import sb.components.savelaps
import sb.components.recordingcontroller
import sb.components.lapoptimizer
import sb.components.blank
import sb.components.speed
import sb.components.rpm
import sb.components.gear

class Screen(QStackedWidget):
    def __init__(self, keyRedirect):
        super().__init__()
        self.keyRedirect = keyRedirect

    def keyPressEvent(self, e):
        self.keyRedirect.keyPressEvent(e)


class DashMaker:
    def __init__(self, parent, cfg, data, callbacks, components):
        self.parent = parent
        self.cfg = cfg
        self.data = data
        self.callbacks = callbacks
        self.components = components

        self.usedShortcuts = set()
        self.usedShortcuts.add (Qt.Key.Key_Escape)
        self.usedShortcuts.add (Qt.Key.Key_C)
        self.usedShortcuts.add (Qt.Key.Key_P)
        self.usedShortcuts.add (Qt.Key.Key_Equal)
        self.usedShortcuts.add (Qt.Key.Key_Minus)
        self.usedShortcuts.add (Qt.Key.Key_Left)
        self.usedShortcuts.add (Qt.Key.Key_Right)

    def createComponent(self, e): # TODO: Consider putting screen creation into its own class
        newComponent = sb.component.componentLibrary[e['component']](self.cfg, self.data, self.callbacks)
        if "title" in e:
            newComponent.setTitle (e['title'])
        if "fontScale" in e:
            logPrint("Scale font", e['fontScale'])
            newComponent.setFontScale (float(e['fontScale']))

        title = newComponent.title()
        shortcuts = []
        self.components.append(newComponent)
        if 'shortcut' in e:
            if e['shortcut'] in Qt.Key.__dict__:
                if not Qt.Key.__dict__[e['shortcut']] in self.usedShortcuts:
                    shortcuts.append((Qt.Key.__dict__[e['shortcut']], e['shortcut'], title))
                    self.usedShortcuts.add(Qt.Key.__dict__[e['shortcut']])
                else:
                    QMessageBox.critical(self, "Duplicate keyboard shortcut", "Duplicate keyboard shortcut in configuration.\n" + e['shortcut'] + " will not be used for page of component " + e['component'] + "!")
        if 'actions' in e:
            for k in e['actions']:
                if k in Qt.Key.__dict__:
                    if not Qt.Key.__dict__[k] in self.usedShortcuts:
                        self.data.componentKeys[Qt.Key.__dict__[k]] = (newComponent, e['actions'][k], k)
                        self.usedShortcuts.add(Qt.Key.__dict__[k])
                    else:
                        QMessageBox.critical(self, "Duplicate keyboard shortcut", "Duplicate keyboard shortcut in configuration.\n" + k + " will not be used for component " + e['component'] + "!")
        widget = None
        if title is None:
            print("New component:", e['component'])
            widget = newComponent.getWidget()
        else:
            print("New component:", title)
            widget = newComponent.getTitledWidget(title)
        return (widget, shortcuts)

    def makeDashEntry(self, e, horizontal = True):
        page = QWidget()
        shortcuts = []
        if horizontal:
            layout = QHBoxLayout()
        else:
            layout = QVBoxLayout()
        layout.setContentsMargins(0,0,0,0)
        page.setLayout(layout)
        if "list" in e:
            for c in e['list']:
                w = self.makeDashEntry(c, not horizontal)
                if not w[0] is None:
                    layout.addWidget(w[0], w[1])
                shortcuts += w[2]
        elif "component" in e:
            print(e['component'])
            compWidget, s = self.createComponent(e)
            shortcuts += s
            if not compWidget is None:
                layout.addWidget (compWidget)
        stretch = 1
        if 'stretch' in e:
            stretch = e['stretch']
        if layout.count() == 0:
            return [None, stretch, shortcuts]
        return [page, stretch, shortcuts]

    def makeDashPage(self, e):
        shortcuts = []
        page = QWidget()
        layout = QVBoxLayout()
        layout.setContentsMargins(0,0,0,0)
        page.setLayout(layout)
        if isinstance(e, list):
            print("Page with multiple components")
            for c in e:
                w = self.makeDashEntry(c)
                shortcuts += w[2]
                layout.addWidget(w[0], w[1])
        elif isinstance(e, dict):
            print("Page:", e['component'])
            compWidget, s = self.createComponent(e)
            shortcuts += s
            if not compWidget is None:
                layout.addWidget (compWidget)
        if layout.count () == 0:
            return (None, shortcuts)
        return (page, shortcuts)


    def makeDashScreen(self, e):
        print("Screen")
        screen = Screen(self.parent)
        for c in e:
            p, s = self.makeDashPage(c)
            if not p is None:
                screen.addWidget(p)
            for i in s:
                self.data.pageKeys[i[0]] = (screen, screen.count()-1, i[1], i[2])
        return screen

    def makeDashFromSpec(self, spec):
        screens = []
        for c in spec:
            screens.append(self.makeDashScreen(c))
        return screens
        

