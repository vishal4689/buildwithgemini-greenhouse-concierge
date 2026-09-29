# ruff: noqa
# Copyright 2026 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     https://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import datetime
from typing import Any, Dict, List, Optional
from zoneinfo import ZoneInfo

from google.adk.agents import Agent
from google.adk.apps import App
from google.adk.models import Gemini
from google.cloud import firestore
from google.genai import types

MODEL = "gemini-3.6-flash"

# Hardcode project ID to prevent Agent Platform returning numeric project numbers
FIRESTORE_PROJECT_ID = "qwiklabs-gcp-04-1c46a551f47b"
PLANTS_COLLECTION = "plants"


def get_firestore_client() -> firestore.Client:
    """Returns a Firestore client configured with the hardcoded project ID."""
    return firestore.Client(project=FIRESTORE_PROJECT_ID)


def list_plants(care_level: Optional[str] = None, pet_safe_only: Optional[bool] = None) -> List[Dict[str, Any]]:
    """Lists houseplants available in the greenhouse catalog with optional filters.

    Args:
        care_level: Optional filter for care difficulty, e.g., 'Easy', 'Very Easy', 'Moderate'.
        pet_safe_only: If True, returns only pet-safe plants.

    Returns:
        A list of plant records with details like care level, light, watering, and price.
    """
    db = get_firestore_client()
    query = db.collection(PLANTS_COLLECTION)

    if pet_safe_only is True:
        query = query.where("pet_safe", "==", True)

    results = []
    for doc in query.stream():
        data = doc.to_dict()
        data["id"] = doc.id
        if care_level:
            if data.get("care_level", "").lower() != care_level.lower():
                continue
        results.append(data)

    return results


def get_plant_details(plant_id: str) -> Dict[str, Any]:
    """Retrieves full information for a specific plant by its identifier or name slug.

    Args:
        plant_id: The document ID of the plant (e.g., 'monstera-deliciosa', 'snake-plant', 'spider-plant').

    Returns:
        A dictionary with the plant's details, or an error dictionary if not found.
    """
    db = get_firestore_client()
    doc_ref = db.collection(PLANTS_COLLECTION).document(plant_id.strip().lower())
    doc = doc_ref.get()

    if not doc.exists:
        # Fallback search by name if exact ID didn't match
        normalized = plant_id.strip().lower()
        for d in db.collection(PLANTS_COLLECTION).stream():
            p_data = d.to_dict()
            if normalized in p_data.get("name", "").lower() or normalized in d.id.lower():
                p_data["id"] = d.id
                return p_data
        return {"error": f"Plant '{plant_id}' not found in the greenhouse catalog."}

    data = doc.to_dict()
    data["id"] = doc.id
    return data


def add_plant(
    plant_id: str,
    name: str,
    care_level: str,
    light_requirement: str,
    watering_frequency_days: int,
    price_usd: float,
    description: str,
    pet_safe: bool = False,
    stock: int = 10,
    scientific_name: str = "",
    humidity_preference: str = "Medium",
) -> Dict[str, Any]:
    """Adds a new plant or updates an existing plant entry in the greenhouse catalog.

    Args:
        plant_id: Unique slug/id for the plant (e.g., 'pothos-golden').
        name: Common name of the plant (e.g., 'Golden Pothos').
        care_level: Care level (e.g., 'Easy', 'Moderate', 'Advanced').
        light_requirement: Lighting requirement (e.g., 'Low to bright indirect light').
        watering_frequency_days: Number of days between watering cycles.
        price_usd: Price in USD.
        description: Short overview or care advice for the plant.
        pet_safe: Whether the plant is non-toxic to pets. Default is False.
        stock: Number of units currently available in inventory. Default is 10.
        scientific_name: Scientific botanical name (optional).
        humidity_preference: Humidity needs (e.g., 'High', 'Medium', 'Low').

    Returns:
        A dictionary confirming the plant record was written to Firestore.
    """
    db = get_firestore_client()
    doc_id = plant_id.strip().lower().replace(" ", "-")
    doc_ref = db.collection(PLANTS_COLLECTION).document(doc_id)

    plant_data = {
        "id": doc_id,
        "name": name,
        "scientific_name": scientific_name,
        "care_level": care_level,
        "light_requirement": light_requirement,
        "watering_frequency_days": watering_frequency_days,
        "humidity_preference": humidity_preference,
        "pet_safe": pet_safe,
        "price_usd": float(price_usd),
        "stock": int(stock),
        "description": description,
        "updated_at": datetime.datetime.now(ZoneInfo("UTC")).isoformat(),
    }

    doc_ref.set(plant_data)
    return {"status": "success", "message": f"Plant '{name}' added to greenhouse catalog.", "plant": plant_data}


def update_plant_stock(plant_id: str, new_stock: int) -> Dict[str, Any]:
    """Updates inventory stock count for a plant in the catalog.

    Args:
        plant_id: Unique ID of the plant.
        new_stock: The updated quantity of stock available.

    Returns:
        Status dictionary with update details.
    """
    db = get_firestore_client()
    doc_id = plant_id.strip().lower()
    doc_ref = db.collection(PLANTS_COLLECTION).document(doc_id)
    doc = doc_ref.get()

    if not doc.exists:
        return {"error": f"Plant with id '{plant_id}' does not exist."}

    doc_ref.update({"stock": int(new_stock)})
    return {"status": "success", "plant_id": doc_id, "updated_stock": int(new_stock)}


root_agent = Agent(
    name="root_agent",
    model=Gemini(
        model=MODEL,
        retry_options=types.HttpRetryOptions(attempts=3),
    ),
    instruction="""You are Greenhouse Concierge, an expert houseplant and greenhouse assistant.
You help plant enthusiasts and indoor gardeners discover plants, understand their care requirements,
and manage the plant catalog. Always provide helpful, encouraging advice and use the available tools
to query or update the Firestore greenhouse catalog.""",
    tools=[list_plants, get_plant_details, add_plant, update_plant_stock],
)

app = App(
    root_agent=root_agent,
    name="app",
)
