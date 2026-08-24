import os
import sys
from datetime import datetime, timedelta
import uuid
import sqlite3

# Add the backend/ directory to Python path
sys.path.append(os.path.abspath(os.path.dirname(__file__)))

from app.core.database import init_db, get_db_connection

def seed_database():
    print("Initialising database tables via sqlite3...")
    init_db()
    
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        # Clear existing data to allow fresh re-seeding with complete combination metrics
        print("Clearing old tables for fresh re-seeding...")
        cursor.execute("DELETE FROM daily_prices")
        cursor.execute("DELETE FROM commodities")
        cursor.execute("DELETE FROM mandis")
        cursor.execute("DELETE FROM buyers")
        cursor.execute("DELETE FROM dealers")
        cursor.execute("DELETE FROM users")
        conn.commit()
            
        print("Seeding Mandis...")
        mandis_data = [
            (str(uuid.uuid4()), "Karnataka", "Shivamogga", "Shimoga APMC", "KN-SHM-01", 13.9299, 75.5681),
            (str(uuid.uuid4()), "Karnataka", "Davanagere", "Davanagere APMC", "KN-DVG-02", 14.4644, 75.9218),
            (str(uuid.uuid4()), "Karnataka", "Bengaluru", "Yeshwanthpur APMC", "KN-BLR-03", 13.0279, 77.5409),
            (str(uuid.uuid4()), "Madhya Pradesh", "Indore", "Indore APMC (Choithram)", "MP-IND-01", 22.7196, 75.8577),
            (str(uuid.uuid4()), "Madhya Pradesh", "Ujjain", "Ujjain APMC", "MP-UJN-02", 23.1760, 75.7885),
            (str(uuid.uuid4()), "Maharashtra", "Nashik", "Lasalgaon APMC", "MH-NSK-01", 20.1444, 74.2250),
            (str(uuid.uuid4()), "Maharashtra", "Pune", "Pune APMC (Gultekdi)", "MH-PUN-02", 18.5204, 73.8567)
        ]
        
        cursor.executemany("""
        INSERT INTO mandis (id, state, district, mandi_name, apmc_code, latitude, longitude)
        VALUES (?, ?, ?, ?, ?, ?, ?)
        """, mandis_data)
        
        print("Seeding Commodities...")
        commodities_data = [
            (str(uuid.uuid4()), "Maize", '{"en": "Maize", "hi": "मक्का", "kn": "ಮೆಕ್ಕೆಜೋಳ"}', "Cereal"),
            (str(uuid.uuid4()), "Wheat", '{"en": "Wheat", "hi": "गेहूं", "kn": "ಗೋಧಿ"}', "Cereal"),
            (str(uuid.uuid4()), "Paddy (Rice)", '{"en": "Paddy", "hi": "धान", "kn": "ಭತ್ತ"}', "Cereal"),
            (str(uuid.uuid4()), "Soyabean", '{"en": "Soyabean", "hi": "सोयाबीन", "kn": "ಸೋಯಾಬೀನ್"}', "Oilseed"),
            (str(uuid.uuid4()), "Onion", '{"en": "Onion", "hi": "प्याज", "kn": "ಈರುಳ್ಳಿ"}', "Vegetable"),
            (str(uuid.uuid4()), "Tomato", '{"en": "Tomato", "hi": "टमाटर", "kn": "ಟೊಮೆಟೊ"}', "Vegetable"),
            (str(uuid.uuid4()), "Toor Dal", '{"en": "Toor Dal", "hi": "तुअर दाल", "kn": "ತೊಗರಿ ಬೇಳೆ"}', "Pulses"),
            (str(uuid.uuid4()), "Cotton", '{"en": "Cotton", "hi": "कपास", "kn": "ಹತ್ತಿ"}', "Fiber"),
            (str(uuid.uuid4()), "Gram (Chana)", '{"en": "Chana", "hi": "चना", "kn": "ಕಡಲೆ"}', "Pulses")
        ]
        
        cursor.executemany("""
        INSERT INTO commodities (id, commodity_name, local_name, category)
        VALUES (?, ?, ?, ?)
        """, commodities_data)
        
        conn.commit() # Save so we can query them back
        
        # Load mandis and commodities maps to link prices
        cursor.execute("SELECT id, mandi_name FROM mandis")
        mandi_map = {row["mandi_name"]: row["id"] for row in cursor.fetchall()}
        
        cursor.execute("SELECT id, commodity_name FROM commodities")
        commodity_map = {row["commodity_name"]: row["id"] for row in cursor.fetchall()}
        
        print("Seeding 7-day Daily Prices for ALL combinations...")
        today = datetime.now().date()
        
        base_commodity_prices = {
            "Maize": 2200,
            "Wheat": 2500,
            "Paddy (Rice)": 2100,
            "Soyabean": 4500,
            "Onion": 1800,
            "Tomato": 2000,
            "Toor Dal": 7500,
            "Cotton": 6800,
            "Gram (Chana)": 5200
        }
        
        prices_data = []
        for mandi_name, mandi_id in mandi_map.items():
            for comm_name, comm_id in commodity_map.items():
                base_price = base_commodity_prices.get(comm_name, 2000)
                # Create a slight variance between mandis
                mandi_offset = (len(mandi_name) * 13) % 160 - 80  # Varies between -80 and +80
                base_modal = base_price + mandi_offset
                
                # 7-day trend offsets
                trend_offsets = [-70, -50, -40, -25, -15, -5, 0]
                
                for idx in range(7):
                    price_date = today - timedelta(days=(6 - idx))
                    diff = trend_offsets[idx]
                    modal = base_modal + diff
                    min_p = int(modal * 0.94)
                    max_p = int(modal * 1.06)
                    
                    prices_data.append((
                        str(uuid.uuid4()),
                        mandi_id,
                        comm_id,
                        price_date.isoformat(),
                        min_p,
                        modal,
                        max_p,
                        "AGMARKNET"
                    ))
                
        cursor.executemany("""
        INSERT INTO daily_prices (id, mandi_id, commodity_id, date, min_price, modal_price, max_price, source)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, prices_data)
        
        print("Seeding Buyers (Marketplace)...")
        # Add buyers for multiple crop categories
        buyers_data = [
            (str(uuid.uuid4()), "Karnataka Agri Exports Ltd", "29AAAAA1111A1Z1", "Shivamogga", "Maize", "+919876543210", 1, 4.7),
            (str(uuid.uuid4()), "Shimoga Grain Processors", "29BBBBB2222B2Z2", "Shivamogga", "Maize", "+919876543211", 1, 4.2),
            (str(uuid.uuid4()), "Bengaluru Food Wholesalers", "29BFLB2222B2Z2", "Bengaluru", "Wheat", "+919876543233", 1, 4.6),
            (str(uuid.uuid4()), "Karnataka Rice Mills", "29KRM2222B2Z2", "Bengaluru", "Paddy (Rice)", "+919876543234", 1, 4.5),
            (str(uuid.uuid4()), "Davanagere Poultry Feeds", "29CCCCC3333C3Z3", "Davanagere", "Maize", "+919876543212", 1, 4.5),
            (str(uuid.uuid4()), "Indore Flour Mills Co.", "23DDDDD4444D4Z4", "Indore", "Wheat", "+919876543213", 1, 4.8),
            (str(uuid.uuid4()), "Ujjain Soya Industries", "23EEEEE5555E5Z5", "Ujjain", "Soyabean", "+919876543214", 1, 4.6),
            (str(uuid.uuid4()), "Nashik Onion Exporters", "27FFFFF6666F6Z6", "Nashik", "Onion", "+919876543215", 1, 4.4)
        ]
        
        cursor.executemany("""
        INSERT INTO buyers (id, company, gst_number, district, commodity, phone, verified, rating)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, buyers_data)
        
        print("Seeding Fertilizer & Input Dealers...")
        dealers_data = [
            (str(uuid.uuid4()), "Sri Manjunatha Fertilizer Agencies", 1, 1, 1, "Shivamogga", 1),
            (str(uuid.uuid4()), "Shimoga Krishi Kendra", 1, 1, 0, "Shivamogga", 1),
            (str(uuid.uuid4()), "Davanagere Seed & Fertilizer Depot", 1, 1, 1, "Davanagere", 1),
            (str(uuid.uuid4()), "Indore Krishi Vikas Seva", 1, 1, 1, "Indore", 1),
            (str(uuid.uuid4()), "Ujjain Kisan Bazaar", 1, 0, 1, "Ujjain", 1),
            (str(uuid.uuid4()), "Lasalgaon Seed House", 0, 1, 1, "Lasalgaon", 1),
            (str(uuid.uuid4()), "Bengaluru Seed Corp", 1, 1, 1, "Bengaluru", 1)
        ]
        
        cursor.executemany("""
        INSERT INTO dealers (id, shop_name, fertilizer, seed, pesticide, location, verified)
        VALUES (?, ?, ?, ?, ?, ?, ?)
        """, dealers_data)
        
        conn.commit()
        print("Database seeded successfully with sqlite3!")
        
    except Exception as e:
        conn.rollback()
        print(f"Error seeding database: {e}")
        raise
    finally:
        conn.close()

if __name__ == "__main__":
    seed_database()
