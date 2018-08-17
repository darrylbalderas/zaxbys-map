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


def get_latitude_longitude(address, city, state):
    mapping_url = 'https://maps.googleapis.com/maps/api/geocode/json?address='
    split_address = '+'.join(address.split(" "))
    split_city = '+'.join(city.split(" "))
    split_state = '+'.join(state.split(" "))
    string = mapping_url + split_address + ",+" + split_city + ",+" + split_state
    response = requests.get(string).json()
    try:
        location = response['results'][0]['geometry']['location']
        return location['lat'], location['lng']
    except:
        return None, None


def create_list_of_locations(state_informations):
    """
    Writes to a specified csv file
    """
    df = pandas.DataFrame(columns=['latitude', 'longitude'])
    for key in state_informations.index:
        lat, lng = get_latitude_longitude(
            state_informations.iloc[key]['address'], state_informations.iloc[key]['city'], state_informations.iloc[key]['state'])
        if lat == None and lng == None:
            pass
        else:
            df.loc[key] = [lat, lng]
    return df

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
        df = pandas.concat([df, create_list_of_locations(state_information)])
    df.to_csv('coordinates.csv', index=False)





                
if __name__ == "__main__":
    main()


