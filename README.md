# financial_background_innoscripta


Create a tool to collect data from counterparties balance sheets to keep company's reputation safe and
make working routine easier. 

For the Innoscripta company. 

The tool accepts files or links to the web or local balance sheets and returns a conveniant *.csv file with financial 
background data for further research.
The tool is developed in the light of the fact that there are no anti-scraping protections on the website. 

The following technologies are used to implement the scraping:

- Python 3.9.0
- beautifulsoup4==4.9.3
- certifi==2020.6.20
- chardet==4.0.0 
- et-xmlfile==1.1.0
- html5lib==1.1
- idna==2.10
- lxml==4.6.3
- numpy==1.21.0
- openpyxl==3.0.7
- pandas==1.2.5
- python-dateutil==2.8.1
- pytz==2021.1
- requests==2.25.1
- requests-file==1.5.1
- six==1.16.0
- soupsieve==2.2.1
- urllib3==1.26.6
- webencodings==0.5.1

## How to use

The tool accepts files or web/local urls and returns the *.csv file 
to the './out' directory.
If the source was a local file, the destination file will have the same name.
If the source was the web url, the destination file will be a url string 
with the non-ASCII characters replaced.
Source files should be located in './in/src_files' directory.
Source url string should be added to urls.txt file as a new line.
The handled files are moved to the './out/archive/ directory to prevent 
double processing.

### To run script:

Install requirements:

##### ~$ pip install -r requirements.txt

Execute the command 

##### ~$ python main.py

from the tool's root folder
