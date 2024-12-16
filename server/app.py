#!/usr/bin/env python3
from models import db, Restaurant, RestaurantPizza, Pizza
from flask_migrate import Migrate
from flask import Flask, request, make_response
from flask_restful import Api, Resource
import os

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
DATABASE = os.environ.get("DB_URI", f"sqlite:///{os.path.join(BASE_DIR, 'app.db')}")

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = DATABASE
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.json.compact = False

migrate = Migrate(app, db)

db.init_app(app)

api = Api(app)

class Restaurants(Resource):
    def get(self):
        restaurants = db.session.execute(db.select(Restaurant)).scalars()
        list_restaurants = [r.to_dict(rules=('-restaurant_pizzas',)) for r in restaurants]
        return make_response(list_restaurants, 200)
    
class RestaurantById(Resource):
    def get(self, id):
        try:
            restaurant = db.session.execute(db.select(Restaurant).filter_by(id=id)).scalar_one()
            return make_response(restaurant.to_dict(), 200)
        except:
            error = {'error': 'Restaurant not found'}
            return make_response(error, 404)
        
    def delete(self, id):
        try:
            restaurant = db.session.execute(db.select(Restaurant).filter_by(id=id)).scalar_one()
            db.session.delete(restaurant)
            db.session.commit()
            return make_response('', 204)
        except:
            error = {'error': 'Restaurant not found'}
            return make_response(error, 404)
        
class Pizzas(Resource):
    def get(self):
        pizzas = db.session.execute(db.select(Pizza)).scalars()
        list_pizzas = [pizza.to_dict(rules=('-restaurant_pizzas',)) for pizza in pizzas]
        return make_response(list_pizzas, 200)
    
class RestaurantPizzas(Resource):
    def post(self):
        try:
            data = request.json
            new_restaurant_pizza = RestaurantPizza(price=data['price'], restaurant_id=data['restaurant_id'], pizza_id=data['pizza_id'])
            db.session.add(new_restaurant_pizza)
            db.session.commit()
            return make_response(new_restaurant_pizza.to_dict(), 201)
        except:
            error = {'errors': ['validation errors']}
            return make_response(error, 400)

api.add_resource(Restaurants, '/restaurants')
api.add_resource(RestaurantById, '/restaurants/<int:id>')
api.add_resource(Pizzas, '/pizzas')
api.add_resource(RestaurantPizzas, '/restaurant_pizzas')

if __name__ == "__main__":
    app.run(port=5555, debug=True)
