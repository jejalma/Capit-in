from datetime import date

import streamlit as st

from security import can
from services import ServiceError, accounts, master
from services import transactions as tx
from views.components import Html, badge_html, confirm, data_table, flash, page_header, section_title
from views.fmt import kg, rp, tgl
from views.pages.dashboard import type_badge

TYPE_DEFAULTS = {'PAKAN': {'qty': 5.0, 'unit_price': 10000.0}, 'GAJI': {'qty': 1.0}}
FIELDS = ['collector_id', 'product_id', 'employee_id', 'account_id', 'qty', 'unit_price', 'amount', 'note', 'payment']
K = 'tx-'


def _reset_fields() -> None:
    t = st.session_state.get(K + 'type', 'PENJUALAN')
    for f in FIELDS:
        st.session_state.pop(K + f, None)
    for f, v in TYPE_DEFAULTS.get(t, {}).items():
        st.session_state[K + f] = v


def _state() -> dict:
    s = st.session_state
    data = {f: s.get(K + f) for f in FIELDS}
    data.update(type=s.get(K + 'type', 'PENJUALAN'), payment=data['payment'] or 'kas', note=data['note'] or '')
    d = s.get(K + 'date')
    data['date'] = d.isoformat() if d else None
    return data


def _pick_product(products: dict) -> None:
    pid = st.session_state.get(K + 'product_id')
    if pid:
        st.session_state[K + 'unit_price'] = float(products[pid]['price_per_kg'])


def _save(user_id: int) -> None:
    data = _state()
    try:
        result = tx.record(data['type'], data, user_id)
    except ServiceError as exc:
        st.session_state[K + 'error'] = str(exc)
        return
    st.session_state.pop(K + 'error', None)
    flash(f'Transaksi {result["ref_no"]} tersimpan dan dijurnal.')
    _reset_fields()


def _select(label: str, options: dict, field: str, **kw):
    keys = list(options)
    return st.selectbox(label, keys, format_func=lambda k: options[k], index=None, key=K + field,
                        placeholder='Pilih...', **kw)


def _num(label: str, field: str, step: float = 1.0) -> None:
    extra = {} if K + field in st.session_state else {'value': None}
    st.number_input(label, min_value=0.0, step=step, format='%.0f' if step >= 1 else '%.1f', key=K + field, **extra)


def _fields() -> None:
    t = st.session_state.get(K + 'type', 'PENJUALAN')
    st.date_input('Tanggal', value=date.today(), key=K + 'date', format='DD/MM/YYYY')
    if t in ('PENJUALAN', 'PENERIMAAN_PIUTANG'):
        _select('Pengepul', {c['id']: c['name'] + (f'  ·  piutang {rp(c["receivable"])}' if c['receivable'] else '')
                             for c in master.list_collectors()}, 'collector_id')
    if t == 'PENJUALAN':
        products = {p['id']: p for p in master.list_products()}
        _select('Produk Kepiting', {k: f'{p["name"]}  ·  stok {kg(p["stock_kg"])}' for k, p in products.items()},
                'product_id', on_change=_pick_product, args=(products,))
        c1, c2 = st.columns(2)
        with c1:
            _num('Jumlah (kg)', 'qty', 0.5)
        with c2:
            _num('Harga per kg', 'unit_price', 1000.0)
    if t == 'PAKAN':
        c1, c2 = st.columns(2)
        with c1:
            _num('Ikan rucah (kg)', 'qty', 0.5)
        with c2:
            _num('Harga per kg', 'unit_price', 1000.0)
    if t == 'GAJI':
        _select('Karyawan', {e['id']: f'{e["name"]}  ·  {rp(e["daily_wage"])}/hari'
                             for e in master.list_employees(active_only=True)}, 'employee_id')
        _num('Jumlah hari kerja', 'qty')
    if t == 'OPERASIONAL':
        _select('Akun Beban', {a['id']: f'{a["code"]} · {a["name"]}' for a in accounts.list_accounts('BEBAN')},
                'account_id')
    if t in ('OPERASIONAL', 'MODAL', 'PRIVE', 'PENERIMAAN_PIUTANG'):
        _num('Nominal (Rp)', 'amount', 1000.0)
    payments = {k: v for k, v in tx.PAYMENTS.items() if k != 'piutang' or t == 'PENJUALAN'}
    if st.session_state.get(K + 'payment') not in payments:
        st.session_state[K + 'payment'] = 'kas'
    st.selectbox('Kas / Bank' if t != 'PENJUALAN' else 'Metode Pembayaran', list(payments),
                 format_func=lambda k: payments[k], key=K + 'payment')
    st.text_input('Keterangan (opsional)', key=K + 'note')


def _preview() -> None:
    data = _state()
    try:
        draft = tx.preview(data['type'], data)
    except ServiceError as exc:
        st.markdown(f'<div class="sia-preview" data-testid="tx-preview"><div class="sia-eyebrow">Pratinjau Jurnal'
                    f'</div><div data-testid="tx-preview-message" style="color:#6B7578;font-size:.88rem;'
                    f'margin-top:6px">{exc}</div></div>', unsafe_allow_html=True)
        return
    lines = ''.join(
        f'<div class="sia-line" style="{"" if ln["debit"] else "padding-left:24px"}"><span>{ln["code"]}  {ln["name"]}'
        f'</span><span class="num" style="font-family:monospace;color:{"#0F4C5C" if ln["debit"] else "#E07A3F"}">'
        f'{"Dr " if ln["debit"] else "Cr "}{rp(ln["debit"] or ln["credit"])}</span></div>' for ln in draft['lines'])
    st.markdown(f'<div class="sia-preview" data-testid="tx-preview"><div style="display:flex;justify-content:'
                f'space-between"><span class="sia-eyebrow">Pratinjau Jurnal</span>{badge_html("SEIMBANG", "moss")}'
                f'</div><div class="total" data-testid="tx-preview-total">{rp(draft["amount"])}</div>{lines}</div>',
                unsafe_allow_html=True)


def _form(user: dict) -> None:
    with st.container(border=True):
        section_title('Catat Transaksi Baru', 'Jurnal debit/kredit dibuat otomatis saat disimpan')
        types = {k: v[0] for k, v in tx.TYPES.items()}
        st.selectbox('Jenis Transaksi', list(types), format_func=lambda k: types[k], key=K + 'type',
                     on_change=_reset_fields)
        _fields()
        _preview()
        st.button('Simpan Transaksi', icon=':material/check:', type='primary', key=K + 'submit-button',
                  on_click=_save, args=(user['id'],), width='stretch')
        if st.session_state.get(K + 'error'):
            st.error(st.session_state[K + 'error'], icon=':material/error:')


def _list(user: dict) -> None:
    with st.container(border=True):
        section_title('Daftar Transaksi')
        types = {'': 'Semua jenis', **{k: v[0] for k, v in tx.TYPES.items()}}
        c1, c2, c3 = st.columns(3)
        t = c1.selectbox('Jenis', list(types), format_func=lambda k: types[k], key='tx-filter-type')
        start = c2.date_input('Dari', value=None, key='tx-filter-start', format='DD/MM/YYYY')
        end = c3.date_input('Sampai', value=None, key='tx-filter-end', format='DD/MM/YYYY')
        search = st.text_input('Cari keterangan / no. ref', key='tx-filter-search')
        items = tx.list_transactions(t or None, start.isoformat() if start else None,
                                     end.isoformat() if end else None, search)
        st.markdown(f'<div style="font-size:.75rem;color:#6B7578" data-testid="tx-list-summary">{len(items)} transaksi'
                    f' · total {rp(sum(i["amount"] for i in items))}</div>', unsafe_allow_html=True)
        rows = [[tgl(i['date']), i['ref_no'], type_badge(i['type']), i['description'], Html(rp(i['amount']))]
                for i in items]
        data_table([('Tanggal', 'left'), ('No. Ref', 'left'), ('Jenis', 'left'), ('Keterangan', 'left'),
                    ('Nilai', 'right')], rows, 'Belum ada transaksi.', 'tx-table')
        if can(user['role'], 'delete') and items:
            by_id = {i['id']: i for i in items}
            d1, d2 = st.columns([3, 1], vertical_alignment='bottom')
            picked = d1.selectbox('Hapus transaksi', list(by_id), index=None, key='tx-delete-pick',
                                  format_func=lambda i: f'{by_id[i]["ref_no"]} · {by_id[i]["description"]}',
                                  placeholder='Pilih transaksi...')
            if d2.button('Hapus', icon=':material/delete:', key='tx-delete-button', disabled=picked is None,
                         width='stretch'):
                ref = by_id[picked]['ref_no']
                confirm(f'Hapus transaksi {ref}? Jurnal dan pergerakan stoknya ikut terhapus.',
                        lambda: tx.delete_transaction(picked), 'Transaksi dihapus.')


def render(user: dict) -> None:
    page_header('Transaksi', 'Penjualan kepiting, pakan, gaji, beban operasional, modal & prive')
    left, right = st.columns([5, 7], gap='medium')
    with left:
        _form(user)
    with right:
        _list(user)
