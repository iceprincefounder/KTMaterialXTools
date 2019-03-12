try:
  from Katana import QtGui
except:
  from PyQt4 import QtGui

class Widget(QtGui.QWidget):
    def __init__(self, parent=None):
        QtGui.QWidget.__init__(self, parent)
