# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
from genericpath import exists
import os
import re
from itemadapter import ItemAdapter
import zipfile
from gobilda_parts_bot.settings import FILES_STORE, SKU_FILE_NAMES

def get_valid_filename(name):
    s = str(name).strip().replace(' ', '_')
    s = re.sub(r'(?u)[^-\w.]', '', s)
    return s

class GobildaPartsBotPipeline:
    def process_item(self, item, spider):
        adapter = ItemAdapter(item)
        if adapter.get('files'):
            path = adapter['files'][0]['path']
            # Item loaders give us a list with one value, so we have to access the first
            # element of the list to get the actual string data
            name = adapter['sku'][0] if SKU_FILE_NAMES else get_valid_filename(adapter['name'][0])

            zip_path = f'{FILES_STORE}/{path}' 
            if exists(zip_path):
                with zipfile.ZipFile(zip_path, 'r') as zip:
                    file_in_zip = zip.namelist()[0] # Should be only 1 file in zip
                    
                    unzipped_path = zip.extract(file_in_zip, FILES_STORE)
                    os.rename(unzipped_path, FILES_STORE + '/' + name + '.STEP')

                os.remove(zip_path)
        return item