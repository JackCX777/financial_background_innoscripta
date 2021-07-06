from file_handlers import get_urls, get_files, dump_to_csv, move_files
from data_handlers import parse_balance


path_to_urls_list_file = './in/urls.txt'
src_dir = './in/src_files'
arch_dir = './out/archive'


def parse():
    """
            The parse func performs all steps to gather the financial background from url into a *.csv file.

            Parameters:
                None.

            Returns:
                None.
    """
    try:
        urls_list = get_urls(path_to_urls_list_file)
        urls_list = get_files(src_dir, urls_list)
        for url in urls_list:
            balance_dataframe = parse_balance(url)
            dump_to_csv(balance_dataframe)
        move_files(src_dir, arch_dir)
    except Exception as exception:
        print(exception.__repr__())
        print(exception.__context__)


if __name__ == '__main__':
    parse()
