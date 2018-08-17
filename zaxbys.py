from bs4 import BeautifulSoup
import requests
import os
import pandas

def clear_csv_file(filename):
    """
    Removes csv file
    """
    if(os.path.exists(filename)):
        os.remove(filename)

def get_state_names(location_url):
    """
    Get state names for a given location url
    """
    # Get all state_names location data from zaxbys homepage
    page = requests.get(location_url)
    # Create a BeautifulSoup object
    soup = BeautifulSoup(page.text, 'html.parser')
    options = soup.find(id='state-selector').find_all('option')[1:]
    return [option['value'] for option in options]

def get_location_list(location_url, state_name):
    """
    Gets all the locations for  a given state
    """
    # Get desired location data from zaxbys
    state_url = location_url + '/' + state_name + '/'
    page = requests.get(state_url)
    # Create a BeautifulSoup object
    soup = BeautifulSoup(page.text, 'html.parser')
    locations = soup.find(class_='location-ctn').find_all(class_="location-address-ctn")
    state_information = dict()
    for index, location in enumerate(locations):
        state_information[index] = dict()
        location_address = location.find(class_="location-address").find_all('p')
        state_information[index]['address'] = location_address[0].contents[0]
        temp = location_address[1].contents[0].split(",")
        state_information[index]['city'] = temp[0]
        temp2 = temp[1].strip().split(" ")
        state_information[index]['state'] = temp2[0]
        state_information[index]['zip-code'] = temp2[1]
    return pandas.DataFrame(state_information).transpose()

def main():
    """
    Scrapes state data for the amount of zaxbys in the state
    """
    filename = "location_info.csv"
    clear_csv_file(filename)
    location_url = 'https://www.zaxbys.com/locations/'
    df = pandas.DataFrame()
    state_names = get_state_names(location_url)
    for state_name in state_names:
        state_information = get_location_list(location_url, state_name)
        df = pandas.concat([df, state_information])
    df.to_csv('location_info.csv', index=False)





                
if __name__ == "__main__":
    main()


