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
    super_admin = Resident.query.filter_by(email="superadmin@example.com").first()
    if super_admin is None:
        super_admin = Resident(
            name="Super Admin",
            email="superadmin@example.com",
            password=generate_password_hash("superpassword"),
            role="SuperAdmin",
            neighborhood_id=default_neighborhood.id  # Assign to default neighborhood
        )
        db.session.add(super_admin)
    else:
        super_admin.name = "Super Admin"
        super_admin.password = generate_password_hash("superpassword")
        super_admin.role = "SuperAdmin"
        super_admin.neighborhood_id = default_neighborhood.id

    db.session.commit()

    # Create or Update Admins
    admin1 = Resident.query.filter_by(email="adminjohn@example.com").first()
    if admin1 is None:
        admin1 = Resident(
            name="Admin John",
            email="adminjohn@example.com",
            password=generate_password_hash("adminpassword"),
            role="Admin",
            neighborhood_id=neighborhood1.id
        )
        db.session.add(admin1)
    else:
        admin1.name = "Admin John"
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
    resident1 = Resident.query.filter_by(email="bob_unique@example.com").first()
    if resident1 is None:
        resident1 = Resident(
            name="Resident Bob",
            email="bob_unique@example.com",
            password=generate_password_hash("residentpassword"),
            role="Resident",
            neighborhood_id=neighborhood1.id,
            house_number="101"
        )
        db.session.add(resident1)
    else:
        resident1.name = "Resident Bob"
        resident1.password = generate_password_hash("residentpassword")
        resident1.role = "Resident"
        resident1.neighborhood_id = neighborhood1.id
        resident1.house_number = "101"

    resident2 = Resident.query.filter_by(email="alice_unique@example.com").first()
    if resident2 is None:
        resident2 = Resident(
            name="Resident Alice",
            email="alice_unique@example.com",
            password=generate_password_hash("residentpassword"),
            role="Resident",
            neighborhood_id=neighborhood2.id,
            house_number="202"
        )
        db.session.add(resident2)
    else:
        resident2.name = "Resident Alice"
        resident2.password = generate_password_hash("residentpassword")
        resident2.role = "Resident"
        resident2.neighborhood_id = neighborhood2.id
        resident2.house_number = "202"

    db.session.commit()

    # The rest of your seed data logic...
    print("Database seeded successfully!")

if __name__ == "__main__":
    from app import app  # Import the app to use its context

    with app.app_context():
        seed_data()
