import re
import requests
from bs4 import BeautifulSoup
import json
import csv

class Zillow():

    # Grabs the base params required by zillow.com for querying
    # The site for data
    def getParams(self, north=-115.56063652038574, east=-110.18832206726074, south=31.701736103303432, west=35.29649332118693):
        params = {
            "searchQueryState": {
                "pagination": {},
                "usersSearchTerm": "Scottsdale, AZ",
                "mapBounds": {
                    "north": north,
                    "east": east,
                    "south": south,
                    "west": west
                },
                "mapZoom": 14,
                "isMapVisible": True,
                "filterState": {
                "ah": {
                    "value": True
                },
                "sort": {
                    "value": "globalrelevanceex"
                }
                },
                    "isListVisible": True,
                    "regionSelection": [
                    {
                        "regionId": 38590,
                        "regionType": 6
                    }
                ]
            }
        }

        return params

    # Grabs the base headers required by zillow.com for querying
    # The site for data
    def getHeaders(self):
        headers = {
            'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
            'accept-encoding': 'gzip, deflate, br',
            'accept-language': 'en-US,en;q=0.9',
            'cache-control': 'max-age=0',
            'sec-fetch-dest': 'document',
            'sec-fetch-mode': 'navigate',
            'sec-fetch-site': 'same-origin',
            'sec-fetch-user': '71',
            'upgrade-insecure-requests': '1',
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.110 Safari/537.36'
        }
        return headers


    def beginScraper(self, offline=False, passthrough=False): 
        sandbox = None
        homes = None
        url = "https://www.zillow.com/homes/for_sale/"
        headers = self.getHeaders()
        params = self.getParams()

        if offline:
            success_check = False
            try:
                with open('sandbox.html', 'r') as s:
                    sandbox = s.read()

            except:
                print("It appears either the sandbox.html file was deleted or moved.")
                print("Downloading HTML from Zillow...")
                try:
                    success_check = self.downloadHTML(url, params)
                    if success_check:
                        with open('sandbox.html', 'r') as s:
                            sandbox = s.read()
                        print("done.")
                    else:
                        print("Failed to download HTML.")
                        return False

                except Exception as e:
                    print(e)
                    print("Something went wrong on line 91")

            homes = self.parse(sandbox)

        else:
            response = self.fetch(url, headers, params)
            homes = self.parse(response.text)

        formatted = self.format(homes)

        if passthrough:
            return formatted
        else:
            csv = self.send2csv(formatted)
    

    # To best avoid being blocked either via IP/User-Agent/Cookie or
    # What have you, I recommend using this function to download
    # The Site so u can just query the HTML file.
    def downloadHTML(self, url, params):
        headers = self.getHeaders()
        results = requests.get(url, headers=headers, params=params) 
        status = str(results.status_code)

        if str(200) not in status:
            print("Something went wrong. HTTP status code: " + status)
            print("This could be due to Zillow's")
            print("Captcha services detecting suspicious activity")
            return False
        else:     
            with open('sandbox.html', 'w') as i:
                i.write(str(BeautifulSoup(results.text, 'html.parser').prettify()))
            return True


    # Makes request to zillow.com for site data
    def fetch(self, url, headers, params):
        print("Fetching site data...")
        response = requests.get(url, headers=headers, params=params)
        status = str(response.status_code)
        if str(200) not in status:
            print("Something went wrong. HTTP status code: " + status)
            print("This could be due to Zillow's")
            print("Captcha services detecting suspicious activity")
        else:
            print(status + " Success")
            return response
        

    # parse() will need response.text once ready for making 
    # HTTP requests
    def parse(self, response):
        DATA_LIST = []
        JSON_PARSED = []

        script_count = 0
        span_count = 0
        img_count = 0
        try:
            soup = BeautifulSoup(response, 'html.parser')  
        except Exception as e:
            print(e)
            print("\n")
            print(response)

        listings = soup.find('ul', {'class': 'photo-cards'})

        #Grabs majority of data
        for l in listings.contents:
            try:                    
                if listings.contents[script_count].script.contents[0]:
                    script = listings.contents[script_count].script.contents[0]
                    
                    DATA_LIST.append(script)
                    d = DATA_LIST[span_count]
                    JSON_PARSED.append(json.loads(d))

                    if listings.contents[script_count].span.contents[0]:
                        price = listings.contents[script_count].span.contents[0]
                        p = JSON_PARSED[span_count]
                        p['price'] = re.findall(r'\S+', price)
                        span_count += 1

            except Exception as e:
                #print(e)
                pass

            script_count += 1

        return JSON_PARSED


    # Takes a dict type param which is used to remove redudant
    # Data.
    def format(self, data):
        FORMATTED = []

        for d in data:
            d['price'] = re.sub(r'[^\d$,]', '', str(d['price']))
            if '@context' in d:
                d.pop('@context')
            if '@type' in d:
                d.pop('@type')

        # Formats floorSize key with just the floor size
        for d in data:
            x = str(re.findall(r"'value': '([^']*)'", str(d['floorSize'])))
            y = re.sub(r'\D', '', x)
            d['floorSize'] = y

        for d in data:
            d['streetAddress'] = d['address']['streetAddress']
            d['city'] = d['address']['addressLocality']
            d['state'] = d['address']['addressRegion']
            d['zip'] = d['address']['postalCode']
            x = d['address']
            d.pop('address')

            d['fullAddress'] = d['name']
            d.pop('name')
                
        for d in data:
            x = d['geo']
            if 'latitude'in x:
                d['latitude'] = x['latitude']
            
            if 'longitude' in x:
                d['longitude'] = x['longitude']
            
            d.pop('geo')
        
        return data


    # Preps data to be exported to CSV
    def send2csv(self, data, filename='housingdata.csv', all=True):
        KEYS = []
        VALUES = []

        HOMES_DICT = {}

        count = 0

        if 'housingdata.csv' in filename:
            print("No filename specified. Using " + filename)

        for d in data[1].keys():
            KEYS.append(d)

        for d in data:
            
            VALUES.append(d.values())


        
        
        for v in VALUES:
            new_list_name = f"home{count}"
            HOMES_DICT[new_list_name] = []
            
            for d in v:
                HOMES_DICT[f"home{count}"].append(d)

            count += 1
        
        count = 0

        try:
            with open(filename, 'w', newline='') as f:
                excel = csv.writer(f)
                
                excel.writerow(KEYS)

                for h in HOMES_DICT:
                    excel.writerow(HOMES_DICT[f"home{count}"])
                    count += 1

            print("Data uploaded to " + filename + " successfully.")
        
        except Esception as e:
            print(e)



if __name__ == "__main__":
    z = Zillow()
    z.beginScraper()




