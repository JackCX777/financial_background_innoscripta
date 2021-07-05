import os
import shutil
from string import ascii_letters, digits


def get_urls(urls_file_path):
    """
            The get_urls_from_file reads urls.txt file from source directiory.

            Parameters:
                file_path (str): The path to the txt file with urls.

            Returns:
                url_list (list): List of balance urls from txt file.
    """
    url_list = []
    try:
        urls_file_path = os.path.abspath(urls_file_path)
        with open(urls_file_path, 'r') as file:
            for line in file:
                url = line.strip()
                url_list.append(url)
    except FileNotFoundError as exception:
        print(exception.__repr__())
    return url_list


def get_files(source_dir, files_urls_list=[]):
    """
            The get_files takes files paths from the source directory and adds them to the incoming list of urls.

            Parameters:
                source_dir (str): Path to the files source directory.
                files_urls_list (list): The list of urls.

            Returns:
                url_list (list): List of balance urls from txt file extended with files urls.
    """
    try:
        source_dir = os.path.abspath(source_dir)
        source_files_list = os.listdir(source_dir)
        for file_name in source_files_list:
            file_path_src = os.path.join(source_dir, file_name)
            file_url = ''.join(['file://', file_path_src])
            files_urls_list.append(file_url)
    except FileNotFoundError as exception:
        print(exception.__repr__())
    return files_urls_list


def move_files(source_dir, archive_dir):
    """
            The move_files moves the source files from the source directory to the archive directory
            to prevent them from being processed again.

            Parameters:
                source_dir (str): Path to the files source directory.
                archive_dir (str): Path to the archive directory.

            Returns:
                None.
    """
    try:
        source_dir = os.path.abspath(source_dir)
        archive_dir = os.path.abspath(archive_dir)
        source_files_list = os.listdir(source_dir)
        for file_name in source_files_list:
            file_path_src = os.path.join(source_dir, file_name)
            file_path_dst = os.path.join(archive_dir, file_name)
            shutil.move(file_path_src, file_path_dst)
    except FileNotFoundError as exception:
        print(exception.__repr__())


def dump_to_csv(dataframe):
    """
            The dump_to_csv takes dataframe and writes it to a *.csv file in output directory.

            Parameters:
                dataframe (pandas.DataFrame instance): Current dataframe.

            Returns:
                None.
    """
    url = dataframe.attrs.get('url')
    url_scheme = url.split(':')[0]
    if url_scheme == 'file':
        file_name = os.path.basename(url).split('.')[0]
    else:
        valid_ch_set = set(''.join([ascii_letters, digits]))
        url_path_raw = url.split(':')[1].lstrip('//')
        file_name = ''.join([ch if ch in valid_ch_set else '_' for ch in url_path_raw])
    if not os.path.exists('./out'):
        os.mkdir('./out')
    dataframe.to_csv(f'./out/{file_name}.csv')


if __name__ == '__main__':
    pass
