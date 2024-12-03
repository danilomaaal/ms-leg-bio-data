# MS Leg Data

A script to scrape Mississippi state legislature bio data from [senators](https://www.legislature.ms.gov/legislators/senators) and [representatives](https://www.legislature.ms.gov/legislators/representatives). This script first extract links from a pdf list, which was obtained from the MS legislature website, and saves it as a csv file.

Usage:

```bash

$ scrape.py --input files/legislature_links.pdf --output files/bio_data.csv

```

