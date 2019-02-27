from Katana import QtCore, QtGui, UI4, QT4Widgets, QT4FormWidgets

import ScriptActions as SA

import logging
log = logging.getLogger('MaterialXBakeEditor')

# Class Definitions -----------------------------------------------------------

class MaterialXBakeEditor(QtGui.QWidget):
    """
    Example of a Super Tool editing widget that displays:
        - Its own parameters.
        - Parameters from node's in the SuperTool's internal node network.
        - Custom Qt Widgets.
    """

    # Initializer -------------------------------------------------------------

    def __init__(self, parent, node):
        """
        Initializes an instance of the class.
        """
        QtGui.QWidget.__init__(self, parent)

        self.__node = node

        # Get the SuperTool's parameters
        rootLocationsParameter = self.__node.getParameter('rootLocations')
        passesParameter = self.__node.getParameter('passes')
        saveToParameter = self.__node.getParameter('saveTo')
        writeMatexOutButton = self.__node.getParameter("writeMaterialxOut")

        CreateParameterPolicy = UI4.FormMaster.CreateParameterPolicy
        self.__rootLocationsParameterPolicy = CreateParameterPolicy(
            None, rootLocationsParameter)

        self.__passesParameterPolicy = CreateParameterPolicy(
            None, passesParameter)

        self.__saveToParameterPolicy = CreateParameterPolicy(
            None, saveToParameter)

        self.__writeMatexOutButtonPolicy = CreateParameterPolicy(
                None, writeMatexOutButton)

        WidgetFactory = UI4.FormMaster.KatanaFactory.ParameterWidgetFactory
        rootLocationsWidget = WidgetFactory.buildWidget(
            self, self.__rootLocationsParameterPolicy)
        passesWidget = WidgetFactory.buildWidget(
            self, self.__passesParameterPolicy)
        saveToWidget = WidgetFactory.buildWidget(
            self, self.__saveToParameterPolicy)
        writeMatexOutButtonWidget = WidgetFactory.buildWidget(
            self, self.__writeMatexOutButtonPolicy)

        # Build a group widget
        self.group_layout = passesWidget.getPopdownWidget().layout()
        self.add_button = QtGui.QPushButton("Add New Pass")
        self.remove_button = QtGui.QPushButton("Remove Last Pass")
        self.connect(
                self.add_button,
                QtCore.SIGNAL('clicked(bool)'),
                self.onAddButtonPressed)
        self.connect(
                self.remove_button,
                QtCore.SIGNAL('clicked(bool)'),
                self.onRemoveButtonPressed)

        # parameter = self.__node.getParameters().getChild("look_origin")
        # if not parameter:
        #     parameter = self.__node.getParameters().createChildString("look_origin", 'default')
        # policy = UI4.FormMaster.CreateParameterPolicy(None, parameter)
        # widget = WidgetFactory.buildWidget(self, policy)

        if not passesParameter.getChild("default"):
            passesParameter.createChildString("default", 'default')

        self.button_layout = QtGui.QHBoxLayout()
        self.button_layout.addWidget(self.add_button)
        self.button_layout.addWidget(self.remove_button)
        self.group_layout.addLayout( self.button_layout );

        line = QtGui.QFrame()
        line.setFrameShape( QtGui.QFrame.HLine )
        line.setFrameShadow( QtGui.QFrame.Sunken )

        # Create a layout and add the parameter editing widgets to it
        mainLayout = QtGui.QVBoxLayout()
        mainLayout.addWidget(rootLocationsWidget)
        mainLayout.addWidget(passesWidget)
        mainLayout.addWidget(line)
        mainLayout.addWidget(saveToWidget)
        mainLayout.addWidget(writeMatexOutButtonWidget)
        # Apply the layout to the widget
        self.setLayout(mainLayout)

    # Public Functions --------------------------------------------------------
    def OnAddPressed(self):
        switch_node = SA.GetRefNode(self.__node, 'switch')
        WidgetFactory = UI4.FormMaster.KatanaFactory.ParameterWidgetFactory
        index = self.passes_layout.count() + 1
        name = 'look_%i'%index
        parameter = self.__node.getParameters().createChildString(name, name)
        policy = UI4.FormMaster.CreateParameterPolicy(None, parameter)
        widget = WidgetFactory.buildWidget(self, policy)
        self.passes_layout.addWidget(widget)
        self.__node.addInputPort(name)
        self_node_port = self.__node.getSendPort(name)
        switch_node_port = switch_node.addInputPort(name)
        self_node_port.connect(switch_node_port)

    def onAddButtonPressed(self):
        switch_node = SA.GetRefNode(self.__node, 'switch')
        parameter = self.__node.getParameter('passes')
        size = len(parameter.getChildren())

        if size >= 1 and size <= 14:
            name = "look_%s"%SA.ALPHABET[size -1]
            parameter.createChildString(name,name)

            self.__node.addInputPort(name)
            self_node_port = self.__node.getSendPort(name)
            switch_node_port = switch_node.addInputPort(name)
            self_node_port.connect(switch_node_port)

    def onRemoveButtonPressed(self):
        switch_node = SA.GetRefNode(self.__node, 'switch')
        parameter = self.__node.getParameter('passes')
        size = len(parameter.getChildren())
        
        if size >= 2 and size <= 15:
            name = "look_%s"%SA.ALPHABET[size -2]
            parameter.deleteChild(parameter.getChild(name))

            self.__node.removeInputPort(name)
            switch_node.removeInputPort(name)

    def OnRemovePressed(self):
        return
        switch_node = SA.GetRefNode(self.__node, 'switch')
        layout = self.passes_layout
        index = self.passes_layout.count()
        if layout is not None:
            item = layout.takeAt(index-1)
            if item is not None:
                widget = item.widget()
                widget.deleteLater()
                name = 'look_%i'%index
                self.__node.removeInputPort(name)
                switch_node.removeInputPort(name)
                parameter = self.__node.getParameters().getChild(name)
                self.__node.getParameters().deleteChild(parameter)
        UI4.FormMaster.ClearCache()