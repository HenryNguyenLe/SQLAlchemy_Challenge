# Vacation Planning at Hawaii
## Overview
Hawaii is known for one of the best places in the world for vacation, thanks to its evergreen islands and extremely comfortable weather. In this repository, Hawaii weather parameters such as precipitation and temperature are analyzed to see if the weather of the pre-picked vacation dates are good or not.
  
![Hawaii Image - Henry Le](/Images/Hawaii.jpg)
  
## Workflow  
* Establish connection between Jupyter Notebook and SQL_Lite Database  
* Perform Precipitaion Analysis:  
    - Retrieve data during the past 12 months (from the lastest available date)  
    - Plot total rainfall over time  
    - Perform quick statistic analysis on the rainfall data (mean, max, min, count, etc.)
 * Perform Station Analysis:  
    - Produce a comprehensive list of all available stations and number of records  
    - Identify the most active weather station (most data amount recorded)  
    - Plot the temperature histogram of this most active station
    - Find the most active temperature-recording weather station:  
          - Get :: ID, Name, Rainfall, Longitude, Latitude, Elevation  
    - 
