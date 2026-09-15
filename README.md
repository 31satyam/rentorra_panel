# Rentorra - Property Rental Lead-Generation Platform

> **"Find Your Perfect Rental Home"**  
> A high-conversion, production-ready property rental discovery and lead-generation portal built with Django, PostgreSQL, Bootstrap 5, and custom styling.

---

## 1. Business Architecture

Rentorra is engineered specifically for **lead generation** across rental properties (1 BHK, 2 BHK, 3 BHK, 4 BHK, Flats, Apartments, Builder Floors). The core funnel is:

$$\text{Advertisement / Organic Traffic} \longrightarrow \text{Property Catalog} \longrightarrow \text{Enquiry Intake} \longrightarrow \text{Lead Attribution} \longrightarrow \text{Sales Team Conversion}$$

### Key Features
- **Lead Capture & Attribution Engine**: Automatic UTM tracking (`utm_source`, `utm_medium`, `utm_campaign`, `utm_term`, `utm_content`) with session persistence across browsing journeys.
- **Requirement Intake Form (`/find-property/`)**: High-conversion 3-section form with instant lead capture.
- **Dynamic Property Catalog**: Multi-filtering by City, Area, BHK, Property Type, Budget Min/Max, and Furnishing with pagination.
- **Property Details & SEO**: Image gallery, specification cards, verified badges, OpenGraph tags, and JSON-LD structured data (`RealEstateListing`).
- **Mobile First Experience**: Sticky mobile action bar (`Call` | `WhatsApp` | `Enquire`) and floating WhatsApp connect button.
- **Internal Sales CRM Dashboard (`/dashboard/`)**: Staff KPI metrics, pipeline stages (New, Contacted, Visit Scheduled, Converted), source breakdown, and instant WhatsApp/Call outreach links.
- **Advertisement Module**: Banner placements (`homepage_hero`, `homepage_banner`, `property_listing`, `property_detail`), click tracking, and UTM injection.
- **Spam Defense**: Honeypot anti-spam verification, mobile number format checks, and 5-minute duplicate submission deduplication.
- **Notification Services**: Asynchronous-safe HTML email dispatch to `ADMIN_EMAIL` on new lead submission.

---

## 2. Technology Stack

- **Backend**: Python 3.12+, Django 5.x
- **Database**: PostgreSQL (with automatic SQLite fallback for local zero-configuration development)
- **Frontend**: Bootstrap 5, Bootstrap Icons, Google Fonts (Outfit & Inter), Vanilla CSS/JS
- **Media & Assets**: Pillow (image processing), Whitenoise (production static asset serving)
- **Production Server**: Gunicorn WSGI, Nginx Reverse Proxy, Systemd process supervision

---

## 3. Local Development Setup

### 3.1. Clone Repository & Create Virtual Environment

**Windows (PowerShell):**
```powershell
git clone <repository_url> rentorra
cd rentorra
python -m venv venv
.\venv\Scripts\Activate.ps1
```

**Linux / macOS:**
```bash
git clone <repository_url> rentorra
cd rentorra
python3 -m venv venv
source venv/bin/activate
```

---

### 3.2. Install Dependencies

```bash
pip install --upgrade pip
pip install -r requirements.txt
```

---

### 3.3. Configure Environment Variables

Create your `.env` file from `.env.example`:

**Windows:**
```powershell
copy .env.example .env
```

**Linux / macOS:**
```bash
cp .env.example .env
```

*Note: In development, if `DATABASE_URL` is left blank, Rentorra will automatically use local SQLite (`db.sqlite3`). For PostgreSQL, set:*
```ini
DATABASE_URL=postgres://postgres:postgres@localhost:5432/rentorra_db
```

---

### 3.4. Database Setup, Migrations & Initial Seed Data

Run Django migrations:
```bash
python manage.py makemigrations
python manage.py migrate
```

Populate the database with realistic Indian property listings (Noida, Gurugram, Bengaluru, South Delhi), amenities, locations, sample CRM leads, and banner ads:
```bash
python manage.py seed_data
```

*Default administrator credentials created by `seed_data`:*
- **Username**: `admin`
- **Password**: `rentorra@2026`
- **Admin Portal**: `http://127.0.0.1:8000/admin/`
- **Internal Staff CRM**: `http://127.0.0.1:8000/dashboard/`

---

### 3.5. Run Development Server

```bash
python manage.py runserver
```

Open [http://127.0.0.1:8000/](http://127.0.0.1:8000/) in your browser.

---

### 3.6. Run Automated Tests & Quality Checks

Run system sanity check:
```bash
python manage.py check
```

Run test suite:
```bash
python manage.py test
```

---

## 4. Production Deployment Guide (Ubuntu 22.04 / 24.04 VPS)

Follow this complete step-by-step guide to deploy Rentorra on a Linux VPS (DigitalOcean, Linode, AWS EC2, or Hetzner).

### Step 1: Server Preparation & System Updates
```bash
sudo apt update && sudo apt upgrade -y
sudo apt install -y python3-pip python3-venv python3-dev libpq-dev postgresql postgresql-contrib nginx curl git
```

---

### Step 2: Configure PostgreSQL Database
```bash
sudo -u postgres psql
```

Inside PostgreSQL prompt:
```sql
CREATE DATABASE rentorra_db;
CREATE USER rentorra_user WITH PASSWORD 'ReplaceWithStrongSecurePassword123!';
ALTER ROLE rentorra_user SET client_encoding TO 'utf8';
ALTER ROLE rentorra_user SET default_transaction_isolation TO 'read committed';
ALTER ROLE rentorra_user SET timezone TO 'Asia/Kolkata';
GRANT ALL PRIVILEGES ON DATABASE rentorra_db TO rentorra_user;
\q
```

---

### Step 3: Deploy Application Code
```bash
sudo mkdir -p /var/www/rentorra
sudo chown -R $USER:$USER /var/www/rentorra
git clone <your_repo_url> /var/www/rentorra
cd /var/www/rentorra
```

---

### Step 4: Python Virtual Environment & Requirements
```bash
python3 -m venv venv
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
```

---

### Step 5: Configure Production `.env`
Create `/var/www/rentorra/.env`:
```bash
nano /var/www/rentorra/.env
```

Add your production parameters:
```ini
SECRET_KEY=generate-a-strong-random-50-character-secret-key
DEBUG=False
ALLOWED_HOSTS=rentorra.com,www.rentorra.com,your_server_ip

# PostgreSQL connection string
DATABASE_URL=postgres://rentorra_user:ReplaceWithStrongSecurePassword123!@localhost:5432/rentorra_db

# Email settings for notifications
EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=notifications@rentorra.com
EMAIL_HOST_PASSWORD=your_smtp_app_password
DEFAULT_FROM_EMAIL=Rentorra Leads <notifications@rentorra.com>
ADMIN_EMAIL=sales@rentorra.com

# Contact Info
COMPANY_PHONE=+919876543210
WHATSAPP_NUMBER=+919876543210
COMPANY_EMAIL=contact@rentorra.com
COMPANY_ADDRESS=Plot 45, Sector 62, Noida, UP 201309
```

---

### Step 6: Migrations, Static Collection & Seed Data
```bash
source venv/bin/activate
python manage.py migrate
python manage.py seed_data
python manage.py collectstatic --noinput
```

Ensure permissions for media directory:
```bash
sudo chown -R www-data:www-data /var/www/rentorra/media
sudo chmod -R 775 /var/www/rentorra/media
```

---

### Step 7: Configure Gunicorn Systemd Service
Create service file `/etc/systemd/system/rentorra.service`:
```bash
sudo nano /etc/systemd/system/rentorra.service
```

Paste:
```ini
[Unit]
Description=Gunicorn daemon for Rentorra Property Portal
After=network.target

[Service]
User=www-data
Group=www-data
WorkingDirectory=/var/www/rentorra
ExecStart=/var/www/rentorra/venv/bin/gunicorn \
          --access-logfile - \
          --workers 3 \
          --bind unix:/run/rentorra.sock \
          config.wsgi:application

[Install]
WantedBy=multi-user.target
```

Enable and start Gunicorn:
```bash
sudo systemctl daemon-reload
sudo systemctl start rentorra
sudo systemctl enable rentorra
sudo systemctl status rentorra
```

---

### Step 8: Configure Nginx Reverse Proxy
Create `/etc/nginx/sites-available/rentorra`:
```bash
sudo nano /etc/nginx/sites-available/rentorra
```

Paste:
```nginx
server {
    listen 80;
    server_name rentorra.com www.rentorra.com;

    client_max_body_size 25M;

    location = /favicon.ico { access_log off; log_not_found off; }

    # Static files handled by Nginx
    location /static/ {
        alias /var/www/rentorra/staticfiles/;
        expires 30d;
        add_header Cache-Control "public, max-age=2592000";
    }

    # Media files (property uploads, banners)
    location /media/ {
        alias /var/www/rentorra/media/;
        expires 30d;
    }

    # Gunicorn reverse proxy
    location / {
        include proxy_params;
        proxy_pass http://unix:/run/rentorra.sock;
    }
}
```

Enable site and test Nginx:
```bash
sudo ln -s /etc/nginx/sites-available/rentorra /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx
```

---

### Step 9: Configure SSL with Let's Encrypt (Certbot)
```bash
sudo apt install -y certbot python3-certbot-nginx
sudo certbot --nginx -d rentorra.com -d www.rentorra.com
```

Select automatic redirect to HTTPS. Certbot will configure SSL renewal cron automatically.

---

### Step 10: Production Maintenance Commands

**Reload Application after code update:**
```bash
cd /var/www/rentorra
git pull origin main
source venv/bin/activate
pip install -r requirements.txt
python manage.py migrate
python manage.py collectstatic --noinput
sudo systemctl restart rentorra
sudo systemctl reload nginx
```

**Check Live Logs:**
```bash
# Gunicorn Logs
sudo journalctl -u rentorra -f

# Nginx Error Logs
sudo tail -f /var/log/nginx/error.log
```

---

## 5. Deployment Verification Checklist

- [x] Environment `.env` has `DEBUG=False` in production.
- [x] Unique `SECRET_KEY` generated.
- [x] PostgreSQL connection active and migrations up to date.
- [x] Gunicorn daemon active on `unix:/run/rentorra.sock`.
- [x] Nginx serving `/static/` and `/media/` directories directly.
- [x] SSL certificate active with automatic HTTPS redirect.
- [x] Test lead submitted on `/find-property/?utm_source=facebook&utm_campaign=test_launch` saves UTM attribution.
- [x] Email notification arrives at `ADMIN_EMAIL`.
- [x] WhatsApp click-to-chat opens pre-filled enquiry message.
- [x] `/sitemap.xml` and `/robots.txt` respond with HTTP 200.
- [x] `/dashboard/` loads staff KPIs and pipeline lead table.
