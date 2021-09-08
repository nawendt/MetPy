#  Copyright (c) 2021 MetPy Developers.
#  Distributed under the terms of the BSD 3-Clause License.
#  SPDX-License-Identifier: BSD-3-Clause
"""
NOAA SPC Probabilistic Outlook
==============================

Demonstrate the use of geoJSON and shapefile data with PlotGeometry in MetPy's simplified
plotting interface. This example walks through plotting the Day 1 Probabilistic Tornado
Outlook from NOAA Storm Prediction Center. The geoJSON file was retrieved from the
`Storm Prediction Center's archives <https://www.spc.noaa.gov/archive/>`_.
"""

import geopandas

from metpy.cbook import get_test_data
from metpy.plots import MapPanel, PanelContainer, PlotGeometry

###########################
# Read in the geoJSON file containing the convective outlook.
day1_outlook = geopandas.read_file(
    get_test_data('spc_day1otlk_20210317_1200_torn.lyr.geojson')
)

###########################
# Preview the data.
day1_outlook

###########################
# Plot the shapes from the 'geometry' column. Give the shapes their fill and stroke color by
# providing the 'fill' and 'stroke' columns. Use text from the 'LABEL' column as labels for the
# shapes. For the SIG area, remove the fill and label while adding the proper hatch effect.
geo = PlotGeometry()
geo.geometry = day1_outlook['geometry']
geo.fill = day1_outlook['fill']
geo.stroke = day1_outlook['stroke']
geo.labels = day1_outlook['LABEL']
sig_index = day1_outlook['LABEL'].values.tolist().index('SIGN')
geo.fill[sig_index] = 'none'
geo.labels[sig_index] = None
geo.label_fontsize = 'large'
geo.hatch = ['SS' if label == 'SIGN' else None for label in day1_outlook['LABEL']]

###########################
# Add the geometry plot to a panel and container.
panel = MapPanel()
panel.title = 'SPC Day 1 Probabilistic Tornado Outlook (Valid 12z Mar 17 2021)'
panel.plots = [geo]
panel.area = [-120, -75, 25, 50]
panel.projection = 'lcc'
panel.layers = ['lakes', 'land', 'ocean', 'states', 'coastline', 'borders']

pc = PanelContainer()
pc.size = (12, 8)
pc.panels = [panel]
pc.show()
