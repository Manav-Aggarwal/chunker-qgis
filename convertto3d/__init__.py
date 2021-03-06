# -*- coding: utf-8 -*-
"""
/***************************************************************************
 ConvertTo3D
                                 A QGIS plugin
 This plugin takes in a 2D kml file and outputs a 3D version of it.
 Generated by Plugin Builder: http://g-sherman.github.io/Qgis-Plugin-Builder/
                             -------------------
        begin                : 2018-07-11
        copyright            : (C) 2018 by Skylark Drones
        email                : manav@stanford.edu
        git sha              : $Format:%H$
 ***************************************************************************/

/***************************************************************************
 *                                                                         *
 *   This program is free software; you can redistribute it and/or modify  *
 *   it under the terms of the GNU General Public License as published by  *
 *   the Free Software Foundation; either version 2 of the License, or     *
 *   (at your option) any later version.                                   *
 *                                                                         *
 ***************************************************************************/
 This script initializes the plugin, making it known to QGIS.
"""


# noinspection PyPep8Naming
def classFactory(iface):  # pylint: disable=invalid-name
    """Load ConvertTo3D class from file ConvertTo3D.

    :param iface: A QGIS interface instance.
    :type iface: QgsInterface
    """
    #
    from .convertTo3D import ConvertTo3D
    return ConvertTo3D(iface)
