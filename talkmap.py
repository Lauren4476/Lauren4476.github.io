# Leaflet cluster map of academic places (universities, jobs, conferences, visits)
#
# Run this from the repo root. It reads .md files in _places/, which contains
# one file per place with a `location` YAML field. This scrapes that field,
# geolocates it with geopy/Nominatim, and uses the getorg library to output
# data, HTML, and Javascript for a standalone cluster map.
import frontmatter
import glob
import getorg
from geopy import Nominatim
from geopy.location import Location
from geopy.exc import GeocoderTimedOut

# Set the default timeout, in seconds
TIMEOUT = 5

# Collect the Markdown files
g = glob.glob("_places/*.md")

# Prepare to geolocate
geocoder = Nominatim(user_agent="academicpages.github.io")
location_dict = {}
location = ""
permalink = ""
title = ""

# Perform geolocation
for file in g:
    # Read the file
    data = frontmatter.load(file)
    data = data.to_dict()

    # Press on if the location is not present
    if 'location' not in data:
        continue

    # Prepare the description
    title = data['title'].strip()
    venue = data['venue'].strip()
    location = data['location'].strip()
    description = f"{title}<br />{venue}; {location}"

    # If the file supplies manual coordinates, use those directly and skip
    # geocoding entirely. This is useful for remote sites (e.g. mountaintop
    # observatories) that Nominatim doesn't recognize or geocodes incorrectly.
    if 'latitude' in data and 'longitude' in data:
        location_dict[description] = Location(
            address=location,
            point=(data['latitude'], data['longitude'], 0),
            raw={}
        )
        print(description, location_dict[description])
        continue

    # Geocode the location and report the status
    try:
        location_dict[description] = geocoder.geocode(location, timeout=TIMEOUT)
        print(description, location_dict[description])
    except ValueError as ex:
        print(f"Error: geocode failed on input {location} with message {ex}")
    except GeocoderTimedOut as ex:
        print(f"Error: geocode timed out on input {location} with message {ex}")
    except Exception as ex:
        print(f"An unhandled exception occurred while processing input {location} with message {ex}")

# Save the map
m = getorg.orgmap.create_map_obj()
getorg.orgmap.output_html_cluster_map(location_dict, folder_name="talkmap", hashed_usernames=False)