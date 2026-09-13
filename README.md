## Bihar Ration Cards 2022

[![Data: Dataverse](https://img.shields.io/badge/data-10.7910%2FDVN%2FCAVZMQ-blue)](https://doi.org/10.7910/DVN/CAVZMQ)
[![License: MIT](https://img.shields.io/badge/code-MIT-green)](LICENSE)

> **Point-in-time scrape.** The code records how the data were collected in November 2022. It is not maintained and is not expected to run against today's portal.

Every ration card listed on Bihar's public distribution system portal at [epds.bihar.gov.in](http://epds.bihar.gov.in/DistrictWiseRationCardDetailsBH.aspx) in November 2022: 17,696,683 cards, 16,145,164 rural and 1,551,519 urban, each with its card type, fair price shop, village, address, mobile number, and the list of household members with age and relation to the head. The data are one SQLite database on Harvard Dataverse at [doi:10.7910/DVN/CAVZMQ](https://doi.org/10.7910/DVN/CAVZMQ); because they name individuals, access is restricted to researchers with an approved IRB protocol.

A second, smaller collection, transaction histories for 101,395 cards in November 2021 from a different portal, is in [`transactions_2021/`](transactions_2021/).

### Data

| File | Bytes | What |
|---|--:|---|
| `ration_cards.sqlite.gz.001` | 2,097,152,000 | first half of one gzip file |
| `ration_cards.sqlite.gz.002` | 1,199,961,053 | second half |

Rebuild and open with `cat ration_cards.sqlite.gz.00? | gunzip > ration_cards.sqlite`. The result is 56,741,351,424 bytes (53 GiB), so check disk space first.

**Tables.**

| Table | Rows | One row per | Key |
|---|--:|---|---|
| `ration_card_details` | 17,696,683 | ration card | `ration_card_number` |
| `family_members_tables` | 17,696,683 | ration card, members as JSON | `id` = `ration_card_number` |
| `village` | 41,267 | village (rural) | `id` = `ration_card_details.village_id` |
| `fps` | 4,567 | fair price shop (urban) | `id` = `ration_card_details.fps_id` |
| `district` | 38 | district | `id` |
| `tahsil` | 534 | block | `id` |
| `panchayat` | 8,530 | gram panchayat | `id` |
| `town` | 2 | `rural` (1) or `urban` (2) | `id` |

Every non-blank `village_id` on a card matches a `village` row and every non-blank `fps_id` matches an `fps` row. The `district`, `tahsil` and `panchayat` tables are name lists only: no column on a card points to them, so a card cannot be placed in a district or panchayat from this database alone. A rural card has a `village_id` and no `fps_id`; an urban card has an `fps_id` and no `village_id`.

**Columns of `ration_card_details`.** Source labels are the Hindi field names on the card page.

| Column | Source label | Notes |
|---|---|---|
| `ration_card_number` | राशनकार्ड संख्या | 20 digits (13,653,803 cards) or 24 digits (4,042,865); 15 cards have other lengths. |
| `card_type` | कार्ड का प्रकार | `PHH` priority household (15,441,008), `AAY` Antyodaya (2,255,674), blank (1). |
| `img_url` | | Portal URL of the family photo; blank for 1 card. The spider recorded the URL and did not download photos. |
| `know` | पता | **Address**, despite the column name. Free text; blank for 243,642 cards. |
| `mobile_number` | मोबाईल संख्या | Blank for 9,019,637 cards (51%). |
| `fair_price_shopkeeper_name` | उचित मूल्य दुकानदार का नाम | |
| `fps_id` | | 12-digit shop code; urban cards only. |
| `village_id` | | 16-digit village code; rural cards only. |
| `plc_id` | | 16-digit code from the page URL; blank for 2 cards. |
| `unique_rc_id` | | 8 digits, from the page URL. |
| `url` | | Blank in every row. |
| `family_members_table_id` | | Equals `ration_card_number`. |

**`family_members_tables`.** `sub_table` is a JSON list with one object per household member, keyed by the page's column headers: `S.NO.`, `सदस्य का नाम` (member name), `पिता का नाम` (father's name), `आयु` (age), `मुखिया से सम्बन्ध` (relation to head). `members_qty` counts one more than the members in `sub_table`: the parser counted the header row before dropping it. This held in all of the first 20,000 rows checked; it has not been verified for the whole table. If it holds throughout, the database lists 85,798,262 people.

The `village` table uses the village name as its `id` for 130 villages the portal listed without a code; the other 41,137 ids are 16-digit codes.

### How the data were collected

1. [`scripts/ration_bihar/spiders/bihar.py`](scripts/ration_bihar/spiders/bihar.py) is a Scrapy spider. It walks the portal's ASP.NET grids from district down to card, following each postback link and paging through results, and saves every card page's details and member table as JSON. [`scripts/execute.sh`](scripts/execute.sh) ran many spider instances in parallel, each taking three rows of the district grid (`-a n=<instance>`). In the committed code the spider's entry point (`parse`) is disabled; the three lines that start a crawl are commented out.
2. [`scripts/parser/main.py`](scripts/parser/main.py) streams the JSON with `ijson` into the SQLite schema above.
3. [`tests/check_dups.py`](tests/check_dups.py) counts repeated card records in one JSON output.

### transactions_2021

Card-level transaction histories from `epos.bihar.gov.in/SRC_Trans_Details.jsp` for November 2021, originally in `in-rolls/bihar_ration_transaction_details`.

- [`url.txt`](transactions_2021/url.txt): 101,395 card URLs, all for month 11 of 2021.
- [`scrape_ration_card.ipynb`](transactions_2021/scrape_ration_card.ipynb): fetches all of them in parallel, twice (the second pass re-fetches pages that came back empty), and writes `output_all_r1.csv` / `output_all_r2.csv`. Those outputs are not in this repository or on Dataverse.
- [`getTransactionDetails.py`](transactions_2021/getTransactionDetails.py): a parser for the saved pages that handles the four page shapes the portal returns (card not found; card and entitlement only; with transactions; with transactions and authentication). It has hard-coded local paths and loops over the first 1,000 URLs only.
- [`sample_output.csv`](transactions_2021/sample_output.csv): ten rows of parser output showing the columns. Member names are replaced with `<redacted>` and the last eight digits of each card number with `X`. Codes `-9` mean the card was not found and `-8` that it had no transactions.

### Getting the data

Request access on [Dataverse](https://doi.org/10.7910/DVN/CAVZMQ) with an approved IRB protocol that covers individual-level administrative data.

### Citation

See [CITATION.cff](CITATION.cff). Please cite the Dataverse DOI for the data.

### License

Code is MIT. The records are published by the Food and Consumer Protection Department, Government of Bihar; the Dataverse copy is restricted to research use.
