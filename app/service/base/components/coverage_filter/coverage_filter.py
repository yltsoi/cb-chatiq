import os
import requests
import boto3
from botocore.exceptions import ClientError
from service.base.components.utils.constants import *
from service.base.components.utils.jpmc_auth import get_coverage_token
from service.base.components.utils.utils import is_valid_eci, update_if_not_none
from collections import defaultdict
class Coverage_Filter:
    """
    This class represents a coverage filter module that takes a list of Open Search documents 
    and retrieve information about the coverage of those companies. It provides method for
    checking whether a company is covered as well as more details about the level of coverage
    and individuals involved
    
    Methods:
        __init__: Initialized the Coverage Filter instance
        is_valid_eci: Determine whether a given company card has a valid ECI
        generate_api_url_with_filters: Creates an api url with given filters and values
        get_ecis: Retrieves all the valid ecis from a list of company cards

        get_filtered_company_cards: Based on if user wants covered or uncovered companies
        add_primary_banker_to_company_card: return the primary banker for a list of company cards
    
    """

    def __init__(self, update_primay_banker_on_company_card=False, update_coverage_officers_on_company_card=False):

        self.update_primay_banker_on_company_card = update_primay_banker_on_company_card
        self.update_coverage_officers_on_company_card = update_coverage_officers_on_company_card
    
    def generate_api_url_with_filters( self, filterValues: dict):

        base_url = "https://es.cbds.prod.aws.jpmchase.net/es/get/v1/mdm-wholesale-coverage?"

        filter_name = "filtername="
        filter_name += "^|^".join(filterValues.keys())
        filter_name += "&"

        filter_values = "filtervalue="
        filter_values += "^|^".join("|".joiin(v) if isinstance(v, list) else v for v in filterValues.values())

        final_url = base_url + filter_name + filter_values

        return final_url
    
    def get_ecis(self, company_cards: list)
        
        eci_list = []

        for card in company_cards:
            # Retreive the eci from the company card
            card_source = card[SOURCE]
            try:
                eci = card_source[ATTR_ECI]
                valid = is_valid_eci(eci)
                if valid:
                    eci_list.append(eci)
            except:
                continue
        
        return eci_list
    
    


        