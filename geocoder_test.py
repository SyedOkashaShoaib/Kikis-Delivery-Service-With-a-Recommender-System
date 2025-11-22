
from geopy.geocoders import get_geocoder_for_service
from typing import Dict, Optional
from geopy.location import Location
import time

class Location_Handler:

    @staticmethod
    def Address_LookUp(address) -> Optional[Location]:
        #Basic lookup with a given string: First Choice Nominatim: Second Choice Photon
        
        #Nominatim Lookup:
        try:
            nominatim_cls = get_geocoder_for_service('nominatim')
            nominatim_geolocator = nominatim_cls(user_agent="Food_Deilvery_App")
            location = nominatim_geolocator.geocode(address)
            time.sleep(1)
            if location: #Location Found
                #print("Nominatim Found :")
                return location
        except:
            #print("Fail Once")
            pass

        #Photon Lookup:
        try:
            photon_cls = get_geocoder_for_service('photon')
            photon_geolocator = photon_cls(user_agent="Food_Delivery_App", timeout=10)
            location = photon_geolocator.geocode(address)
            time.sleep(1)
            if location:
                #print("Photon Found :")
                return location
        except:
            #3print("Fail Twice")
            pass

        #Failed
        return None
    '''
    @staticmethod
    def Reverse_Address_LookUp(location : Location) -> Dict[str, Optional[str]]: #This will take a location and return a dictionary that can map to data model for location
        
        if not hasattr(location, 'raw'): # Means the location we have was taken from the Photon API, we want Nominatim for more structured details
            try:
                nominatim_cls = get_geocoder_for_service('nominatim')
                nominatim_geolocator = nominatim_cls(user_agent="Food_Deilvery_App")
                new_location = nominatim_geolocator.reverse(location.latitude, location.longitude)
                time.sleep(1)
                if new_location: #Location Found
                    #print("Nominatim Found :")
                    location = new_location 
                else:
                    #print("Reverse Lookup Failed")
                    return None
            except:
                #print("Fail Once")
                return None
            
            #print(location.address)
            #print("Succeed")
        
        details = {
            'latitude': location.latitude,
            'longitude': location.longitude,
            'full_address': location.address,
            'name': None,
            'street': None,
            'city': None,
            'osm_id': None,
            'osm_type': None,
            'data_source': 'unknown'
        }

        raw_data = location.raw
        
        # Parse based on service type. Nominatim has nested address dictionary
        if 'address' in raw_data:
            # Nominatim structure
            details['data_source'] = 'nominatim'
            address_components = raw_data['address']
            
            details.update({
                'osm_id': raw_data.get('osm_id'),
                'osm_type': raw_data.get('osm_type'),
                'name': raw_data.get('name'),
                'street': address_components.get('road'),
                'city': address_components.get('city') or address_components.get('town') or address_components.get('village')
            })
            
        elif 'properties' in raw_data:
            # Photon structure
            details['data_source'] = 'photon'
            properties = raw_data['properties']
            
            details.update({
                'osm_id': properties.get('osm_id'),
                'osm_type': properties.get('osm_type'),
                'name': properties.get('name'),
                'street': properties.get('street'),
                'city': properties.get('city')
            })
        else:
            print("wrong struct")

        #print(details)
        
        return details
    '''
    @staticmethod
    def Reverse_Address_LookUp(location: Location) -> Dict[str, Optional[str]]:
        if not hasattr(location, 'raw'):
            try:
                nominatim_cls = get_geocoder_for_service('nominatim')
                nominatim_geolocator = nominatim_cls(user_agent="Food_Deilvery_App")
                new_location = nominatim_geolocator.reverse(location.latitude, location.longitude)
                time.sleep(1)
                if new_location:
                    location = new_location
                else:
                    return None
            except Exception as e:
                print(f"Reverse lookup error: {e}")
                return None

        details = {
            'latitude': location.latitude,
            'longitude': location.longitude,
            'full_address': location.address,
            'name': None,
            'street': None,
            'city': None,
            'osm_id': None,
            'osm_type': None,
            'data_source': 'unknown'
        }

        if not hasattr(location, 'raw') or location.raw is None:
            return details

        raw_data = location.raw

        #print("DEBUG TESTING")
        #print(location.raw)
        #print("DEBUG TESTING END ")
        
        # Unified extraction approach
        def get_nested_value(data, keys):
            """Try multiple possible keys to get a value"""
            for key in keys:
                if key in data:
                    return data[key]
            return None

        # Extract address components based on common patterns
        if 'address' in raw_data and isinstance(raw_data['address'], dict):
            # Nominatim-style nested address
            address_comp = raw_data['address']
            details['data_source'] = 'nominatim'
            details.update({
                'osm_id': raw_data.get('osm_id'),
                'osm_type': raw_data.get('osm_type'),
                'name': get_nested_value(raw_data, ['name', 'display_name']),
                'street': get_nested_value(address_comp, ['road', 'street', 'highway']),
                'city': get_nested_value(address_comp, ['city', 'town', 'village', 'municipality', 'county'])
            })
        elif 'properties' in raw_data and isinstance(raw_data['properties'], dict):
            # Photon-style
            properties = raw_data['properties']
            details['data_source'] = 'photon'
            details.update({
                'osm_id': properties.get('osm_id'),
                'osm_type': properties.get('osm_type'),
                'name': properties.get('name'),
                'street': properties.get('street'),
                'city': properties.get('city')
            })
        else:
            # Direct extraction from root level
            details['data_source'] = 'direct'
            details.update({
                'osm_id': raw_data.get('osm_id'),
                'osm_type': raw_data.get('osm_type'),
                'name': get_nested_value(raw_data, ['name', 'display_name']),
                'street': get_nested_value(raw_data, ['road', 'street']),
                'city': get_nested_value(raw_data, ['city', 'town', 'village'])
            })

        for key in details:
            if details[key] is None:
                details[key] = 'None'
        
        return details    

    @staticmethod
    def Address_LookUp_Advanced(address_dict : Dict[str, str]) -> Optional[Location]:
        #Might have change the function parameters to accept a bunch of string or a list depending on the workflow. Try to avoid that as dict is the best option
        #All the feilds of address_dict are required and assumed complete with the exception of house number for user accessibility
        '''
        address_dict Structure{
        name: Optional[str] = None,        # name/landmark
        street: Optional[str] = None,      
        house_number: Optional[str] = None, 
        city: Optional[str] = None,        
        postal_code: Optional[str] = None, 
        country: Optional[str] = None,     
        neighborhood: Optional[str] = None 
        }
        '''
        # To try different Combinations of parameters to get a usable location: sorted by most to least accurate
        strategies = [ 
            _strategy_complete_address,   
            _strategy_street_city_country,  
            _strategy_postal_city_country, 
            _strategy_landmark_city,      
        ]

        for strategy in strategies:
            location = strategy(address_dict)
            if location:
                return location # A viable Location Found!
        
        return None # All Locations Failed. Invalid Location

def _strategy_complete_address(address_dict: Dict) -> Optional[Location]:
    house_number = address_dict.get("house_number")
    if house_number is None: #in-case house number is not given
        house_number = address_dict.get("name")
    
    address_parts = [
        house_number,
        address_dict.get('street'),
        address_dict.get('neighborhood'),
        address_dict.get('city'),
        address_dict.get('postal_code'),
        address_dict.get('country')
    ]
    address = ", ".join(address_parts)
    return Location_Handler.Address_LookUp(address)

def _strategy_street_city_country(address_dict: Dict) -> Optional[Location]:  
    address = f"{address_dict['street']}, {address_dict['city']}, {address_dict['country']}"
    return Location_Handler.Address_LookUp(address)

def _strategy_postal_city_country(address_dict: Dict) -> Optional[Location]:     
    city_part = address_dict.get('city', '') #city might be empty if the data is to be retrieved from nominatim API
    address = f"{address_dict['postal_code']}, {city_part}, {address_dict['country']}"
    return Location_Handler.Address_LookUp(address.strip(', '))

def _strategy_landmark_city(address_dict: Dict) -> Optional[Location]:
    address = f"{address_dict['name']}, {address_dict['city']}"
    if address_dict.get('country'):
        address += f", {address_dict['country']}"
    return Location_Handler.Address_LookUp(address)

'''
address = "Hot N Spicy Malir link hw Karachi"
location = Location_Handler.Address_LookUp(address)
if location:
    print(f"{location.address}")
    Location_Handler.Reverse_Address_LookUp(location)
else:
    print("LookUp Failed")
'''

'''
address_dict = {"name" : "Hot N Spicy", "street" : "Malir Link to Super Hwy", "house_number" : "", "city" : "Karachi", "postal_code" : "75070", "country" : "Pakistan", "neighborhood" : "Malir"}
location = Address_LookUp_Advanced(address_dict)
if location:
    print(f"{location.address}")
    #Reverse_Address_LookUp(location)
else:
    print("LookUp Failed")
'''


#geolocator = Nominatim(user_agent="testing_app")
#location = geolocator.geocode("Tipu Sultan Housing Society, Rufi Down Town, Karachi")
#print(location.address)
#Flatiron Building, 175, 5th Avenue, Flatiron, New York, NYC, New York, ...
#print((location.latitude, location.longitude))
#(40.7410861, -73.9896297241625)
#print(location.raw)
#{'place_id': '9167009604', 'type': 'attraction', ...}
