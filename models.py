from datetime import datetime
from extensions import db


class Admin(db.Model):
    id = db.Column(db.Integer, primary_key=True)

    username = db.Column(db.String(100), nullable=False, unique=True)

    password = db.Column(db.String(255), nullable=False)

    created_at = db.Column(db.DateTime, default=datetime.utcnow)


class Product(db.Model):
    id = db.Column(db.Integer, primary_key=True)

    name = db.Column(db.String(200), nullable=False)

    category = db.Column(db.String(100))

    description = db.Column(db.Text)

    price = db.Column(db.Float, nullable=False)

    image = db.Column(db.String(255))

    featured = db.Column(db.Boolean, default=False)

    in_stock = db.Column(db.Boolean, default=True)

    views = db.Column(db.Integer, default=0)

    whatsapp_clicks = db.Column(db.Integer, default=0)

    created_at = db.Column(db.DateTime, default=datetime.utcnow)


class Gallery(db.Model):
    id = db.Column(db.Integer, primary_key=True)

    title = db.Column(db.String(200))

    image = db.Column(db.String(255), nullable=False)

    created_at = db.Column(db.DateTime, default=datetime.utcnow)


class Testimonial(db.Model):
    id = db.Column(db.Integer, primary_key=True)

    customer_name = db.Column(db.String(150), nullable=False)

    rating = db.Column(db.Integer)

    message = db.Column(db.Text, nullable=False)

    approved = db.Column(db.Boolean, default=False)

    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class WebsiteSettings(db.Model):
    id = db.Column(db.Integer, primary_key=True)

    # Business Information
    business_name = db.Column(db.String(200))
    slogan = db.Column(db.String(255))
    description = db.Column(db.Text)

    # Contact
    whatsapp = db.Column(db.String(30))
    customer_care = db.Column(db.String(30))
    email = db.Column(db.String(200))
    address = db.Column(db.String(255))
    business_hours = db.Column(db.String(255))

    # Branding
    logo = db.Column(db.String(255))
    hero_image = db.Column(db.String(255))
    primary_color = db.Column(db.String(20), default="#0B6E4F")
    secondary_color = db.Column(db.String(20), default="#D4AF37")

    # Homepage
    hero_title = db.Column(db.String(255))
    hero_subtitle = db.Column(db.Text)

    # Statistics
    stat1_number = db.Column(db.String(20))
    stat1_label = db.Column(db.String(100))

    stat2_number = db.Column(db.String(20))
    stat2_label = db.Column(db.String(100))

    stat3_number = db.Column(db.String(20))
    stat3_label = db.Column(db.String(100))

    stat4_number = db.Column(db.String(20))
    stat4_label = db.Column(db.String(100))

    # Promotional Banner
    promo_text = db.Column(db.String(255))
    promo_enabled = db.Column(db.Boolean, default=True)

    # Social Media
    facebook = db.Column(db.String(255))
    instagram = db.Column(db.String(255))
    tiktok = db.Column(db.String(255))
    linkedin = db.Column(db.String(255))


class ActivityLog(db.Model):
    id = db.Column(db.Integer, primary_key=True)

    activity = db.Column(db.String(255))

    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class QuoteRequest(db.Model):
    id = db.Column(db.Integer, primary_key=True)

    full_name = db.Column(db.String(150), nullable=False)
    phone = db.Column(db.String(30), nullable=False)
    email = db.Column(db.String(200))
    business_name = db.Column(db.String(200))
    message = db.Column(db.Text, nullable=False)

    status = db.Column(
        db.String(50),
        default="Pending"
    )

    created_at = db.Column(
        db.DateTime,
        default=datetime.utcnow
    )