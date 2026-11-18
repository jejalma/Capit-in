from datetime import date

import streamlit as st

from security import can
from services import ServiceError, accounts, journal, reports
from views.components import badge, confirm, data_table, flash, page_header, report_block, section_title
from views.fmt import rp, rp_or_dash, tgl
from views.period import Period, period_picker

INDENT = '\u2003\u2003'
MJ = 'mj-'


def _journal_rows(data: dict) -> list:
    rows = []
    for entry in data['entries']:
        for i, ln in enumerate(entry['lines']):
            name = f'{ln["code"]} {ln["name"]}'
            rows.append(([tgl(entry['date']) if i == 0 else '', entry['ref_no'] if i == 0 else '',
                          name if ln['debit'] else INDENT + name, rp_or_dash(ln['debit']),
                          rp_or_dash(ln['credit'])], ''))
        rows.append((['', '', f'({entry["description"]})', '', ''], 'muted'))
    rows.append((['', '', 'TOTAL', rp(data['total_debit']), rp(data['total_credit'])], 'bold'))
    return rows


def general_journal_tab(period: Period) -> None:
    data = reports.general_journal(period.start, period.end)
    badge('SEIMBANG' if data['balanced'] else 'TIDAK SEIMBANG', 'moss' if data['balanced'] else 'rose',
          'general-journal-status')
    st.caption(f'{len(data["entries"])} jurnal')
    report_block(title='Jurnal Umum', subtitle=period.label,
                 headers=[('Tanggal', 'left'), ('No. Ref', 'left'), ('Akun', 'left'), ('Debit', 'right'),
                          ('Kredit', 'right')],
                 rows=_journal_rows(data), widths=[14, 13, 43, 15, 15], filename='jurnal-umum.pdf',
                 testid='general-journal')


def ledger_tab(period: Period) -> None:
    options = {a['id']: f'{a["code"]} · {a["name"]}' for a in accounts.list_accounts()}
    account_id = st.selectbox('Pilih Akun', list(options), format_func=lambda k: options[k],
                              key='ledger-account-select')
    if not account_id:
        return
    data = reports.ledger(account_id, period.start, period.end)
    acc = data['account']
    rows = [(['', '', 'Saldo Awal', '', '', rp(data['opening'])], 'section')]
    rows += [([tgl(r['date']), r['ref_no'], r['description'], rp_or_dash(r['debit']), rp_or_dash(r['credit']),
               rp(r['balance'])], '') for r in data['rows']]
    rows.append((['', '', 'Saldo Akhir', rp(data['total_debit']), rp(data['total_credit']), rp(data['closing'])],
                 'bold'))
    report_block(title=f'Buku Besar {acc["code"]} {acc["name"]}',
                 subtitle=f'{period.label} · Saldo normal {acc["normal_balance"]}',
                 headers=[('Tanggal', 'left'), ('No. Ref', 'left'), ('Keterangan', 'left'), ('Debit', 'right'),
                          ('Kredit', 'right'), ('Saldo', 'right')],
                 rows=rows, widths=[12, 11, 35, 14, 14, 14], filename=f'buku-besar-{acc["code"]}.pdf',
                 testid='ledger')


def trial_balance_tab(period: Period) -> None:
    data = reports.trial_balance(period.end)
    rows = [([r['code'], r['name'], rp_or_dash(r['debit']), rp_or_dash(r['credit'])], '') for r in data['rows']]
    rows.append((['', 'TOTAL', rp(data['total_debit']), rp(data['total_credit'])], 'bold'))
    badge('SEIMBANG' if data['balanced'] else 'TIDAK SEIMBANG', 'moss' if data['balanced'] else 'rose',
          'trial-balance-status')
    report_block(title='Neraca Saldo', subtitle=period.end_label,
                 headers=[('Kode', 'left'), ('Nama Akun', 'left'), ('Debit', 'right'), ('Kredit', 'right')],
                 rows=rows, widths=[12, 48, 20, 20], filename='neraca-saldo.pdf', testid='trial-balance')


# ---------- jurnal manual ----------
def _line_ids() -> list[int]:
    return st.session_state.setdefault(MJ + 'lines', [0, 1])


def _add_line() -> None:
    ids = _line_ids()
    ids.append(max(ids) + 1)


def _remove_line(i: int) -> None:
    ids = _line_ids()
    if len(ids) > 2:
        ids.remove(i)


def _lines() -> list[tuple]:
    s = st.session_state
    return [(s.get(f'{MJ}{i}-account'), float(s.get(f'{MJ}{i}-debit') or 0), float(s.get(f'{MJ}{i}-credit') or 0))
            for i in _line_ids()]


def _save_manual(user_id: int) -> None:
    s = st.session_state
    d = s.get(MJ + 'date')
    try:
        journal.create_manual_entry(d.isoformat() if d else None, s.get(MJ + 'description', ''), _lines(), user_id)
    except ServiceError as exc:
        s[MJ + 'error'] = str(exc)
        return
    for key in [k for k in s.keys() if str(k).startswith(MJ)]:
        del s[key]
    flash('Jurnal manual tersimpan.')


def manual_editor(user: dict) -> None:
    with st.container(border=True):
        section_title('Jurnal Manual / Penyesuaian', 'Untuk penyusutan, koreksi, atau transaksi di luar menu')
        c1, c2 = st.columns([1, 3])
        c1.date_input('Tanggal', value=date.today(), key=MJ + 'date', format='DD/MM/YYYY')
        c2.text_input('Keterangan', key=MJ + 'description')
        options = {a['id']: f'{a["code"]} · {a["name"]}' for a in accounts.list_accounts()}
        for n, i in enumerate(_line_ids()):
            cols = st.columns([5, 2, 2, 1], vertical_alignment='bottom')
            cols[0].selectbox(f'Akun baris {n + 1}', list(options), format_func=lambda k: options[k], index=None,
                              key=f'{MJ}{i}-account', placeholder='Pilih akun...')
            cols[1].number_input('Debit', min_value=0.0, step=1000.0, format='%.0f', value=None, key=f'{MJ}{i}-debit')
            cols[2].number_input('Kredit', min_value=0.0, step=1000.0, format='%.0f', value=None,
                                 key=f'{MJ}{i}-credit')
            cols[3].button('', icon=':material/close:', key=f'{MJ}{i}-remove', on_click=_remove_line, args=(i,),
                           help='Hapus baris')
        lines = _lines()
        debit, credit = round(sum(ln[1] for ln in lines), 2), round(sum(ln[2] for ln in lines), 2)
        balanced = debit == credit and debit > 0
        b1, b2 = st.columns([1, 3], vertical_alignment='center')
        b1.button('Tambah Baris', icon=':material/add:', key=MJ + 'add-line-button', on_click=_add_line)
        with b2:
            st.markdown(f'<div style="text-align:right;font-family:monospace;font-size:.88rem">'
                        f'<span style="color:#0F4C5C">Debit {rp(debit)}</span> &nbsp; '
                        f'<span style="color:#E07A3F">Kredit {rp(credit)}</span> &nbsp; '
                        f'<span data-testid="mj-balance-status">'
                        f'{"SEIMBANG" if balanced else "SELISIH " + rp(abs(debit - credit))}</span></div>',
                        unsafe_allow_html=True)
        st.button('Simpan Jurnal', icon=':material/check:', type='primary', key=MJ + 'submit-button',
                  on_click=_save_manual, args=(user['id'],))
        if st.session_state.get(MJ + 'error'):
            st.error(st.session_state.pop(MJ + 'error'), icon=':material/error:')


def manual_list(user: dict, period: Period) -> None:
    data = reports.general_journal(period.start, period.end)
    manual = [e for e in data['entries'] if e['source'] == 'MANUAL']
    with st.container(border=True):
        section_title('Riwayat Jurnal Manual', period.label)
        data_table([('Tanggal', 'left'), ('No. Ref', 'left'), ('Keterangan', 'left'), ('Nilai', 'right')],
                   [[tgl(e['date']), e['ref_no'], e['description'], rp(sum(ln['debit'] for ln in e['lines']))]
                    for e in manual], 'Belum ada jurnal manual pada periode ini.', 'mj-table')
        if can(user['role'], 'delete') and manual:
            by_id = {e['id']: e for e in manual}
            d1, d2 = st.columns([3, 1], vertical_alignment='bottom')
            picked = d1.selectbox('Hapus jurnal manual', list(by_id), index=None, key='mj-delete-pick',
                                  format_func=lambda i: f'{by_id[i]["ref_no"]} · {by_id[i]["description"]}',
                                  placeholder='Pilih jurnal...')
            if d2.button('Hapus', icon=':material/delete:', key='mj-delete-button', disabled=picked is None,
                         width='stretch'):
                confirm(f'Hapus jurnal {by_id[picked]["ref_no"]}?', lambda: journal.delete_manual_entry(picked),
                        'Jurnal dihapus.')


def render(user: dict) -> None:
    page_header('Jurnal & Buku Besar', 'Semua jurnal tercatat otomatis dari transaksi')
    period = period_picker('journal-period')
    allow_manual = can(user['role'], 'journal.manual')
    labels = ['Jurnal Umum', 'Buku Besar', 'Neraca Saldo'] + (['Jurnal Manual'] if allow_manual else [])
    tabs = st.tabs(labels)
    with tabs[0], st.container(border=True):
        general_journal_tab(period)
    with tabs[1], st.container(border=True):
        ledger_tab(period)
    with tabs[2], st.container(border=True):
        trial_balance_tab(period)
    if allow_manual:
        with tabs[3]:
            manual_editor(user)
            manual_list(user, period)
