Project aims to create universal interface to download data from stocks exchange, using the python API provided by brokers by MT5 application. Data downloaded using python scripts is saved by RAM database,
currently using H2 embedded in Spring enviorment. Subsequent script extrapolate data to equal time steps, which allows easy further data processing. 
These processed data then will be output for an Excel sheet which allows flexible construction any mathematics, for any numbers of entries at once. What common popular interfaces like Ctrader, MT5, TradingView do not allows. 

as a technology I chose the Spring framework in Java. Python scripts are run in it - this is related to the API that is used in broker applications - MT5, MT4. 
The main logic of data processing and saving data to the H2 database is created within the Python scripts. 
From there, the values ​​will be transferred to Excel sheets, using Java technology.

That will make possible to test any of idea of indicator, which exceeds the capabilities of common tools. 
Using the RAM database is very light and efficient. Historical results do not have to be saved, because the saving process can be preceded by a script, peaking any number of historical entries for a given symbol. 
The list of downloaded symbols is loaded from a txt file and needs to be fit for proper Broker - data provider. Configuration data is also loaded from a txt file. 
The speed of data download is configurable in the txt file. 
And it must be adjusted so as not to exceed the broker's courtesy. In my case, the acceptable load that I agreed with my provider's support is 50-80 queries per second.
Individual options are currently launched via the HTTP method using the Postman program, in the further part of the project it will be necessary to build a simple, graphical interface.

kind regards
Matelko
