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

sb.component.componentLibrary['Help'] = Help
