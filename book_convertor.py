
import pytesseract
from PIL import Image
import pandas as pd
import re
from pdf2image import convert_from_path
from PIL import Image
import os
import glob
import PyPDF2
import logging
from typing import List


logger = logging.getLogger(__name__)
file_handler = logging.FileHandler(filename='output.log', mode='w')
stream_handler = logging.StreamHandler()

file_handler.setLevel(logging.ERROR)
stream_handler.setLevel(logging.ERROR)

formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
file_handler.setFormatter(formatter)
stream_handler.setFormatter(formatter)

logger.addHandler(file_handler)
logger.addHandler(stream_handler)


def extarct_number_of_pdf_pages(pdf_path):
    with open(pdf_path,'rb') as file:
        pdf_read = PyPDF2.PdfReader(file)
        num_pages = len(pdf_read.pages)
    return num_pages

def extract_city(r):
    if len(r.split(','))==2:
        return r.split(',')[0]
    return ''

def extract_country(r):
    if len(r.split(','))==2:
        return r.split(',')[1]
    return r




def convert_pdf_to_image(pdf_path,start_page, end_page):
    # Convert specific pages (e.g., pages 2 and 3)
    # Note: Page numbers are 1-based (1 is the first page)
    pdf_folder_path = pdf_path.split(".")[0]
    images = convert_from_path(pdf_path,first_page=start_page,last_page=end_page)
    # print()
    # Save or process each image
    for i, image in enumerate(images, start=start_page):
        image.save(f'{pdf_folder_path}/page_{i}.jpg', 'JPEG')  # Save as JPEG, or you could use PNG, etc.
        print(f'Page {i} of {pdf_folder_path} saved as image')





def detect_two_columns_in_img(image):
    pass


def convert_images_to_dataframe(images_path):
    images_paths = glob.glob(f'{images_path}/*.jpg')
    images_paths.sort(key=lambda x: int(re.search(r'page_(\d+)',x).group(1)))

    all_df = pd.DataFrame()
    for image_path in images_paths:
        pdf_name = image_path.split("/")[1]
        page_number = image_path.split("/")[-1].split('.')[0]
        image = Image.open(image_path)

        # top_margin = 400
        # left_margin = 150
        # bottom_margin = 150
        # right_margin = 150

        # width,height = image.size
        # left = left_margin
        # upper = top_margin
        # right = width - right_margin
        # lower = height - bottom_margin

        # image = image.crop((left,upper,right,lower))
        # Use pytesseract to extract text
        # text = pytesseract.image_to_string(img,lang='fra')
        text = pytesseract.image_to_string(image, config='--oem 1 -c preserve_interword_spaces=1 --psm 4', lang='fra')
        pattern = r'\s{2,}'
        lines = text.split('\n')
        names=[]
        places=[]
        number_of_seperated_lines = 0
        for line in lines:
            parts = re.split(pattern,line)
            if len(parts)==2:
                number_of_seperated_lines += 1
                names.append(parts[0])
                places.append(parts[1])

        if number_of_seperated_lines > 10:
            with open(f'{pdf_name}.txt','a') as file:
                file.write(f'{page_number}\n')
            print(f'two columns detected in {pdf_name} in page {page_number}')
        try:
            df = pd.DataFrame({'Name':names,'Place':places})
            df['City'] = df['Place'].apply(extract_city)
            df['Country'] = df['Place'].apply(extract_country)
            df['Page'] = page_number
            all_df = pd.concat([df,all_df],axis=0)
        except Exception as e:
            logger.error(f'Error converting {pdf_name} page {page_number} to dataframe: {e}',exc_info=True)
    try:
        all_df.to_csv(f'{pdf_name}.csv',index=False)
    except Exception as e:
        logger.error(f'Error in writing {pdf_file}.csv',exc_info=True)



def create_page_range_from_txt_file(pdf_file_name:str) -> List[tuple]:

    with open(f'{pdf_file_name}_human_verified.txt','r') as file:
        lines = file.read().strip()
    page_ranges = []
    for line in lines.split('\n'):
        matches = re.search(r'page_(\d+), page_(\d+)',line)
        start_page = int(matches.group(1))
        end_page = int(matches.group(2))
        page_ranges.append((start_page,end_page))
    return page_ranges
        


def convert_page_range_to_dataframes(pdf_file_name: str, page_ranges: List[tuple]) -> pd.DataFrame:
    book_df = pd.DataFrame()
    for page_range in page_ranges:
        print(f'start getting page range between page {page_range[0]} and page {page_range[1]}')
        image_paths = [f'books/{pdf_file_name}/page_{page}.jpg' for page in range(page_range[0],page_range[1]+1)]
        page_range_df = pd.DataFrame()
        for image_path in image_paths:
            page_re = re.search(r'page_(\d+)',image_path)
            page_number = page_re.group(1)
            image = Image.open(image_path)
            top_margin = 400
            left_margin = 150
            bottom_margin = 150
            right_margin = 150

            width,height = image.size
            left = left_margin
            upper = top_margin
            right = width - right_margin
            lower = height - bottom_margin

            image = image.crop((left,upper,right,lower))
            text = pytesseract.image_to_string(image,config='--oem 1 -c preserve_interword_spaces=1 --psm 4')
            pattern = r'\s{2,}'
            lines = text.split('\n')
            names=[]
            places=[]
            for line in lines:
                line.replace('.',' ')
                parts = re.split(pattern,line)
                if len(parts)==2:
                    names.append(parts[0])
                    places.append(parts[1])

            df = pd.DataFrame({'Name':names,'Place':places})
            df['City'] = df['Place'].apply(extract_city)
            df['Country'] = df['Place'].apply(extract_country)
            df['Page'] = page_number
            page_range_df = pd.concat([df,page_range_df],axis=0)
        book_df = pd.concat([page_range_df,book_df],axis=0)
    book_df.to_csv(f'{pdf_file_name}_human_verified.csv',index=False)
    return book_df
    
    







if __name__ == '__main__':
    pdf_paths = glob.glob('books/*.pdf')
    # pdf_paths = ['books/capaub_cataub_1925-28.pdf']
    for pdf_path in pdf_paths:
        image_folder_save_path = pdf_path.split('.')[0]
        if not os.path.exists(image_folder_save_path):
            os.mkdir(image_folder_save_path)


        # # The 1962-66 pdf has some issue which extract_number_of_pdf_pages function fails to detect number of pages
        # # So here we add it manually
        # if '1962-66' in pdf_path:  
        #     number_of_pages=1263
        # else:
        #     number_of_pages = extarct_number_of_pdf_pages(pdf_path)
        # print(f'{image_folder_save_path} has {number_of_pages} pages')
        # for p in range(1,number_of_pages,10):
        #     convert_pdf_to_image(pdf_path,start_page=p,end_page=p+9)


        # date_ranges = ('1925-28','1928-31','1930-35','1934-37','1937-40')
        date_ranges = ('1928-31','1930-35','1934-37','1937-40')
        if any(date_range in pdf_path for date_range in date_ranges):
            print(f'start finding two columns text in images for {pdf_path}')
            pdf_file_name = pdf_path.split('.')[0].split('/')[1]
            page_ranges = create_page_range_from_txt_file(pdf_file_name)
            book_df = convert_page_range_to_dataframes(pdf_file_name,page_ranges)



