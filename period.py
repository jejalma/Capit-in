from dataclasses import dataclass
from datetime import date

import streamlit as st

from services.reports import month_range
from views.fmt import tgl


@dataclass
class Period:
    start: str | None
    end: str | None

    @property
    def label(self) -> str:
        if not self.start and not self.end:
            return 'Semua periode'
        return f'Periode {tgl(self.start) if self.start else "awal"} s.d. {tgl(self.end) if self.end else "sekarang"}'

    @property
    def end_label(self) -> str:
        return f'Per {tgl(self.end)}' if self.end else 'Per hari ini'


def _preset(key: str, start: date | None, end: date | None) -> None:
    st.session_state[f'{key}-start'] = start
    st.session_state[f'{key}-end'] = end


def period_picker(key: str) -> Period:
    """Filter periode (dari–sampai) dengan tombol cepat."""
    today = date.today()
    first, last = (date.fromisoformat(d) for d in month_range(today))
    st.session_state.setdefault(f'{key}-start', first)
    st.session_state.setdefault(f'{key}-end', last)
    cols = st.columns([2, 2, 1, 1, 1], vertical_alignment='bottom')
    start = cols[0].date_input('Dari', key=f'{key}-start', format='DD/MM/YYYY')
    end = cols[1].date_input('Sampai', key=f'{key}-end', format='DD/MM/YYYY')
    cols[2].button('Bulan ini', key=f'{key}-month', on_click=_preset, args=(key, first, last),
                   width='stretch')
    cols[3].button('Tahun ini', key=f'{key}-year', on_click=_preset,
                   args=(key, date(today.year, 1, 1), date(today.year, 12, 31)), width='stretch')
    cols[4].button('Semua', key=f'{key}-all', on_click=_preset, args=(key, None, None), width='stretch')
    return Period(start.isoformat() if start else None, end.isoformat() if end else None)
