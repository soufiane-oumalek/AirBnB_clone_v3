#!/usr/bin/python3
"""users al7bin"""
from flask import abort, make_response, request
from api.v1.views import app_views
from models import storage
from models.user import User
from models.place import Place
from models.state import State
from models.city import City
from models.amenity import Amenity
from json import dumps


def json_ser(obj):
    json_obj = {}
    for key in obj:
        json_obj[key] = obj[key].to_dict()
    return (json_obj)


def places_json(lst):
    json_list = []
    for place in lst:
        json_list.append(place.to_dict())
    return (json_list)


@app_views.route('/cities/<city_id>/places', methods=['GET'])
def get_places(city_id):
    city = storage.get(City, city_id)
    if city is None:
        return abort(404)
    return make_response(
        dumps(places_json(city.places)), 200)


@app_views.route('/places/<place_id>', methods=['GET'])
def get_place(place_id):
    place = storage.get(Place, place_id)
    if place is None:
        return abort(404)
    return (place.to_dict())


@app_views.route('/places/<place_id>', methods=['DELETE'])
def delete_place(place_id):
    place = storage.get(Place, place_id)
    if place is None:
        abort(404)
    place.delete()
    storage.save()
    return make_response({}, 200)


@app_views.route('/cities/<city_id>/places', methods=['POST'])
def create_place(city_id):
    city = storage.get(City, city_id)
    if city is None:
        return abort(404)
    data = request.get_json()
    if data is None:
        abort(400, "Not a JSON")
    if 'user_id' not in data:
        abort(400, "Missing user_id")
    if storage.get(User, data['user_id']) is None:
        return abort(404)
    if 'name' not in data:
        abort(400, "Missing name")
    place = Place(city_id=city_id, **data)
    storage.new(place)
    storage.save()
    return make_response((place.to_dict()), 201)


@app_views.route('/places/<place_id>', methods=['PUT'])
def update_place(place_id):
    place = storage.get(Place, place_id)
    if place is None:
        abort(404)
    data = request.get_json()
    if data is None:
        abort(400, "Not a JSON")
    for key in data:
        if key in ['id', 'user_id', 'city_id', 'created_at', 'updated_at']:
            continue
        value = data[key]
        if hasattr(place, key):
            try:
                value = type(getattr(place, key))(value)
            except ValueError:
                pass
            setattr(place, key, value)
    storage.save()
    return make_response(place.to_dict(), 200)


@app_views.route('/places_search', methods=['POST'])
def search_place():
    data = request.get_json()
    if data is None:
        abort(400, "Not a JSON")
    if data == {} or list(data.values()) == [[], [], []]:
        print('here')
        places = storage.all(Place)
        return make_response(
            dumps(list(json_ser(places).values())), 200)
    else:
        states = []
        places = []
        if 'states' in data:
            for id in data['states']:
                states.append(storage.get(State, id))
            for st in states:
                if st:
                    for city in st.cities:
                        for place in city.places:
                            places.append(place)
        if 'cities' in data:
            cities = []
            for id in data['cities']:
                cities.append(storage.get(City, id))
            for city in cities:
                if city:
                    if city.state not in states:
                        for place in city.places:
                            places.append(place)
        if 'amenities' in data:
            amen = []
            for id in data['amenities']:
                amen.append(storage.get(Amenity, id))
            for am in amen:
                if am:
                    for plc in am.place_amenities:
                        if plc not in places:
                            places.append(plc)
    return make_response(
        dumps(places_json(places)), 200)
