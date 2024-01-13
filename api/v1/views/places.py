#!/usr/bin/python3
""" objects that handle all default RestFul API actions for Places """
from models.state import State
from models.city import City
from models.place import Place
from models.user import User
from models.amenity import Amenity
from models import storage
from api.v1.views import app_views
from flask import abort, jsonify, make_response, request
from flasgger.utils import swag_from


@app_views.route('/cities/<city_id>/places', methods=['GET'],
                 strict_slashes=False)
@swag_from('documentation/place/get_places.yml', methods=['GET'])
def get_places(city_id):
    """
    Retrieves the list of all Place objects of a City
    """
    city = storage.get(City, city_id)

    if not city:
        abort(404)

    places = [place.to_dict() for place in city.places]

    return jsonify(places)


@app_views.route('/places/<place_id>', methods=['GET'], strict_slashes=False)
@swag_from('documentation/place/get_place.yml', methods=['GET'])
def get_place(place_id):
    """
    Retrieves a Place object
    """
    place = storage.get(Place, place_id)
    if not place:
        abort(404)

    return jsonify(place.to_dict())


@app_views.route('/places/<place_id>', methods=['DELETE'],
                 strict_slashes=False)
@swag_from('documentation/place/delete_place.yml', methods=['DELETE'])
def delete_place(place_id):
    """
    Deletes a Place Object
    """

    place = storage.get(Place, place_id)

    if not place:
        abort(404)

    storage.delete(place)
    storage.save()

    return make_response(jsonify({}), 200)


@app_views.route('/cities/<city_id>/places', methods=['POST'],
                 strict_slashes=False)
@swag_from('documentation/place/post_place.yml', methods=['POST'])
def post_place(city_id):
    """
    Creates a Place
    """
    city = storage.get(City, city_id)

    if not city:
        abort(404)

    if not request.get_json():
        abort(400, description="Not a JSON")

    if 'user_id' not in request.get_json():
        abort(400, description="Missing user_id")

    data = request.get_json()
    user = storage.get(User, data['user_id'])

    if not user:
        abort(404)

    if 'name' not in request.get_json():
        abort(400, description="Missing name")

    data["city_id"] = city_id
    instance = Place(**data)
    instance.save()
    return make_response(jsonify(instance.to_dict()), 201)


@app_views.route('/places/<place_id>', methods=['PUT'], strict_slashes=False)
@swag_from('documentation/place/put_place.yml', methods=['PUT'])
def put_place(place_id):
    """
    Updates a Place
    """
    place = storage.get(Place, place_id)

    if not place:
        abort(404)

    data = request.get_json()
    if not data:
        abort(400, description="Not a JSON")

    ignore = ['id', 'user_id', 'city_id', 'created_at', 'updated_at']

    for key, value in data.items():
        if key not in ignore:
            setattr(place, key, value)
    storage.save()
    return make_response(jsonify(place.to_dict()), 200)


@app_views.route('/places_search', methods=['POST'], strict_slashes=False)
@swag_from('documentation/place/post_search.yml', methods=['POST'])
def places_search():
    """retrieve places depending on JSON request"""

    try:
        request_dict = request.get_json()
    except Exception:
        return 'Not a JSON', 400

    if type(request_dict) is not dict:
        return 'Not a JSON', 400

    states = request_dict.get('states')
    cities = request_dict.get('cities')
    if not cities:
        cities = []
    amenities = request_dict.get('amenities')

    if not states and not cities:
        places = list(storage.all(Place).values())
    else:
        places = []

        if states:
            for state_id in states:
                state = storage.get(State, state_id)
                if not state:
                    abort(404)
                for city in state.cities:
                    for place in city.places:
                        places.append(place)

        if cities:
            for city_id in cities:
                city = storage.get(City, city_id)
                if not city:
                    abort(404)
                for place in city.places:
                    if place not in places:
                        places.append(place)

    amenity_ids = request_dict.get('amenities')

    if amenity_ids:

        # Filter places based on amenity_ids
        for place in list(places):
            if not place.amenities:
                places.remove(place)
            else:
                place_amenities_ids = [am.id for am in place.amenities]
                for am_id in amenity_ids:
                    if am_id not in place_amenities_ids:
                        places.remove(place)

    places_dicts = [place.to_dict() for place in places]

    for pd in places_dicts:
        if 'amenities' in pd.keys():
            place_amenities = [amn.to_dict() for amn in pd['amenities']]
            pd['amenities'] = place_amenities

    return jsonify(places_dicts)
