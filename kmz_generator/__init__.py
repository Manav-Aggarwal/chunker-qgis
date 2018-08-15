# -*- coding: utf-8 -*-
"""
/***************************************************************************
 KMZ_Generator
                                 A QGIS plugin
 This plugin takes in flight folders and generates kmz from them
 Generated by Plugin Builder: http://g-sherman.github.io/Qgis-Plugin-Builder/
                             -------------------
        begin                : 2018-08-09
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
    """Load KMZ_Generator class from file KMZ_Generator.

    :param iface: A QGIS interface instance.
    :type iface: QgsInterface
    """
    #
    from .kmz_generator import KMZ_Generator
    return KMZ_Generator(iface)
