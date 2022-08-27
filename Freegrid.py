#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
User Interface to generate In3D.ca storage components in FreeCAD.

*******************************************************************************
*   Copyright (c) 2022 In3D.ca
*
*   This program is free software: you can redistribute it and/or modify it
*   under the terms of the GNU Affero General Public License as published by
*   the Free Software Foundation, either version 3 of the License, or (at your
*   option) any later version.
*
*   This program is distributed in the hope that it will be useful, but WITHOUT
*   ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or
*   FITNESS FOR A PARTICULAR PURPOSE. See the GNU Affero General Public License
*   for more details.
*
*   You should have received a copy of the GNU Affero General Public License
*   along with this program. If not, see <https://www.gnu.org/licenses/>.
*******************************************************************************
"""

__Name__ = 'In3D.ca FreeGrid Storage System'
__Comment__ = 'Generate In3D.ca FreeGrid storage components'
__Author__ = "Alan Langford <prints@in3d.ca>"
__Version__ = '0.0.0'
__Date__ = '20xx-xx-xx'
__License__ = 'GNU AGPLv3+'
__Web__ = 'https://in3d.ca'
__Wiki__ = ''
__Icon__ = ''
__Help__ = 'Select object type and characteristics and click on the create button. Repeat. Close when done.'
__Status__ = ''
__Requires__ = ''
__Communication__ = ''
__Files__ = ''

import FreeCAD
import FreeCADGui
import Part

import DraftVecUtils

from in3dca import StorageGrid, StorageBox

from PySide import QtCore, QtGui
from PySide.QtCore import QT_TRANSLATE_NOOP

try:
    _encoding = QtGui.QApplication.UnicodeUTF8


    def tr(context, text):
        return QtGui.QApplication.translate(context, text, None, _encoding)
except AttributeError:
    def tr(context, text):
        return QtGui.QApplication.translate(context, text, None)

try:
    _fromUtf8 = QtCore.QString.fromUtf8
except AttributeError:
    _fromUtf8 = lambda s: s


class In3dGridUi(QtGui.QWidget):
    def __init__(self, MainWindow):
        super(In3dGridUi, self).__init__(MainWindow)
        self.window = MainWindow

        plus_int = QtGui.QIntValidator()
        plus_int.setBottom(1)

        self.resize(370, 350)

        # We have rows for: the tabs, the global options, the generate/close buttons, and a message
        # Start with the tabs
        self.tabs = QtGui.QTabWidget()

        # Tab 0: box generation
        self.box_tab = QtGui.QWidget()
        self.tabs.addTab(self.box_tab, "Boxes")
        form = QtGui.QFormLayout()
        self.box_x = QtGui.QLineEdit()
        self.box_x.setValidator(plus_int)
        self.box_x.setMaxLength(3)
        self.box_x.setText("1")
        self.box_x.selectAll()
        form.addRow("Box Width (x, 50mm units)", self.box_x)
        self.box_y = QtGui.QLineEdit()
        self.box_y.setValidator(plus_int)
        self.box_y.setMaxLength(3)
        self.box_y.setText("1")
        form.addRow("Box Depth (y, 50mm units)", self.box_y)
        self.box_z = QtGui.QLineEdit()
        self.box_z.setValidator(plus_int)
        self.box_z.setMaxLength(3)
        self.box_z.setText("1")
        form.addRow("Box Height (z, 10mm units)", self.box_z)
        self.box_divs = QtGui.QLineEdit()
        self.box_divs.setValidator(plus_int)
        self.box_divs.setMaxLength(3)
        self.box_divs.setText("1")
        form.addRow("Number of divisions", self.box_divs)
        self.box_open_front = QtGui.QCheckBox("Leave front of box open")
        self.box_open_front.setChecked(False)
        form.addRow(self.box_open_front)
        self.box_ramp = QtGui.QCheckBox("Add scoop inside front of box")
        self.box_ramp.setChecked(True)
        form.addRow(self.box_ramp)
        self.box_grip = QtGui.QCheckBox("Add grip/label area at rear of box")
        self.box_grip.setChecked(True)
        form.addRow(self.box_grip)
        self.box_grip_depth = QtGui.QLineEdit()
        self.box_grip_depth.setValidator(QtGui.QIntValidator())
        self.box_grip_depth.setMaxLength(3)
        self.box_grip_depth.setText("15")
        form.addRow("Depth of grip (mm)", self.box_grip_depth)
        self.box_tab.setLayout(form)

        # Tab 1: Grid options
        self.grid_tab = QtGui.QWidget()
        self.tabs.addTab(self.grid_tab, "Grids")
        form = QtGui.QFormLayout()
        self.grid_x = QtGui.QLineEdit()
        self.grid_x.setValidator(plus_int)
        self.grid_x.setMaxLength(3)
        self.grid_x.setText("1")
        form.addRow("Grid Width (x, 50mm units)", self.grid_x)
        self.grid_y = QtGui.QLineEdit()
        self.grid_y.setValidator(plus_int)
        self.grid_y.setMaxLength(3)
        self.grid_y.setText("1")
        form.addRow("Grid Depth (y, 50mm units)", self.grid_y)
        self.grid_tab.setLayout(form)

        # Tab 2: Sketch options
        self.sketch_tab = QtGui.QWidget()
        self.tabs.addTab(self.sketch_tab, "Sketcher")
        form = QtGui.QFormLayout()
        self.sketch_x = QtGui.QLineEdit()
        self.sketch_x.setValidator(plus_int)
        self.sketch_x.setMaxLength(3)
        self.sketch_x.setText("1")
        form.addRow("Width (x, 50mm units)", self.sketch_x)
        self.sketch_y = QtGui.QLineEdit()
        self.sketch_y.setValidator(plus_int)
        self.sketch_y.setMaxLength(3)
        self.sketch_y.setText("1")
        form.addRow("Depth (y, 50mm units)", self.sketch_y)
        self.sketch_open_front = QtGui.QCheckBox("Include open front")
        form.addWidget(self.sketch_open_front)
        self.inside_sketch_button = QtGui.QPushButton("Generate Inner Box Profile")
        form.addWidget(self.inside_sketch_button)
        self.sketch_tab.setLayout(form)

        # Then the global options
        self.global_opts = QtGui.QVBoxLayout()

        # Magnet options in a group
        self.opt_magnet_group = QtGui.QGroupBox("Options for magnet mounts")

        grid = QtGui.QVBoxLayout()
        grid.setSpacing(10)

        self.opt_magnets_all = QtGui.QRadioButton("At all box/grid intersections")
        self.opt_magnets_all.setChecked(True)
        grid.addWidget(self.opt_magnets_all)
        self.opt_magnets_box = QtGui.QRadioButton("Box corners only / all grid intersections")
        grid.addWidget(self.opt_magnets_box)
        self.opt_magnets_none = QtGui.QRadioButton("No magnet mounts")
        grid.addWidget(self.opt_magnets_none)

        self.opt_magnet_group.setLayout(grid)
        self.global_opts.addWidget(self.opt_magnet_group)

        self.opt_as_objects = QtGui.QCheckBox("Generate components as individual shapes")
        self.global_opts.addWidget(self.opt_as_objects)


        # Near the bottom, the buttons
        self.buttons = QtGui.QHBoxLayout()
        self.buttons.addStretch()
        self.ok_button = QtGui.QPushButton("Ok", self)
        self.buttons.addWidget(self.ok_button)
        self.apply_button = QtGui.QPushButton("Apply", self)
        self.buttons.addWidget(self.apply_button)
        self.close_button = QtGui.QPushButton("Close", self)
        self.buttons.addWidget(self.close_button)

        # A message area
        self.message = QtGui.QLabel()

        main_layout = QtGui.QVBoxLayout()
        main_layout.addWidget(self.tabs)
        main_layout.addStretch()
        main_layout.addLayout(self.global_opts)
        main_layout.addStretch()
        main_layout.addWidget(self.message)
        main_layout.addStretch()
        main_layout.addLayout(self.buttons)
        main_layout.addWidget(self.ok_button)
        main_layout.addWidget(self.apply_button)
        main_layout.addWidget(self.close_button)
        self.setLayout(main_layout)

        # Now set up events
        self.box_grip.clicked.connect(self.box_grip_click)
        self.box_open_front.clicked.connect(self.box_open_front_click)
        self.apply_button.clicked.connect(self.start_button_click)
        self.close_button.clicked.connect(self.close_button_click)
        self.inside_sketch_button.clicked.connect(self.inside_sketch_button_click)
        self.ok_button.clicked.connect(self.ok_button_click)
        self.show()

    def box_grip_click(self, state):
        self.box_grip_depth.setEnabled(state)

    def box_open_front_click(self, state):
        if state:
            self.box_ramp.setChecked(False)

    def close_button_click(self):
        self.window.hide()

    def generate_box(self):
        # We are creating a box
        box = StorageBox.StorageBox()
        box.as_components = self.opt_as_objects.isChecked()
        box.closed_front = not self.box_open_front.isChecked()
        depth = int(self.box_grip_depth.text())
        box.divisions = int(self.box_divs.text())
        if box.divisions < 1:
            box.divisions = 1
        if self.box_grip.isChecked() and depth > 0:
            box.grip_depth = depth
        if self.opt_magnets_none.isChecked():
            box.magnets = False
            box.magnets_corners_only = True
        else:
            box.magnets = True
            box.magnets_corners_only = self.opt_magnets_box.isChecked()
        box.ramp = self.box_ramp.isChecked()

        x = int(self.box_x.text())
        y = int(self.box_y.text())
        z = int(self.box_z.text())
        if x > 0 and y > 0 and z > 0:
            self.message.setText("Generating...")
            self.message.repaint()
            size = str(x) + "x" + str(y) + "x" + str(z)
            Part.show(box.make(x, y, z), "In3D_" + size + "_box")
            msg = "Created " + str(x) + "x" + str(y) + "x" + str(z) + " box"
            if box.as_components:
                msg += " as components"
            msg += "."
            self.message.setText(msg)
            # box.insert_as_sketch()
        else:
            self.message.setText("Box sizes must be greater than zero.")

    def generate_grid(self):
        grid = StorageGrid.StorageGrid()
        grid.magnets = not self.opt_magnets_none.isChecked()
        x = int(self.grid_x.text())
        y = int(self.grid_y.text())
        if x > 0 and y > 0:
            self.message.setText("Generating...")
            self.message.repaint()
            size = str(x) + "x" + str(y)
            Part.show(grid.make(x, y), "In3D_" + size + "_grid")
            msg = "Created " + str(x) + "x" + str(y) + " grid."
            self.message.setText(msg)
        else:
            self.message.setText("Grid sizes must be greater than zero.")


    def inside_sketch_button_click(self):
        box = StorageBox.StorageBox()
        x = int(self.sketch_x.text())
        y = int(self.sketch_y.text())
        if x > 0 and y > 0:
            box.closed_front = not self.sketch_open_front.isChecked()
            box.insert_as_sketch(x, y)
            self.message.setText("Sketch generated.")
        else:
            self.message.setText("Sizes must be greater than zero.")

    def ok_button_click(self):
        self.start_button_click()
        self.close_button_click()

    def start_button_click(self):
        # Determine what we're creating
        if self.tabs.currentIndex() == 0:
            self.generate_box()
        elif self.tabs.currentIndex() == 1:
            # We are creating a grid
            self.generate_grid()
        elif self.tabs.currentIndex() == 2:
            pass

class FreegridCommand:
    def __init__(self):
        pass

    def GetResources(self):
        return {
            'Pixmap': '',
            'MenuText': QT_TRANSLATE_NOOP('Freegrid', 'Freegrid'),
            'ToolTip': QT_TRANSLATE_NOOP('Freegrid', 'Create Freegrid elements')
        }

    def Activated(self):
        MainWindow = QtGui.QMainWindow()
        MainWindow.setWindowTitle("In3D.ca FreeGrid Storage System")
        MainWindow.setMinimumSize(QtCore.QSize(370, 350))
        MainWindow.setMaximumSize(QtCore.QSize(370, 350))
        MainWindow.setWindowFlags(QtCore.Qt.WindowStaysOnTopHint)
        MainWindow.setWindowModality(QtCore.Qt.ApplicationModal)
        ui = In3dGridUi(MainWindow)
        MainWindow.show()

    def isActive(self):
        return True

FreeCADGui.addCommand('Freegrid', FreegridCommand())
