import base64
from functools import lru_cache
from pathlib import Path

import streamlit as st

from security import ROLE_LABELS
from views.session import logout

LOGO = Path(__file__).resolve().parents[1] / 'static' / 'logo.png'


@lru_cache
def logo_data_uri() -> str:
    return 'data:image/png;base64,' + base64.b64encode(LOGO.read_bytes()).decode()


def brand_html(dark: bool = False) -> str:
    c1 = 'rgba(255,255,255,.7)' if dark else '#6B7578'
    c2 = '#fff' if dark else '#1F2A2E'
    return (f'<div class="sia-brand" data-testid="brand"><img src="{logo_data_uri()}" alt="Capit-in"/>'
            f'<div><div class="t1" style="color:{c1}">SIA TAMBAK KEPITING</div>'
            f'<div class="t2" style="color:{c2}">Capit-in</div></div></div>')


def sidebar_user(user: dict) -> None:
    with st.sidebar:
        st.markdown(f'<div class="sia-user" style="text-align:left"><div class="n" data-testid="current-user-name">'
                    f'{user["name"]}</div><div class="r" data-testid="current-user-role">'
                    f'{ROLE_LABELS[user["role"]]}</div></div>', unsafe_allow_html=True)
        if st.button('Keluar', icon=':material/logout:', key='logout-button', width='stretch'):
            logout()
            st.rerun()
