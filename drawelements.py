class CrossMarker:
    def __init__(self, group, x1, z1, color, bold=2):
        self.group = group
        self.x1 = x1
        self.z1 = z1
        self.color = color
        self.bold = bold

class PlusMarker:
    def __init__(self, group, x1, z1, color, bold=2):
        self.group = group
        self.x1 = x1
        self.z1 = z1
        self.color = color
        self.bold = bold

class SquareMarker:
    def __init__(self, group, x1, z1, color, bold=2):
        self.group = group
        self.x1 = x1
        self.z1 = z1
        self.color = color
        self.bold = bold

class CircleMarker:
    def __init__(self, group, x1, z1, color, bold=2):
        self.group = group
        self.x1 = x1
        self.z1 = z1
        self.color = color
        self.bold = bold

class UpMarker:
    def __init__(self, group, x1, z1, color, bold=2, text=None):
        self.group = group
        self.x1 = x1
        self.z1 = z1
        self.color = color
        self.bold = bold
        self.text = text

class DownMarker:
    def __init__(self, group, x1, z1, color, bold=2, text=None):
        self.group = group
        self.x1 = x1
        self.z1 = z1
        self.color = color
        self.bold = bold
        self.text = text

class LeftLineMarker:
    def __init__(self, group, x1, z1, x2, z2, color, bold=2, length=100, endText = None):
        self.group = group
        self.x1 = x1
        self.z1 = z1
        self.x2 = x2
        self.z2 = z2
        self.color = color
        self.bold = bold
        self.length = length
        self.endText = endText

class Text:
    def __init__(self, group, x1, z1, text, offsetx, offsetz, color, bold=2):
        self.group = group
        self.x1 = x1
        self.z1 = z1
        self.offsetx = offsetx
        self.offsetz = offsetz
        self.text = text
        self.color = color
        self.bold = bold

class Line:
    def __init__(self, group, x1, z1, x2, z2, color, bold=2):
        self.group = group
        self.x1 = x1
        self.z1 = z1
        self.x2 = x2
        self.z2 = z2
        self.color = color
        self.bold = bold

class Triangle:
    def __init__(self, group, x1, z1, x2, z2, x3, z3, color):
        self.group = group
        self.x1 = x1
        self.z1 = z1
        self.x2 = x2
        self.z2 = z2
        self.x3 = x3
        self.z3 = z3
        self.color = color


