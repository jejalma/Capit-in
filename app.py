import sys
from pathlib import Path

import streamlit as st

sys.path.insert(0, str(Path(__file__).resolve().parent))

import config  # noqa: E402
import database  # noqa: E402
from security import can  # noqa: E402
from views import theme  # noqa: E402
from views.components import show_flash  # noqa: E402
from views.layout import LOGO, sidebar_user  # noqa: E402
from views.pages import accounts, dashboard, journal, master_data, reports, stock, transactions  # noqa: E402
from views.pages.login import login_page  # noqa: E402
from views.session import current_user  # noqa: E402

st.set_page_config(page_title=f'{config.APP_NAME} · SIA Tambak Kepiting', page_icon='🦀', layout='wide')


@st.cache_resource
def _init_db() -> bool:
    database.init_db()
    return True


NAV = [
    ('', [
        ('dashboard', 'Dashboard', 'dashboard', dashboard.render, None),
        ('transaksi', 'Transaksi', 'receipt_long', transactions.render, None),
        ('jurnal', 'Jurnal & Buku Besar', 'menu_book', journal.render, None),
        ('laporan', 'Laporan Keuangan', 'bar_chart', reports.render, None),
    ]),
    ('Master Data', [
        ('produk', 'Produk Kepiting', 'set_meal', master_data.products_page, None),
        ('pengepul', 'Pengepul', 'groups', master_data.collectors_page, None),
        ('karyawan', 'Karyawan', 'badge', master_data.employees_page, None),
        ('akun', 'Bagan Akun', 'account_tree', accounts.render, None),
        ('stok', 'Stok Kepiting', 'inventory_2', stock.render, None),
    ]),
    ('Sistem', [
        ('pengguna', 'Pengguna', 'admin_panel_settings', master_data.users_page, 'users.manage'),
    ]),
]


def _page(user: dict, slug: str, title: str, icon: str, builder) -> st.Page:
    def run() -> None:
        show_flash()
        builder(user)

    run.__name__ = f'page_{slug}'
    return st.Page(run, title=title, icon=f':material/{icon}:', url_path=slug, default=slug == 'dashboard')


def main() -> None:
    _init_db()
    theme.apply()
    user = current_user()
    if not user:
        st.navigation([st.Page(login_page, title='Masuk', url_path='login')], position='hidden').run()
        return
    st.logo(str(LOGO), size='large')
    pages = {}
    for section, items in NAV:
        visible = [_page(user, s, t, i, b) for s, t, i, b, perm in items if not perm or can(user['role'], perm)]
        if visible:
            pages[section] = visible
    nav = st.navigation(pages)
    sidebar_user(user)
    nav.run()


main()
