import os
import random
from io import BytesIO
from datetime import date, timedelta
from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from django.core.files.base import ContentFile
from PIL import Image, ImageDraw, ImageFont
from apps.properties.models import Location, Amenity, Property, PropertyImage
from apps.enquiries.models import Enquiry
from apps.advertisements.models import Advertisement

class Command(BaseCommand):
    help = "Seeds initial production-ready demonstration data for Rentorra"

    def create_sample_image(self, text, bg_color=(24, 43, 73), text_color=(255, 255, 255), width=800, height=550):
        """Generates a clean, branded demo property photo in memory."""
        img = Image.new('RGB', (width, height), color=bg_color)
        draw = ImageDraw.Draw(img)

        # Draw aesthetic geometric architectural accents
        draw.rectangle([20, 20, width - 20, height - 20], outline=(255, 255, 255, 60), width=2)
        draw.rectangle([width - 240, 40, width - 40, 100], fill=(13, 148, 136))
        
        # Add badge text
        draw.text((width - 220, 60), "RENTORRA VERIFIED", fill=(255, 255, 255))
        
        # Main label
        draw.text((60, height - 120), text, fill=text_color)
        draw.text((60, height - 70), "rentorra.com • Find Your Perfect Rental Home", fill=(200, 220, 240))

        buffer = BytesIO()
        img.save(buffer, format='JPEG', quality=85)
        buffer.seek(0)
        return buffer.getvalue()

    def handle(self, *args, **options):
        self.stdout.write(self.style.NOTICE("Seeding Rentorra demo data..."))

        # 1. Ensure Superuser
        admin_user, created = User.objects.get_or_create(username='admin')
        if created:
            admin_user.set_password('rentorra@2026')
            admin_user.email = 'admin@rentorra.com'
            admin_user.is_superuser = True
            admin_user.is_staff = True
            admin_user.save()
            self.stdout.write(self.style.SUCCESS("Created superuser: admin / rentorra@2026"))

        # 2. Seed Locations
        locations_data = [
            # Noida
            {'city': 'Noida', 'area': 'Sector 62', 'description': 'Premier IT and corporate hub in Noida with excellent metro connectivity to Delhi and rapid transit corridors.'},
            {'city': 'Noida', 'area': 'Sector 137', 'description': 'Modern residential belt along Noida Expressway featuring lush gated societies, clubhouse communities and reputed schools.'},
            {'city': 'Noida', 'area': 'Sector 150', 'description': 'Low-density green luxury sector offering sports complexes, expansive golf park views and signal-free connectivity.'},
            {'city': 'Noida', 'area': 'Sector 75', 'description': 'Vibrant central neighborhood near Sector 50 Metro with walkable markets, clinics, and family-friendly apartment complexes.'},
            # Gurugram
            {'city': 'Gurugram', 'area': 'DLF Phase 5', 'description': 'Elite upscale enclave on Golf Course Road housing top luxury condominiums, premium shopping, and multinational headquarters.'},
            {'city': 'Gurugram', 'area': 'Golf Course Extn', 'description': 'Rapidly booming residential stretch with modern gated skyscrapers, international schools, and seamless Cyber City access.'},
            {'city': 'Gurugram', 'area': 'Cyber City & Sector 24', 'description': 'Prime executive corridor adjacent to corporate towers, rapid metro, and gourmet high-street dining.'},
            # Bengaluru
            {'city': 'Bengaluru', 'area': 'Whitefield', 'description': 'Bangalore tech capital boasting major IT tech parks, shopping malls, international schools, and newly extended metro lines.'},
            {'city': 'Bengaluru', 'area': 'HSR Layout', 'description': 'Startup capital of India, peaceful wide leafy avenues, booming cafe culture and supreme central connectivity.'},
            {'city': 'Bengaluru', 'area': 'Koramangala', 'description': 'Dynamic cosmopolitan hotspot with world-class restaurants, co-working hubs, and charming tree-lined residences.'},
            # Delhi
            {'city': 'South Delhi', 'area': 'Greater Kailash', 'description': 'Prestigious South Delhi address known for grand independent floors, bustling M-Block markets, and serene parks.'},
            {'city': 'South Delhi', 'area': 'Saket', 'description': 'Sought-after residential neighborhood near Select Citywalk Mall, metro stations, and historic green sanctuaries.'},
        ]

        location_objs = {}
        for loc in locations_data:
            obj, _ = Location.objects.get_or_create(
                city=loc['city'], area=loc['area'],
                defaults={'description': loc['description'], 'is_active': True}
            )
            location_objs[f"{loc['area']}, {loc['city']}"] = obj

        self.stdout.write(self.style.SUCCESS(f"Seeded {len(location_objs)} Locations."))

        # 3. Seed Amenities
        amenities_data = [
            ('High Speed Elevator / Lift', 'bi-arrow-down-up', True),
            ('24x7 Security & Guard', 'bi-shield-check', True),
            ('100% Power Backup', 'bi-lightning-charge', True),
            ('Dedicated Covered Car Parking', 'bi-car-front', True),
            ('Gymnasium & Fitness Studio', 'bi-heart-pulse', True),
            ('Swimming Pool', 'bi-water', True),
            ('Gated Society with CCTV', 'bi-camera-video', True),
            ('Private Balcony', 'bi-sun', False),
            ('Club House & Community Hall', 'bi-people', False),
            ('High Speed Fiber Internet', 'bi-wifi', False),
            ('Modular Kitchen & Chimney', 'bi-grid-1x2', True),
            ('RO Water Purifier System', 'bi-droplet', False),
            ('Children Play Park & Lawn', 'bi-emoji-smile', False),
            ('Piped Natural Gas (PNG)', 'bi-fire', False),
            ('Intercom Facility', 'bi-telephone', False),
        ]

        amenity_objs = []
        for name, icon, featured in amenities_data:
            a_obj, _ = Amenity.objects.get_or_create(
                name=name,
                defaults={'icon_class': icon, 'is_featured': featured}
            )
            amenity_objs.append(a_obj)

        self.stdout.write(self.style.SUCCESS(f"Seeded {len(amenity_objs)} Amenities."))

        # 4. Seed Properties
        properties_data = [
            {
                'title': 'Sunlit 2 BHK High-Rise Flat in Sector 62',
                'property_type': 'flat',
                'bhk': '2_bhk',
                'rent': 26000,
                'security_deposit': 52000,
                'maintenance_charges': 2500,
                'loc_key': 'Sector 62, Noida',
                'address': 'Tower B, Express Park View, Sector 62',
                'pincode': '201309',
                'area_sqft': 1150,
                'bedrooms': 2,
                'bathrooms': 2,
                'balconies': 2,
                'furnishing': 'semi_furnished',
                'parking': '1_car',
                'floor_no': '7th of 18',
                'facing': 'North-East',
                'status': 'available',
                'is_featured': True,
                'description': 'Beautifully ventilated 2 BHK apartment situated inside a top-tier gated society. Features wooden flooring in master bedroom, modular kitchen with chimney, and expansive morning sunlight. Walking distance from Sector 62 Electronic City Metro Station.',
            },
            {
                'title': 'Luxury 3 BHK Park-Facing Apartment in Sector 137',
                'property_type': 'apartment',
                'bhk': '3_bhk',
                'rent': 42000,
                'security_deposit': 84000,
                'maintenance_charges': 3500,
                'loc_key': 'Sector 137, Noida',
                'address': 'Paras Tierea, Sector 137, Noida Expressway',
                'pincode': '201305',
                'area_sqft': 1680,
                'bedrooms': 3,
                'bathrooms': 3,
                'balconies': 3,
                'furnishing': 'fully_furnished',
                'parking': '2_cars',
                'floor_no': '12th of 24',
                'facing': 'East',
                'status': 'available',
                'is_featured': True,
                'description': 'Experience luxury living in this fully furnished 3 BHK home overlooking landscaped gardens. Includes Italian marble flooring, 4 split ACs, king-size beds, 55-inch smart TV, and refrigerator. Club house with pool and gym right downstairs.',
            },
            {
                'title': 'Modern 1 BHK Studio Apartment in Sector 75',
                'property_type': 'flat',
                'bhk': '1_bhk',
                'rent': 18500,
                'security_deposit': 37000,
                'maintenance_charges': 1800,
                'loc_key': 'Sector 75, Noida',
                'address': 'Supertech CapeTown, Sector 75',
                'pincode': '201307',
                'area_sqft': 625,
                'bedrooms': 1,
                'bathrooms': 1,
                'balconies': 1,
                'furnishing': 'fully_furnished',
                'parking': 'two_wheeler',
                'floor_no': '4th of 19',
                'facing': 'North',
                'status': 'available',
                'is_featured': False,
                'description': 'Cozy, hassle-free 1 BHK ready to move in for working executives or couples. Furnished with sofa set, workstation table, wardrobe, geyser, and induction cooktop. 500m to Sector 50 Aqua Line Metro.',
            },
            {
                'title': 'Ultra Premium 4 BHK Penthouse on Golf Course Road',
                'property_type': 'penthouse',
                'bhk': '4_bhk',
                'rent': 115000,
                'security_deposit': 230000,
                'maintenance_charges': 8000,
                'loc_key': 'DLF Phase 5, Gurugram',
                'address': 'The Pinnacle, DLF Phase 5, Golf Course Road',
                'pincode': '122002',
                'area_sqft': 3450,
                'bedrooms': 4,
                'bathrooms': 5,
                'balconies': 4,
                'furnishing': 'fully_furnished',
                'parking': '2_cars',
                'floor_no': '19th of 20',
                'facing': 'North-East',
                'status': 'available',
                'is_featured': True,
                'description': 'Magnificent sky villa offering panoramic vistas of the DLF Golf Course. Comes with bespoke imported furniture, designer modular island kitchen, servant quarters, private jacuzzi, and concierge service.',
            },
            {
                'title': 'Spacious 3 BHK Gated Society Flat in Golf Course Extn',
                'property_type': 'apartment',
                'bhk': '3_bhk',
                'rent': 55000,
                'security_deposit': 110000,
                'maintenance_charges': 4000,
                'loc_key': 'Golf Course Extn, Gurugram',
                'address': 'M3M Merlin, Golf Course Extension Road',
                'pincode': '122018',
                'area_sqft': 1950,
                'bedrooms': 3,
                'bathrooms': 3,
                'balconies': 2,
                'furnishing': 'semi_furnished',
                'parking': '1_car',
                'floor_no': '9th of 22',
                'facing': 'East',
                'status': 'available',
                'is_featured': True,
                'description': 'Contemporary Singapore-style architectural layout featuring huge sundeck balcony, central green view, wooden textures, and high ceiling rooms. Super close to leading multinational offices and Rapid Metro.',
            },
            {
                'title': 'Executive 2 BHK Apartment near Cyber City',
                'property_type': 'flat',
                'bhk': '2_bhk',
                'rent': 38000,
                'security_deposit': 76000,
                'maintenance_charges': 3000,
                'loc_key': 'Cyber City & Sector 24, Gurugram',
                'address': 'Belvedere Park, DLF Phase 2, Near Cyber City',
                'pincode': '122002',
                'area_sqft': 1300,
                'bedrooms': 2,
                'bathrooms': 2,
                'balconies': 2,
                'furnishing': 'semi_furnished',
                'parking': '1_car',
                'floor_no': '6th of 16',
                'facing': 'North',
                'status': 'available',
                'is_featured': False,
                'description': 'Ideal home for corporate executives working in Cyber Hub or DLF Cyber City. Gated complex with high security, lush internal walking tracks, power backup, and swift access to NH-48 highway.',
            },
            {
                'title': 'Chic 2 BHK Tech-Corridor Flat in Whitefield',
                'property_type': 'flat',
                'bhk': '2_bhk',
                'rent': 34000,
                'security_deposit': 100000,
                'maintenance_charges': 2800,
                'loc_key': 'Whitefield, Bengaluru',
                'address': 'Prestige Shantiniketan, Whitefield Main Road',
                'pincode': '560066',
                'area_sqft': 1290,
                'bedrooms': 2,
                'bathrooms': 2,
                'balconies': 2,
                'furnishing': 'semi_furnished',
                'parking': '1_car',
                'floor_no': '8th of 18',
                'facing': 'East',
                'status': 'available',
                'is_featured': True,
                'description': 'Prime residential opportunity in Whitefield township. Close to ITPL, Nexus Shantiniketan Mall, and Kadugodi Tree Park Metro. Includes modular kitchen, wardrobes, geysers, and serene garden orientation.',
            },
            {
                'title': 'Vibrant 3 BHK Family Home in HSR Layout Sector 2',
                'property_type': 'independent_floor',
                'bhk': '3_bhk',
                'rent': 58000,
                'security_deposit': 150000,
                'maintenance_charges': 0,
                'loc_key': 'HSR Layout, Bengaluru',
                'address': '27th Main Road, Sector 2, HSR Layout',
                'pincode': '560102',
                'area_sqft': 1800,
                'bedrooms': 3,
                'bathrooms': 3,
                'balconies': 2,
                'furnishing': 'fully_furnished',
                'parking': '1_car',
                'floor_no': '2nd of 4',
                'facing': 'North',
                'status': 'available',
                'is_featured': True,
                'description': 'Independent builder floor in the heart of HSR Layout. Tree-lined street, close to leading cafes, quick commerce hubs, and Outer Ring Road. Zero maintenance hassle and peaceful residential ambiance.',
            },
            {
                'title': 'Cozy 1 BHK Rental Floor in Koramangala 4th Block',
                'property_type': 'flat',
                'bhk': '1_bhk',
                'rent': 24000,
                'security_deposit': 60000,
                'maintenance_charges': 1200,
                'loc_key': 'Koramangala, Bengaluru',
                'address': 'Near Maharaja Signal, 4th Block Koramangala',
                'pincode': '560034',
                'area_sqft': 650,
                'bedrooms': 1,
                'bathrooms': 1,
                'balconies': 1,
                'furnishing': 'fully_furnished',
                'parking': 'two_wheeler',
                'floor_no': '3rd of 4',
                'facing': 'East',
                'status': 'available',
                'is_featured': False,
                'description': 'Fully furnished boutique 1 BHK flat with high-speed WiFi setup, double bed, smart TV, microwave, and separate dining nook. Perfect for professionals desiring immediate move-in in Koramangala.',
            },
            {
                'title': 'Graceful 3 BHK Independent Builder Floor in GK 2',
                'property_type': 'independent_floor',
                'bhk': '3_bhk',
                'rent': 85000,
                'security_deposit': 170000,
                'maintenance_charges': 0,
                'loc_key': 'Greater Kailash, South Delhi',
                'address': 'E-Block, Greater Kailash II',
                'pincode': '110048',
                'area_sqft': 2200,
                'bedrooms': 3,
                'bathrooms': 3,
                'balconies': 2,
                'furnishing': 'semi_furnished',
                'parking': '2_cars',
                'floor_no': '1st of 3',
                'facing': 'North-East',
                'status': 'available',
                'is_featured': True,
                'description': 'Refined South Delhi living in GK-2. Expansive living-cum-dining room with Italian chandeliers, elevator access directly into apartment foyer, stilt car parking, and strict 24-hour guard gating.',
            },
            {
                'title': 'Elegant 2 BHK Apartment near Saket Metro',
                'property_type': 'flat',
                'bhk': '2_bhk',
                'rent': 35000,
                'security_deposit': 70000,
                'maintenance_charges': 2000,
                'loc_key': 'Saket, South Delhi',
                'address': 'Near Saket Sports Complex, J-Block',
                'pincode': '110017',
                'area_sqft': 1100,
                'bedrooms': 2,
                'bathrooms': 2,
                'balconies': 1,
                'furnishing': 'semi_furnished',
                'parking': '1_car',
                'floor_no': '2nd of 4',
                'facing': 'South',
                'status': 'available',
                'is_featured': False,
                'description': 'Charming 2-bedroom home adjacent to Saket Sports Complex and 5 minutes from Yellow Line Metro. Bright airy rooms, dedicated utility area, and verified landlord.',
            },
            {
                'title': 'Serene 3 BHK Sports City Apartment in Sector 150',
                'property_type': 'apartment',
                'bhk': '3_bhk',
                'rent': 36000,
                'security_deposit': 72000,
                'maintenance_charges': 3200,
                'loc_key': 'Sector 150, Noida',
                'address': 'ATS Pristine, Sector 150, Expressway',
                'pincode': '201310',
                'area_sqft': 1750,
                'bedrooms': 3,
                'bathrooms': 3,
                'balconies': 3,
                'furnishing': 'semi_furnished',
                'parking': '1_car',
                'floor_no': '14th of 26',
                'facing': 'North-East',
                'status': 'available',
                'is_featured': False,
                'description': 'Eco-friendly residence nestled in Noida low-density sports corridor. 80% open green landscapes, cricket pitch, tennis courts, temperature-controlled swimming pool, and pristine air quality.',
            },
        ]

        # Palette colors for generating sample property photography
        photo_palettes = [
            ((15, 23, 42), "LIVING ROOM & LOUNGE"),
            ((30, 41, 59), "MASTER BEDROOM SUITE"),
            ((13, 148, 136), "MODULAR KITCHEN"),
            ((14, 116, 144), "BALCONY & GREEN VIEW"),
        ]

        created_properties = []
        for prop_dict in properties_data:
            loc = location_objs.get(prop_dict['loc_key'])
            city = loc.city if loc else 'Noida'
            area = loc.area if loc else 'Sector 62'

            p_obj, created = Property.objects.get_or_create(
                title=prop_dict['title'],
                defaults={
                    'property_type': prop_dict['property_type'],
                    'bhk': prop_dict['bhk'],
                    'rent': prop_dict['rent'],
                    'security_deposit': prop_dict['security_deposit'],
                    'maintenance_charges': prop_dict['maintenance_charges'],
                    'location': loc,
                    'city': city,
                    'area': area,
                    'address': prop_dict['address'],
                    'pincode': prop_dict['pincode'],
                    'area_sqft': prop_dict['area_sqft'],
                    'bedrooms': prop_dict['bedrooms'],
                    'bathrooms': prop_dict['bathrooms'],
                    'balconies': prop_dict['balconies'],
                    'furnishing': prop_dict['furnishing'],
                    'parking': prop_dict['parking'],
                    'floor_no': prop_dict['floor_no'],
                    'facing': prop_dict['facing'],
                    'status': prop_dict['status'],
                    'is_featured': prop_dict['is_featured'],
                    'description': prop_dict['description'],
                    'available_from': date.today() + timedelta(days=random.randint(1, 15)),
                }
            )

            # Attach random 5-7 amenities
            selected_amenities = random.sample(amenity_objs, min(len(amenity_objs), 7))
            p_obj.amenities.set(selected_amenities)

            # Generate and attach 2-3 sample images if none exist
            if p_obj.images.count() == 0:
                for idx, (bg_col, label) in enumerate(photo_palettes[:3]):
                    image_bytes = self.create_sample_image(
                        f"{p_obj.get_bhk_display()} • {label}",
                        bg_color=bg_col
                    )
                    filename = f"property_{p_obj.pk}_img{idx}.jpg"
                    PropertyImage.objects.create(
                        property=p_obj,
                        image=ContentFile(image_bytes, name=filename),
                        alt_text=f"{p_obj.title} - {label}",
                        display_order=idx,
                        is_primary=(idx == 0)
                    )

            created_properties.append(p_obj)

        self.stdout.write(self.style.SUCCESS(f"Seeded {len(created_properties)} Properties with images."))

        # 5. Seed Demonstration Enquiries / Leads for CRM
        lead_samples = [
            {
                'name': 'Vikram Mehra', 'phone': '9811223344', 'email': 'vikram.m@tcs.com',
                'city': 'Noida', 'preferred_area': 'Sector 62', 'bhk': '2 BHK',
                'min_budget': 25000, 'max_budget': 30000, 'source': 'Google',
                'utm_source': 'google', 'utm_medium': 'cpc', 'utm_campaign': 'noida_flats_search',
                'status': 'new', 'admin_remark': 'Lead came via Google Ads. Looking for immediate move-in.'
            },
            {
                'name': 'Pooja Agarwal', 'phone': '9876501234', 'email': 'pooja.agarwal@gmail.com',
                'city': 'Gurugram', 'preferred_area': 'Golf Course Extn', 'bhk': '3 BHK',
                'min_budget': 50000, 'max_budget': 60000, 'source': 'Facebook',
                'utm_source': 'facebook', 'utm_medium': 'cpc', 'utm_campaign': 'gurgaon_luxury_living',
                'status': 'contacted', 'admin_remark': 'Spoke on phone. Prefers gated society with swimming pool. Sending WhatsApp portfolio.'
            },
            {
                'name': 'Aditya Sen', 'phone': '9711445566', 'email': 'aditya.sen@flipkart.com',
                'city': 'Bengaluru', 'preferred_area': 'HSR Layout', 'bhk': '3 BHK',
                'min_budget': 55000, 'max_budget': 65000, 'source': 'Instagram',
                'utm_source': 'instagram', 'utm_medium': 'influencer', 'utm_campaign': 'bangalore_rentals',
                'status': 'visit_scheduled', 'admin_remark': 'Visit scheduled for Saturday 11 AM.'
            },
            {
                'name': 'Rohan & Neha Kapoor', 'phone': '9955887766', 'email': 'neha.kapoor@deloitte.com',
                'city': 'South Delhi', 'preferred_area': 'Greater Kailash', 'bhk': '3 BHK',
                'min_budget': 80000, 'max_budget': 90000, 'source': 'Direct',
                'utm_source': '', 'utm_medium': '', 'utm_campaign': '',
                'status': 'converted', 'admin_remark': 'Deal closed! Token received for GK-2 builder floor.'
            },
            {
                'name': 'Ankit Verma', 'phone': '9822334455', 'email': 'ankit.v@infosys.com',
                'city': 'Bengaluru', 'preferred_area': 'Whitefield', 'bhk': '2 BHK',
                'min_budget': 30000, 'max_budget': 35000, 'source': 'WhatsApp',
                'utm_source': 'whatsapp', 'utm_medium': 'referral', 'utm_campaign': '',
                'status': 'interested', 'admin_remark': 'Sent 3 property links over WhatsApp. Client reviewing.'
            },
        ]

        for lead_dict in lead_samples:
            target_prop = created_properties[0] if lead_dict['status'] == 'converted' else None
            Enquiry.objects.get_or_create(
                phone=lead_dict['phone'],
                city=lead_dict['city'],
                defaults={
                    'name': lead_dict['name'],
                    'email': lead_dict['email'],
                    'property': target_prop,
                    'bhk': lead_dict['bhk'],
                    'preferred_area': lead_dict['preferred_area'],
                    'min_budget': lead_dict['min_budget'],
                    'max_budget': lead_dict['max_budget'],
                    'source': lead_dict['source'],
                    'utm_source': lead_dict['utm_source'],
                    'utm_medium': lead_dict['utm_medium'],
                    'utm_campaign': lead_dict['utm_campaign'],
                    'status': lead_dict['status'],
                    'admin_remark': lead_dict['admin_remark'],
                    'assigned_to': admin_user,
                    'message': 'Looking for a peaceful, well-maintained society with parking and power backup.',
                }
            )

        self.stdout.write(self.style.SUCCESS("Seeded sample leads and CRM entries."))

        # 6. Seed Sample Banner Advertisement
        if Advertisement.objects.count() == 0 and len(created_properties) > 0:
            ad_banner_bytes = self.create_sample_image(
                "HOT DEAL: Verified 3 BHK Flats with Zero Brokerage",
                bg_color=(15, 118, 110),
                width=1100, height=250
            )
            Advertisement.objects.create(
                title="Special Monsoon Rental Offer - Zero Brokerage",
                image=ContentFile(ad_banner_bytes, name='ad_banner_monsoon.jpg'),
                description="Explore handpicked verified homes across Noida and Gurugram with direct landlord coordination.",
                property=created_properties[0],
                placement='homepage_banner',
                start_date=date.today() - timedelta(days=5),
                end_date=date.today() + timedelta(days=45),
                is_active=True
            )
            self.stdout.write(self.style.SUCCESS("Seeded sample active Advertisement banner."))

        self.stdout.write(self.style.SUCCESS("All Rentorra demo data seeded successfully!"))
