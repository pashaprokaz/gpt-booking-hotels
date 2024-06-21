from copy import copy

from components.data_loaders.base import BaseDataLoader


class MockDataLoader(BaseDataLoader):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.data = {
            "hotels": [
                {
                    "id": 1,
                    "name": "Hotel A",
                    "location": "Praha",
                    "rating": 4.5,
                    "price": 200,
                    "class": 8.5,
                    "address": "Address A",
                },
                {
                    "id": 2,
                    "name": "Hotel B",
                    "location": "Praha",
                    "rating": 4.0,
                    "price": 150,
                    "class": 6.0,
                    "address": "Address B",
                },
                {
                    "id": 3,
                    "name": "Hotel C",
                    "location": "Praha",
                    "rating": 3.5,
                    "price": 100,
                    "class": 4.0,
                    "address": "Address C",
                },
            ]
        }

    def load(self):
        return self.data

    def load_with_filters(
        self,
        location,
        checkin_date,
        checkout_date,
        order_by="popularity",
        adults_number=1,
        children_number=0,
        min_rating=None,
        min_price=None,
        max_price=None,
        **kwargs,
    ):
        filtered_data = []

        for hotel in self.data["hotels"]:
            copied_hotel = copy(hotel)
            copied_hotel["location"] = location
            filtered_data.append(copied_hotel)

        return filtered_data
