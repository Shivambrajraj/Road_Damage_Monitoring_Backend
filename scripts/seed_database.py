# scripts/seed_database.py
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.core.database import SessionLocal
from app.models.report import Report
from app.models.damage import Damage

def seed_data():
    db = SessionLocal()
    try:
        print("Wiping previous report data caches...")
        db.query(Damage).delete()
        db.query(Report).delete()
        db.commit()

        print("Injecting clean development datasets...")

        # Mock Sample 1: Severe Pothole Bundle
        report_1 = Report(
            image_path="app/storage/uploads/original/sample_pothole.jpg",
            damage_category="Pothole",
            severity_level="High",
            latitude=40.7128,
            longitude=-74.0060
        )
        db.add(report_1)
        db.commit()
        db.refresh(report_1)

        damage_1 = Damage(report_id=report_1.id, category="pothole", confidence=0.92)
        damage_2 = Damage(report_id=report_1.id, category="pothole", confidence=0.88)
        db.add_all([damage_1, damage_2])

        # Mock Sample 2: Surface Cracking
        report_2 = Report(
            image_path="app/storage/uploads/original/sample_crack.jpg",
            damage_category="Crack",
            severity_level="Medium",
            latitude=40.7250,
            longitude=-74.0100
        )
        db.add(report_2)
        db.commit()
        db.refresh(report_2)

        damage_3 = Damage(report_id=report_2.id, category="longitudinal crack", confidence=0.76)
        db.add(damage_3)

        db.commit()
        print("Database population complete! Initial mock records deployed successfully.")

    except Exception as e:
        db.rollback()
        print(f"Seeding process encountered an anomaly: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    seed_data()