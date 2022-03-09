import googlemaps
import os

gmaps = googlemaps.Client(key=os.environ.get('GMAPS_KEY'))

def get_places_location(query:str):
    autocomplete = gmaps.places_autocomplete(input_text=query, location="30.29, -98.0", radius=20000)[0]['place_id']
    place = gmaps.place(autocomplete)['result']
    return {
        "name": place['name'],
        "address": place['formatted_address'],
        "location": place['geometry']['location']
    }
    
if __name__ == "__main__":
    print(get_places_location(query="Lous"))