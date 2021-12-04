from YandexImagesParser.ImageParser import YandexImage
import requests
import os
from transliterate import translit
import re
import csv
from pprint import pprint
import random
import time
import datetime

# create YandexImage parser's instance
parser = YandexImage()
print(parser.about, parser.version, 'successfully initiated/n')

# define the name of the directory to be created
img_dir_name = 'downloaded_images'

# define the path of the directory to be created for saving images
img_dir_path_ = os.path.join(os.getcwd(), img_dir_name)

# source csv file (delimeter=',') with colors
file_name_ = 'colors_list.csv'
file_path_ = os.path.join(os.getcwd(), file_name_)


def get_color_list(file_path: str, show_dict: bool = False) -> list:
    """
    The function creates a list of colors from csv file
    :param file_path: string, full csv file path
    :param show_dict: boolean, to show dict with raw colors or not
    :return:list, for example: ['lightslateblue', 'cadetblue']
    """
    # check types
    assert type(file_path) == str
    assert type(show_dict) == bool

    # create a multiple for unique colors and dict for all variants of colors
    colors_mul = set()
    colors_dict = {}

    with open(file_path, encoding='utf-8') as r_file:
        file_reader = csv.reader(r_file, delimiter=",")
        for row in file_reader:
            # get a string in lower case
            color_raw = row[0].split(",")[0].lower()
            # get a cleared string without digits
            color_cleared = re.sub("[0-9]", "", color_raw)
            # add color in the dict
            colors_mul.add(color_cleared)

            if color_cleared in colors_dict:
                # if key (color) exists a value (color variant) will be added
                colors_dict[color_cleared].append(color_raw)
            else:
                # if key (color) doesn't exist
                # a new key, value (empty list) will be created
                colors_dict[color_cleared] = []

    if show_dict is True:
        pprint(colors_dict)
        print(f'Colors count: {len(colors_mul)}\n')
    return list(colors_mul)


def latinic(string: str) -> str:
    """
    The function transliterates a string in latin alphabet
    :param string: string of a search query, example: 'Dark forest'
    :return:string: string in transliterated string with '_' instead of ' ',
        example: 'dark_forest'
    """
    # check types
    assert type(string) == str
    # transliterate a string
    string = translit(string, reversed=True)
    # replace punctuation symbols
    string = " ".join(re.split("[!;,'\s_]+", string))
    pattern = re.compile('( | )')
    # replace whitespaces with underscores
    string = pattern.sub('_', string)
    return string


def img_saver(request_str: str, img_count: int,
              img_dir_path: str, parser) -> None:
    """
    The function parses and saves images from Yandex
    :param request_str: string with request phrase/word,
        example: 'Interior in colors'
    :param img_count: int, how many images to save
    :param img_dir_path: string, path where to save images
    :param parser: a YandexImage parser's instance
    :return: None
    """
    try:
        os.mkdir(img_dir_path)
    except OSError:
        pass
    else:
        print(f"The directory {img_dir_path} is successfully created")

    for num, item in enumerate(
            parser.search(request_str, sizes=parser.size.small)
    ):
        # stop iters if iter number is more than img_count
        if num > (img_count-1):
            break
        print(f"iter #{num}")
        print(item.title)
        print(item.url)
        print(item.preview.url)
        print("(", item.size, ")", sep='')
        img_data = requests.get(item.preview.url).content
        path_img_subdir = os.path.join(img_dir_path, request_str)
        print("Saved in subdir: ", path_img_subdir)

        try:
            os.mkdir(path_img_subdir)
            print(f"Subdir created: {path_img_subdir}")
        except OSError:
            print(f"Creation of the subdirectory {request_str}" +
                  " failed (subdir exists)")
        else:
            print(f"Successfully created the subdirectory {request_str}")

        img_path = os.path.join(path_img_subdir, str(datetime.datetime.now().timestamp()).replace(".", ""))+'.jpg'

        with open(img_path, 'wb') as handler:
            handler.write(img_data)
            print("Image downloaded!")
        time.sleep(random.random()*2)


if __name__ == '__main__':
    color_list = get_color_list(file_path=file_path_, show_dict=True)

    for color in color_list:
        request_str_ = color
        request_str_ = latinic('интерьер в цвете ' + color)
        img_saver(request_str=request_str_, img_count=50,
                  img_dir_path=img_dir_path_, parser=parser)
