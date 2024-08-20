from models import db, Resident, Neighborhood, News, Event, Contact
from werkzeug.security import generate_password_hash
from datetime import datetime, timezone

def seed_data():
    # Create Neighborhoods
    default_neighborhood = Neighborhood(name="Default Neighborhood", location="N/A", image_url="https://example.com/default.jpg")
    neighborhood1 = Neighborhood(name="Greenfield", location="123 Green St", image_url="https://example.com/greenfield.jpg")
    neighborhood2 = Neighborhood(name="Sunnyvale", location="456 Sun St", image_url="https://example.com/sunnyvale.jpg")

    db.session.add_all([default_neighborhood, neighborhood1, neighborhood2])
    db.session.commit()

    # Create or Update SuperAdmin
    super_admin = Resident.query.filter_by(email="princesssuperadmin@gmail.com").first()
    if super_admin is None:
        super_admin = Resident(
            name="princess",
            email="princesssuperadmin@gmail.com",
            password=generate_password_hash("superpassword"),
            role="SuperAdmin",
            neighborhood_id=default_neighborhood.id
        )
        db.session.add(super_admin)
    else:
        super_admin.name = "princess"
        super_admin.password = generate_password_hash("superpassword")
        super_admin.role = "SuperAdmin"
        super_admin.neighborhood_id = default_neighborhood.id

    db.session.commit()

    # Create or Update Admins
    admin1 = Resident.query.filter_by(email="admingift@gmail.com").first()
    if admin1 is None:
        admin1 = Resident(
            name="Gift Omandi",
            email="admingift@gmail.com",
            password=generate_password_hash("adminpassword"),
            role="Admin",
            neighborhood_id=neighborhood1.id
        )
        db.session.add(admin1)
    else:
        admin1.name = "Gift Omandi"
        admin1.password = generate_password_hash("adminpassword")
        admin1.role = "Admin"
        admin1.neighborhood_id = neighborhood1.id

    admin2 = Resident.query.filter_by(email="adminjane@example.com").first()
    if admin2 is None:
        admin2 = Resident(
            name="Admin Jane",
            email="adminjane@example.com",
            password=generate_password_hash("adminpassword"),
            role="Admin",
            neighborhood_id=neighborhood2.id
        )
        db.session.add(admin2)
    else:
        admin2.name = "Admin Jane"
        admin2.password = generate_password_hash("adminpassword")
        admin2.role = "Admin"
        admin2.neighborhood_id = neighborhood2.id

    db.session.commit()

    # Create or Update Residents
    resident1 = Resident.query.filter_by(email="arnold@gmail.com").first()
    if resident1 is None:
        resident1 = Resident(
            name="Arnold",
            email="arnold@gmail.com",
            password=generate_password_hash("residentpassword"),
            role="Resident",
            neighborhood_id=neighborhood1.id,
            house_number="101"
        )
        db.session.add(resident1)
    else:
        resident1.name = "Arnold"
        resident1.password = generate_password_hash("residentpassword")
        resident1.role = "Resident"
        resident1.neighborhood_id = neighborhood1.id
        resident1.house_number = "101"

    resident2 = Resident.query.filter_by(email="alice_unique@example.com").first()
    if resident2 is None:
        resident2 = Resident(
            name="Alice",
            email="alice_unique@example.com",
            password=generate_password_hash("residentpassword"),
            role="Resident",
            neighborhood_id=neighborhood2.id,
            house_number="202"
        )
        db.session.add(resident2)
    else:
        resident2.name = "Alice"
        resident2.password = generate_password_hash("residentpassword")
        resident2.role = "Resident"
        resident2.neighborhood_id = neighborhood2.id
        resident2.house_number = "202"

    db.session.commit()

    # Create News
    news1 = News(
        title="Neighborhood Cleanup Day",
        description="Join us for a community cleanup event this Saturday.",
        date_created=datetime.now(timezone.utc),
        image_url="https://example.com/cleanup.jpg"
    )

    news2 = News(
        title="New Park Opening",
        description="A new park is opening in Sunnyvale next week!",
        date_created=datetime.now(timezone.utc),
        image_url="https://example.com/park.jpg"
    )

    db.session.add_all([news1, news2])
    db.session.commit()

    # Create Events
    event1 = Event(
        name="Summer Festival",
        description="A fun summer festival with music, food, and games.",
        date=datetime.now(timezone.utc),
        image_url="https://example.com/festival.jpg"
    )

    event2 = Event(
        name="Winter Gala",
        description="Celebrate the winter season with a grand gala event.",
        date=datetime.now(timezone.utc),
        image_url="https://example.com/gala.jpg"
    )

    db.session.add_all([event1, event2])
    db.session.commit()

    # Optional: Add some contact messages
    contact1 = Contact(
        name="John Doe",
        subject="Inquiry about the cleanup event",
        message="Looking forward to the neighborhood cleanup event!"
    )

    contact2 = Contact(
        name="Jane Smith",
        subject="Feedback on the new park",
        message="Excited about the new park opening!"
    )

    db.session.add_all([contact1, contact2])
    db.session.commit()

    print("Database seeded successfully with residents, news, events, and contacts!")

if __name__ == "__main__":
    from app import app  # Import the app to use its context

    with app.app_context():
        seed_data()
