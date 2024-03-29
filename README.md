# The Zillow Web-Scraper

 Basic Webscraper specialized for Zillow (http://www.zillow.com) that grabs important data from home listings such as prices, addresses, etc.

![Demo](./assets/Zillow-Web-Scraper-Demo-Short.mp4)

## Table of Contents
- [Features](#features)
- [Installation](#installation)
- [Usage](#usage)
- [License](#license)

## Features
These are the following functions that you can use for scraping data from Zillow.

### beginScraper()

- The entry point of the scraper that accepts 2 optional parameters:

    > `offline=False` : When set to `True`, the scraper attempts to read an HTML file called "sandbox.html" that contains previously downloaded data. If the file exists, it reads its content and proceeds to parse the data using the `parse()` function. If the file doesn't exist, it attempts to download the HTML from Zillow using the `downloadHTML()` function and the provided URL and parameters. If the download is successful, it saves the HTML to the "sandbox.html" file, reads its content, and parses it. If any errors occur during the process, appropriate error messages are displayed.
    >
    > If offline is set to `False`, the scraper sends a request to the Zillow website using the `fetch()` function, passing the URL, headers, and parameters. The response is then parsed using the `parse()` function.
    >
    > After parsing the data, the `format()` function is called to transform the parsed data into a desired format. 


     <br>

    > `passthrough=False` : Finally, if passthrough is set to `True`, the formatted data is returned. Otherwise, the data is converted to a CSV format using the `send2csv()` function.

### getHeaders()

- Returns the HTTP headers used when making web requests

### getParams()

- Returns default parameters but can be tweaked using 5 optional parameters:

    - `userSearchTerm="Los Angeles, CA"`
    - `west=-119.08327180664062`
    - `east=-117.74019319335937`
    - `south=33.5731428127787`
    - `north=34.46664636821635`

    <br>
- These parameters determine what region Zillow will search and pull housing data from. They are required by Zillow for displaying the map which is then populated with home listings. The `userSearchTerm` parameter is supposed to tell Zillow the general location of the housing data you want while the `west`, `east`, `north`, and `south` parameters generate the mapbounds that the home listings will populate in. 


### downloadHTML(url, params)

- Allows you to download the HTML content from Zillow using the requests library. The purpose of this function is to help you avoid being blocked by Zillow's security measures, such as IP/User-Agent/Cookie restrictions, by allowing you to query the downloaded HTML file instead of making direct requests to the website. 

    > `url` : URL used to create the web request.

    > `params` : Parameters that are url-encoded and appended to the URL for getting location specific data.


- <b>This should only be used if you are going to be making multiple requests when running code.</b>

### fetch(url, headers, params)

- Responsible for making a request to the Zillow website to fetch site data. It takes in a URL, headers, and parameters as inputs.

    > `url` : URL used to create the web request.

    > `headers` : HTTP Headers that are passed to the requests.get method when making web requests. 

    > `params`: Parameters that are url-encoded and appended to the URL for getting location specific data.

- Upon execution, the code first prints a message indicating that it is fetching the site data. It then encodes the parameters and constructs the full URL. The requests.get method is used to send a GET request to the Zillow website with the provided headers and full URL. The HTTP response status code is then checked. If the status code is not 200 (indicating a successful request), an error message is printed, suggesting that it might be due to Zillow's captcha services detecting the scraper.

- However, if the status code is 200, indicating a successful request, the code prints a success message along with the status code and returns the response object, allowing the caller of this function to access the fetched site data.

### parse(response)

- Responsible for parsing raw HTML response data using the response parameters.

    > `response`: Takes in a <b>requests.get</b> `response.text` object, which should contain the HTML content of a webpage. The code begins by initializing two empty lists, `DATA_LIST` and `JSON_PARSED`.

    <br>

- Attempts to parse the HTML content using the <b>BeautifulSoup</b> library, using the `'html.parser'` parser. If an exception occurs during parsing, the error message and the response content are printed for debugging purposes.

- Finds the `<ul>` elements with the class 'photo-cards' within the parsed HTML. This element is expected to contain multiple listings.

- A loop iterates through each listing within the listings object. For each listing, the code tries to access the script and span elements within the listing. If the script element exists and has contents, it is appended to `DATA_LIST`. The content of the script is then extracted and parsed as JSON, which is appended to the `JSON_PARSED` list.

- If the span element exists within the script, the code retrieves the price from the span element's contents. The price is then added to the corresponding JSON object in the `JSON_PARSED` list.

- Finally, the `JSON_PARSED` list, containing the extracted data from the listings, is returned.

### format(data)

- Formats the scraped data to remove redundant information. The format function takes a dictionary parameter data and performs several formatting operations on it.

> `data` : Takes a dictionary object that should've been returned by the `parse()` function.

- The code first removes the `@context` and `@type` keys from each dictionary in the data list, if they exist. Then, it formats the `'floorSize'` key by extracting only the numerical value from the original string and assigns it back to the `'floorSize'` key.

- Next, the code restructures the address information by extracting specific components from the nested `'address'` dictionary. The `'streetAddress'`, `'city'`, `'state'`, and `'zip'` keys are created and assigned the corresponding values. The original `'address'` dictionary is then removed from the dictionary.

- After that, the code handles the `'geo'` information. If the `'latitude'` key exists in the `'geo'` dictionary, it is assigned to the `'latitude'` key in the main dictionary. Similarly, if the `'longitude'` key exists, it is assigned to the `'longitude'` key in the main dictionary. The `'geo'` key is then removed from the dictionary.

- Finally, the formatted data dictionary is returned as the output of the function.

- This code improves the readability and structure of the scraped data, making it more suitable for further analysis and manipulation.

### send2csv(data)

- Takes 1 required parameter as well as 1 optional paramter: 

> `data` :  Takes dict type values which should be the formatted data.

> `filename` : Specifies the name of the CSV file to be created (default is housingdata.csv).

The code begins by initializing empty lists (`KEYS` and `VALUES`) and an empty dictionary (`HOMES_DICT`). It then iterates through the keys of the data dictionary and appends them to the `KEYS` list. Next, it loops through each item in the data list, appends the corresponding values to the `VALUES` list, and assigns a unique name to each list in `HOMES_DICT`.

After the data preparation, the code attempts to open the specified file in write mode. It writes the `KEYS` list as the header row in the CSV file. Then, it iterates through the `HOMES_DICT` dictionary, writing each list as a row in the CSV file. Finally, it prints a success message if the data is uploaded successfully or prints an error message if an exception occurs during the process.

This code is a useful utility for exporting Zillow housing data to a CSV format, enabling further analysis and manipulation of the scraped data.

## Installation

### Prerequisites

1. Python 3.10 or later must be installed

2. If you would like to run the demo.ipynb demo file, you will need to install Jupyter Notebook first. You can do the following by running the following pip command 
```shell
pip install jupyter
```
- Alternatively, you can also install the jupyter notebook extension if you are using VSCode / VSCodium.

### Download
1. Run the following command in your terminal:
    ```shell
    git clone https://github.com/h8ngryDev4Hire/ZillowWebScraper
    ```
2. BOOM! You're done! You'll be able to play around with the scraper using the demo.ipynb demo file or by importing it into your python project.

3. If you are opting to use the zillow.py code in your project, you can simply import it like so:
    ```python
    from zillow import Zillow
    ```

## Usage
- You are welcome to use the code in this repository for your own projects. However, if you use this code, I kindly request that you provide proper attribution by mentioning that it was created by me. You can include the following acknowledgment in your project documentation, README, or wherever appropriate:

<br>

> "Parts of this project are based on code from [Zillow Web-Scraper](https://github.com/h8ngryDev4Hire/ZillowWebScraper) by [h8ngryDev4Hire](https://github.com/h8ngryDev4Hire/)."


<br>

- Feel free to modify the code to suit your needs, but please remember to acknowledge the original source.


## Contributing
<<<<<<< HEAD
- This is a personal project I made. Feel free to use it in your code projects. 
=======
- This is a personal project I made. Feel free to use it in your code projects!
>>>>>>> c332e5cb68db9c6b5a79b0ddedb5e17731b23dcd

## License
- This project is licensed under the GPL3 License. Check [LICENSE.md](https://github.com/h8ngryDev4Hire/ZillowWebScraper/blob/main/LICENSE.md) for more information. 
