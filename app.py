import requests
from bs4 import BeautifulSoup
import pdb
from lxml import html
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

app = FastAPI()

class InputData(BaseModel):
    input_district: str
    input_tehsil: str
    input_village: str
    input_khasra: str


def get_code(soup,value,input):
    if input != None:
        dropdown = soup.find('select', {'id': value}) 
        if dropdown:
            options = dropdown.find_all('option')
            if input in str(options):
                for option in options:
                    if input in option.text:
                        print(option.get('value'))
                        return option.get('value')
            else:
                raise HTTPException(status_code=400, detail="Input is not in the list")
    else:
        return soup.find('select',{'id':'ctl00_ContentPlaceHolder1_ddlPeriod'}).find_all('option')[1].get('value')
        
def get_data(tree,given_xpath):
    try:
        data_elements = tree.xpath(given_xpath)
        data = data_elements[0].text_content().strip()
    except:
        data = None
    return data


@app.post("/get-land-records/")
async def get_land_records(data: InputData):
    url = 'https://jamabandi.nic.in/land%20records/NakalRecord'

    session = requests.Session()
    response = session.get(url)

    soup = BeautifulSoup(response.text, 'html.parser')
    viewstate = soup.find('input', {'name': '__VIEWSTATE'})['value']
    eventvalidation = soup.find('input', {'name': '__EVENTVALIDATION'})['value']

    radio_data = {
        "__EVENTTARGET": "ctl00$ContentPlaceHolder1$RdobtnKhasra",
        "__EVENTARGUMENT": "",
        "__LASTFOCUS": "",
        "__VIEWSTATE": viewstate,
        "__VIEWSTATEGENERATOR": "9C91F57C",
        "__SCROLLPOSITIONX": 0,
        "__SCROLLPOSITIONY": 0,
        "__VIEWSTATEENCRYPTED": "",
        "__EVENTVALIDATION": eventvalidation,
        "ctl00$ContentPlaceHolder1$a": "RdobtnKhasra",
        "ctl00$ContentPlaceHolder1$ddldname": -1
    }

    response = session.post(url, data=radio_data)

    soup = BeautifulSoup(response.text, 'html.parser')
    viewstate = soup.find('input', {'name': '__VIEWSTATE'})['value']
    eventvalidation = soup.find('input', {'name': '__EVENTVALIDATION'})['value']

    dropdown_data = [
    ("ctl00$ContentPlaceHolder1$ddldname", "ctl00_ContentPlaceHolder1_ddldname",data.input_district),
    ("ctl00$ContentPlaceHolder1$ddltname", "ctl00_ContentPlaceHolder1_ddltname",data.input_tehsil),
    ("ctl00$ContentPlaceHolder1$ddlvname", "ctl00_ContentPlaceHolder1_ddlvname",data.input_village),
    ("ctl00$ContentPlaceHolder1$ddlPeriod", "ctl00_ContentPlaceHolder1_ddlPeriod",None),
    ("ctl00$ContentPlaceHolder1$ddlkhasra","ctl00_ContentPlaceHolder1_ddlkhasra",data.input_khasra)
    ]
    for dropdown, value,input_x in dropdown_data:
        try:
            radio_data[dropdown] = get_code(soup,value,input_x) 
            radio_data["__VIEWSTATE"] = viewstate
            radio_data["__EVENTVALIDATION"] = eventvalidation
            radio_data["__EVENTTARGET"] = dropdown
            
            response = session.post(url, data=radio_data)
            soup = BeautifulSoup(response.text, 'html.parser')
            viewstate = soup.find('input', {'name': '__VIEWSTATE'})['value']
            eventvalidation = soup.find('input', {'name': '__EVENTVALIDATION'})['value']
        except:
            output = {
                f'{input_x} does not exist'
            }
            return output

    radio_data["__EVENTTARGET"] = 'ctl00$ContentPlaceHolder1$GridView1'
    radio_data["__EVENTARGUMENT"] = "Select$0"
    radio_data["__VIEWSTATE"] = viewstate
    radio_data["__EVENTVALIDATION"] = eventvalidation

    response = session.post(url, data=radio_data)
    soup = BeautifulSoup(response.text, 'html.parser')

    try:
        khewat_no = soup.find('table',{'id':'ctl00_ContentPlaceHolder1_GridView1'}).find_all('td')[1].find('b').text
        khatoni_no = soup.find('table',{'id':'ctl00_ContentPlaceHolder1_GridView1'}).find_all('td')[2].find('b').text
    except:
        khewat_no = None,
        khatoni_no = None
    
    nakal_url = 'https://jamabandi.nic.in/land%20records/Nakal_khewat'
    nakal_response = session.get(nakal_url)

    with open("nakal_response.html", "w", encoding="utf-8") as file:
        file.write(nakal_response.text)

    with open("nakal_response.html", 'r', encoding='utf-8') as file:
        html_content = file.read()
    
    tree = html.fromstring(html_content)

    vil_name = get_data(tree,given_xpath='//span[@id="lblvill"]/b')
    had_name = get_data(tree,given_xpath='//span[@id="lblhad"]/b')
    teh_name = get_data(tree,given_xpath='//span[@id="lblteh"]/b')
    dis_name = get_data(tree,given_xpath='//span[@id="lbldis"]/b')
    year_name = get_data(tree,given_xpath='//span[@id="lblyer"]/b')

    output = {
        'district_name': data.input_district,
        'district_code': radio_data['ctl00$ContentPlaceHolder1$ddldname'],
        'tehsil_name': data.input_tehsil,
        'tehsil_code': radio_data['ctl00$ContentPlaceHolder1$ddltname'],
        'village_name': data.input_village,
        'village_code': radio_data['ctl00$ContentPlaceHolder1$ddlvname'],
        'jamabandi_year':radio_data['ctl00$ContentPlaceHolder1$ddlPeriod'],
        'khewat_no': khewat_no,
        'khatoni_no': khatoni_no,
        'inner_details':{
            'village':vil_name,
            'hadbast no':had_name,
            'tehsil': teh_name,
            'district':dis_name,
            'year':year_name
        }
    }
    return output

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)



