import pandas as pd
import streamlit as st

from security import can
from services import ServiceError
from services import accounts as acc_service
from views.components import Html, badge_html, confirm, data_table, flash, page_header
from views.crud import form_dialog
from views.fmt import rp, rp_or_dash
from views.theme import PALETTE

CATEGORY_TONES = {'ASET': 'teal', 'KEWAJIBAN': 'ember', 'MODAL': 'sand', 'PENDAPATAN': 'moss', 'BEBAN': 'rose'}
A = 'coa-'


def balance_panel(status: dict, testid: str, compact: bool = False) -> None:
    ok = status['balanced']
    border, bg = (PALETTE['accent'], PALETTE['moss_soft']) if ok else (PALETTE['negative'], PALETTE['rose_soft'])
    size = '.88rem' if compact else '1.1rem'
    items = ''.join(f'<div><div class="k">{label}</div><div class="v" style="font-size:{size}" '
                    f'data-testid="{testid}-{key}">{rp(status[key])}</div></div>'
                    for label, key in [('Total Saldo Awal Debit', 'debit'), ('Total Saldo Awal Kredit', 'credit'),
                                       ('Selisih', 'diff')])
    note = '' if compact else ('<div style="font-size:.75rem;color:#6B7578">Saldo awal debit harus sama dengan saldo '
                               'awal kredit</div>')
    st.markdown(f'<div class="sia-panel" style="border:1px solid {border};background:{bg}" data-testid="{testid}">'
                f'{items}<div class="grow"></div><div style="text-align:right">'
                f'{badge_html("SEIMBANG" if ok else "TIDAK SEIMBANG", "moss" if ok else "rose", testid + "-badge")}'
                f'{note}</div></div>', unsafe_allow_html=True)


def _status_cell(a: dict) -> Html:
    if a['system_key']:
        return badge_html('INTI', 'teal')
    return badge_html('TERPAKAI', 'sand') if a['used'] else Html('-')


def _open_form(all_accounts: list[dict], record: dict | None = None) -> None:
    locked = bool(record) and bool(record['system_key'] or record['used'])
    fields = [
        {'key': 'category', 'label': 'Kategori', 'kind': 'select', 'options': acc_service.CATEGORIES,
         'disabled': locked},
        {'key': 'code', 'label': 'Kode akun', 'hint': 'Format X-XXXX, diawali 1 Aset, 2 Kewajiban, 3 Modal, '
                                                      '4 Pendapatan, 5 Beban', 'disabled': locked},
        {'key': 'name', 'label': 'Nama akun'},
        {'key': 'normal_balance', 'label': 'Saldo normal', 'kind': 'select', 'options': ['DEBIT', 'KREDIT'],
         'disabled': locked},
        {'key': 'opening_balance', 'label': 'Saldo awal (Rp)', 'kind': 'number'},
        {'key': 'description', 'label': 'Catatan (opsional)'},
    ]

    def live(values: dict) -> None:
        normal = values.get('normal_balance') or acc_service.DEFAULT_NORMAL.get(values.get('category'))
        preview = [a for a in all_accounts if not record or a['id'] != record['id']]
        preview.append({'id': -1, 'normal_balance': normal or 'DEBIT',
                        'opening_balance': float(values.get('opening_balance') or 0)})
        if values.get('category') and not values.get('normal_balance'):
            st.caption(f'Saldo normal umum untuk {values["category"]}: {normal}')
        if locked:
            st.caption('Akun inti / sudah dipakai di jurnal: kode, kategori & saldo normal dikunci.')
        st.markdown('<div class="sia-eyebrow">Status saldo awal setelah disimpan</div>', unsafe_allow_html=True)
        balance_panel(acc_service.opening_status(preview), 'coa-form-balance', compact=True)

    def submit(values: dict) -> None:
        if record:
            acc_service.update_account(record['id'], values)
        else:
            acc_service.create_account(values)

    form_dialog('Ubah Akun' if record else 'Tambah Akun', fields, record or {'opening_balance': 0}, submit, 'coa',
                live)


def _set_mode(mode: str) -> None:
    st.session_state[A + 'mode'] = mode
    st.session_state.pop(A + 'editor', None)


def _toolbar(role: str, all_accounts: list[dict]) -> None:
    mode = st.session_state.get(A + 'mode', 'view')
    cols = st.columns([3, 1, 1], vertical_alignment='center')
    if mode == 'opening':
        cols[0].markdown('<div style="text-align:right;color:#E07A3F;font-size:.88rem">Mode isi saldo awal — ketik '
                         'saldo pada kolom Saldo Awal</div>', unsafe_allow_html=True)
        cols[1].button('Batal', key=A + 'opening-cancel', on_click=_set_mode, args=('view',), width='stretch')
        return cols[2]
    if can(role, 'master.edit'):
        cols[1].button('Isi Saldo Awal', icon=':material/edit_note:', key=A + 'opening-mode-button',
                       on_click=_set_mode, args=('opening',), width='stretch')
    if can(role, 'master.create') and cols[2].button('Tambah', icon=':material/add:', type='primary',
                                                     key=A + 'add-button', width='stretch'):
        _open_form(all_accounts)
    return None


def _opening_editor(items: list[dict]) -> dict[int, float]:
    df = pd.DataFrame([{'id': a['id'], 'Kode': a['code'], 'Nama Akun': a['name'], 'Kategori': a['category'],
                        'Saldo Awal': float(a['opening_balance']), 'Saldo Normal': a['normal_balance']} for a in items])
    edited = st.data_editor(
        df, key=A + 'editor', hide_index=True, width='stretch', height=min(38 * (len(df) + 1) + 4, 760),
        disabled=['id', 'Kode', 'Nama Akun', 'Kategori', 'Saldo Normal'], column_order=[
            'Kode', 'Nama Akun', 'Kategori', 'Saldo Awal', 'Saldo Normal'],
        column_config={'Saldo Awal': st.column_config.NumberColumn('Saldo Awal', min_value=0, step=1000,
                                                                   format='%.0f', width='medium')})
    return {int(r['id']): float(r['Saldo Awal'] or 0) for _, r in edited.iterrows()}


def _save_opening(drafts: dict[int, float], all_accounts: list[dict]) -> None:
    status = acc_service.opening_status(all_accounts, drafts)
    try:
        acc_service.set_opening_balances(drafts)
    except ServiceError as exc:
        st.error(str(exc))
        return
    if status['balanced']:
        flash('Saldo awal tersimpan.')
    else:
        flash(f'Saldo awal tersimpan, namun belum seimbang (selisih {rp(status["diff"])}).', 'warning')
    _set_mode('view')
    st.rerun()


def _view_table(role: str, items: list[dict], all_accounts: list[dict]) -> None:
    rows = [[a['code'], a['name'], badge_html(a['category'], CATEGORY_TONES[a['category']]),
             rp_or_dash(a['opening_balance']), a['normal_balance'], _status_cell(a)] for a in items]
    data_table([('Kode', 'left'), ('Nama Akun', 'left'), ('Kategori', 'left'), ('Saldo Awal', 'right'),
                ('Saldo Normal', 'left'), ('Status', 'left')], rows, 'Belum ada akun.', 'coa-table')
    if not can(role, 'master.edit'):
        return
    by_id = {a['id']: a for a in all_accounts}
    cols = st.columns([3, 1, 1], vertical_alignment='bottom')
    picked = cols[0].selectbox('Pilih akun untuk diubah / dihapus', list(by_id), index=None, key=A + 'pick',
                               format_func=lambda i: f'{by_id[i]["code"]} · {by_id[i]["name"]}',
                               placeholder='Pilih akun...')
    if cols[1].button('Ubah', icon=':material/edit:', key=A + 'edit-button', disabled=picked is None,
                      width='stretch'):
        _open_form(all_accounts, by_id[picked])
    rec = by_id.get(picked)
    can_delete = rec is not None and can(role, 'delete') and not rec['system_key'] and not rec['used']
    if can(role, 'delete') and cols[2].button('Hapus', icon=':material/delete:', key=A + 'delete-button',
                                              disabled=not can_delete, width='stretch'):
        confirm(f'Hapus akun {rec["code"]} {rec["name"]}?', lambda: acc_service.delete_account(rec['id']),
                'Akun dihapus.')


def render(user: dict) -> None:
    role = user['role']
    all_accounts = acc_service.list_accounts()
    page_header('Bagan Akun (Chart of Accounts)',
                'Susun sendiri struktur akun dan isi saldo awalnya — status keseimbangan tampil langsung')
    save_slot = _toolbar(role, all_accounts)
    status_slot = st.empty()
    opening = st.session_state.get(A + 'mode') == 'opening'
    with st.container(border=True):
        cats = {'': 'Semua', **{c: c.title() for c in acc_service.CATEGORIES}}
        cat = st.segmented_control('Kategori', list(cats), format_func=lambda k: cats[k], default='',
                                   key=A + 'category-filter', label_visibility='collapsed')
        items = [a for a in all_accounts if not cat or a['category'] == cat]
        if opening:
            drafts = {a['id']: a['opening_balance'] for a in all_accounts}
            drafts.update(_opening_editor(all_accounts))
        else:
            _view_table(role, items, all_accounts)
    with status_slot.container():
        balance_panel(acc_service.opening_status(all_accounts, drafts if opening else None), 'coa-balance-status')
    if opening and save_slot.button('Simpan Saldo Awal', icon=':material/check:', type='primary',
                                    key=A + 'opening-save', width='stretch'):
        _save_opening(drafts, all_accounts)
