from flask import Flask, request, make_response
from flask_restful import Api, Resource
from flask_sqlalchemy import SQLAlchemy
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime, timedelta
from models import db, Resident, Neighborhood, News, Event, Notifications, Contact  # Ensure Notifications is imported
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
    return make_response({"message": "Welcome to the Neighborhood API"}, 200)

# ------------------- Role-Based Permissions -------------------
PERMISSIONS = {
    'Resident': {
        'news': ['GET', 'POST', 'PUT', 'DELETE'],
        'events': ['GET', 'POST', 'PUT', 'DELETE'],
        'residents': ['GET'],
        'notifications': ['GET', 'DELETE'],
        'contacts': ['POST'],
    },
    'Admin': {
        'residents': ['GET', 'POST', 'PUT', 'DELETE'],
        'news': ['GET', 'POST', 'PUT', 'DELETE'],
        'events': ['GET', 'POST', 'PUT', 'DELETE'],
        'contacts': ['POST'],
        'notifications': ['GET', 'DELETE'],
    },
    'SuperAdmin': {
        'neighborhoods': ['GET', 'POST', 'PUT', 'DELETE'],
        'admins': ['GET', 'POST', 'PUT', 'DELETE'],
        'contacts': ['GET', 'POST', 'PUT', 'DELETE'],
        'notifications': ['GET', 'DELETE'],
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
                return make_response({"error": "Unauthorized: Insufficient role"}, 403)
            return fn(*args, **kwargs)
        return wrapper
    return decorator

# ------------------- Resource Classes -------------------

# Login Resource
class LoginResource(Resource):
    def post(self):
        data = request.json
        email = data.get('email')
        password = data.get('password')

        if not email or not password:
            return make_response({"error": "Email and password required"}, 400)

        user = Resident.query.filter_by(email=email).first()
        if not user or not check_password_hash(user.password, password):
            return make_response({"error": "Invalid credentials"}, 401)

        access_token = create_access_token(identity={
            'id': user.id,
            'role': user.role
        })
        return make_response({
            'access_token': access_token,
            'role': user.role,
            'id': user.id
        }, 200)

# Neighborhood Resource
class NeighborhoodGetResource(Resource):
    @role_required(['SuperAdmin', 'Admin'])
    def get(self, neighborhood_id=None):
        if neighborhood_id:
            neighborhood = Neighborhood.query.get_or_404(neighborhood_id)
            return make_response(neighborhood.to_dict(), 200)
        neighborhoods = Neighborhood.query.all()
        return make_response([neighborhood.to_dict() for neighborhood in neighborhoods], 200)

class NeighborhoodPostResource(Resource):
    @role_required(['SuperAdmin'])
    def post(self):
        data = request.json
        new_neighborhood = Neighborhood(
            name=data['name'],
            location=data.get('location', 'N/A'),
            image_url=data.get('image_url', '')
        )
        db.session.add(new_neighborhood)
        db.session.commit()
        return make_response(new_neighborhood.to_dict(), 201)

class NeighborhoodPutResource(Resource):
    @role_required(['SuperAdmin'])
    def put(self, neighborhood_id):
        neighborhood = Neighborhood.query.get_or_404(neighborhood_id)
        data = request.json
        neighborhood.name = data.get('name', neighborhood.name)
        neighborhood.location = data.get('location', neighborhood.location)
        neighborhood.image_url = data.get('image_url', neighborhood.image_url)
        db.session.commit()
        return make_response(neighborhood.to_dict(), 200)

class NeighborhoodDeleteResource(Resource):
    @role_required(['SuperAdmin'])
    def delete(self, neighborhood_id):
        neighborhood = Neighborhood.query.get_or_404(neighborhood_id)
        db.session.delete(neighborhood)
        db.session.commit()
        return make_response({"message": "Neighborhood deleted"}, 200)

# Resident Resource
class ResidentGetResource(Resource):
    @role_required(['Admin', 'SuperAdmin'])
    def get(self, neighborhood_id):
        residents = Resident.query.filter_by(neighborhood_id=neighborhood_id).all()
        return make_response([resident.to_dict() for resident in residents], 200)

class ResidentPostResource(Resource):
    @role_required(['Admin'])
    def post(self, neighborhood_id):
        data = request.json
        new_resident = Resident(
            name=data['name'],
            email=data['email'],
            password=generate_password_hash(data['password']),
            role='Resident',
            neighborhood_id=neighborhood_id,
            house_number=data.get('house_number', '')
        )
        db.session.add(new_resident)
        db.session.commit()
        return make_response(new_resident.to_dict(), 201)

class ResidentPutResource(Resource):
    @role_required(['Admin'])
    def put(self, resident_id):
        resident = Resident.query.get_or_404(resident_id)
        data = request.json
        resident.name = data.get('name', resident.name)
        resident.email = data.get('email', resident.email)
        if 'password' in data:
            resident.password = generate_password_hash(data['password'])
        resident.house_number = data.get('house_number', resident.house_number)
        db.session.commit()
        return make_response(resident.to_dict(), 200)

class ResidentDeleteResource(Resource):
    @role_required(['Admin'])
    def delete(self, resident_id):
        resident = Resident.query.get_or_404(resident_id)
        db.session.delete(resident)
        db.session.commit()
        return make_response({"message": "Resident deleted"}, 200)

# News Resource
class NewsGetResource(Resource):
    @role_required(['Admin', 'SuperAdmin', 'Resident'])
    def get(self, neighborhood_id=None, news_id=None):
        user_id = get_jwt_identity()['id']
        if news_id:
            news_item = News.query.get_or_404(news_id)
            if get_jwt_identity()['role'] == 'Resident' and news_item.resident_id != user_id:
                return make_response({"error": "Unauthorized"}, 403)
            return make_response(news_item.to_dict(), 200)
        if neighborhood_id:
            news_items = News.query.filter_by(neighborhood_id=neighborhood_id).all()
            if get_jwt_identity()['role'] == 'Resident':
                news_items = [news for news in news_items if news.resident_id == user_id]
            return make_response([news_item.to_dict() for news_item in news_items], 200)
        return make_response({"error": "Neighborhood ID required"}, 400)

class NewsPostResource(Resource):
    @role_required(['Admin', 'Resident'])
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
        return make_response(new_news.to_dict(), 201)

class NewsPutResource(Resource):
    @role_required(['Admin', 'Resident'])
    def put(self, news_id):
        user_id = get_jwt_identity()['id']
        news_item = News.query.get_or_404(news_id)
        if get_jwt_identity()['role'] == 'Resident' and news_item.resident_id != user_id:
            return make_response({"error": "Unauthorized"}, 403)
        data = request.json
        image = request.files.get('image')
        if image:
            upload_result = cloudinary.uploader.upload(image)
            news_item.image_url = upload_result['url']
        news_item.title = data.get('title', news_item.title)
        news_item.description = data.get('description', news_item.description)
        db.session.commit()
        return make_response(news_item.to_dict(), 200)

class NewsDeleteResource(Resource):
    @role_required(['Admin', 'Resident'])
    def delete(self, news_id):
        user_id = get_jwt_identity()['id']
        news_item = News.query.get_or_404(news_id)
        if get_jwt_identity()['role'] == 'Resident' and news_item.resident_id != user_id:
            return make_response({"error": "Unauthorized"}, 403)
        neighborhood_id = news_item.neighborhood_id
        db.session.delete(news_item)
        db.session.commit()
        return make_response({"message": "News deleted"}, 200)

# Event Resource
class EventGetResource(Resource):
    @role_required(['Admin', 'SuperAdmin', 'Resident'])
    def get(self, neighborhood_id=None, event_id=None):
        user_id = get_jwt_identity()['id']
        if event_id:
            event = Event.query.get_or_404(event_id)
            if get_jwt_identity()['role'] == 'Resident' and event.resident_id != user_id:
                return make_response({"error": "Unauthorized"}, 403)
            return make_response(event.to_dict(), 200)
        if neighborhood_id:
            events = Event.query.filter_by(neighborhood_id=neighborhood_id).all()
            if get_jwt_identity()['role'] == 'Resident':
                events = [event for event in events if event.resident_id == user_id]
            return make_response([event.to_dict() for event in events], 200)
        return make_response({"error": "Neighborhood ID required"}, 400)

class EventPostResource(Resource):
    @role_required(['Admin', 'Resident'])
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
        return make_response(new_event.to_dict(), 201)

class EventPutResource(Resource):
    @role_required(['Admin', 'Resident'])
    def put(self, event_id):
        user_id = get_jwt_identity()['id']
        event = Event.query.get_or_404(event_id)
        if get_jwt_identity()['role'] == 'Resident' and event.resident_id != user_id:
            return make_response({"error": "Unauthorized"}, 403)
        data = request.json
        image = request.files.get('image')
        if image:
            upload_result = cloudinary.uploader.upload(image)
            event.image_url = upload_result['url']
        event.title = data.get('title', event.title)
        event.description = data.get('description', event.description)
        db.session.commit()
        return make_response(event.to_dict(), 200)

class EventDeleteResource(Resource):
    @role_required(['Admin', 'Resident'])
    def delete(self, event_id):
        user_id = get_jwt_identity()['id']
        event = Event.query.get_or_404(event_id)
        if get_jwt_identity()['role'] == 'Resident' and event.resident_id != user_id:
            return make_response({"error": "Unauthorized"}, 403)
        neighborhood_id = event.neighborhood_id
        db.session.delete(event)
        db.session.commit()
        return make_response({"message": "Event deleted"}, 200)

# Notification Resource
class NotificationGetResource(Resource):
    @role_required(['Resident', 'Admin'])
    def get(self):
        resident_id = get_jwt_identity()['id']
        notifications = Notifications.query.filter_by(resident_id=resident_id).all()
        return make_response([notification.to_dict() for notification in notifications], 200)

class NotificationDeleteResource(Resource):
    @role_required(['Resident', 'Admin', 'SuperAdmin'])  # Adjusted to allow all roles
    def delete(self, notification_id):
        notification = Notifications.query.get_or_404(notification_id)
        db.session.delete(notification)
        db.session.commit()
        return make_response({"message": "Notification deleted"}, 200)
    
# Contact Resource
class ContactGetResource(Resource):
    @jwt_required()
    @role_required(['SuperAdmin'])
    def get(self, contact_id=None):
        if contact_id:
            contact = Contact.query.get_or_404(contact_id)
            return make_response(contact.to_dict(), 200)
        contacts = Contact.query.all()
        return make_response([contact.to_dict() for contact in contacts], 200)

class ContactPostResource(Resource):
    @jwt_required()
    @role_required(['Admin', 'Resident'])
    def post(self):
        data = request.json
        new_contact = Contact(
            name=data['name'],
            subject=data['subject'],
            message=data['message']
        )
        db.session.add(new_contact)
        db.session.commit()
        return make_response(new_contact.to_dict(), 201)

class ContactPutResource(Resource):
    @jwt_required()
    @role_required(['SuperAdmin', 'Resident'])  # Updated to allow residents to update their own contacts
    def put(self, contact_id):
        contact = Contact.query.get_or_404(contact_id)
        user_id = get_jwt_identity()['id']
        if get_jwt_identity()['role'] != 'SuperAdmin' and contact.resident_id != user_id:
            return make_response({"error": "Unauthorized", "message": "You can only update your own contacts"}, 403)
        data = request.json
        contact.name = data.get('name', contact.name)
        contact.subject = data.get('subject', contact.subject)
        contact.message = data.get('message', contact.message)
        db.session.commit()
        return make_response(contact.to_dict(), 200)

class ContactDeleteResource(Resource):
    @jwt_required()
    @role_required(['SuperAdmin'])
    def delete(self, contact_id):
        contact = Contact.query.get_or_404(contact_id)
        db.session.delete(contact)
        db.session.commit()
        return make_response({"message": "Contact deleted"}, 200)


# Register the resources with the API
#add api for login
api.add_resource(LoginResource, '/login')
api.add_resource(NeighborhoodGetResource, '/neighborhoods', '/neighborhoods/<int:neighborhood_id>')
api.add_resource(NeighborhoodPostResource, '/neighborhoods')
api.add_resource(NeighborhoodPutResource, '/neighborhoods/<int:neighborhood_id>')
api.add_resource(NeighborhoodDeleteResource, '/neighborhoods/<int:neighborhood_id>')

api.add_resource(ResidentGetResource, '/neighborhoods/<int:neighborhood_id>/residents')
api.add_resource(ResidentPostResource, '/neighborhoods/<int:neighborhood_id>/residents')
api.add_resource(ResidentPutResource, '/residents/<int:resident_id>')
api.add_resource(ResidentDeleteResource, '/residents/<int:resident_id>')

api.add_resource(NewsGetResource, '/neighborhoods/<int:neighborhood_id>/news', '/news/<int:news_id>')
api.add_resource(NewsPostResource, '/neighborhoods/<int:neighborhood_id>/news')
api.add_resource(NewsPutResource, '/news/<int:news_id>')
api.add_resource(NewsDeleteResource, '/news/<int:news_id>')

api.add_resource(EventGetResource, '/neighborhoods/<int:neighborhood_id>/events', '/events/<int:event_id>')
api.add_resource(EventPostResource, '/neighborhoods/<int:neighborhood_id>/events')
api.add_resource(EventPutResource, '/events/<int:event_id>')
api.add_resource(EventDeleteResource, '/events/<int:event_id>')

api.add_resource(NotificationGetResource, '/notifications')
api.add_resource(NotificationDeleteResource, '/notifications/<int:notification_id>')  # Added for deletion

api.add_resource(ContactGetResource, '/contacts', '/contacts/<int:contact_id>')
api.add_resource(ContactPostResource, '/contacts')
api.add_resource(ContactPutResource, '/contacts/<int:contact_id>')
api.add_resource(ContactDeleteResource, '/contacts/<int:contact_id>')




# Run the app
if __name__ == '__main__':
    app.run(debug=True)
