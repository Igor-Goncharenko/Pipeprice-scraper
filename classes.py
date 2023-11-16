from typing import NamedTuple


class Category(NamedTuple):
    category: str
    subcategory: str
    link: str


class ProductUrl(NamedTuple):
    category: str
    subcategory: str
    link: str


class Product(NamedTuple):
    name: str
    price: str
    link: str
    category: str
    subcategory: str
    image_urls: list[str]
    in_stock: bool

    def list_view(self) -> list:
        image_urls_str = " | ".join(self.image_urls)
        return [
            self.name,
            self.price,
            self.link,
            self.category,
            self.subcategory,
            image_urls_str,
            self.in_stock
        ]
