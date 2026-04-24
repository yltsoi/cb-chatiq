import json
import math
import os
import re
import time
from queue import Queue
from typing import Any, Dict, List
from uuid import uuid4
import boto3


from service.base.components.utils.constants import *

def number_to_text(number):

    try:
        number = int(float(number))
    except:
        print(
            "Error in converstion of number to string"
        )
        return str(number)
    
    if len(str(number)) > 15:
        return "999 trillion"
    if number == 0:
        return "zero"
    
    units = ["", "thousand", "million", "billion", "trillion"]
    num_str = str(number)
    num_groups=int(math.ceil(len(num_str) / 3 ))
    num_str = num_str.zfill(num_groups * 3 )
    text = ""

    for i in range(num_groups):
        group = int(num_str[i * 3 : (i+1) * 3])
        if group != 0:
            if i != 0:
                text += " "
            text += f"{group}{units[num_groups -i -1]}"
    
    return text.strip()


def load_config_filepaths(env, chatiq_version = CHATIQ_BASE, components = [] ):

    config_file_dict = {}
    if not env:
        return config_file_dict
    
    config_load_filename = "service/" + chatiq_version.replace('chatiq_', "") + '/' + env.lower() + '_components_config.json'
    with open(config_load_filename, "r'") as f:
        config_file_dict = json.load(f)

    return config_file_dict


def split_and_add_to_queue( text, queue):
    """
    Splits the input text string into words and whitespace ( including newlines) and put them into the queue

    Args:
    text (str): the input text string to be split
    queue( queue): the queue to store the words and whitespace
    """
    tokens = split_string(text)
    for token in tokens:
        queue.put(token)
    # stop signal
    queue.put(None)

def split_string(text):
    """
    Split the input text string into words and whitespace (including newline)
    return list of substring
      
    """

    return re.findall(r'\S+|\s+', text)

def recreate_string_from_queue(queue):
    """
    Recreate the original string by popping elements from the queue

    Args:
    queue : Thequeu containing the word and whitespace
    
    """
    result = []
    while not queue.empty():
        result.append(queue.get())
    return ''.join(result)

# helper function
def yield_content(content, special_format, token_throttling_time=0.025):
    time.sleep(token_throttling_time)
    return f"data: {content}\n " if special_format else content

def get_region_name():
    try:
        region_name = boto3.session.Session().region_name
        if region_name is None:
            region_name = 'us-east-1'
        return region_name
    except Exception as e:
        print(e)
        return "us-east-1"
    
    
