import os
from pathlib import Path

from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent
load_dotenv(BASE_DIR / '.env')

APP_NAME = 'Capit-in'
COMPANY_NAME = 'Tambak Kepiting Bapak Salim'
COMPANY_ADDRESS = 'Jl. Tambak Layur, Desa Morodemak, Kec. Bonang, Kab. Demak, Jawa Tengah'

DB_PATH = os.environ['SIA_DB_PATH']
PORT = int(os.environ['SIA_PORT'])
STORAGE_SECRET = os.environ['SIA_STORAGE_SECRET']

SEED_USERS = [
    ('Bapak Salim', os.environ['SIA_ADMIN_EMAIL'], os.environ['SIA_ADMIN_PASSWORD'], 'admin'),
    ('Akuntan', os.environ['SIA_AKUNTAN_EMAIL'], os.environ['SIA_AKUNTAN_PASSWORD'], 'akuntan'),
    ('Kasir', os.environ['SIA_KASIR_EMAIL'], os.environ['SIA_KASIR_PASSWORD'], 'kasir'),
]
