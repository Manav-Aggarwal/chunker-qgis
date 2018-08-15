# -*- coding: utf-8 -*-
"""
/***************************************************************************
 SaveChunk
                                 A QGIS plugin
 Saves a chunk to the desired location
 Generated by Plugin Builder: http://g-sherman.github.io/Qgis-Plugin-Builder/
                              -------------------
        begin                : 2018-07-26
        git sha              : $Format:%H$
        copyright            : (C) 2018 by Skylark Drones
        email                : manav@stanford.edu
 ***************************************************************************/

/***************************************************************************
 *                                                                         *
 *   This program is free software; you can redistribute it and/or modify  *
 *   it under the terms of the GNU General Public License as published by  *
 *   the Free Software Foundation; either version 2 of the License, or     *
 *   (at your option) any later version.                                   *
 *                                                                         *
 ***************************************************************************/
"""
from PyQt5.QtCore import QSettings, QTranslator, qVersion, QCoreApplication, QThread
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import (QApplication, QWidget, QFileDialog, QHBoxLayout,
                             QPushButton, QVBoxLayout, QLabel, QLineEdit, QStatusBar,
                             QFileDialog, QAction, QMessageBox)
from qgis.core import QgsMessageLog, QgsVectorDataProvider, QgsVectorFileWriter, QgsField, QgsProject

# Initialize Qt resources from file resources.py
from .resources import *
# Import the code for the dialog
from .save_chunk_dialog import SaveChunkDialog
import os.path
import shutil
from time import sleep

class SaveChunk:
    """QGIS Plugin Implementation."""

    def __init__(self, iface):
        """Constructor.

        :param iface: An interface instance that will be passed to this class
            which provides the hook by which you can manipulate the QGIS
            application at run time.
        :type iface: QgsInterface
        """
        # Save reference to the QGIS interface
        self.iface = iface
        # initialize plugin directory
        self.plugin_dir = os.path.dirname(__file__)
        # initialize locale
        locale = QSettings().value('locale/userLocale')[0:2]
        locale_path = os.path.join(
            self.plugin_dir,
            'i18n',
            'SaveChunk_{}.qm'.format(locale))

        if os.path.exists(locale_path):
            self.translator = QTranslator()
            self.translator.load(locale_path)

            if qVersion() > '4.3.3':
                QCoreApplication.installTranslator(self.translator)

        # Create the dialog (after translation) and keep reference
        self.dlg = SaveChunkDialog()

        # Declare instance attributes
        self.actions = []
        self.menu = self.tr(u'&Save Chunk')

        self.toolbar = self.iface.addToolBar(u'SaveChunk')
        self.toolbar.setObjectName(u'SaveChunk')

        #Connect buttons to functions
        self.dlg.chunks_2.activated.connect(self.updateFolders)
        self.dlg.folders.activated.connect(self.updateText)
        self.dlg.chunkPathButton.clicked.connect(self.load_chunkPath)
        self.dlg.destinationFolderButton.clicked.connect(self.load_destFolder)
        self.dlg.verifyButton.clicked.connect(self.verify_and_link)
        self.dlg.verifyChunkButton.clicked.connect(self.verifyChunk)
        self.dlg.copyImagesButton.clicked.connect(self.copyImages)
        self.dlg.clearButton.clicked.connect(self.clearLayout)

    # noinspection PyMethodMayBeStatic
    def tr(self, message):
        """Get the translation for a string using Qt translation API.

        We implement this ourselves since we do not inherit QObject.

        :param message: String for translation.
        :type message: str, QString

        :returns: Translated version of message.
        :rtype: QString
        """
        # noinspection PyTypeChecker,PyArgumentList,PyCallByClass
        return QCoreApplication.translate('SaveChunk', message)


    def add_action(
        self,
        icon_path,
        text,
        callback,
        enabled_flag=True,
        add_to_menu=True,
        add_to_toolbar=True,
        status_tip=None,
        whats_this=None,
        parent=None):
        """Add a toolbar icon to the toolbar.

        :param icon_path: Path to the icon for this action. Can be a resource
            path (e.g. ':/plugins/foo/bar.png') or a normal file system path.
        :type icon_path: str

        :param text: Text that should be shown in menu items for this action.
        :type text: str

        :param callback: Function to be called when the action is triggered.
        :type callback: function

        :param enabled_flag: A flag indicating if the action should be enabled
            by default. Defaults to True.
        :type enabled_flag: bool

        :param add_to_menu: Flag indicating whether the action should also
            be added to the menu. Defaults to True.
        :type add_to_menu: bool

        :param add_to_toolbar: Flag indicating whether the action should also
            be added to the toolbar. Defaults to True.
        :type add_to_toolbar: bool

        :param status_tip: Optional text to show in a popup when mouse pointer
            hovers over the action.
        :type status_tip: str

        :param parent: Parent widget for the new action. Defaults None.
        :type parent: QWidget

        :param whats_this: Optional text to show in the status bar when the
            mouse pointer hovers over the action.

        :returns: The action that was created. Note that the action is also
            added to self.actions list.
        :rtype: QAction
        """

        icon = QIcon(icon_path)
        action = QAction(icon, text, parent)
        action.triggered.connect(callback)
        action.setEnabled(enabled_flag)

        if status_tip is not None:
            action.setStatusTip(status_tip)

        if whats_this is not None:
            action.setWhatsThis(whats_this)

        if add_to_toolbar:
            self.toolbar.addAction(action)

        if add_to_menu:
            self.iface.addPluginToMenu(
                self.menu,
                action)

        self.actions.append(action)

        return action

    def initGui(self):
        """Create the menu entries and toolbar icons inside the QGIS GUI."""

        icon_path = ':/plugins/save_chunk/icon.png'
        self.add_action(
            icon_path,
            text=self.tr(u'Save Chunk'),
            callback=self.run,
            parent=self.iface.mainWindow())

    def unload(self):
        """Removes the plugin menu item and icon from QGIS GUI."""
        for action in self.actions:
            self.iface.removePluginMenu(
                self.tr(u'&Save Chunk'),
                action)
            self.iface.removeToolBarIcon(action)
        # remove the toolbar
        del self.toolbar

    #Run method that performs all the real work
    def run(self):
        self.dlg.statusBar.setText("")
        self.dlg.progressBar.setValue(0)
        self.dlg.chunks.SizeAdjustPolicy = self.dlg.chunks.AdjustToContentsOnFirstShow
        self.dlg.chunks_2.SizeAdjustPolicy = self.dlg.chunks.AdjustToContentsOnFirstShow

        scrollAreaWidget = QWidget()
        self.scrollAreaLayout = QVBoxLayout()
        scrollAreaWidget.setLayout(self.scrollAreaLayout)
        self.dlg.scrollArea.setWidget(scrollAreaWidget)

        #get a list of point layers only (exclude polygon layers)
        layers = self.getPointLayers()
        
        #add these layers to the combo boxes
        for layer in layers:
            self.dlg.chunks.addItem(layer.name())
            self.dlg.chunks_2.addItem(layer.name())

        #Initialize the initial items of the combo boxes
        if layers:
            self.initLayersToFolders()
            initalFolders = self.layerToFolders[self.dlg.chunks_2.currentText()]
            for folder in initalFolders:
                self.dlg.folders.addItem(folder)
            chunkPath = initalFolders[self.dlg.folders.currentText()]
            self.dlg.chunkPath.setText(chunkPath)

        # show the dialog
        self.dlg.show()
        # Run the dialog event loop
        result = self.dlg.exec_()
        # See if OK was pressed
        if result:
            pass
        self.dlg.chunks.clear()
        self.dlg.chunks_2.clear()
        self.dlg.folders.clear()
        self.clearLayout()

    def clearLayout(self):
        layout = self.dlg.scrollArea.widget().layout()
        for i in reversed(range(layout.count())): 
            layout.itemAt(i).widget().setParent(None)
        self.dlg.statusBar.setText("")

    #Returns a list of current point layers
    def getPointLayers(self):
        pointLayers = []
        for layer in QgsProject.instance().mapLayers().values():
            try:
                if(layer.geometryType() == 0):
                    pointLayers.append(layer)
            except AttributeError:
                pass
        return pointLayers

    #Returns a layer from layer name
    def getLayerFromName(self, layerName):
        return QgsProject.instance().mapLayersByName(layerName)[0]

    """
        Initalizes a dictionary that maps a layer name to another dictionary which in turn maps subfolders in a layer to image directories
        layerToFolders[layer name] = folders
        folders[folder name] = image directory of folder
    """
    def initLayersToFolders(self):
        layers = self.getPointLayers()
        self.layerToFolders = {}
        for layer in layers:
            folders = {}
            for feature in layer.getFeatures():
                folderName = str(feature["folderName"])
                folders[folderName] = str(feature["imgDir"])
            self.layerToFolders[layer.name()] = folders

    #Updates the subfolders in the combobox folders if the layer selected is changed
    def updateFolders(self, index):
        layerName = self.dlg.chunks.itemText(index)
        self.dlg.folders.clear()
        folders = self.layerToFolders[layerName]
        for folder in folders:
            self.dlg.folders.addItem(folder)
        chunkPath = folders[self.dlg.folders.currentText()]
        self.dlg.chunkPath.setText(chunkPath)

    #Updates the chunk path if the folder selected in the combobox is changed
    def updateText(self, index):
        layerName = self.dlg.chunks_2.currentText()
        folders = self.layerToFolders[layerName]
        folderName = self.dlg.folders.itemText(index)
        chunkPath = folders[folderName]
        self.dlg.chunkPath.setText(chunkPath)

    #Loads a directory and sets chunkPath to it
    def load_chunkPath(self):
        self.load_dir(self.dlg.chunkPath)

    #Loads a directory and sets destination folder to it
    def load_destFolder(self):
        self.load_dir(self.dlg.destinationFolderPath)

    #Loads a directory
    def load_dir(self, lineEdit):
        dirPath = str(QFileDialog.getExistingDirectory(self.dlg, "Select Directory", ""))
        lineEdit.setText(dirPath)

    #Verifies a subfolder in a chunk and links it if succcessful
    def verify_and_link(self):
        chunk = self.dlg.chunks_2.currentText()
        folder = self.dlg.folders.currentText()
        if(self.verifyFolder(chunk, folder)):
            self.logMessage("Successfully verified and linked {} in {}!".format(folder, chunk), "green")
        else:
            self.logMessage("Failed to verify {} in {}! Please select a valid directory.".format(folder, chunk), "red")

    #Verify a subfolder in a chunks within a layer
    def verifyFolder(self, layerName, folderName):
        verified = True
        layer = self.getLayerFromName(layerName)
        features = list((feature for feature in layer.getFeatures() if str(feature["folderName"]) == folderName))
        for feature in features:
            imgPath = os.path.join(self.dlg.chunkPath.text(), str(feature["imgName"]))
            if not os.path.exists(imgPath):
                verified = False
                self.logMessage('{} file not found.'.format(imgPath), "red", False)
        if(verified):
            layer.startEditing()
            for feature in features:
                feature["imgDir"] = self.dlg.chunkPath.text()
                layer.updateFeature(feature)
            layer.commitChanges()
            self.initLayersToFolders()
        return verified

    #Verifies that all images within a chunk exist and returns True if successful, otherwise False
    def verifyChunk(self):
        layerName = self.dlg.chunks.currentText()
        verified = True
        layer = self.getLayerFromName(layerName)
        for feature in layer.getFeatures():
            imgPath = os.path.join(str(feature["imgDir"]), str(feature["imgName"]))
            if not os.path.exists(imgPath):
                verified = False
                break
        if(not verified):
            self.logMessage("Failed to verify {}!".format(layerName), "red")
        else:
            self.logMessage("Successfully verified {}!".format(layerName), "green")
        return verified

    def logMessage(self, message, color, setStatusBar=True):
        if(setStatusBar):
            self.dlg.statusBar.setText(message)
            self.dlg.statusBar.setStyleSheet("QLabel {{ color : black; }}")
        label = QLabel(message)
        label.setStyleSheet("QLabel {{ color : {}; }}".format(color))
        self.scrollAreaLayout.addWidget(label)
        QApplication.processEvents()

    #Constructs a list of image paths by appending image names and image directories in a layer and returns it
    def getImgPathsFromLayerName(self, layerName):
        layer = self.getLayerFromName(layerName)
        imgPaths = []
        warningGiven = False
        for feature in layer.getFeatures():
            imgPath = os.path.join(str(feature["imgDir"]), str(feature["imgName"]))
            if(not os.path.exists(imgPath)):
                if(not warningGiven):
                    reply = QMessageBox.question(self.iface.mainWindow(), 'Continue?', 
                     'Warning: {} cannot be found. Still continue?'.format(imgPath), QMessageBox.Yes, QMessageBox.No)
                    if(reply == QMessageBox.Yes):
                        warningGiven = True
                    else:
                        return
            imgPaths.append(imgPath)
        return imgPaths

    def generateKMZ(self, layerName, destinationFolderPath):
        layer = self.getLayerFromName(layerName)
        layer.startEditing()

        destinationFile = os.path.join(destinationFolderPath, os.path.basename(destinationFolderPath))
        wantedFields = ["description", "imgName", "imgDir", "folderName", "Latitude", "Longitude", "Altitude"]
        attributeIndices = []
        fields = layer.dataProvider().fields()
        index = 0
        for field in fields:
            if field.name() in wantedFields:
                attributeIndices.append(index)
            index += 1
        QgsVectorFileWriter.writeAsVectorFormat(layer, destinationFile, "utf-8", layer.crs(), "KML", attributes=attributeIndices)

    #Copies images from the selected chunk to the specified destination folder
    def copyImages(self):
        destinationFolderPath = self.dlg.destinationFolderPath.text()
        if(not os.path.exists(destinationFolderPath)):
            self.dlg.statusBar.setText("Please select a valid directory...")
            self.dlg.statusBar.setStyleSheet("QLabel {{ color : red; }}")
            return

        layerName = self.dlg.chunks.currentText()
        imgPaths = self.getImgPathsFromLayerName(layerName)

        totalPhotos = sum(1 for imgPath in imgPaths)
        photosCopied = 0

        for imgPath in imgPaths:
            self.dlg.progressBar.setValue((101*float(photosCopied)/totalPhotos))
            try:
                shutil.copy(imgPath, destinationFolderPath)
                self.logMessage('{} file copied.'.format(imgPath), "green", False)
                photosCopied += 1
            except FileNotFoundError:
                self.logMessage('{} file not found.'.format(imgPath), "red", False)
        self.logMessage('Finished copying {}/{} images.'.format(photosCopied, totalPhotos), "green")
        self.generateKMZ(layerName, destinationFolderPath)