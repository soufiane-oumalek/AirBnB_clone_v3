#!/usr/bin/python3
"""users al7bin"""
from flask import abort, make_response, request
from api.v1.views import app_views
from models import storage, storage_t
from models.user import User
from models.amenity import Amenity
from models.place import Place
from models.review import Review
from json import dumps


def json_ser(obj):
    json_obj = {}
    for key in obj:
        json_obj[key] = obj[key].to_dict()
    return (json_obj)


def rev_json(lst):
    json_list = []
    for id in lst:
        amen = storage.get(Amenity, id)
        json_list.append(amen.to_dict())
    return (json_list)


def ids_json(lst):
    json_list = []
    for place in lst:
        json_list.append(place.to_dict())
    return (json_list)


@app_views.route('places/<place_id>/amenities', methods=['GET'])
def get_amen(place_id):
    place = storage.get(Place, place_id)
    if place is None:
        return abort(404)
    if storage_t == 'db':
        return make_response(
            dumps(rev_json(place.amenities)), 200)
    else:
        return make_response(
            dumps(ids_json(place.amenity_ids)), 200)


@app_views.route('/places/<place_id>/amenities/<amenity_id>',
                 methods=['DELETE'])
def delete_amen(place_id, amenity_id):
    amenity = storage.get(Amenity, amenity_id)
    place = storage.get(Place, place_id)
    if amenity is None or place is None:
        abort(404)
    if storage_t == 'db':
        if amenity not in place.amenities:
            abort(404)
        place.amenities.remove(amenity)
    else:
        if amenity.id not in place.amenity_ids:
            abort(404)
        place.amenity_ids.remove(amenity_id)
    storage.save()
    return make_response({}, 200)


@app_views.route('/places/<place_id>/amenities/<amenity_id>',
                 methods=['POST'])
def create_amen(place_id, amenity_id):
    place = storage.get(Place, place_id)
    amenity = storage.get(Amenity, amenity_id)
    if place is None or amenity is None:
        return abort(404)
    if storage_t == 'db':
        if amenity in place.amenities:
            return make_response(amenity.to_dict(), 200)
        place.amenities.append(amenity)
    else:
        if amenity_id in place.amenity_ids:
            return make_response(amenity.to_dict(), 200)
        place.amenity_ids.append(amenity_id)
    storage.save()
    return make_response(amenity.to_dict(), 201)
