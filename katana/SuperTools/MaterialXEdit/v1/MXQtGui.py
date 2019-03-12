try:
  from Katana import QtGui
except:
  from PyQt4 import QtGui

class MaterialXEditor(QtGui.QWidget):
    def __init__(self, parent=None):
        QtGui.QWidget.__init__(self, parent)

        main_lay = QtGui.QHBoxLayout()
        self.listWidget = QtGui.QListView()

        self.editorWidget = QtGui.QWidget()
        self.editorWidget.setMinimumWidth(250)
        main_lay.addWidget(self.listWidget)
        main_lay.addWidget(self.editorWidget)

        self.setLayout(main_lay)
if __name__ == '__main__':

    import sys
    app = QtGui.QApplication(sys.argv)
    window = MaterialXEditor(None)
    window.show()
    sys.exit(app.exec_())