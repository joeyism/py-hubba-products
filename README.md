#Hubba Product

## Installation
Dependencies can be installed by pip with

```bash
pip3 install -r requirements.txt
```

## Download CSV Files
Due to size limitations, you must download prods, actions, and buyers csv file

## Scraper
To run it normally (from the root of the project), run

```bash
python3 scraper.py [CSV FILENAME]
```

**For Example**

```bash
python3 scraper.py prods_scraped.csv
```

which will save it in `prods_scraped.csv` file.

### Headless
If you want to run it headlessly (in an EC2 instance), simply add the flag `--headless`, such that 

```bash
python3 scraper.py prods_scraped.csv --headless
```


