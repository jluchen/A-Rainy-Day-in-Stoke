A Rainy Day in Stoke: Comparing Soccer Players
Team 15: Justin Chen, Morissa Chen, Mihir Dhoot, Ashwin Nallan
CSE 6242 Final Project, Fall 2020

1. Description
The following code suite is used to build "A Rainy Day in Stoke", a website that seeks to improve fan engagement and knowledege in the sport of soccer.
The EDA folder contains the Jupyter notebooks used to scrape and analyze data from FBref.com.
The Clustering folder contains the Jupyter notebooks used to cluster/pair the data.
The viz folder contains the files necessary to build the website. You do not need to run the EDA or Clustering data.  The outputs from those scripts are already stored in the databases.

2. Installation
The code was built on Python 3.7.1.  Other versions are not guaranteed to be supported.
The following Python libraries are required (most should be included in either the standard library or in a typical Anaconda install)
-Flask, Pandas, json, sqlite3, numpy, functools, matplotlib
-seaborn, skelarn, pylab, mpl_toolkits, base64, io
There is also HTML, CSS, and Javascript code, which should require no dependencies. Requisite d3 and JQuery libraries are included locally.
The website was built for Firefox version 83.0.  Other versions are not guaranteed to be supported.
To "install" the code, just download and unzip the folder.

3. Execution
Accessing and running the data scraping and analysis code simply requires opening and running the Jupyter notebooks.
-This is not necessary to do for the website to run. The data and analyzed results have already been compiled and stored in provided db files.

In order to launch the website:
-In your terminal/command line, navigate to the viz folder
-Type "python app.py"
-Open Firefox and go to "127.0.0.1:3001"
-Have fun exploring!

4. Demo Video
https://youtu.be/0-y7rkQcq3w
