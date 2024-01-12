#!/usr/bin/python3
""" Starts a Flash Web Application """
from models import storage
from models.state import State
from models.amenity import Amenity
from models.place import Place
from flask import Flask, render_template
import uuid


app = Flask(__name__)


@app.route('/0-hbnb', strict_slashes=False)
def hbnb():
    """ Display a list of states, cities, places and amenities! """
    states = storage.all(State).values()
    amenities = storage.all(Amenity).values()
    places = storage.all(Place).values()
    cache_id = uuid.uuid4()

    return render_template('0-hbnb.html',
                           states=states,
                           amenities=amenities,
                           places=places,
                           cache_id=cache_id)


@app.teardown_appcontext
def close_db(error):
    """ Remove the current SQLAlchemy Session """
    storage.close()


if __name__ == "__main__":
    """ Main Function """
    app.run(host='0.0.0.0', port=5000)
