from flask import Blueprint, render_template, request, redirect, session
from werkzeug.utils import secure_filename
from werkzeug.security import check_password_hash
import os

from extensions import db
from models import (
    Product,
    Admin,
    Gallery,
    Testimonial,
    WebsiteSettings,
    QuoteRequest
)

main = Blueprint("main", __name__)

ALLOWED_IMAGE_EXTENSIONS = {
    "jpg",
    "jpeg",
    "png",
    "webp",
    "gif"
}


def allowed_image(filename):
    return (
        "." in filename
        and filename.rsplit(".", 1)[1].lower()
        in ALLOWED_IMAGE_EXTENSIONS
    )


# ==========================
# GLOBAL WEBSITE SETTINGS
# ==========================

@main.context_processor
def inject_settings():

    settings = WebsiteSettings.query.first()

    return {
        "site_settings": settings
    }


# ==========================
# MAIN WEBSITE
# ==========================

@main.route("/")
def home():

    featured_products = Product.query.filter_by(
        featured=True,
        in_stock=True
    ).order_by(
        Product.created_at.desc()
    ).limit(6).all()

    testimonials = Testimonial.query.filter_by(
        approved=True
    ).order_by(
        Testimonial.created_at.desc()
    ).limit(6).all()

    return render_template(
        "index.html",
        featured_products=featured_products,
        testimonials=testimonials
    )


@main.route("/about")
def about():

    return render_template("about.html")


@main.route("/products")
def products():

    products = Product.query.filter_by(
        in_stock=True
    ).order_by(
        Product.created_at.desc()
    ).all()

    return render_template(
        "products.html",
        products=products
    )


@main.route("/gallery")
def gallery():

    gallery_images = Gallery.query.order_by(
        Gallery.created_at.desc()
    ).all()

    return render_template(
        "gallery.html",
        gallery_images=gallery_images
    )


# ==========================
# TESTIMONIALS
# ==========================

@main.route("/testimonials", methods=["GET", "POST"])
def testimonials():

    if request.method == "POST":

        customer_name = request.form.get("customer_name")
        rating = request.form.get("rating")
        message = request.form.get("message")

        if customer_name and message:

            testimonial = Testimonial(
                customer_name=customer_name,
                rating=int(rating) if rating else None,
                message=message,
                approved=False
            )

            db.session.add(testimonial)
            db.session.commit()

        return redirect("/testimonials")

    approved_testimonials = Testimonial.query.filter_by(
        approved=True
    ).order_by(
        Testimonial.created_at.desc()
    ).all()

    return render_template(
        "testimonials.html",
        testimonials=approved_testimonials
    )


@main.route("/contact")
def contact():

    return render_template("contact.html")


# ==================================================
# ADMIN LOGIN
# ==================================================

@main.route("/admin", methods=["GET", "POST"])
def admin_login():

    if request.method == "POST":

        username = request.form.get("username")
        password = request.form.get("password")

        admin = Admin.query.filter_by(
            username=username
        ).first()

        if admin and check_password_hash(
            admin.password,
            password
        ):

            session["admin_logged_in"] = True
            session["admin_username"] = admin.username

            return redirect("/admin/dashboard")

        return render_template(
            "admin/login.html",
            error="Invalid username or password."
        )

    return render_template("admin/login.html")


# ==================================================
# ADMIN LOGOUT
# ==================================================

@main.route("/admin/logout")
def admin_logout():

    session.pop("admin_logged_in", None)
    session.pop("admin_username", None)

    return redirect("/admin")


# ==================================================
# ADMIN DASHBOARD
# ==================================================


@main.route("/admin/dashboard")
def admin_dashboard():

    if not session.get("admin_logged_in"):
        return redirect("/admin")

    product_count = Product.query.count()

    gallery_count = Gallery.query.count()

    testimonial_count = Testimonial.query.count()

    quote_count = QuoteRequest.query.count()

    pending_quotes = QuoteRequest.query.filter_by(
        status="Pending"
    ).count()

    contacted_quotes = QuoteRequest.query.filter_by(
        status="Contacted"
    ).count()

    completed_quotes = QuoteRequest.query.filter_by(
        status="Completed"
    ).count()

    cancelled_quotes = QuoteRequest.query.filter_by(
        status="Cancelled"
    ).count()

    return render_template(
        "admin/dashboard.html",
        product_count=product_count,
        gallery_count=gallery_count,
        testimonial_count=testimonial_count,
        quote_count=quote_count,
        pending_quotes=pending_quotes,
        contacted_quotes=contacted_quotes,
        completed_quotes=completed_quotes,
        cancelled_quotes=cancelled_quotes
    )




# ==================================================
# ADMIN PRODUCTS
# ==================================================

@main.route("/admin/products")
def admin_products():

    if not session.get("admin_logged_in"):
        return redirect("/admin")

    products = Product.query.order_by(
        Product.created_at.desc()
    ).all()

    return render_template(
        "admin/products.html",
        products=products
    )


@main.route("/admin/products/add", methods=["POST"])
@main.route("/admin/products/add", methods=["POST"])
def add_product():

    if not session.get("admin_logged_in"):
        return redirect("/admin")

    name = request.form.get("name")
    category = request.form.get("category")
    description = request.form.get("description")
    price = request.form.get("price")

    featured = request.form.get("featured") == "on"
    in_stock = request.form.get("in_stock") == "on"

    image_file = request.files.get("image")

    image_filename = None

    # Handle image only if one was selected
    if image_file and image_file.filename:

        if not allowed_image(image_file.filename):
            return redirect("/admin/products")

        image_filename = secure_filename(
            image_file.filename
        )

        upload_folder = os.path.join(
            os.getcwd(),
            "static",
            "uploads"
        )

        os.makedirs(
            upload_folder,
            exist_ok=True
        )

        image_file.save(
            os.path.join(
                upload_folder,
                image_filename
            )
        )

    product = Product(
        name=name,
        category=category,
        description=description,
        price=float(price),
        image=image_filename,
        featured=featured,
        in_stock=in_stock
    )

    db.session.add(product)
    db.session.commit()

    return redirect("/admin/products")

# ==========================
# DELETE PRODUCT
# ==========================

@main.route(
    "/admin/products/delete/<int:product_id>",
    methods=["POST"]
)
def delete_product(product_id):

    if not session.get("admin_logged_in"):
        return redirect("/admin")

    product = Product.query.get_or_404(
        product_id
    )

    db.session.delete(product)
    db.session.commit()

    return redirect("/admin/products")


# ==========================
# EDIT PRODUCT
# ==========================

@main.route(
    "/admin/products/edit/<int:product_id>",
    methods=["GET", "POST"]
)
def edit_product(product_id):

    if not session.get("admin_logged_in"):
        return redirect("/admin")

    product = Product.query.get_or_404(
        product_id
    )

    if request.method == "POST":

        product.name = request.form.get("name")

        product.category = request.form.get(
            "category"
        )

        product.description = request.form.get(
            "description"
        )

        product.price = float(
            request.form.get("price")
        )

        product.featured = (
            request.form.get("featured") == "on"
        )

        product.in_stock = (
            request.form.get("in_stock") == "on"
        )

        image_file = request.files.get("image")

        if image_file and image_file.filename:

            image_filename = secure_filename(
                image_file.filename
            )

            upload_folder = os.path.join(
                os.getcwd(),
                "static",
                "uploads"
            )

            os.makedirs(
                upload_folder,
                exist_ok=True
            )

            image_file.save(
                os.path.join(
                    upload_folder,
                    image_filename
                )
            )

            product.image = image_filename

        db.session.commit()

        return redirect("/admin/products")

    return render_template(
        "admin/edit_product.html",
        product=product
    )


# ==================================================
# ADMIN GALLERY
# ==================================================

@main.route("/admin/gallery")
def admin_gallery():

    if not session.get("admin_logged_in"):
        return redirect("/admin")

    gallery = Gallery.query.order_by(
        Gallery.created_at.desc()
    ).all()

    return render_template(
        "admin/gallery.html",
        gallery=gallery
    )


@main.route(
    "/admin/gallery/add",
    methods=["POST"]
)
def add_gallery():

    if not session.get("admin_logged_in"):
        return redirect("/admin")

    title = request.form.get("title")

    image_file = request.files.get("image")

    if not image_file or not image_file.filename:

        return redirect("/admin/gallery")
    if not allowed_image(image_file.filename):
        return redirect("/admin/gallery")

    image_filename = secure_filename(
        image_file.filename
    )

    upload_folder = os.path.join(
        os.getcwd(),
        "static",
        "uploads"
    )

    os.makedirs(
        upload_folder,
        exist_ok=True
    )

    image_file.save(
        os.path.join(
            upload_folder,
            image_filename
        )
    )

    gallery = Gallery(
        title=title,
        image=image_filename
    )

    db.session.add(gallery)
    db.session.commit()

    return redirect("/admin/gallery")


@main.route(
    "/admin/gallery/delete/<int:gallery_id>",
    methods=["POST"]
)
def delete_gallery(gallery_id):

    if not session.get("admin_logged_in"):
        return redirect("/admin/gallery")

    gallery = Gallery.query.get_or_404(
        gallery_id
    )

    db.session.delete(gallery)
    db.session.commit()

    return redirect("/admin/gallery")


# ==================================================
# ADMIN TESTIMONIALS
# ==================================================

@main.route("/admin/testimonials")
def admin_testimonials():

    if not session.get("admin_logged_in"):
        return redirect("/admin")

    testimonials = Testimonial.query.order_by(
        Testimonial.created_at.desc()
    ).all()

    return render_template(
        "admin/testimonials.html",
        testimonials=testimonials
    )


@main.route(
    "/admin/testimonials/approve/<int:testimonial_id>",
    methods=["POST"]
)
def approve_testimonial(testimonial_id):

    if not session.get("admin_logged_in"):
        return redirect("/admin")

    testimonial = Testimonial.query.get_or_404(
        testimonial_id
    )

    testimonial.approved = True

    db.session.commit()

    return redirect("/admin/testimonials")


@main.route(
    "/admin/testimonials/delete/<int:testimonial_id>",
    methods=["POST"]
)
def delete_testimonial(testimonial_id):

    if not session.get("admin_logged_in"):
        return redirect("/admin")

    testimonial = Testimonial.query.get_or_404(
        testimonial_id
    )

    db.session.delete(testimonial)

    db.session.commit()

    return redirect("/admin/testimonials")


# ==================================================
# SUBMIT QUOTE REQUEST
# ==================================================

@main.route(
    "/quote",
    methods=["POST"]
)
def submit_quote():

    full_name = request.form.get(
        "full_name"
    )

    phone = request.form.get(
        "phone"
    )

    email = request.form.get(
        "email"
    )

    business_name = request.form.get(
        "business_name"
    )

    message = request.form.get(
        "message"
    )

    if not full_name or not phone or not message:

        return redirect("/")

    quote = QuoteRequest(
        full_name=full_name,
        phone=phone,
        email=email,
        business_name=business_name,
        message=message,
        status="Pending"
    )

    db.session.add(quote)
    db.session.commit()

    return redirect("/")


# ==================================================
# ADMIN QUOTE REQUESTS
# ==================================================

@main.route("/admin/quotes")
def admin_quotes():

    if not session.get("admin_logged_in"):
        return redirect("/admin")

    quotes = QuoteRequest.query.order_by(
        QuoteRequest.created_at.desc()
    ).all()

    return render_template(
        "admin/quotes.html",
        quotes=quotes
    )


# ==========================
# UPDATE QUOTE STATUS
# ==========================

@main.route(
    "/admin/quotes/status/<int:quote_id>",
    methods=["POST"]
)
def update_quote_status(quote_id):

    if not session.get("admin_logged_in"):
        return redirect("/admin")

    quote = QuoteRequest.query.get_or_404(
        quote_id
    )

    status = request.form.get("status")

    allowed_statuses = [
        "Pending",
        "Contacted",
        "Completed",
        "Cancelled"
    ]

    if status in allowed_statuses:

        quote.status = status

        db.session.commit()

    return redirect("/admin/quotes")


# ==========================
# DELETE QUOTE
# ==========================

@main.route(
    "/admin/quotes/delete/<int:quote_id>",
    methods=["POST"]
)
def delete_quote(quote_id):

    if not session.get("admin_logged_in"):
        return redirect("/admin")

    quote = QuoteRequest.query.get_or_404(
        quote_id
    )

    db.session.delete(quote)

    db.session.commit()

    return redirect("/admin/quotes")




# ==================================================
# ADMIN SETTINGS
# ==================================================

@main.route(
    "/admin/settings",
    methods=["GET", "POST"]
)
def admin_settings():

    if not session.get("admin_logged_in"):
        return redirect("/admin")

    settings = WebsiteSettings.query.first()

    if not settings:

        settings = WebsiteSettings(
            business_name="Chidinma Standard Ventures",
            slogan="Quality products, trusted service.",
            primary_color="#0B6E4F",
            secondary_color="#D4AF37",
            promo_enabled=True
        )

        db.session.add(settings)
        db.session.commit()

    if request.method == "POST":

        settings.business_name = request.form.get(
            "business_name"
        )

        settings.slogan = request.form.get(
            "slogan"
        )

        settings.description = request.form.get(
            "description"
        )

        settings.whatsapp = request.form.get(
            "whatsapp"
        )

        settings.customer_care = request.form.get(
            "customer_care"
        )

        settings.email = request.form.get(
            "email"
        )

        settings.address = request.form.get(
            "address"
        )

        settings.business_hours = request.form.get(
            "business_hours"
        )

        settings.hero_title = request.form.get(
            "hero_title"
        )

        settings.hero_subtitle = request.form.get(
            "hero_subtitle"
        )

        settings.primary_color = request.form.get(
            "primary_color"
        )

        settings.secondary_color = request.form.get(
            "secondary_color"
        )

        settings.stat1_number = request.form.get(
            "stat1_number"
        )

        settings.stat1_label = request.form.get(
            "stat1_label"
        )

        settings.stat2_number = request.form.get(
            "stat2_number"
        )

        settings.stat2_label = request.form.get(
            "stat2_label"
        )

        settings.stat3_number = request.form.get(
            "stat3_number"
        )

        settings.stat3_label = request.form.get(
            "stat3_label"
        )

        settings.stat4_number = request.form.get(
            "stat4_number"
        )

        settings.stat4_label = request.form.get(
            "stat4_label"
        )

        settings.promo_text = request.form.get(
            "promo_text"
        )

        settings.promo_enabled = (
            request.form.get("promo_enabled") == "on"
        )

        settings.facebook = request.form.get(
            "facebook"
        )

        settings.instagram = request.form.get(
            "instagram"
        )

        settings.tiktok = request.form.get(
            "tiktok"
        )

        settings.linkedin = request.form.get(
            "linkedin"
        )

        db.session.commit()

        return redirect("/admin/settings")

    return render_template(
        "admin/settings.html",
        settings=settings
    )

