# How data was collected

This data was quite crudely collected. PDF's are a pain to parse
mainly becuase of unexpected newlines, spaces, funny characters
etc. The workflow consisted of checking
"http://knoxvilletn.gov/government/city_departments_offices/311/performance_measures/"
for available reports in `HTML`. Next it parses each on the pdfs. To
parse the pdfs all the text is extracted, newlines/tabs removed, and a
very ineficient usage of regular expressions to get all the values.

# Requests

Includes all of the data from the Category, Total Cases, % on time
table. This provides an overview of all the calls each month.

# Services

This provides a count of the top 5 service requests each month.

# Statistics

Provides high level statistics about each call. Number of calls,
average answer time, grade of service (calls answerd in 20 sec or
less).
