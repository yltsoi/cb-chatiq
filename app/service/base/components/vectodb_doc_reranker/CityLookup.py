from allcities import cities

class CityLookup:

    def __init__(self):

            city_list = list(cities._set)
            self.city_dicts = [city.dict for city in city_list]
            self.city_data = {}
            for city_dict in self.city_dicts:
                country_code = city_dict["country_code"]
                name = city_dict["name"]
                if country_code not in self.city_data:
                     self.city_data[country_code] = {}
                if name not in self.city_data[contry_code]:
                     self.city_data[country_code][name] = []
                     self.city_data[country_code][name].append(city_dict)

                     
    