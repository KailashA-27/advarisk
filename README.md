# advarisk
Web Scraping Assignment

Land Records Extraction API

This project provides an API to extract land records from the Jamabandi website.In this project, the requests library is used to handle HTTP requests to interact with the Jamabandi website. It uses BeautifulSoup for HTML parsing, and lxml for XPath querying, also uses FastAPI for creating a web server which exposes an API endpoint,

Requirements
Python==3.9+
requests
beautifulsoup4
lxml
fastapi
pydantic
You can install the required packages using: requirements.txt

Run the Server
1) Clone the repo in your system
2) Create an environment using the requirements.txt file
3) Run the follwing command along with port number of your choice:
uvicorn app:app --host 0.0.0.0 --port {port_number} --reload
4) Put this in your browser 
http://0.0.0.0:{port_number}/docs#/

After running 

Get Land Records
URL: /get-land-records/
Method: POST
Content-Type: application/json
Request Body:
{
    "input_district": "District Name",
    "input_tehsil": "Tehsil Name",
    "input_village": "Village Name",
    "input_khasra": "Khasra Number"
}

Response:
{
    "district_name": "District Name",
    "district_code": "District Code",
    "tehsil_name": "Tehsil Name",
    "tehsil_code": "Tehsil Code",
    "village_name": "Village Name",
    "village_code": "Village Code",
    "jamabandi_year": "Jamabandi Year",
    "khewat_no": "Khewat Number",
    "khatoni_no": "Khatoni Number",
    "inner_details": {
        "village": "Village Name",
        "hadbast no": "Hadbast Number",
        "tehsil": "Tehsil Name",
        "district": "District Name",
        "year": "Year"
    }
}

Code Explanation

Main Modules and Functions:

Initial part of the code is responsible for initiating a session with the Jamabandi website, extracting necessary hidden form fields (__VIEWSTATE and __EVENTVALIDATION), and posting data to simulate interaction with the website's form.
1) A requests.Session object is created to persist certain parameters across multiple requests. It can be used to handle cookies, headers, and other session-related information.
2) The session sends a GET request to the URL. The response contains the HTML content of the page.
3) The HTML content of the page is parsed using BeautifulSoup to facilitate easy extraction of required data.
4) The values of the hidden fields __VIEWSTATE and __EVENTVALIDATION are extracted. 
5) A dictionary radio_data is created to hold the form data that will be sent in the POST request.
  __EVENTTARGET: The target control that initiated the postback (ctl00$ContentPlaceHolder1$RdobtnKhasra).
  __EVENTARGUMENT, __LASTFOCUS, __SCROLLPOSITIONX, __SCROLLPOSITIONY, __VIEWSTATEENCRYPTED: Various state management parameters.
  __VIEWSTATE and __EVENTVALIDATION: The extracted values from the initial GET request.
  ctl00$ContentPlaceHolder1$a: The value indicating the selected radio button (RdobtnKhasra).
  ctl00$ContentPlaceHolder1$ddldname: An initial value for the dropdown list (-1).
6) The session sends a POST request to the URL with the radio_data. This simulates a form submission on the website.
7) The HTML content of the response is parsed again using BeautifulSoup to extract the updated __VIEWSTATE and __EVENTVALIDATION values, as these fields often change with each request.
8) The updated values of __VIEWSTATE and __EVENTVALIDATION are extracted from the response. These will be used in subsequent form submissions to maintain state.
9) Create a dropdown list that contains tuples where each tuple represents a dropdown field. Each tuple includes the form field name, the HTML element ID, and the input value provided by the user.
10) get_code(soup, value, input_x) is called to get the code for the selected input value. This function extracts the value corresponding to the user's input from the dropdown options.
The radio_data dictionary is updated with the extracted code and other required form fields.
A POST request is sent with the updated radio_data.
The response HTML is parsed again using BeautifulSoup to extract the updated __VIEWSTATE and __EVENTVALIDATION values for the next iteration.
If an error occurs (e.g., the input value is not found in the dropdown), the API returns an error message.
11) After iterating through all the dropdowns, a final POST request is sent to select the first row in the resulting grid view (if any). This is done by setting __EVENTTARGET to ctl00$ContentPlaceHolder1$GridView1 and __EVENTARGUMENT to Select$0.
12) The code then attempts to extract khewat_no and khatoni_no from the resulting table in the HTML response. If these elements are not found, the values are set to None.
13) A GET request is sent to the Nakal URL to fetch additional details. The response is saved to a file for further processing.
14) The HTML content is read from the saved file and parsed using lxml.
The get_data function is used to extract various details using XPath queries.
15) The extracted data is assembled into a dictionary and returned as the output of the API endpoint. This includes the district, tehsil, village, jamabandi year, khewat number, khatoni number, and additional inner details.

Imports:
requests: To handle HTTP requests.
BeautifulSoup from bs4: For parsing HTML content.
html from lxml: For XPath querying.
FastAPI and HTTPException from fastapi: To create the API.
BaseModel from pydantic: For data validation.

Class InputData:
Defines the expected structure of the input data for the API endpoint.

Function get_code:
Extracts the code for a given input value from the dropdown in the HTML. Used for getting district_code,village_code,etc

Function get_data:
Extracts data from the HTML content using XPath. Used for getting data from inner_details.

API Endpoint /get-land-records/:
Handles the POST request to fetch land records based on the provided input data.
Interacts with the Jamabandi website to submit the required form data and extract the necessary details.



