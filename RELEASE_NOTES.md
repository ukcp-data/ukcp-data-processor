# Release 1.1.2

This release addresses:

* Provide daily data for the GCM and RCM


# Release 1.1.1

This release addresses:

* Fix issues with plume plots when overlaying land_prob data


# Release 1.1.0

This release addresses:

* Add support for land-cpm data
* Adjust font sizes and line thicknesses on the plots and maps


# Release 1.0.8

This release addresses:

* The title for plots now use the grid reference of the centre of a grid cell, when the selection method is grid cell


# Release 1.0.7

This release addresses:

* Fix issue generating anomalies when all months or all seasons are selected. This issue resulted in no data being returned.


# Release 1.0.6

This release addresses:

* Update sea level anomalies plume plots to show 5th, 10th, 30th, 33rd, 50th, 67th, 70th, 90th and 95th percentiles
* Add processes to subset sea level anomaly data


# Release 1.0.5

This release addresses:

* Ensure boundaries are drawn on choropleth maps 


# Release 1.0.4

This release addresses:

* Fix links to the data on the CEDA achieve on the jobs output page 


# Release 1.0.3

This release addresses:

* Fix issue when selecting a single cell with a bounding box.
* Add the option to select the Hadley 15 members for GMC products.
* Update Land Prob plume plots with a colour option and 5th, 25th, 75th and 95th percentile data.


# Release 1.0.2

This release addresses:

* Fixes to CSV output for subsets of GCM and RCM


# Release 1.0.1

Issues address:

* Do not show the legend when it is empty on plots.
* Update the precision of the data written to CSV files.
* Update label for time_slice_type in CSV files.
* Improve performance of plotting.
* Reduce resolution of shapefiles used for plotting maps.
* Remove duplicate points from PDF plots and files, these are produced due to the clipping of the data.
* Fix Datetime serialised in CSV files.
* Fix location value in CSV files.
* Fix region selection for GCM and RCM.
* Fix to ensure random sampling returns correct number of samples
