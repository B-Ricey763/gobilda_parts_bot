## goBILDA Parts Bot

A [ Scrapy ](https://scrapy.org/) spider written in python that scrapes almost the entirety of the goBILDA website for each and every `.STEP` file, for use in any CAD software supporting `.STEP`. 

## How to Run

1. Install [ scrapy ](https://scrapy.org/) and [ tqdm ](https://tqdm.github.io/) (assuming you already have python installed)
```cmd
pip install scrapy tqdm
```
> Tip: if the installation fails, you might want to try installing scrapy in a [ virtualenv ](https://docs.python.org/3/tutorial/venv.html)

2. Make sure you have a valid `FILES_STORE` defined in `settings.py`. By default, you will have to create a folder at the root of this repository called `models`:
```
├───gobilda_parts_bot
│   ├───spiders
│   │   └───__pycache__
│   └───__pycache__
└───models  <-- what you need to make 
```
> Feel free to change `FILES_STORE` to whatever suits your needs

3. set `SKU_FILE_NAMES` (also defined in `settings.py`). By default, file names are the full product name as displayed on the goBILDA website. These names are long, which can cause problems with uploading to Fusion. To get filenames that consist only of the part's SKU, set `SKU_FILE_NAMES` to `True`.

4. Run the `parts` spider:
```cmd
scrapy crawl parts
```
5. Wait for the `FILES_STORE` to populate, and you are good to go!
> Note: there will be some empty folders left behind in the models folder, like `full` and some with `assembly` in the name. Don't worry, nothing went wrong, I just didn't bother trying to find a simple solution to delete them.

## How it works
The goBILDA website is organized with repetitive product grid items that a web scraper can easily detect and follow to an indiviudal product page. The spider, responsible for crawling the website and downloading the `.STEP` files, starts at a couple main URLS on the goBILDA website to try and get as many parts as possible downloaded while ommitting repeats, merch, and kits.
```python
	start_urls = [
		'https://www.gobilda.com/motion',
		'https://www.gobilda.com/structure/',
		'https://www.gobilda.com/electronics/',
		'https://www.gobilda.com/hardware/',
	]
```
For every page, the spider's `parse()` method is called:
```python
	def parse(self, response):
        # Get the link attribute from a product box
		partsList = response.css('li.product a')
		if partsList:
			# Sometimes, catalog pages are within others, so we have to recursively
			# go through each page to get to actual parts
			yield from response.follow_all(partsList, self.parse)
		else:
			# We are at an actual part page, with the step file,
			# so we process the actual values scraped from the page
			yield self.parse_product_page(response)
```
Since some of the parts catalogs contain sub-catalogs within them, we have to do some recursion in order to get to each individual part.

Once we are the product page, we get the name of the part, the sku number (currently not used for anything), and the `.STEP` file:
```python
	def parse_product_page(self, response):
		step_file = response.css('a.ext-zip::attr(href)').get()
		name = response.css( 'h1.productView-title::text').get()
		if step_file and 'Bundle' not in name: # bundles will contain repeats, we don't want that
			loader = ItemLoader(Product(), response=response)
			loader.add_css('sku', 'span.productView-sku-input::text')
			loader.add_value('file_urls', [f'https://www.gobilda.com{step_file}'])
			loader.add_value('name', name)
			return loader.load_item()
```

After that, its a relatively simple matter of downloading the zipped `.STEP` file, extracting the file, deleting the zip, and renaming the file. One thing to note: the file's names don't look exactly like the names displayed on the website, as I had to get rid of colons, spaces, and other forbidden characters to get a clean filename. 

> Note: When I uploaded the complete parts folder to Fusion 360 (my CAD software of choice), it said 10 out of the 80 models failed to upload. I'm not sure which ones are the culprits, or if it is just Fusion being fusion,but create an issue or pull request if you've found the problem and/or solution. 