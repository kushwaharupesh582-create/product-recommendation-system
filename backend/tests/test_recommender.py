import unittest

from sqlalchemy import create_engine
from sqlalchemy.orm import Session

from app.database import Base
from app.models import Customer, Product, Purchase
from app.recommender import recommend_products


class RecommenderTests(unittest.TestCase):
    def setUp(self):
        self.engine = create_engine("sqlite://")
        Base.metadata.create_all(self.engine)
        self.session = Session(self.engine)
        products = [
            Product(
                name="Trail Tent",
                category="Outdoors",
                description="Lightweight camping shelter for hiking trips.",
                price=100,
                image_url="",
                tags=["camping", "hiking"],
            ),
            Product(
                name="Hiking Pack",
                category="Outdoors",
                description="A durable backpack for hiking and camping adventures.",
                price=80,
                image_url="",
                tags=["camping", "hiking", "travel"],
            ),
            Product(
                name="Ceramic Vase",
                category="Home",
                description="Handmade decorative vase for a living room.",
                price=40,
                image_url="",
                tags=["ceramic", "decor"],
            ),
        ]
        customers = [Customer(name="Alex"), Customer(name="Sam")]
        self.session.add_all([*products, *customers])
        self.session.flush()
        self.session.add_all(
            [
                Purchase(customer_id=customers[0].id, product_id=products[0].id),
                Purchase(customer_id=customers[0].id, product_id=products[2].id),
                Purchase(customer_id=customers[1].id, product_id=products[0].id),
                Purchase(customer_id=customers[1].id, product_id=products[1].id),
            ]
        )
        self.session.commit()

    def tearDown(self):
        self.session.close()
        self.engine.dispose()

    def test_recommendations_exclude_purchases_and_return_ranked_products(self):
        recommendations = recommend_products(self.session, customer_id=1)

        self.assertTrue(recommendations)
        self.assertEqual([result["product"].id for result in recommendations], [2])
        self.assertGreater(recommendations[0]["score"], 0)

    def test_unknown_customer_gets_popular_catalog_products(self):
        recommendations = recommend_products(self.session, customer_id=999)

        self.assertTrue(recommendations)
        self.assertEqual(recommendations[0]["product"].id, 1)


if __name__ == "__main__":
    unittest.main()
