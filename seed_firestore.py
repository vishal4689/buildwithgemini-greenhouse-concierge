"""Seed Firestore with initial plants catalog."""
from google.cloud import firestore

PROJECT_ID = "qwiklabs-gcp-04-1c46a551f47b"
COLLECTION_NAME = "plants"

SAMPLE_PLANTS = [
    {
        "id": "monstera-deliciosa",
        "name": "Monstera Deliciosa",
        "scientific_name": "Monstera deliciosa",
        "care_level": "Easy",
        "light_requirement": "Bright indirect light",
        "watering_frequency_days": 7,
        "humidity_preference": "Medium to high",
        "pet_safe": False,
        "price_usd": 34.99,
        "stock": 12,
        "description": "Popular houseplant known for its large, glossy leaves with distinctive natural holes (fenestrations).",
    },
    {
        "id": "snake-plant",
        "name": "Snake Plant (Sansevieria)",
        "scientific_name": "Dracaena trifasciata",
        "care_level": "Very Easy",
        "light_requirement": "Low to bright indirect light",
        "watering_frequency_days": 14,
        "humidity_preference": "Low to medium",
        "pet_safe": False,
        "price_usd": 24.99,
        "stock": 25,
        "description": "Hardy, drought-tolerant succulent with upright sword-like foliage, excellent for beginners and low-light corners.",
    },
    {
        "id": "fiddle-leaf-fig",
        "name": "Fiddle Leaf Fig",
        "scientific_name": "Ficus lyrata",
        "care_level": "Moderate",
        "light_requirement": "Bright consistent indirect light",
        "watering_frequency_days": 8,
        "humidity_preference": "High",
        "pet_safe": False,
        "price_usd": 49.99,
        "stock": 8,
        "description": "Striking indoor tree with violin-shaped foliage that loves stable conditions and ample sunlight.",
    },
    {
        "id": "spider-plant",
        "name": "Spider Plant",
        "scientific_name": "Chlorophytum comosum",
        "care_level": "Easy",
        "light_requirement": "Medium to bright indirect light",
        "watering_frequency_days": 6,
        "humidity_preference": "Medium",
        "pet_safe": True,
        "price_usd": 18.50,
        "stock": 18,
        "description": "Pet-friendly and adaptable plant featuring cascading variegated arching ribbons that produces baby plantlets.",
    },
    {
        "id": "peace-lily",
        "name": "Peace Lily",
        "scientific_name": "Spathiphyllum",
        "care_level": "Easy",
        "light_requirement": "Low to medium indirect light",
        "watering_frequency_days": 5,
        "humidity_preference": "High",
        "pet_safe": False,
        "price_usd": 22.00,
        "stock": 14,
        "description": "Lush tropical perennial with deep green leaves and white blooms that droops expressively when thirsty.",
    },
]


def seed():
    db = firestore.Client(project=PROJECT_ID)
    batch = db.batch()
    col_ref = db.collection(COLLECTION_NAME)

    print(f"Seeding '{COLLECTION_NAME}' into project '{PROJECT_ID}'...")
    for plant in SAMPLE_PLANTS:
        doc_ref = col_ref.document(plant["id"])
        batch.set(doc_ref, plant)

    batch.commit()
    print(f"Successfully seeded {len(SAMPLE_PLANTS)} plants into Firestore collection '{COLLECTION_NAME}'.")


if __name__ == "__main__":
    seed()
