from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models import Customer, Product, Purchase


PRODUCTS = [
    ("Everyday Canvas Backpack", "Accessories", "Durable canvas backpack with padded laptop sleeve and water bottle pockets.", 58, "https://images.unsplash.com/photo-1553062407-98eeb64c6a62?w=800", ["travel", "work", "canvas"]),
    ("Wireless Noise-Canceling Headphones", "Electronics", "Over-ear Bluetooth headphones with active noise cancellation and long battery life.", 149, "https://images.unsplash.com/photo-1505740420928-5e560c06d30e?w=800", ["audio", "wireless", "travel"]),
    ("Ceramic Pour-Over Coffee Set", "Home", "A handmade ceramic dripper and matching mug for a simple morning coffee ritual.", 42, "https://images.unsplash.com/photo-1495474472287-4d71bcdd2085?w=800", ["coffee", "ceramic", "kitchen"]),
    ("Classic Leather Sneakers", "Fashion", "Minimal low-top leather sneakers with a cushioned sole for everyday wear.", 92, "https://images.unsplash.com/photo-1542291026-7eec264c27ff?w=800", ["shoes", "casual", "leather"]),
    ("Insulated Stainless Bottle", "Outdoors", "Reusable double-wall insulated bottle that keeps drinks cold or hot on the go.", 28, "https://images.unsplash.com/photo-1602143407151-7111542de6e8?w=800", ["outdoors", "hydration", "travel"]),
    ("Compact Mechanical Keyboard", "Electronics", "Compact mechanical keyboard with tactile switches and a clean desktop footprint.", 109, "https://images.unsplash.com/photo-1587829741301-dc798b83add3?w=800", ["work", "desk", "technology"]),
    ("Linen Everyday Shirt", "Fashion", "Breathable relaxed-fit linen shirt designed for warm days and easy layering.", 64, "https://images.unsplash.com/photo-1598033129183-c4f50c736f10?w=800", ["clothing", "linen", "casual"]),
    ("Weighted Wool Throw", "Home", "Soft woven wool throw blanket for a cozy sofa, reading chair, or bedroom.", 118, "https://images.unsplash.com/photo-1600210492486-724fe5c67fb0?w=800", ["home", "comfort", "wool"]),
    ("Everyday Running Shoes", "Outdoors", "Lightweight running shoes with responsive cushioning for daily training.", 115, "https://images.unsplash.com/photo-1542291026-7eec264c27ff?w=800", ["fitness", "shoes", "running"]),
    ("Portable Bluetooth Speaker", "Electronics", "Water-resistant portable speaker with clear sound for home and outdoor listening.", 79, "https://images.unsplash.com/photo-1608043152269-423dbba4e7e1?w=800", ["audio", "wireless", "outdoors"]),
    ("Hardcover Travel Journal", "Books", "Lay-flat notebook with durable cover and numbered pages for notes and trips.", 22, "https://images.unsplash.com/photo-1544947950-fa07a98d237f?w=800", ["writing", "travel", "stationery"]),
    ("Minimal Ceramic Desk Lamp", "Home", "Warm, dimmable desk light with a sculptural ceramic base and linen shade.", 86, "https://images.unsplash.com/photo-1507473885765-e6ed057f782c?w=800", ["home", "desk", "lighting"]),
    ("Polarized Everyday Sunglasses", "Accessories", "Lightweight polarized sunglasses with a versatile frame for daily use.", 54, "https://images.unsplash.com/photo-1511499767150-a48a237f0083?w=800", ["accessories", "travel", "outdoors"]),
    ("Plant-Based Skincare Kit", "Beauty", "Gentle daily cleanser and moisturizer made with plant-based ingredients.", 48, "https://images.unsplash.com/photo-1608248543803-ba4f8c70ae0b?w=800", ["skincare", "wellness", "daily"]),
    ("Insulated Lunch Tote", "Accessories", "Easy-clean insulated lunch bag with room for a meal, snacks, and a drink.", 34, "https://images.unsplash.com/photo-1547592180-85f173990554?w=800", ["food", "work", "travel"]),
    ("Beginner Watercolor Set", "Arts & Crafts", "Portable watercolor palette with brushes and paper for creative practice.", 36, "https://images.unsplash.com/photo-1513364776144-60967b0f800f?w=800", ["art", "creative", "hobby"]),
    ("Smart Fitness Watch", "Electronics", "Track activity, sleep, and workouts with a bright screen and week-long battery.", 179, "https://images.unsplash.com/photo-1523275335684-37898b6baf30?w=800", ["fitness", "technology", "wellness"]),
    ("Bamboo Cutting Board", "Home", "Knife-friendly bamboo cutting board with a juice groove and easy-grip handles.", 32, "https://images.unsplash.com/photo-1593618998160-e34014e67546?w=800", ["kitchen", "cooking", "bamboo"]),
    ("Everyday Gold Hoop Earrings", "Accessories", "Lightweight polished gold hoops that add an easy finishing touch to everyday outfits.", 38, "https://images.unsplash.com/photo-1535632066927-ab7c9ab60908?w=800", ["jewelry", "gold", "everyday"]),
    ("Soft Knit Cardigan", "Fashion", "A relaxed, midweight knit cardigan made for comfortable layering through the seasons.", 76, "https://images.unsplash.com/photo-1576566588028-4147f3842f27?w=800", ["clothing", "knitwear", "layering"]),
    ("Aroma Essential Oil Diffuser", "Home", "Quiet ultrasonic diffuser with a soft ambient glow for a calm home routine.", 52, "https://images.unsplash.com/photo-1608571423902-eed4a5ad8108?w=800", ["wellness", "home", "aromatherapy"]),
    ("Pocket Instant Camera", "Electronics", "A compact instant camera for turning favorite moments into prints to keep and share.", 89, "https://images.unsplash.com/photo-1516035069371-29a1b244cc32?w=800", ["photography", "creative", "travel"]),
    ("Weekend Duffel Bag", "Accessories", "Roomy recycled-fabric weekender with a separate shoe pocket and carry-on-friendly shape.", 94, "https://images.unsplash.com/photo-1553062407-98eeb64c6a62?w=800", ["travel", "bags", "weekend"]),
    ("Matcha Starter Set", "Home", "Ceramic bowl, bamboo whisk, and scoop for preparing a smooth cup of matcha at home.", 46, "https://images.unsplash.com/photo-1515823064-d6e0c04616a7?w=800", ["tea", "ceramic", "kitchen"]),
    ("Citrus Hand Cream Trio", "Beauty", "Three quick-absorbing hand creams with fresh citrus notes for desk, bag, and bedside.", 24, "https://images.unsplash.com/photo-1608248543803-ba4f8c70ae0b?w=800", ["skincare", "hand care", "gift"]),
    ("Yoga Mat with Carry Strap", "Outdoors", "Supportive non-slip exercise mat with a simple strap for studio and home workouts.", 49, "https://images.unsplash.com/photo-1506629905607-d9c36e2f9f19?w=800", ["fitness", "yoga", "wellness"]),
    ("Hardcover Design Inspiration Book", "Books", "A photo-rich collection of thoughtful interiors, color ideas, and creative spaces.", 39, "https://images.unsplash.com/photo-1544947950-fa07a98d237f?w=800", ["books", "design", "creative"]),
    ("Hand-Poured Soy Candle", "Home", "A clean-burning soy candle with warm cedar and fig notes in a reusable glass vessel.", 31, "https://images.unsplash.com/photo-1603006905003-be475563bc59?w=800", ["home", "scent", "relaxation"]),
    ("Insulated Travel Mug", "Home", "Leak-resistant stainless travel mug with a comfortable grip and easy-clean lid.", 33, "https://images.unsplash.com/photo-1517256064527-09c73fc73e38?w=800", ["coffee", "travel", "hydration"]),
    ("Everyday Crossbody Bag", "Accessories", "Hands-free crossbody bag with adjustable straps and pockets for everyday essentials.", 68, "https://images.unsplash.com/photo-1584917865442-de89df76afd3?w=800", ["bags", "everyday", "travel"]),
    ("Classic Reading Glasses", "Accessories", "Lightweight rounded frames with clear lenses and a slim protective sleeve.", 44, "https://images.unsplash.com/photo-1511499767150-a48a237f0083?w=800", ["accessories", "reading", "style"]),
    ("Waffle Cotton Bath Towel Set", "Home", "Soft quick-drying cotton towels with a textured waffle weave and hanging loops.", 62, "https://images.unsplash.com/photo-1600369671236-e74521d4b6ad?w=800", ["bath", "cotton", "home"]),
    ("Wireless Charging Stand", "Electronics", "A compact angled charging stand for a tidy desk or bedside table.", 41, "https://images.unsplash.com/photo-1586953208448-b95a79798f07?w=800", ["technology", "desk", "charging"]),
    ("Pocket Sketchbook Set", "Arts & Crafts", "Two portable blank sketchbooks with heavyweight paper for drawing on the go.", 19, "https://images.unsplash.com/photo-1513364776144-60967b0f800f?w=800", ["art", "drawing", "creative"]),
    ("Trail-Ready Hiking Socks", "Outdoors", "Cushioned merino-blend socks designed to keep feet comfortable on long walks.", 26, "https://images.unsplash.com/photo-1586350977771-b3b0abd50c82?w=800", ["hiking", "outdoors", "clothing"]),
    ("Adjustable Laptop Stand", "Electronics", "Foldable aluminum laptop riser that improves screen height and desk ergonomics.", 57, "https://images.unsplash.com/photo-1527864550417-7fd91fc51a46?w=800", ["work", "desk", "technology"]),
    ("Everyday Ceramic Planter", "Home", "A small glazed ceramic planter with a drainage tray for favorite indoor plants.", 29, "https://images.unsplash.com/photo-1485955900006-10f4d324d411?w=800", ["plants", "ceramic", "home"]),
    ("Reusable Produce Bag Set", "Outdoors", "Washable mesh bags in assorted sizes for market trips and kitchen storage.", 17, "https://images.unsplash.com/photo-1542838132-92c53300491e?w=800", ["sustainable", "kitchen", "shopping"]),
    ("Travel Toiletry Organizer", "Accessories", "Water-resistant hanging organizer with clear pockets for easy packing and unpacking.", 37, "https://images.unsplash.com/photo-1553531384-411a247ecd73?w=800", ["travel", "organizer", "bags"]),
    ("Natural Lip Balm Set", "Beauty", "A set of nourishing everyday lip balms made with simple, plant-based ingredients.", 16, "https://images.unsplash.com/photo-1608248543803-ba4f8c70ae0b?w=800", ["beauty", "skincare", "daily"]),
    ("Pour-Over Coffee Grinder", "Home", "Adjustable burr grinder for fresh coffee at home, with a compact countertop design.", 73, "https://images.unsplash.com/photo-1517668808822-9ebb02f2a0e6?w=800", ["coffee", "kitchen", "morning"]),
    ("Minimal Silver Chain Necklace", "Accessories", "A delicate sterling-silver chain designed to wear alone or layer with a favorite pendant.", 59, "https://images.unsplash.com/photo-1611591437281-460bfbe1220a?w=800", ["jewelry", "silver", "style"]),
    ("Packable Rain Jacket", "Outdoors", "Lightweight water-resistant shell that packs into its own pocket for changeable weather.", 88, "https://images.unsplash.com/photo-1544923246-77307dd654cb?w=800", ["outdoors", "travel", "clothing"]),
    ("Softcover Daily Planner", "Books", "Undated weekly planner with roomy notes pages to make everyday plans feel manageable.", 27, "https://images.unsplash.com/photo-1506784983877-45594efa4cbe?w=800", ["planning", "stationery", "work"]),
    ("Compact Desk Organizer", "Home", "A tidy catch-all tray with sections for pens, small tools, and everyday desk items.", 35, "https://images.unsplash.com/photo-1498050108023-c5249f4df085?w=800", ["desk", "organization", "work"]),
    ("Portable Power Bank", "Electronics", "Slim high-capacity power bank with USB-C charging for phones and small devices.", 45, "https://images.unsplash.com/photo-1609091839311-d5365f9ff1c5?w=800", ["technology", "travel", "charging"]),
    ("Natural Bristle Hair Brush", "Beauty", "A gentle wooden hair brush with natural bristles and a comfortable palm-sized handle.", 23, "https://images.unsplash.com/photo-1522335789203-aabd1fc54bc9?w=800", ["hair care", "beauty", "daily"]),
    ("Reusable Food Storage Wraps", "Home", "Washable beeswax wraps in assorted sizes for covering bowls and packing snacks.", 21, "https://images.unsplash.com/photo-1606787366850-de6330128bfc?w=800", ["kitchen", "sustainable", "food"]),
    ("Lightweight Travel Umbrella", "Accessories", "Compact wind-resistant umbrella with an automatic open button and wrist strap.", 39, "https://images.unsplash.com/photo-1534274988757-a28bf1a57c17?w=800", ["travel", "everyday", "outdoors"]),
    ("Resistance Band Workout Set", "Outdoors", "Three resistance levels and a carry pouch for simple strength training at home or away.", 25, "https://images.unsplash.com/photo-1517836357463-d25dfeac3438?w=800", ["fitness", "workout", "wellness"]),
    ("Modern Wall Clock", "Home", "Quiet-sweep wall clock with a clean face and natural wood details.", 67, "https://images.unsplash.com/photo-1563861826100-9cb868fdbe1c?w=800", ["home", "decor", "wood"]),
    ("Foldable Phone Tripod", "Electronics", "Pocket-size adjustable phone tripod for video calls, photos, and hands-free viewing.", 32, "https://images.unsplash.com/photo-1512499617640-c74ae3a79d37?w=800", ["photography", "technology", "travel"]),
    ("Plant-Dyed Cotton Scarf", "Fashion", "A lightweight cotton scarf colored with plant-based dyes and finished with soft fringe.", 51, "https://images.unsplash.com/photo-1601924994987-69e26d50dc26?w=800", ["clothing", "cotton", "accessories"]),
    ("Weekend Puzzle, 500 Pieces", "Arts & Crafts", "A relaxing illustrated 500-piece puzzle with a keepsake box for screen-free evenings.", 28, "https://images.unsplash.com/photo-1606503153255-59d8b8b821b4?w=800", ["puzzle", "hobby", "family"]),
    ("Ceramic Serving Bowl", "Home", "A hand-finished stoneware bowl for shared meals, fruit, or a favorite kitchen counter.", 47, "https://images.unsplash.com/photo-1493106641515-6b5631de4bb9?w=800", ["ceramic", "kitchen", "serving"]),
    ("Everyday Baseball Cap", "Fashion", "An adjustable cotton cap with a relaxed profile for sunny walks and weekend errands.", 30, "https://images.unsplash.com/photo-1588850561407-ed78c282e89b?w=800", ["clothing", "cotton", "outdoors"]),
    ("Bamboo Bath Caddy", "Home", "Expandable bamboo tub tray with a book rest and space for bath essentials.", 55, "https://images.unsplash.com/photo-1620626011761-996317b8d101?w=800", ["bath", "bamboo", "relaxation"]),
    ("Wireless Earbud Case", "Electronics", "Protective pocket case with a clip to keep wireless earbuds close while commuting.", 18, "https://images.unsplash.com/photo-1606220945770-b5b6c2c55bf1?w=800", ["audio", "wireless", "travel"]),
    ("Herb Garden Starter Kit", "Outdoors", "A windowsill-ready set with herb seeds, biodegradable pots, and simple growing instructions.", 34, "https://images.unsplash.com/photo-1466692476868-aef1dfb1e735?w=800", ["gardening", "plants", "kitchen"]),
    ("Soft Leather Card Holder", "Accessories", "A slim leather card wallet with four card slots and a center pocket for folded bills.", 43, "https://images.unsplash.com/photo-1627123424574-724758594e93?w=800", ["leather", "wallet", "everyday"]),
    ("Mindful Moments Journal", "Books", "Guided daily prompts for reflection, gratitude, and building a calmer evening routine.", 25, "https://images.unsplash.com/photo-1455390582262-044cdead277a?w=800", ["journal", "wellness", "writing"]),
    ("Soft Fleece House Slippers", "Fashion", "Cushioned indoor slippers with a cozy lining and a durable non-slip sole.", 40, "https://images.unsplash.com/photo-1543163521-1bf539c55dd2?w=800", ["comfort", "shoes", "home"]),
    ("Travel Jewelry Case", "Accessories", "Compact zip case with padded sections to keep small jewelry pieces organized on trips.", 29, "https://images.unsplash.com/photo-1617038220319-276d3cfab638?w=800", ["jewelry", "travel", "organizer"]),
    ("Foldable Picnic Blanket", "Outdoors", "Water-resistant foldable blanket with a carry handle for parks, picnics, and beach days.", 63, "https://images.unsplash.com/photo-1527529482837-4698179dc6ce?w=800", ["outdoors", "travel", "picnic"]),
]

CUSTOMERS = ["Alex Morgan", "Sam Taylor", "Jordan Lee", "Casey Patel"]
PURCHASES = {
    0: [1, 2, 5, 6, 9],
    1: [0, 4, 8, 12, 14],
    2: [2, 7, 11, 17, 15],
    3: [1, 5, 9, 16, 10],
}


def seed_database(session: Session) -> None:
    products_by_name = {
        product.name: product for product in session.scalars(select(Product))
    }
    new_products = [
        Product(
            name=name,
            category=category,
            description=description,
            price=price,
            image_url=image_url,
            tags=tags,
        )
        for name, category, description, price, image_url, tags in PRODUCTS
        if name not in products_by_name
    ]
    session.add_all(new_products)

    customers_by_name = {
        customer.name: customer for customer in session.scalars(select(Customer))
    }
    new_customers = [
        Customer(name=name) for name in CUSTOMERS if name not in customers_by_name
    ]
    session.add_all(new_customers)
    session.flush()

    products_by_name.update({product.name: product for product in new_products})
    customers_by_name.update({customer.name: customer for customer in new_customers})
    if session.scalar(select(Purchase.id).limit(1)) is None:
        session.add_all(
            [
                Purchase(
                    customer=customers_by_name[CUSTOMERS[customer_index]],
                    product=products_by_name[PRODUCTS[product_index][0]],
                )
                for customer_index, product_ids in PURCHASES.items()
                for product_index in product_ids
            ]
        )
    session.commit()
