from abc import ABC, abstractmethod
from src.shop.entities import Item, CatalogSearchParams, CatalogFetchParams, CatalogResult


class Catalog(ABC):
    @abstractmethod
    def fetch(self, query: CatalogFetchParams) -> CatalogResult:
        pass

    @abstractmethod
    def search(self, query: CatalogSearchParams) -> CatalogResult:
        pass


class DummyCatalog(Catalog):
    def __init__(self):
        self.goods = list[Item]([
            Item(code="PL001", title="Rose Plant", description="A healthy potted rose plant.", price=15.99),
            Item(code="PL002", title="Basil Herb Plant", description="Fresh basil herb for kitchen gardens.",
                 price=5.49),
            Item(code="PL003", title="Tomato Seeds", description="Pack of organic tomato seeds.", price=3.99),
            Item(code="PL004", title="Cactus Mix", description="A variety of small cacti in one pot.", price=12.99),
            Item(code="PL005", title="Orchid Fertilizer", description="Specialized fertilizer for orchids.",
                 price=8.99),
            Item(code="PL006", title="Potting Soil", description="Nutrient-rich potting soil, 10L bag.", price=7.49),
            Item(code="PL007", title="Watering Can", description="Metal watering can with long spout, 2L.",
                 price=14.99),
            Item(code="PL008", title="Bamboo Plant", description="Decorative bamboo for indoor spaces.", price=9.99),
            Item(code="PL009", title="Organic Compost", description="Natural compost to enrich soil.", price=6.99),
            Item(code="PL010", title="Cucumber Seeds", description="Pack of heirloom cucumber seeds.", price=4.49),
            Item(code="PL011", title="Garden Gloves", description="Durable gloves for gardening.", price=10.99),
            Item(code="PL012", title="Sunflower Seeds", description="Giant sunflower seeds for planting.", price=3.79),
            Item(code="PL013", title="Peat Pellets", description="Expandable peat pellets for seed starting.",
                 price=5.29),
            Item(code="PL014", title="Lemon Tree", description="Young lemon tree in a pot.", price=29.99),
            Item(code="PL015", title="Coconut Coir", description="Coconut fiber soil amendment, 5kg.", price=8.49),
            Item(code="PL016", title="Terracotta Pot", description="Classic terracotta pot, 8-inch.", price=6.99),
            Item(code="PL017", title="Snake Plant", description="Air-purifying indoor snake plant.", price=18.99),
            Item(code="PL018", title="Trowel", description="Stainless steel hand trowel.", price=9.49),
            Item(code="PL019", title="Strawberry Plants", description="Set of 3 strawberry seedlings.", price=11.99),
            Item(code="PL020", title="Drip Irrigation Kit", description="Complete kit for automated watering.",
                 price=34.99),
        ])

    def fetch(self, query: CatalogFetchParams) -> CatalogResult:
        return CatalogResult(
            items=[item for item in self.goods if item.code in query.codes]
        )

    def search(self, query: CatalogSearchParams) -> CatalogResult:
        query_str = query.query.lower()
        results = []
        for item in self.goods:
            if query_str in item.title.lower():
                results.append(item)
        for item in self.goods:
            if query_str in item.description.lower():
                results.append(item)
        print(f">>> Search call: {query_str}, max_results={query.max_results}, results: {results}")
        return CatalogResult(
            items=results[:query.max_results]
        )
