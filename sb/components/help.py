from PyQt6.QtGui import *
from PyQt6.QtWidgets import *
from PyQt6.QtCore import *

import datetime
import sb.component
from sb.gt7widgets import *
from sb.gt7telepoint import Point
from sb.helpers import logPrint

class Help(sb.component.Component):
    def description():
        return "List of keyboard shortcuts"
    
    def __init__(self, cfg, data):
        super().__init__(cfg, data)

        self.pageScroller = QScrollArea()
        self.widget = QLabel("KEYBOARD SHORTCUTS:\n\n" + shortcutText)
        self.pageScroller.setWidget(self.widget)
        font = self.widget.font()
        font.setPointSize(cfg.fontSizeVerySmall)
        font.setBold(True)
        self.widget.setFont(font)
        self.widget.setAlignment(Qt.AlignmentFlag.AlignLeft)
        pal = self.widget.palette()
        pal.setColor(self.widget.backgroundRole(), cfg.backgroundColor)
        pal.setColor(self.widget.foregroundRole(), cfg.foregroundColor)
        self.widget.setMargin(15)
        self.widget.setPalette(pal)

        self.pageScroller.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOn)
        self.pageScroller.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.pageScroller.setWidgetResizable(True)

    def getWidget(self):
        return self.pageScroller

    def title(self):
        return "Help"

    def newSession(self):
        newText = "KEYBOARD SHORTCUTS:\n\n" + shortcutText
        for k in self.data.componentKeys:
            key = self.data.componentKeys[k]
            actions = key[0].__class__.actions()
            logPrint(actions)
            if key[1] in actions:
                newText += "\n" + key[2].replace("Key_", "") + "\t " + actions[key[1]]
            else:
                newText += "\n" + key[2].replace("Key_", "") + "\t unknown action"
        self.widget.setText(newText)


sb.component.componentLibrary['Help'] = Help
