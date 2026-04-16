"""
Creates a CSV file containing the training images.

This script creates /backend/static/training_data.csv with the
scientific name, the link to the image, whether its native or invasive
a link to the associated Australian Native Plants Society (Australia)
(ANPSA) information page. It selects the most common native plants and
the worst invasive weeds in Australia up to a set limit, in a set 
ratio.

This tool is dependent on the ANPSA database. It can be downloaded at
this link - https://anpsa.org.au/native-plant-profiles/. It also 
requires a txt file, the scientific names of the invasive plants.

This script requires that `galah` be installed within the Python 
environment you are running this script in.

This file can also be imported as a module and contains the following
functions:

    * get_plant_urls - returns the plant image links
    * get_native_plants - returns native plant data
    * get_invasive_plants - returns invasive plant data
    * main - the main function of the script
"""

import galah

def get_plant_urls(scientific_name, earliest_year, url_quantity):
    """
    Gets a list of URLs to images of the plant.

    Retrieves the URLs to a set quantity of links from the Atlas of
    Living Australia (ALA) database. If the quantity desired images, 
    exceeds the number of images in the database a warning message will
    be printed.

    Args:
        scientific_name (str): the name of the plant
        earliest_year (str): the earliest year that images of the
        plant were taken
        url_quantity (int): the numbers of image links

    Returns:
        list: a list URL links to images of the plant

    """

    plant_media = galah.atlas_media(
        axa=scientific_name, 
        filters="year>=" + earliest_year, 
        progress_bar=True
    )

    # Selects image links from the pandas.Dataframe object.
    all_image_urls = plant_media['imageUrl'].tolist()
    if len(all_image_urls > url_quantity):
        print(f"WARNING: insufficient URLs for {scientific_name}")
    
    select_image_urls = all_image_urls[:url_quantity]

    return select_image_urls

def get_native_plants(
        plant_spreadsheet,
        earliest_year, 
        plant_quantity, 
        url_quantity):
    """
    Retrieves the data of the native plants.

    Searches the ALA database for the most commonly occuring native 
    plants found in the ANPSA spreadsheet and then collates the
    data.

    Args:
        plant_database: the location of the ANPSA spreadsheet.
        earliest_year: the earliest year that images of the
        plant were taken
        plant_quantity: the number of native plants collected
        url_quantity: the number of images of each plant

    Returns:
        list[list]: a 2D list of the native plant images with their
        scientific names, a list of image links of the plant a
        "NATIVE" label and a link to corresponding ANPSA information 
        page.

    """

    



# Get Native Plants

# Get Invasive Plants

# Main