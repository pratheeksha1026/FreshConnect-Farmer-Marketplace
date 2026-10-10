import os
import sqlite3
import webbrowser
import threading
from datetime import datetime
from pathlib import Path
from flask import Flask, render_template, request, redirect, url_for, flash, g
from werkzeug.utils import secure_filename

BASE_DIR = Path(__file__).resolve().parent
DATABASE = BASE_DIR / "freshconnect.db"
UPLOAD_FOLDER = BASE_DIR / "static" / "uploads"
ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg", "webp"}

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "change-this-development-secret")
app.config["UPLOAD_FOLDER"] = str(UPLOAD_FOLDER)
app.config["MAX_CONTENT_LENGTH"] = 5 * 1024 * 1024
UPLOAD_FOLDER.mkdir(parents=True, exist_ok=True)

def get_db():
    if "db" not in g:
        g.db = sqlite3.connect(DATABASE)
        g.db.row_factory = sqlite3.Row
        g.db.execute("PRAGMA foreign_keys = ON")
    return g.db

@app.teardown_appcontext
def close_db(_error=None):
    db = g.pop("db", None)
    if db is not None:
        db.close()

def init_db():
    with sqlite3.connect(DATABASE) as db:
        db.execute("""
        CREATE TABLE IF NOT EXISTS listings (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            farmer_name TEXT NOT NULL,
            phone TEXT NOT NULL,
            village TEXT NOT NULL,
            produce_name TEXT NOT NULL,
            category TEXT NOT NULL,
            quantity_kg REAL NOT NULL CHECK(quantity_kg > 0),
            price_per_kg REAL NOT NULL CHECK(price_per_kg >= 0),
            harvest_date TEXT,
            description TEXT,
            image_filename TEXT,
            created_at TEXT NOT NULL
        )
        """)
        count = db.execute("SELECT COUNT(*) FROM listings").fetchone()[0]
        if count == 0:
            examples = [
                ("Ravi", "9876543210", "Nanjangud", "Tomato", "Vegetables", 80, 5, "", "Fresh tomatoes available today. Price is negotiable for bulk orders.", None, datetime.now().isoformat(timespec="minutes")),
                ("Lakshmi", "9876501234", "Hunsur", "Banana", "Fruits", 45, 12, "", "Ripe bananas from a local farm.", None, datetime.now().isoformat(timespec="minutes")),
                ("Manjunath", "9876512345", "Mysuru outskirts", "Beans", "Vegetables", 25, 18, "", "Freshly harvested beans. Please call before pickup.", None, datetime.now().isoformat(timespec="minutes"))
            ]
            db.executemany("""INSERT INTO listings
                (farmer_name, phone, village, produce_name, category, quantity_kg,
                 price_per_kg, harvest_date, description, image_filename, created_at)
                 VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""", examples)
        db.commit()

def allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route("/")
def index():
    db = get_db()
    search = request.args.get("q", "").strip()
    category = request.args.get("category", "").strip()
    query = "SELECT * FROM listings WHERE quantity_kg > 0"
    params = []
    if search:
        query += " AND (produce_name LIKE ? OR village LIKE ? OR farmer_name LIKE ?)"
        like = f"%{search}%"
        params.extend([like, like, like])
    if category in ("Vegetables", "Fruits", "Other"):
        query += " AND category = ?"
        params.append(category)
    query += " ORDER BY created_at DESC"
    listings = db.execute(query, params).fetchall()
    return render_template("index.html", listings=listings, q=search, category=category)

@app.route("/add", methods=["GET", "POST"])
def add_listing():
    if request.method == "POST":
        fields = {
            "farmer_name": request.form.get("farmer_name", "").strip(),
            "phone": request.form.get("phone", "").strip(),
            "village": request.form.get("village", "").strip(),
            "produce_name": request.form.get("produce_name", "").strip(),
            "category": request.form.get("category", "").strip(),
            "harvest_date": request.form.get("harvest_date", "").strip(),
            "description": request.form.get("description", "").strip(),
        }
        try:
            quantity = float(request.form.get("quantity_kg", ""))
            price = float(request.form.get("price_per_kg", ""))
        except ValueError:
            flash("Enter valid numbers for quantity and price.", "error")
            return render_template("add_listing.html", form=request.form)
        if not all(fields[k] for k in ("farmer_name", "phone", "village", "produce_name", "category")):
            flash("Please complete all required fields.", "error")
            return render_template("add_listing.html", form=request.form)
        if quantity <= 0 or price < 0:
            flash("Quantity must be above 0 and price cannot be negative.", "error")
            return render_template("add_listing.html", form=request.form)
        if fields["category"] not in ("Vegetables", "Fruits", "Other"):
            flash("Choose a valid category.", "error")
            return render_template("add_listing.html", form=request.form)

        image_filename = None
        image = request.files.get("image")
        if image and image.filename:
            if not allowed_file(image.filename):
                flash("Upload a JPG, JPEG, PNG, or WEBP image only.", "error")
                return render_template("add_listing.html", form=request.form)
            safe_name = secure_filename(image.filename)
            image_filename = f"{datetime.now().strftime('%Y%m%d%H%M%S%f')}_{safe_name}"
            image.save(UPLOAD_FOLDER / image_filename)

        db = get_db()
        db.execute("""INSERT INTO listings
            (farmer_name, phone, village, produce_name, category, quantity_kg,
             price_per_kg, harvest_date, description, image_filename, created_at)
             VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
             (fields["farmer_name"], fields["phone"], fields["village"],
              fields["produce_name"], fields["category"], quantity, price,
              fields["harvest_date"], fields["description"], image_filename,
              datetime.now().isoformat(timespec="minutes")))
        db.commit()
        flash("Your produce listing is live. Buyers can now contact you directly!", "success")
        return redirect(url_for("index"))
    return render_template("add_listing.html", form={})

@app.route("/listing/<int:listing_id>")
def listing_detail(listing_id):
    listing = get_db().execute("SELECT * FROM listings WHERE id = ?", (listing_id,)).fetchone()
    if listing is None:
        flash("That listing could not be found.", "error")
        return redirect(url_for("index"))
    return render_template("listing.html", listing=listing)

@app.route("/listing/<int:listing_id>/delete", methods=["POST"])
def delete_listing(listing_id):
    # Demo-only deletion; production should require farmer authentication.
    db = get_db()
    listing = db.execute("SELECT * FROM listings WHERE id = ?", (listing_id,)).fetchone()
    if listing:
        if listing["image_filename"]:
            try:
                (UPLOAD_FOLDER / listing["image_filename"]).unlink(missing_ok=True)
            except OSError:
                pass
        db.execute("DELETE FROM listings WHERE id = ?", (listing_id,))
        db.commit()
        flash("Listing removed.", "success")
    return redirect(url_for("index"))

@app.route("/about")
def about():
    return render_template("about.html")

with app.app_context():
    init_db()

if __name__ == "__main__":
    if __name__ == "__main__":
        url = "http://127.0.0.1:5000"

    threading.Timer(
        1.5,
        lambda: webbrowser.open(url)
    ).start()

    app.run(debug=False, use_reloader=False)
