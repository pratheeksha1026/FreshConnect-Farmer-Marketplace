# FreshConnect — Direct Farmer-to-Buyer Marketplace

FreshConnect is a student-project MVP that helps farmers list surplus vegetables and fruits directly for nearby households, shops, hostels, restaurants, and other buyers. Farmers choose their own asking price, including a low price for surplus produce, instead of letting edible crops go to waste.

## Features
- Browse available produce listings
- Search by crop, farmer, or village
- Filter by category
- Add a listing with farmer details, quantity, price per kg, harvest date, description, and an optional photo
- Listing detail page with direct phone/WhatsApp contact links
- SQLite database; example listings are added on first launch
- Responsive layout for desktop and mobile

## Technology
Python, Flask, SQLite, HTML, CSS, and a little JavaScript.

## Run on Windows (VS Code)

1. Install Python 3.10 or newer.
2. Extract this folder and open it in VS Code.
3. Open **Terminal → New Terminal**.
4. Create a virtual environment:
   ```bash
   python -m venv .venv
   ```
5. Activate it in PowerShell:
   ```powershell
   .venv\Scripts\Activate.ps1
   ```
   If PowerShell blocks activation, use Command Prompt and run:
   ```bat
   .venv\Scripts\activate.bat
   ```
6. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
7. Start the app:
   ```bash
   python app.py
   ```
8. Open the local URL printed in the terminal, usually `http://127.0.0.1:5000`.

## How to test
1. Open **List your produce**.
2. Add a crop such as Tomato, quantity, price per kg, village, phone number, and a photo.
3. Return to the home page and search for the crop or village.
4. Open a listing and use **Call farmer** or **WhatsApp farmer**. The buyer and farmer should agree on quantity, pickup/delivery, and final price directly.

## Project purpose
The goal is to reduce avoidable food waste and help farmers recover at least some income from surplus produce. The platform does not promise a minimum price or guarantee a buyer; it makes local discovery and direct contact easier.

## Important MVP limitations
This is a learning/demo project, not a production marketplace. It does not yet include user accounts, verified farmer identity, payment processing, delivery logistics, moderation, or secure owner-only listing deletion. The delete button is demo-only. Do not deploy publicly with real personal data until authentication, authorization, privacy protections, input validation, image scanning, HTTPS, and production hosting are added.

## Suggested future improvements
- Farmer and buyer login with role-based access
- OTP/phone verification and report-listing feature
- Location-based discovery and distance filters
- Bulk-order requests for hostels, hotels, shops, and NGOs
- Availability expiry and quantity updates after sale
- Kannada and other regional-language interface
- Admin dashboard and waste-diversion impact statistics
- Notifications for buyers who follow a crop
- Optional pickup point coordination; avoid promising delivery unless a farmer supports it

## Folder structure
```text
FreshConnect_Farmer_Marketplace/
├── app.py
├── requirements.txt
├── README.md
├── .gitignore
├── templates/
│   ├── base.html
│   ├── index.html
│   ├── add_listing.html
│   ├── listing.html
│   └── about.html
└── static/
    ├── css/style.css
    ├── js/main.js
    └── uploads/        # uploaded listing photos
```
The SQLite database (`freshconnect.db`) is created automatically when the app first runs.
