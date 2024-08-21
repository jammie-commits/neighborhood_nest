from flask import Flask, request, make_response
from flask_restful import Api, Resource
from flask_sqlalchemy import SQLAlchemy
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime, timedelta
from models import db, Resident, Neighborhood, News, Event, Contact, Admin
from flask_migrate import Migrate
from flask_cors import CORS
import cloudinary.uploader
import cloudinary
from functools import wraps

# Initialize the app and extensions
app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}})
api = Api(app)

# Configure app
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///neighborhood.db'
app.config['JWT_SECRET_KEY'] = '#24@67$^453'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['JWT_ACCESS_TOKEN_EXPIRES'] = timedelta(minutes=1440)

db.init_app(app)
jwt = JWTManager(app)
migrate = Migrate(app, db)

cloudinary.config(
    cloud_name='dypwsrolf',
    api_key='339349293184484',
    api_secret='zcplKelqPs1MV4wfptQaPXAYgq4'
)

# Home route
@app.route('/')
def home():
    response = make_response({"message": "Welcome to the Neighborhood API"})
    response.mimetype = 'application/json'
    return response

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
        'contacts': ['GET'],
    },
    'SuperAdmin': {
        'neighborhoods': ['GET', 'POST', 'PUT', 'DELETE'],
        'admins': ['GET', 'POST', 'PUT', 'DELETE'],
        'contacts': ['GET'],
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
                response = make_response({"error": "Unauthorized: Insufficient role"})
                response.status_code = 403
                response.mimetype = 'application/json'
                return response
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
            response = make_response({"error": "Email and password required"})
            response.status_code = 400
            response.mimetype = 'application/json'
            return response

        user = Resident.query.filter_by(email=email).first() or Admin.query.filter_by(email=email).first()

        if not user or not check_password_hash(user.password, password):
            response = make_response({"error": "Invalid credentials"})
            response.status_code = 401
            response.mimetype = 'application/json'
            return response

        access_token = create_access_token(identity={
            'id': user.id,
            'role': user.role
        })
        response = make_response({"access_token": access_token, "role": user.role, "id": user.id})
        response.mimetype = 'application/json'
        return response

class NeighborhoodResource(Resource):
    @role_required(['SuperAdmin'])
    def get(self, neighborhood_id=None):
        if neighborhood_id:
            neighborhood = Neighborhood.query.get_or_404(neighborhood_id)
            response = make_response(neighborhood.to_dict())
        else:
            neighborhoods = Neighborhood.query.all()
            response = make_response([neighborhood.to_dict() for neighborhood in neighborhoods])
        response.mimetype = 'application/json'
        return response

    @role_required(['SuperAdmin'])
    def post(self):
        data = request.json
        new_neighborhood = Neighborhood(
            name=data['name'],
            description=data.get('description', ''),
            date_created=datetime.utcnow()
        )
        db.session.add(new_neighborhood)
        db.session.commit()
        response = make_response(new_neighborhood.to_dict())
        response.status_code = 201
        response.mimetype = 'application/json'
        return response

    @role_required(['SuperAdmin'])
    def put(self, neighborhood_id):
        neighborhood = Neighborhood.query.get_or_404(neighborhood_id)
        data = request.json
        neighborhood.name = data.get('name', neighborhood.name)
        neighborhood.description = data.get('description', neighborhood.description)
        db.session.commit()
        response = make_response(neighborhood.to_dict())
        response.mimetype = 'application/json'
        return response

    @role_required(['SuperAdmin'])
    def delete(self, neighborhood_id):
        neighborhood = Neighborhood.query.get_or_404(neighborhood_id)
        db.session.delete(neighborhood)
        db.session.commit()
        response = make_response({"message": "Neighborhood deleted"})
        response.mimetype = 'application/json'
        return response

class ResidentResource(Resource):
    @role_required(['Admin', 'SuperAdmin'])
    def get(self, neighborhood_id):
        residents = Resident.query.filter_by(neighborhood_id=neighborhood_id).all()
        response = make_response([resident.to_dict() for resident in residents])
        response.mimetype = 'application/json'
        return response

    @role_required(['Admin'])
    def post(self, neighborhood_id):
        data = request.json
        new_resident = Resident(
            name=data['name'],
            email=data['email'],
            password=generate_password_hash(data['password']),
            neighborhood_id=neighborhood_id,
            role='Resident',
            date_joined=datetime.utcnow()
        )
        db.session.add(new_resident)
        db.session.commit()
        response = make_response(new_resident.to_dict())
        response.status_code = 201
        response.mimetype = 'application/json'
        return response

    @role_required(['Admin'])
    def put(self, resident_id):
        resident = Resident.query.get_or_404(resident_id)
        data = request.json
        resident.name = data.get('name', resident.name)
        resident.email = data.get('email', resident.email)
        if 'password' in data:
            resident.password = generate_password_hash(data['password'])
        db.session.commit()
        response = make_response(resident.to_dict())
        response.mimetype = 'application/json'
        return response

    @role_required(['Admin'])
    def delete(self, resident_id):
        resident = Resident.query.get_or_404(resident_id)
        db.session.delete(resident)
        db.session.commit()
        response = make_response({"message": "Resident deleted"})
        response.mimetype = 'application/json'
        return response

class NewsResource(Resource):
    @role_required(['Admin', 'SuperAdmin'])
    def get(self, neighborhood_id=None, news_id=None):
        if news_id:
            news_item = News.query.get_or_404(news_id)
            response = make_response(news_item.to_dict())
        elif neighborhood_id:
            news_items = News.query.filter_by(neighborhood_id=neighborhood_id).all()
            response = make_response([news_item.to_dict() for news_item in news_items])
        else:
            response = make_response({"error": "Neighborhood ID required"})
            response.status_code = 400
        response.mimetype = 'application/json'
        return response

    @role_required(['Admin'])
    def post(self, neighborhood_id):
        data = request.json
        image = request.files.get('image')
        image_url = None
        if image:
            upload_result = cloudinary.uploader.upload(image)
            image_url = upload_result['url']
        new_news = News(
            title=data['title'],
            description=data['description'],
            neighborhood_id=neighborhood_id,
            resident_id=get_jwt_identity()['id'],
            date_created=datetime.utcnow(),
            image_url=image_url
        )
        db.session.add(new_news)
        db.session.commit()
        response = make_response(new_news.to_dict())
        response.status_code = 201
        response.mimetype = 'application/json'
        return response

    @role_required(['Admin'])
    def put(self, news_id):
        news_item = News.query.get_or_404(news_id)
        data = request.json
        image = request.files.get('image')
        if image:
            upload_result = cloudinary.uploader.upload(image)
            news_item.image_url = upload_result['url']
        news_item.title = data.get('title', news_item.title)
        news_item.description = data.get('description', news_item.description)
        db.session.commit()
        response = make_response(news_item.to_dict())
        response.mimetype = 'application/json'
        return response

    @role_required(['Admin'])
    def delete(self, news_id):
        news_item = News.query.get_or_404(news_id)
        db.session.delete(news_item)
        db.session.commit()
        response = make_response({"message": "News deleted"})
        response.mimetype = 'application/json'
        return response

class EventResource(Resource):
    @role_required(['Admin', 'SuperAdmin'])
    def get(self, neighborhood_id=None, event_id=None):
        if event_id:
            event = Event.query.get_or_404(event_id)
            response = make_response(event.to_dict())
        elif neighborhood_id:
            events = Event.query.filter_by(neighborhood_id=neighborhood_id).all()
            response = make_response([event.to_dict() for event in events])
        else:
            response = make_response({"error": "Neighborhood ID required"})
            response.status_code = 400
        response.mimetype = 'application/json'
        return response

    @role_required(['Admin'])
    def post(self, neighborhood_id):
        data = request.json
        image = request.files.get('image')
        image_url = None
        if image:
            upload_result = cloudinary.uploader.upload(image)
            image_url = upload_result['url']
        new_event = Event(
            title=data['title'],
            description=data['description'],
            neighborhood_id=neighborhood_id,
            resident_id=get_jwt_identity()['id'],
            date_created=datetime.utcnow(),
            image_url=image_url
        )
        db.session.add(new_event)
        db.session.commit()
        response = make_response(new_event.to_dict())
        response.status_code = 201
        response.mimetype = 'application/json'
        return response

    @role_required(['Admin'])
    def put(self, event_id):
        event = Event.query.get_or_404(event_id)
        data = request.json
        image = request.files.get('image')
        if image:
            upload_result = cloudinary.uploader.upload(image)
            event.image_url = upload_result['url']
        event.title = data.get('title', event.title)
        event.description = data.get('description', event.description)
        db.session.commit()
        response = make_response(event.to_dict())
        response.mimetype = 'application/json'
        return response

    @role_required(['Admin'])
    def delete(self, event_id):
        event = Event.query.get_or_404(event_id)
        db.session.delete(event)
        db.session.commit()
        response = make_response({"message": "Event deleted"})
        response.mimetype = 'application/json'
        return response

class ContactResource(Resource):
    @role_required(['Admin', 'SuperAdmin'])
    def get(self):
        contacts = Contact.query.all()
        response = make_response([contact.to_dict() for contact in contacts])
        response.mimetype = 'application/json'
        return response

class AdminResource(Resource):
    @role_required(['SuperAdmin'])
    def get(self):
        admins = Admin.query.all()
        response = make_response([admin.to_dict() for admin in admins])
        response.mimetype = 'application/json'
        return response

    @role_required(['SuperAdmin'])
    def post(self):
        data = request.json
        new_admin = Admin(
            name=data['name'],
            email=data['email'],
            password=generate_password_hash(data['password']),
            role='Admin'
        )
        db.session.add(new_admin)
        db.session.commit()
        response = make_response(new_admin.to_dict())
        response.status_code = 201
        response.mimetype = 'application/json'
        return response

    @role_required(['SuperAdmin'])
    def put(self, admin_id):
        admin = Admin.query.get_or_404(admin_id)
        data = request.json
        admin.name = data.get('name', admin.name)
        admin.email = data.get('email', admin.email)
        if 'password' in data:
            admin.password = generate_password_hash(data['password'])
        db.session.commit()
        response = make_response(admin.to_dict())
        response.mimetype = 'application/json'
        return response

    @role_required(['SuperAdmin'])
    def delete(self, admin_id):
        admin = Admin.query.get_or_404(admin_id)
        db.session.delete(admin)
        db.session.commit()
        response = make_response({"message": "Admin deleted"})
        response.mimetype = 'application/json'
        return response

# Add resources to the API
api.add_resource(NeighborhoodResource, '/neighborhoods', '/neighborhoods/<int:neighborhood_id>')
api.add_resource(ResidentResource, '/neighborhoods/<int:neighborhood_id>/residents', '/residents/<int:resident_id>')
api.add_resource(NewsResource, '/neighborhoods/<int:neighborhood_id>/news', '/news/<int:news_id>')
api.add_resource(EventResource, '/neighborhoods/<int:neighborhood_id>/events', '/events/<int:event_id>')
api.add_resource(ContactResource, '/contacts')
api.add_resource(AdminResource, '/admins', '/admins/<int:admin_id>')
api.add_resource(LoginResource, '/login')

# Run the app
if __name__ == '__main__':
    app.run(debug=True)
