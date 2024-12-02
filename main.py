import folium
import json
import os
import requests
from dotenv import load_dotenv
from geopy import distance


def fetch_coordinates(apikey, address):
    base_url = "https://geocode-maps.yandex.ru/1.x"
    response = requests.get(base_url, params={
        'geocode': address,
        'apikey': apikey,
        'format': 'json',
    })
    response.raise_for_status()
    found_places = response.json(
    )['response']['GeoObjectCollection']['featureMember']

    if not found_places:
        return None

    most_relevant = found_places[0]
    lon, lat = most_relevant['GeoObject']['Point']['pos'].split(' ')
    return lon, lat


def get_distance(coffeeshop_inf):
    return coffeeshop_inf['distance']


def calculate_distances(your_coords, coffeeshops):
    all_coffeeshops_inf = []
    for coffeeshop in coffeeshops:
        coffeeshop_inf = {
            'title': coffeeshop['Name'],
            'distance': distance.distance(
                reversed(your_coords),
                reversed(coffeeshop['geoData']['coordinates'])).km,
            'latitude': coffeeshop['geoData']['coordinates'][1],
            'longitude': coffeeshop['geoData']['coordinates'][0],
        }
        all_coffeeshops_inf.append(coffeeshop_inf)
    return sorted(all_coffeeshops_inf, key=get_distance)


def create_map(your_coords, coffeeshops):
    m = folium.Map(location=your_coords[::-1], zoom_start=14)

    folium.Marker(
        location=your_coords[::-1],
        tooltip='Это вы!',
        popup='Это вы!',
        icon=folium.Icon(color='red'),
    ).add_to(m)

    for coffeeshop in coffeeshops[:5]:
        folium.Marker(
            location=[coffeeshop['latitude'], coffeeshop['longitude']],
            tooltip='Нажми!',
            popup=coffeeshop['title'],
            icon=folium.Icon(color='green'),
        ).add_to(m)

    return m


def main():
    load_dotenv()
    apikey = os.environ['APIKEY']

    your_location = input('Где вы находитесь? ')
    your_coords = fetch_coordinates(apikey, your_location)

    with open("coffee.json", "r", encoding="cp1251") as coffee_file:
        coffee_file_contents = coffee_file.read()
        coffeeshops = json.loads(coffee_file_contents)

    sorted_all_coffeeshops_inf = calculate_distances(your_coords, coffeeshops)
    coffeeshops_on_the_map = create_map(
        your_coords,
        sorted_all_coffeeshops_inf
    )
    coffeeshops_on_the_map.save("index.html")


if __name__ == '__main__':
    main()
