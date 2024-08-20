from flask import Flask, request, jsonify
from flask_restful import Api, Resource
from flask_sqlalchemy import SQLAlchemy
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
from models import db, Resident, Neighborhood, News, Event, Activity, Contact
from flask_migrate import Migrate
from flask_cors import CORS
import cloudinary.uploader
import cloudinary
from functools import wraps
from datetime import timedelta
# from flask_mail import Mail, Message


# Initialize the app and extensions
app = Flask(__name__)
api = Api(app)
# mail = Mail(app)


# Configure app
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///neighborhood.db'
app.config['JWT_SECRET_KEY'] = '#24@67$^453' 
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['JWT_ACCESS_TOKEN_EXPIRES'] = timedelta(minutes=1440)


db.init_app(app)
jwt = JWTManager(app)
migrate = Migrate(app, db)


CORS(app)  # Allow requests from all origins


cloudinary.config(
   cloud_name='dypwsrolf',
   api_key='339349293184484',
   api_secret='zcplKelqPs1MV4wfptQaPXAYgq4'
)


# Home route
@app.route('/')


def home():
   return jsonify({"message": "Welcome to the Neighborhood API"})


# ------------------- Role-Based Permissions -------------------


PERMISSIONS = {
   'Resident': {
       'news': ['GET', 'POST', 'PUT', 'DELETE'],
       'events': ['GET', 'POST', 'PUT', 'DELETE'],
       'residents': ['GET'],
   },
   'Admin': {
       'residents': ['GET', 'POST', 'PUT', 'DELETE'],
       'news': ['GET', 'POST', 'PUT', 'DELETE'],
       'events': ['GET', 'POST', 'PUT', 'DELETE'],
   },
   'SuperAdmin': {
       'neighborhoods': ['GET', 'POST', 'PUT', 'DELETE'],
       'admins': ['GET', 'POST', 'PUT', 'DELETE'],
       'Contacts': ['GET'],
   },
}


def role_required(required_roles):
   def decorator(fn):
       @wraps(fn)
       @jwt_required()
       def wrapper(*args, **kwargs):
           user_identity = get_jwt_identity()
           user_role = user_identity.get('role')
           if user_role not in required_roles:
               return {"error": "Unauthorized: Insufficient role"}, 403
           return fn(*args, **kwargs)
       return wrapper
   return decorator


# ------------------- Resource Classes -------------------


class LoginResource(Resource):
    def post(self):
       data = request.json
       email = data.get('email')
       password = data.get('password')


       if not email or not password:
           return {"error": "Email and password required"}, 400


       user = Resident.query.filter_by(email=email).first()


       if not user or not user.check_password(password):
           return {"error": "Invalid credentials"}, 401


       access_token = create_access_token(identity={
           'id': user.id,
           'role': user.role
       })
       return jsonify(access_token=access_token, role=user.role, id=user.id) # Updated: Include user ID in response


class ResidentNewsResource(Resource):
    @role_required(['Resident'])
    def get(self, resident_id):
        resident = Resident.query.get_or_404(resident_id)
        news = News.query.filter_by(neighborhood_id=resident.neighborhood_id).all()
        return jsonify([news_item.to_dict() for news_item in news])

    @role_required(['Resident'])
    def post(self, resident_id):
        resident = Resident.query.get_or_404(resident_id)
        data = request.json
        image = request.files.get('image')

        image_url = None
        if image:
            upload_result = cloudinary.uploader.upload(image)
            image_url = upload_result['url']

        new_news = News(
            title=data['title'],
            description=data['description'],
            neighborhood_id=resident.neighborhood_id,
            date_created=datetime.utcnow(),
            image_url=image_url
        )
        db.session.add(new_news)
        db.session.commit()
        return jsonify(new_news.to_dict()), 201

    @role_required(['Resident'])
    def put(self, resident_id, news_id):
        resident = Resident.query.get_or_404(resident_id)
        news = News.query.get_or_404(news_id)
        if news.neighborhood_id != resident.neighborhood_id:
            return {"error": "Unauthorized"}, 403

        data = request.json
        image = request.files.get('image')
        if image:
            upload_result = cloudinary.uploader.upload(image)
            news.image_url = upload_result['url']

        news.title = data.get('title', news.title)
        news.description = data.get('description', news.description)
        db.session.commit()
        return jsonify(news.to_dict())

    @role_required(['Resident'])
    def delete(self, resident_id, news_id):
        resident = Resident.query.get_or_404(resident_id)
        news = News.query.get_or_404(news_id)
        if news.neighborhood_id != resident.neighborhood_id:
            return {"error": "Unauthorized"}, 403
        db.session.delete(news)
        db.session.commit()
        return {"message": "News deleted"}
class ResidentEventResource(Resource):
    @role_required(['Resident'])
    def get(self, resident_id):
        resident = Resident.query.get_or_404(resident_id)
        events = Event.query.filter_by(neighborhood_id=resident.neighborhood_id).all()
        return jsonify([event.to_dict() for event in events])

    @role_required(['Resident'])
    def post(self, resident_id):
        resident = Resident.query.get_or_404(resident_id)
        data = request.json
        image = request.files.get('image')

        image_url = None
        if image:
            upload_result = cloudinary.uploader.upload(image)
            image_url = upload_result['url']

        new_event = Event(
            title=data['title'],
            description=data['description'],
            neighborhood_id=resident.neighborhood_id,
            date_created=datetime.utcnow(),
            image_url=image_url
        )
        db.session.add(new_event)
        db.session.commit()
        return jsonify(new_event.to_dict()), 201

    @role_required(['Resident'])
    def put(self, resident_id, event_id):
        resident = Resident.query.get_or_404(resident_id)
        event = Event.query.get_or_404(event_id)
        if event.neighborhood_id != resident.neighborhood_id:
            return {"error": "Unauthorized"}, 403

        data = request.json
        image = request.files.get('image')
        if image:
            upload_result = cloudinary.uploader.upload(image)
            event.image_url = upload_result['url']

        event.title = data.get('title', event.title)
        event.description = data.get('description', event.description)
        db.session.commit()
        return jsonify(event.to_dict())

    @role_required(['Resident'])
    def delete(self, resident_id, event_id):
        resident = Resident.query.get_or_404(resident_id)
        event = Event.query.get_or_404(event_id)
        if event.neighborhood_id != resident.neighborhood_id:
            return {"error": "Unauthorized"}, 403
        db.session.delete(event)
        db.session.commit()
        return {"message": "Event deleted"}
    
class ResidentNeighborsResource(Resource):
    @role_required(['Resident'])
    def get(self, resident_id):
       resident = Resident.query.get_or_404(resident_id)
       neighbors = Resident.query.filter_by(neighborhood_id=resident.neighborhood_id).all()
       return jsonify([neighbor.to_dict() for neighbor in neighbors])



class AdminResidentsResource(Resource):
   @role_required(['Admin'])
   def get(self, admin_id):
       admin = Resident.query.get_or_404(admin_id)  # Assuming Admin is a Resident for simplicity
       residents = Resident.query.filter_by(neighborhood_id=admin.neighborhood_id).all()
       return jsonify([resident.to_dict() for resident in residents])


   @role_required(['Admin'])
   def post(self, admin_id):
       admin = Resident.query.get_or_404(admin_id)  # Assuming Admin is a Resident for simplicity


       data = request.get_json()
       required_fields = ['name', 'email', 'house_number', 'password']
       for field in required_fields:
           if field not in data:
               return jsonify({'message': f'Missing required field: {field}'}), 400


       profile_image = request.files.get('profile_image')
       profile_image_url = None
       if profile_image:
           upload_result = cloudinary.uploader.upload(profile_image)
           profile_image_url = upload_result.get('url')


       new_resident = Resident(
           name=data['name'],
           email=data['email'],
           house_number=data['house_number'],
           neighborhood_id=admin.neighborhood_id,
           profile_image_url=profile_image_url
       )
       new_resident.set_password(data['password'])
       db.session.add(new_resident)
       db.session.commit()
       return jsonify(new_resident.to_dict()), 201


class AdminResidentResource(Resource):
   @role_required(['Admin'])
   def delete(self, admin_id, resident_id):
       admin = Resident.query.get_or_404(admin_id)  # Assuming Admin is a Resident for simplicity
       resident = Resident.query.get_or_404(resident_id)
       if resident.neighborhood_id != admin.neighborhood_id:
           return {"error": "Unauthorized"}, 403
       db.session.delete(resident)
       db.session.commit()
       return {"message": "Resident deleted"}


class AdminNewsResource(Resource):
   @role_required(['Admin'])
   def post(self, admin_id):
       admin = Resident.query.get_or_404(admin_id)  # Assuming Admin is a Resident for simplicity
       data = request.json
       image = request.files.get('image')


       image_url = None
       if image:
           upload_result = cloudinary.uploader.upload(image)
           image_url = upload_result['url']


       new_news = News(
           title=data['title'],
           description=data['description'],
           neighborhood_id=admin.neighborhood_id,
           date_created=datetime.utcnow(),
           image_url=image_url
       )
       db.session.add(new_news)
       db.session.commit()
       return jsonify(new_news.to_dict()), 201
   
   @role_required(['Admin'])
   def PUT(self, admin_id, news_id):
       admin = Resident.query.get_or_404(admin_id)  # Assuming Admin is a Resident for simplicity
       news = News.query.get_or_404(news_id)
       if news.neighborhood_id != admin.neighborhood_id:
           return {"error": "Unauthorized"}, 403
       data = request.json
       image = request.files.get('image')
       if image:
           upload_result = cloudinary.uploader.upload(image)
           news.image_url = upload_result['url']
       news.title = data.get('title', news.title)
       news.description = data.get('description', news.description)
       db.session.commit()
       return jsonify(news.to_dict()) 


   @role_required(['Admin'])
   def delete(self, admin_id, news_id):
       admin = Resident.query.get_or_404(admin_id)  # Assuming Admin is a Resident for simplicity
       news = News.query.get_or_404(news_id)
       if news.neighborhood_id != admin.neighborhood_id:
           return {"error": "Unauthorized"}, 403
       db.session.delete(news)
       db.session.commit()
       return {"message": "News deleted"}
   
class AdminEventResource(Resource):
    @role_required(['Admin'])
    def get(self, admin_id):
       admin = Resident.query.get_or_404(admin_id)
       events = Event.query.filter_by(neighborhood_id=admin.neighborhood_id).all()
       return jsonify([event.to_dict() for event in events])


    @role_required(['Admin'])
    def post(self, admin_id):
       admin = Resident.query.get_or_404(admin_id)
       data = request.json
       image = request.files.get('image')


       image_url = None
       if image:
           upload_result = cloudinary.uploader.upload(image)
           image_url = upload_result['url']


       new_event = Event(
           title=data['title'],
           description=data['description'],
           neighborhood_id=admin.neighborhood_id,
           date_created=datetime.utcnow(),
           image_url=image_url
       )
       db.session.add(new_event)
       db.session.commit()
       return jsonify(new_event.to_dict()), 201


    @role_required(['Admin'])
    def put(self, admin_id, event_id):
       admin = Resident.query.get_or_404(admin_id)
       event = Event.query.get_or_404(event_id)
       if event.neighborhood_id != admin.neighborhood_id:
           return {"error": "Unauthorized"}, 403


       data = request.json
       image = request.files.get('image')
       if image:
           upload_result = cloudinary.uploader.upload(image)
           event.image_url = upload_result['url']


       event.title = data.get('title', event.title)
       event.description = data.get('description', event.description)
       db.session.commit()
       return jsonify(event.to_dict())


    @role_required(['Admin'])
    def delete(self, admin_id, event_id):
       admin = Resident.query.get_or_404(admin_id)
       event = Event.query.get_or_404(event_id)
       if event.neighborhood_id != admin.neighborhood_id:
           return {"error": "Unauthorized"}, 403
       db.session.delete(event)
       db.session.commit()
       return {"message": "Event deleted"}


class AdminResidentsResource(Resource):
   @role_required(['Admin'])
   def get(self, admin_id):
       admin = Resident.query.get_or_404(admin_id)
       residents = Resident.query.filter_by(neighborhood_id=admin.neighborhood_id).all()
       return jsonify([resident.to_dict() for resident in residents])


   @role_required(['Admin'])
   def post(self, admin_id):
       admin = Resident.query.get_or_404(admin_id)
       data = request.get_json()
       required_fields = ['name', 'email', 'house_number', 'password']
       for field in required_fields:
           if field not in data:
               return jsonify({'message': f'Missing required field: {field}'}), 400


       profile_image = request.files.get('profile_image')
       profile_image_url = None
       if profile_image:
           upload_result = cloudinary.uploader.upload(profile_image)
           profile_image_url = upload_result.get('url')


       new_resident = Resident(
           name=data['name'],
           email=data['email'],
           house_number=data['house_number'],
           neighborhood_id=admin.neighborhood_id,
           profile_image_url=profile_image_url
       )
       new_resident.set_password(data['password'])
       db.session.add(new_resident)
       db.session.commit()
       return jsonify(new_resident.to_dict()), 201


   @role_required(['Admin'])
   def put(self, admin_id, resident_id):
       admin = Resident.query.get_or_404(admin_id)
       resident = Resident.query.get_or_404(resident_id)
       if resident.neighborhood_id != admin.neighborhood_id:
           return {"error": "Unauthorized"}, 403


       data = request.json
       resident.name = data.get('name', resident.name)
       resident.email = data.get('email', resident.email)
       resident.house_number = data.get('house_number', resident.house_number)
       if 'password' in data:
           resident.set_password(data['password'])
       profile_image = request.files.get('profile_image')
       if profile_image:
           upload_result = cloudinary.uploader.upload(profile_image)
           resident.profile_image_url = upload_result.get('url')


       db.session.commit()
       return jsonify(resident.to_dict())


@role_required(['Admin'])
def delete(self, admin_id, resident_id):
    admin = Resident.query.get_or_404(admin_id)
    resident = Resident.query.get_or_404(resident_id)
    if resident.neighborhood_id != admin.neighborhood_id:
           return {"error": "Unauthorized"}, 403
    db.session.delete(resident)
    db.session.commit()
    return {"message": "Resident deleted"}


class SuperAdminNeighborhoodsResource(Resource):
    @role_required(['SuperAdmin'])
    def get(self, superadmin_id):
        neighborhoods = Neighborhood.query.all()
        return jsonify([neighborhood.to_dict() for neighborhood in neighborhoods])

    @role_required(['SuperAdmin'])
    def post(self, superadmin_id):
        data = request.json
        required_fields = ['name', 'location']
        for field in required_fields:
            if field not in data:
                return jsonify({'message': f'Missing required field: {field}'}), 400

        new_neighborhood = Neighborhood(
            name=data['name'],
            location=data['location']
        )
        db.session.add(new_neighborhood)
        db.session.commit()
        return jsonify(new_neighborhood.to_dict()), 201

    @role_required(['SuperAdmin'])
    def put(self, superadmin_id, neighborhood_id):
        neighborhood = Neighborhood.query.get_or_404(neighborhood_id)
        data = request.json
        neighborhood.name = data.get('name', neighborhood.name)
        neighborhood.location = data.get('location', neighborhood.location)
        db.session.commit()
        return jsonify(neighborhood.to_dict())

    @role_required(['SuperAdmin'])
    def delete(self, superadmin_id, neighborhood_id):
        neighborhood = Neighborhood.query.get_or_404(neighborhood_id)
        db.session.delete(neighborhood)
        db.session.commit()
        return {"message": "Neighborhood deleted"}

class SuperAdminAdminsResource(Resource):
    @role_required(['SuperAdmin'])
    def get(self, superadmin_id):
        admins = Resident.query.filter_by(role='Admin').all()
        return jsonify([admin.to_dict() for admin in admins])

    @role_required(['SuperAdmin'])
    def post(self, superadmin_id):
        data = request.json
        required_fields = ['name', 'email', 'password', 'neighborhood_id']
        for field in required_fields:
            if field not in data:
                return jsonify({'message': f'Missing required field: {field}'}), 400

        # Check if the neighborhood exists
        neighborhood = Neighborhood.query.get(data['neighborhood_id'])
        if not neighborhood:
            return jsonify({'message': 'Invalid neighborhood ID'}), 400

        new_admin = Resident(
            name=data['name'],
            email=data['email'],
            role='Admin',
            neighborhood_id=data['neighborhood_id']
        )
        new_admin.set_password(data['password'])
        db.session.add(new_admin)
        db.session.commit()
        return jsonify(new_admin.to_dict()), 201

    @role_required(['SuperAdmin'])
    def put(self, superadmin_id, admin_id):
        admin = Resident.query.filter_by(id=admin_id, role='Admin').first_or_404()
        data = request.json

        # If neighborhood_id is provided, reassign the admin to a new neighborhood
        if 'neighborhood_id' in data:
            neighborhood = Neighborhood.query.get(data['neighborhood_id'])
            if not neighborhood:
                return jsonify({'message': 'Invalid neighborhood ID'}), 400
            admin.neighborhood_id = data['neighborhood_id']

        admin.name = data.get('name', admin.name)
        admin.email = data.get('email', admin.email)
        if 'password' in data:
            admin.set_password(data['password'])

        db.session.commit()
        return jsonify(admin.to_dict())

    @role_required(['SuperAdmin'])
    def delete(self, superadmin_id, admin_id):
        admin = Resident.query.filter_by(id=admin_id, role='Admin').first_or_404()
        db.session.delete(admin)
        db.session.commit()
        return {"message": "Admin deleted"}

class SuperAdminContactMessagesResource(Resource):
   @role_required(['SuperAdmin'])
   def get(self, super_admin_id):
       super_admin = Resident.query.get_or_404(super_admin_id)
       messages = Contact.query.all()
       return jsonify([message.to_dict() for message in messages])








# Add resources to the API
api.add_resource(LoginResource, '/login')
api.add_resource(ResidentNewsResource, '/residents/<int:resident_id>/news')
api.add_resource(ResidentNeighborsResource, '/residents/<int:resident_id>/neighbors')
api.add_resource(ResidentEventResource, '/residents/<int:resident_id>/events')
api.add_resource(AdminNewsResource, '/admins/<int:admin_id>/news')
api.add_resource(AdminEventResource, '/admins/<int:admin_id>/events')
api.add_resource(AdminResidentsResource, '/admins/<int:admin_id>/residents')
api.add_resource(SuperAdminNeighborhoodsResource, '/superadmins/<int:superadmin_id>/neighborhoods', '/superadmins/<int:superadmin_id>/neighborhoods/<int:neighborhood_id>')
api.add_resource(SuperAdminAdminsResource, '/superadmins/<int:superadmin_id>/admins', '/superadmins/<int:superadmin_id>/admins/<int:admin_id>')
api.add_resource(SuperAdminContactMessagesResource, '/superadmins/<int:super_admin_id>/messages')  # Updated Route

if __name__ == '__main__':
   app.run(debug=True)





