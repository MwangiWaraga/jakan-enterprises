# Data model notes

## Identity model

```text
internal_sku_id        = your permanent product/SKU ID
source_product_key     = supplier key, e.g. Oraimo EAN/model/slug
marketplace_sku_key    = Kilimall sku_id
```

## Mapping files

- `sku_source_map.csv`
- `sku_listing_map.csv`

Fuzzy matching is only a review tool. Permanent joins should use mapping seeds.
