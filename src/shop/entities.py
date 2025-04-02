from pydantic import BaseModel, constr, conlist, Field


class Item(BaseModel):
    code: str = Field(description="Item code")
    title: str = Field(description="Item title")
    description: str = Field(description="Item description")
    price: float = Field(description="Item price in USD")


class CatalogSearchParams(BaseModel):
    query: constr(min_length=1) = Field(description="Short text to search for in the catalog")
    max_results: int = Field(default=5, description="Maximum number of results to return")


class CatalogFetchParams(BaseModel):
    codes: conlist(str, min_length=1) = Field(description="List of product codes to fetch from the catalog")


class CatalogResult(BaseModel):
    items: list[Item] = Field(description="List of items returned from the catalog")


class ShoppingCart(BaseModel):
    items: dict[str, int] = Field(default_factory=dict[str, int], description="Quantities of each product by code in the shopping cart")


class ItemQuantity(BaseModel):
    item_code: str = Field(description="Product code")
    quantity: int = Field(description="Product quantity")