# How Data was Collected

Data was collected from `http://communitycrimemap.com`. It was a quite
convenient site to scrape once I understood the API. 

There is a datagrid that queries the API at
`http://communitycrimemap.com/Protected/RAIDS/Data/DataGrid.serv`.

The query string is extremely complex and is worth just looking at the
source code `source/crime.py`.

# Crime.csv

Details all the crime in the knoxville area.

Columns include date, time, location, and type of crime that occured.
