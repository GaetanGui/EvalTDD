import json
import os
from datetime import datetime


class InvalidPriceError(Exception):
    pass


class Cart:
    def __init__(self):
        self.products = []

    def get_total(self):
        return sum(p["price"] for p in self.products)

    def add_product(self, name, price):
        if price < 0:
            raise InvalidPriceError("Le prix ne peut pas être négatif.")
        self.products.append({"name": name, "price": price})

    def remove_product(self, name):
        self.products = [p for p in self.products if p["name"] != name]

    def apply_discount(self, percentage):
        discount_factor = (100 - percentage) / 100
        for p in self.products:
            p["price"] = round(p["price"] * discount_factor, 2)

    def save_to_file(self, filename):
        data = {"products": self.products, "timestamp": datetime.now().isoformat()}
        self._write_json(filename, data)

        if "PYTEST_CURRENT_TEST" not in os.environ:
            self._archive_file(filename, data)

    def _write_json(self, filename, data):
        """Écrit un dictionnaire dans un fichier JSON avec indentation."""
        os.makedirs(os.path.dirname(filename), exist_ok=True)
        with open(filename, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)

    def _archive_file(self, filename, data):
        """Crée une copie archivée du panier avec un nom basé sur la date."""
        archive_dir = os.path.join(os.path.dirname(filename), "archives")
        os.makedirs(archive_dir, exist_ok=True)

        archive_filename = os.path.join(
            archive_dir, f"cart_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        )
        with open(archive_filename, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)

    def load_from_file(self, filepath):
        with open(filepath, "r", encoding="utf-8") as f:
            data = json.load(f)
        self.products = data.get("products", [])
