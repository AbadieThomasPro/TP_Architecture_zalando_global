from decimal import Decimal

from django.db import migrations
from django.utils.text import slugify


CATEGORY_NAMES = [
    "T-Shirts",
    "Shirts",
    "Blouses",
    "Pants",
    "Jeans",
    "Shorts",
    "Skirts",
    "Dresses",
    "Jumpsuits",
    "Sweatshirts",
    "Hoodies",
    "Sweaters",
    "Cardigans",
    "Jackets",
    "Coats",
    "Blazers",
    "Suits",
    "Sportswear",
    "Tracksuits",
    "Leggings",
    "Underwear",
    "Bras",
    "Lingerie",
    "Socks",
    "Pajamas",
    "Swimwear",
    "Beachwear",
    "Sneakers",
    "Running Shoes",
    "Boots",
    "Sandals",
    "Heels",
    "Flats",
    "Bags",
    "Backpacks",
    "Wallets",
    "Belts",
    "Hats",
    "Caps",
    "Scarves",
    "Gloves",
    "Sunglasses",
    "Watches",
    "Jewelry",
    "Earrings",
    "Necklaces",
    "Bracelets",
    "Rings",
    "Active Tops",
    "Active Bottoms",
]

PRODUCT_TYPES = [
    "T-Shirt",
    "Polo",
    "Shirt",
    "Blouse",
    "Sweater",
    "Cardigan",
    "Hoodie",
    "Jacket",
    "Coat",
    "Blazer",
    "Vest",
    "Pants",
    "Jeans",
    "Chinos",
    "Shorts",
    "Skirt",
    "Dress",
    "Jumpsuit",
    "Tracksuit",
    "Leggings",
    "Sneakers",
    "Boots",
    "Sandals",
    "Backpack",
    "Bag",
]

BRANDS = [
    "Adidas",
    "Nike",
    "Puma",
    "Reebok",
    "New Balance",
    "Asics",
    "Under Armour",
    "Levis",
    "Calvin Klein",
    "Tommy Hilfiger",
    "Lacoste",
    "Diesel",
    "Guess",
    "Zara",
    "Mango",
    "Hugo Boss",
    "Armani",
    "Uniqlo",
    "Converse",
    "Vans",
]

COLORS = [
    "Black",
    "White",
    "Brown",
    "Beige",
    "Grey",
    "Navy",
    "Blue",
    "Sky Blue",
    "Green",
    "Olive",
    "Red",
    "Burgundy",
    "Orange",
    "Yellow",
    "Pink",
    "Purple",
    "Cream",
    "Khaki",
]

SIZES = ["XXS", "XS", "S", "M", "L", "XL", "XXL", "3XL"]

MATERIALS = [
    "cotton",
    "organic cotton",
    "linen",
    "wool",
    "denim",
    "viscose",
    "polyester",
    "recycled polyester",
    "leather",
    "fleece",
]

FITS = ["slim", "regular", "relaxed", "oversized", "straight", "tapered"]

STYLES = [
    "casual",
    "streetwear",
    "minimal",
    "sport",
    "smart",
    "urban",
    "retro",
    "modern",
]


def _build_unique_category_payloads():
    payloads = []
    seen_slugs = set()

    for idx, name in enumerate(CATEGORY_NAMES, start=1):
        base_slug = slugify(name)
        slug = base_slug
        suffix = 2
        while slug in seen_slugs:
            slug = f"{base_slug}-{suffix}"
            suffix += 1
        seen_slugs.add(slug)
        payloads.append({"name": name, "slug": slug})

    return payloads


def _build_product_data(idx, category):
    product_type = PRODUCT_TYPES[idx % len(PRODUCT_TYPES)]
    brand = BRANDS[(idx // len(PRODUCT_TYPES)) % len(BRANDS)]
    color = COLORS[(idx // (len(PRODUCT_TYPES) * len(BRANDS))) % len(COLORS)]
    size = SIZES[(idx // 7) % len(SIZES)]
    material = MATERIALS[(idx // 11) % len(MATERIALS)]
    fit = FITS[(idx // 13) % len(FITS)]
    style = STYLES[(idx // 17) % len(STYLES)]

    name = f"{product_type} {brand} {color} {size}"
    slug = slugify(f"{product_type}-{brand}-{color}-{size}-{idx + 1}")
    price = Decimal("19.90") + (Decimal((idx * 37) % 18000) / Decimal("100"))
    stock = (idx * 13) % 250

    description = (
        f"{style.title()} {product_type.lower()} by {brand}, "
        f"{fit} fit, made from {material}, color {color.lower()}, size {size}."
    )

    return {
        "name": name,
        "slug": slug,
        "description": description,
        "price": price,
        "stock": stock,
        "category": category,
        "is_active": True,
    }


def seed_fashion_catalog(apps, schema_editor):
    Category = apps.get_model("catalog", "Category")
    Product = apps.get_model("catalog", "Product")

    Product.objects.all().delete()
    Category.objects.all().delete()

    category_payloads = _build_unique_category_payloads()
    Category.objects.bulk_create([Category(**payload) for payload in category_payloads], batch_size=200)

    categories = list(Category.objects.order_by("id"))

    total_products = 100000
    batch_size = 2000
    to_create = []

    for idx in range(total_products):
        category = categories[idx % len(categories)]
        product_data = _build_product_data(idx, category)
        to_create.append(Product(**product_data))

        if len(to_create) >= batch_size:
            Product.objects.bulk_create(to_create, batch_size=batch_size)
            to_create = []

    if to_create:
        Product.objects.bulk_create(to_create, batch_size=batch_size)


def rollback_fashion_catalog(apps, schema_editor):
    Category = apps.get_model("catalog", "Category")
    Product = apps.get_model("catalog", "Product")

    Product.objects.all().delete()
    Category.objects.all().delete()


class Migration(migrations.Migration):

    dependencies = [
        ("catalog", "0001_initial"),
    ]

    operations = [
        migrations.RunPython(seed_fashion_catalog, rollback_fashion_catalog),
    ]
