import os
from dotenv import load_dotenv
from bs4 import BeautifulSoup

load_dotenv()


if __name__ == '__main__':
    secret_1 = os.getenv('SECRET')
    print(secret_1)
