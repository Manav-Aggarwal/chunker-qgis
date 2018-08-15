**Installation instructions:**

	Packages required:
		- pykml
		- piexif
	
	To make sure you install these packages in the correct python version, first navigate to the directory where the python version for QGIS (3.6.5) is installed, and then
	run the commands:

		- python -m pip install pykml
		- python -m pip install piexif

	If you have trouble running python, try copying "python36.dll" located in the DLL folder to C:\Windows\System32 and then retry

	The pykml package installed is supported for python2 by default so we need to make some changes.

	Follow these steps:
	- Navigate to the directory where python is installed in the machine.
	- Go to lib/python3.6/site-packages/pykml
	- Open parser.py:
		- Change "import urllib2" to "import urllib3"
	- Open factory.py:
		- Go to the last line (216) and insert paranthesis in the print function

**Plugins:**
	
	1. Convert to 3D:
	Converts 2D KML to 3D KML by changing the altitudemode of each placemark of the KML to absolute. Accepts KML/KMZ files or folder containing KMZs. 
    (Note: It reads all the KMZs inside the given folder so any invalid KMZ would crash the plugin.)
	2. Load Layer: 
	Loads a KML/KMZ file or a folder with geotagged images into QGIS. 
	Adds these attributes in the attribute table of the layer: 
	- Folder name (Customizable)
	- Image name
	- Image directory (Customizable)
	- Latitude
	- Longitude
	- Altitude
	3. Merge Layers: 
	Copies the "selected features" in the selected layers into a new layer. The name of the layer is customizable.
	4. Save Chunk: 
	Verifies and copies images in a chunk to a specified folder. Also allows re-linkining of image directories stored within chunks.
	5. Generate Flight KMZs
	Takes in a project folder with different flight folders containing "Geotagged-Images". Allows selecting the flight folders to use. 
    Reads EXIF data of every image in the folders "Geotagged-Images" for each flight and generates KMZs from those folders in the specified location.
	6. Side Viewer: 
	Graphs the Latitude, Longitude, Altitude of features in the selected layers. Selected features show up in red and clicking on a feature displays the image name associated with it and its altitude. Checking/Unchecking layers in layer toolbar and selected/unselecting features reflects changes in the graph immediately.	
    7. Qgis2threejs: 
    Located under Web tab in QGIS. Allows visualizing the layers in 3D space. Make sure to go on properties of the each layer and set the Z coordinate to Altitude. You can also set the flat plane property to the image of the google maps tile layer to better the experience.

**Chunking in QGIS:**

	1. Load the layers you want to chunk using the load layer plugin.
	2. Visualize the layers in Side-Viewer or Qgis2threejs and decide how you need to chunk the layers.
	3. Go to Layer -> Create new layer -> New Shapefile Layer... and create a new polygon layer.
	4. Click Toggle Editing (Pencil icon) and add a new polygon feature to create a polygon.
	5. After deciding on the vertices of the new polygon, right click and enter a feature id to create the polygon.
	6. Go to Vector -> Research Tools -> Select By Location..., put the point layer you want to select from in the first dropdown, and the polygon layer in the second dropdown, 
	   and click run to select the features from the layer inside the polygon.
	7. Repeat step 5 for as many layers as you want.
	8. After you're done selecting features from different layer, open the "Merge layers" plugin, select the layers you want in the list by holding down Ctrl. Enter a new layer 	name and click ok to create a new layer with the selected features from the selected layers.
	9. To download the images in the chunk, use the "Save Chunk" plugin. Select the chunk you want to download, verify to make sure all the images in the chunk exist, select a 	destination folder, and click copy images.
	10. If the verification fails for some reason in step 8, go to the link tab in the "Save Chunk" plugin, and re-link folders within chunks to fix it to make the chunk valid.

**Loading a Google Satellite layer in QGIS:**
	
	Simplified the instructions located here: https://linuxhint.com/import-google-earth-into-qgis/
	1. Right click on XYZ Tiles from the Browser, and click on New Connection...
	2. Enter Name as Google Satellite, the URL as http://www.google.cn/maps/vt?lyrs=s@189&gl=cn&x={x}&y={y}&z={z} and set max zoom level to 19.
	3. Click OK and then double click on the new tile to load it as layer (I noticed that loading the map layer before any other point layers works better for some reason.)

**Video tutorial link:**
    
    https://drive.google.com/file/d/1SeCmzSTDCPYmMdeMGgM-S_6NRfgDKxO_/view?usp=sharing
