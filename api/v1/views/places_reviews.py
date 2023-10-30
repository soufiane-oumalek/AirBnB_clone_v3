#!/usr/bin/python3
"""users al7bin"""
from flask import abort, make_response, request
from api.v1.views import app_views
from models import storage
from models.user import User
from models.place import Place
from models.review import Review
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


@app_views.route('places/<place_id>/reviews', methods=['GET'])
def get_reviews(place_id):
    place = storage.get(Place, place_id)
    if place is None:
        return abort(404)
    return make_response(
        dumps(places_json(place.reviews)), 200)


@app_views.route('/reviews/<review_id>', methods=['GET'])
def get_review(review_id):
    review = storage.get(Review, review_id)
    if review is None:
        return abort(404)
    return (review.to_dict())


@app_views.route('/reviews/<review_id>', methods=['DELETE'])
def delete_review(review_id):
    review = storage.get(Review, review_id)
    if review is None:
        abort(404)
    review.delete()
    storage.save()
    return make_response({}, 200)


@app_views.route('/places/<place_id>/reviews', methods=['POST'])
def create_review(place_id):
    place = storage.get(Place, place_id)
    if place is None:
        return abort(404)
    data = request.get_json()
    if data is None:
        abort(400, "Not a JSON")
    if 'user_id' not in data:
        abort(400, "Missing user_id")
    if storage.get(User, data['user_id']) is None:
        return abort(404)
    if 'text' not in data:
        abort(400, "Missing text")
    review = Review(place_id=place_id, **data)
    storage.new(review)
    storage.save()
    return make_response((review.to_dict()), 201)


@app_views.route('/reviews/<review_id>', methods=['PUT'])
def update_review(review_id):
    review = storage.get(Review, review_id)
    if review is None:
        abort(404)
    data = request.get_json()
    if data is None:
        abort(400, "Not a JSON")
    for key in data:
        if key in ['id', 'user_id', 'place_id', 'created_at', 'updated_at']:
            continue
        value = data[key]
        if hasattr(review, key):
            try:
                value = type(getattr(review, key))(value)
            except ValueError:
                pass
            setattr(review, key, value)
    storage.save()
    return make_response(review.to_dict(), 200)
