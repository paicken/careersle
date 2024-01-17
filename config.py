import os
from dotenv import load_dotenv

basedir = os.path.abspath(os.path.dirname(__file__))
load_dotenv(os.path.join(basedir, '.env'))


class Config:
    BASE_URL = os.environ['BASE_URL']
    PATH_FORMAT = os.environ['PATH_FORMAT']