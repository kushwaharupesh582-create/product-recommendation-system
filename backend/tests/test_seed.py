import unittest

from sqlalchemy import create_engine, func, select
from sqlalchemy.orm import Session

from app.database import Base
from app.models import Customer, Product, Purchase
from app.seed import PRODUCTS, seed_database


class SeedDatabaseTests(unittest.TestCase):
    def test_seed_creates_catalog_and_purchase_history_once(self):
        engine = create_engine("sqlite://")
        Base.metadata.create_all(engine)

        try:
            with Session(engine) as session:
                seed_database(session)

                self.assertEqual(
                    session.scalar(select(func.count()).select_from(Product)),
                    len(PRODUCTS),
                )
                self.assertEqual(session.scalar(select(func.count()).select_from(Customer)), 4)
                self.assertEqual(session.scalar(select(func.count()).select_from(Purchase)), 20)
                self.assertEqual(
                    session.scalar(select(Purchase).limit(1)).product.name,
                    "Wireless Noise-Canceling Headphones",
                )

                seed_database(session)
                self.assertEqual(
                    session.scalar(select(func.count()).select_from(Product)),
                    len(PRODUCTS),
                )
                self.assertEqual(session.scalar(select(func.count()).select_from(Purchase)), 20)
        finally:
            engine.dispose()

    def test_seed_adds_catalog_products_to_an_existing_database(self):
        engine = create_engine("sqlite://")
        Base.metadata.create_all(engine)

        try:
            with Session(engine) as session:
                session.add(
                    Product(
                        name=PRODUCTS[0][0],
                        category=PRODUCTS[0][1],
                        description=PRODUCTS[0][2],
                        price=PRODUCTS[0][3],
                        image_url=PRODUCTS[0][4],
                        tags=PRODUCTS[0][5],
                    )
                )
                session.commit()

                seed_database(session)

                self.assertEqual(
                    session.scalar(select(func.count()).select_from(Product)),
                    len(PRODUCTS),
                )
                self.assertEqual(
                    session.scalar(select(func.count()).select_from(Purchase)), 20
                )
        finally:
            engine.dispose()


if __name__ == "__main__":
    unittest.main()
