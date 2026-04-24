from allcities import cities

class CityLookup:
    """
    This class represents a city lookup module that helps to find city information
    such as latitude, longitude, and other details based on the city name, country_code,
    and admin1 code. It provides methods for finding city objects and looking up latitude
    and longitude
    
    Methods:
        __init__: Initializes the CityLookup instance and sets up the city data structure
        find_city_object: Finds a city object based on the city name, country code, and admin1 code
        lookup_lat_long: Returns the latitude and longitude of a city dictionary
    
    """

    def __init__(self):
        """
        Initialize the CityLookup instance and sets up the city data structure

        This method initalized the CityLookup instance by coverting the imported city
        data into a list of dictionaries and organizing them into a nested dictionary
        structure based on country codes and city names for easier searching
        
        """
        city_list = list(cities._set)
        self.city_dicts = [city.dict for city in city_list]
        self.city_data = {}
        for city_dict in self.city_dicts:
            country_code = city_dict["country_code"]
            name = city_dict["name"]
            if country_code not in self.city_data:
                self.city_data[country_code] =  {}
            if name not in self.city_data[country_code]:
                self.city_data[country_code][name] = []
            self.city_data[country_code][name].append(city_dict)
        
    def find_city_object(self, city_name, country_code=None, admin1_code=None):
        """
        Finds a city object based on the city name, country code, and admin1 code

        Args:
            city_name (str): The name of the city to search for
            country_code( str, optional): The country code of the city to search for
            admin1_code ( str, optional): The amdin1 code of the city to search for
        
        Returns:
            dict: The city dictionary with the matching criteria or None if not found

        This method searches for a city object by first filtering the cities based on the 
        provided country code ( if given) and then searching for the city_name in the filtered
        cities. It further filters the cities based on the admin1 code (if given) and returns
        the matching city object if found. If multiple cities are found, it returns the city
        with the hightes population
        
        """

        found_cities = []
        if country_code:
           if city_name in self.city_data[country_code]:
               found_cities.extend(self.city_data[country_code][city_name])
           else:
               for cities in self.city_data[country_code].values():
                   found_cities.extend(
                       [
                           city
                           for city in cities
                           if city_name in city["alternatenames"]
                       ]
                   )
        else:
            for country in self.city_data.values():
                if city_name in country:
                    found_cities.extend(country[city_name])
                else:
                    for cities in country.values():
                        found_cities.extend(
                            [
                                city
                                for city in cities
                                if city_name in city["alternatenames"]
                            ]
                        )
        
        if len(found_cities) == 1:
            return found_cities[0]
        
    
        if admin1_code:
            found_cities = [
                city
                for city in found_cities
                if city["admin1_code"] == admin1_code

            ]
        
        if len(found_cities) == 1:
            return found_cities[0]
        
        if found_cities:
            return max(found_cities, key=lambda x: x.get("popilation", 1000))
        else:
            return None
    
    def lookup_lat_long(self, city_dict):
        """
        Returns the latitidue and longittude of a city dictionary

        Args:
            city_dict(dict): The city dictionary to look up the latitude and longitude for

        
        Returns:
            tuple: The latitude and longitude
        
        """
        if city_dict:
            return city_dict["latitude"], city_dict["longittude"]
        else:
            return None