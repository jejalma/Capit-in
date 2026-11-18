import sys
from pathlib import Path

from streamlit.web import cli as stcli

import config

if __name__ == '__main__':
    app = Path(__file__).resolve().parent / 'app.py'
    sys.argv = ['streamlit', 'run', str(app), '--server.port', str(config.PORT), '--server.address', '0.0.0.0']
    sys.exit(stcli.main())
