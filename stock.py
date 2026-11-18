from datetime import date

import streamlit as st

from security import can
from services import ServiceError, master, stock
from views.components import badge_html, confirm, data_table, flash, page_header, section_title
from views.fmt import kg, rp, tgl

S = 'stock-'


def _save(user_id: int) -> None:
    s = st.session_state
    d = s.get(S + 'date')
    try:
        stock.add_movement(s.get(S + 'product'), d.isoformat() if d else None, s.get(S + 'kind'), s.get(S + 'qty'),
                           s.get(S + 'note', ''), user_id)
    except ServiceError as exc:
        s[S + 'error'] = str(exc)
        return
    s.pop(S + 'error', None)
    s[S + 'qty'] = None
    s[S + 'note'] = ''
    flash('Pergerakan stok tersimpan.')


def _summary(products: list[dict]) -> None:
    cols = st.columns(max(len(products), 1))
    for col, p in zip(cols, products):
        col.markdown(f'<div class="sia-stock-card"><div class="name">{p["name"]}</div>'
                     f'<div class="kg" data-testid="stock-kg-{p["id"]}">{kg(p["stock_kg"])}</div>'
                     f'<div class="meta">Nilai {rp(p["stock_value"])} · {rp(p["price_per_kg"])}/kg</div></div>',
                     unsafe_allow_html=True)


def _form(user: dict, products: dict) -> None:
    with st.container(border=True):
        section_title('Catat Stok', 'Hasil panen (masuk), kepiting mati/susut, atau koreksi')
        st.selectbox('Produk', list(products), format_func=lambda k: products[k], index=None, key=S + 'product',
                     placeholder='Pilih produk...')
        kinds = {k: v[0] for k, v in stock.KINDS.items()}
        st.selectbox('Jenis', list(kinds), format_func=lambda k: kinds[k], key=S + 'kind')
        c1, c2 = st.columns(2)
        c1.date_input('Tanggal', value=date.today(), key=S + 'date', format='DD/MM/YYYY')
        extra = {} if S + 'qty' in st.session_state else {'value': None}
        c2.number_input('Jumlah (kg)', min_value=0.0, step=0.5, format='%.1f', key=S + 'qty', **extra)
        st.text_input('Catatan (opsional)', key=S + 'note')
        st.button('Simpan', icon=':material/check:', type='primary', key=S + 'submit-button', on_click=_save,
                  args=(user['id'],), width='stretch')
        if st.session_state.get(S + 'error'):
            st.error(st.session_state.pop(S + 'error'), icon=':material/error:')


def _history(user: dict, products: dict) -> None:
    with st.container(border=True):
        h1, h2 = st.columns([2, 1], vertical_alignment='bottom')
        with h1:
            section_title('Riwayat Pergerakan Stok')
        opts = {0: 'Semua produk', **products}
        pid = h2.selectbox('Filter produk', list(opts), format_func=lambda k: opts[k], key=S + 'filter-product',
                           label_visibility='collapsed')
        moves = stock.list_movements(pid or None)
        rows = [[tgl(m['date']), m['product_name'],
                 badge_html(stock.KIND_LABELS.get(m['kind'], m['kind']), 'moss' if m['qty_kg'] > 0 else 'ember'),
                 ('+' if m['qty_kg'] > 0 else '') + kg(m['qty_kg']), m['note'] or '-'] for m in moves]
        data_table([('Tanggal', 'left'), ('Produk', 'left'), ('Jenis', 'left'), ('Jumlah', 'right'),
                    ('Catatan', 'left')], rows, 'Belum ada pergerakan stok.', 'stock-history-table')
        deletable = {m['id']: m for m in moves if not m['transaction_id']}
        if can(user['role'], 'delete') and deletable:
            d1, d2 = st.columns([3, 1], vertical_alignment='bottom')
            picked = d1.selectbox('Hapus catatan stok', list(deletable), index=None, key=S + 'delete-pick',
                                  format_func=lambda i: f'{tgl(deletable[i]["date"])} · {deletable[i]["product_name"]}'
                                                        f' · {kg(deletable[i]["qty_kg"])}',
                                  placeholder='Pilih catatan...')
            if d2.button('Hapus', icon=':material/delete:', key=S + 'delete-button', disabled=picked is None,
                         width='stretch'):
                m = deletable[picked]
                confirm(f'Hapus catatan stok {m["product_name"]} {kg(m["qty_kg"])}?',
                        lambda: stock.delete_movement(picked), 'Catatan stok dihapus.')


def render(user: dict) -> None:
    page_header('Stok Kepiting', 'Stok berkurang otomatis saat penjualan; penjualan ditolak bila stok kurang')
    product_rows = master.list_products()
    _summary(product_rows)
    products = {p['id']: p['name'] for p in product_rows}
    left, right = st.columns([4, 8], gap='medium')
    with left:
        if can(user['role'], 'stock.create'):
            _form(user, products)
    with right:
        _history(user, products)
