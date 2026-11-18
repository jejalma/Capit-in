import streamlit as st

from services import reports
from views.components import badge, page_header, report_block
from views.fmt import kg, rp
from views.period import Period, period_picker

INDENT = '\u2003\u2003'


def income_tab(period: Period) -> None:
    data = reports.income_statement(period.start, period.end)
    rows = [(['PENDAPATAN', ''], 'section')]
    rows += [([f'{INDENT}{r["code"]} {r["name"]}', rp(r['amount'])], '') for r in data['revenues']]
    rows += [(['Total Pendapatan', rp(data['total_revenue'])], 'bold'), (['BEBAN', ''], 'section')]
    rows += [([f'{INDENT}{r["code"]} {r["name"]}', rp(r['amount'])], '') for r in data['expenses']]
    rows += [(['Total Beban', rp(data['total_expense'])], 'bold'),
             (['LABA (RUGI) BERSIH', rp(data['net_income'])], 'bold')]
    report_block(title='Laporan Laba Rugi', subtitle=period.label, headers=[('Keterangan', 'left'), ('Jumlah', 'right')],
                 rows=rows, widths=[70, 30], filename='laporan-laba-rugi.pdf', testid='income-statement')


def balance_tab(period: Period) -> None:
    data = reports.balance_sheet(period.end)
    section = lambda items: [([f'{INDENT}{r["code"]} {r["name"]}'.rstrip(), rp(r['amount'])], '')  # noqa: E731
                             for r in items]
    rows = [(['ASET', ''], 'section'), *section(data['assets']), (['TOTAL ASET', rp(data['total_assets'])], 'bold'),
            (['KEWAJIBAN', ''], 'section'), *section(data['liabilities']),
            (['Total Kewajiban', rp(data['total_liabilities'])], 'bold'),
            (['MODAL', ''], 'section'), *section(data['equity']),
            (['Total Modal', rp(data['total_equity'])], 'bold'),
            (['TOTAL KEWAJIBAN + MODAL', rp(data['total_liabilities'] + data['total_equity'])], 'bold')]
    badge('NERACA SEIMBANG' if data['balanced'] else 'NERACA TIDAK SEIMBANG — periksa saldo awal Bagan Akun',
          'moss' if data['balanced'] else 'rose', 'balance-sheet-status')
    report_block(title='Neraca', subtitle=period.end_label, headers=[('Keterangan', 'left'), ('Jumlah', 'right')],
                 rows=rows, widths=[70, 30], filename='neraca.pdf', testid='balance-sheet')


def cash_flow_tab(period: Period) -> None:
    data = reports.cash_flow(period.start, period.end)
    rows = [(['Saldo Kas & Bank Awal', rp(data['opening'])], 'bold')]
    for sec in data['sections']:
        rows.append(([sec['title'], ''], 'section'))
        rows += [([f'{INDENT}{r["label"]}', rp(r['amount'])], '') for r in sec['rows']] or [
            ([f'{INDENT}Tidak ada arus kas', rp(0)], 'muted')]
        rows.append(([f'Kas Bersih {sec["title"].replace("Arus Kas dari ", "")}', rp(sec['total'])], 'bold'))
    rows += [(['Kenaikan (Penurunan) Kas Bersih', rp(data['net'])], 'bold'),
             (['Saldo Kas & Bank Akhir', rp(data['closing'])], 'bold')]
    report_block(title='Laporan Arus Kas', subtitle=f'{period.label} · metode langsung',
                 headers=[('Keterangan', 'left'), ('Jumlah', 'right')], rows=rows, widths=[70, 30],
                 filename='laporan-arus-kas.pdf', testid='cash-flow')


def stock_tab(period: Period) -> None:
    data = reports.stock_report(period.start, period.end)
    rows = [([r['name'], kg(r['opening']), kg(r['in']), kg(r['out']), kg(r['closing']), rp(r['price']),
              rp(r['value'])], '') for r in data['rows']]
    rows.append((['TOTAL', '', '', '', kg(data['total_kg']), '', rp(data['total_value'])], 'bold'))
    report_block(title='Laporan Stok Kepiting', subtitle=period.label,
                 headers=[('Produk', 'left'), ('Stok Awal', 'right'), ('Masuk', 'right'), ('Keluar', 'right'),
                          ('Stok Akhir', 'right'), ('Harga/kg', 'right'), ('Nilai', 'right')],
                 rows=rows, widths=[26, 12, 12, 12, 12, 12, 14], filename='laporan-stok.pdf', testid='stock-report',
                 orientation='L')


TABS = [('Laba Rugi', income_tab), ('Neraca', balance_tab), ('Arus Kas', cash_flow_tab), ('Stok', stock_tab)]


def render(user: dict) -> None:
    page_header('Laporan Keuangan', 'Laba rugi, neraca, arus kas, dan stok — siap cetak PDF')
    period = period_picker('report-period')
    for tab, (_, builder) in zip(st.tabs([label for label, _ in TABS]), TABS):
        with tab, st.container(border=True):
            builder(period)
