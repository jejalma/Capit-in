from typing import Callable

import streamlit as st

from security import can
from services import ServiceError
from views.components import confirm, data_table, flash, page_header


def _field(f: dict, record: dict, slug: str):
    key, label, kind = f['key'], f['label'], f.get('kind', 'text')
    value, wkey = record.get(key), f'{slug}-form-{key}'
    disabled = f.get('disabled', False)
    if kind == 'number':
        return st.number_input(label, value=float(value) if value is not None else None, min_value=0.0, step=1000.0,
                               format='%.0f', key=wkey, disabled=disabled)
    if kind == 'select':
        opts = f['options'] if isinstance(f['options'], dict) else {o: o for o in f['options']}
        keys = list(opts)
        return st.selectbox(label, keys, index=keys.index(value) if value in keys else None,
                            format_func=lambda k: opts[k], key=wkey, disabled=disabled, placeholder='Pilih...')
    if kind == 'switch':
        return st.toggle(label, value=bool(value), key=wkey)
    if kind == 'password':
        return st.text_input(label, type='password', key=wkey)
    return st.text_input(label, value=value or '', help=f.get('hint'), key=wkey, disabled=disabled)


def form_dialog(title: str, fields: list[dict], record: dict, submit: Callable[[dict], None], slug: str,
                live: Callable[[dict], None] | None = None) -> None:
    @st.dialog(title)
    def _dialog():
        values = {f['key']: _field(f, record, slug) for f in fields}
        if live:
            live(values)
        left, right = st.columns(2)
        if left.button('Batal', key=f'{slug}-form-cancel', width='stretch'):
            st.rerun()
        if right.button('Simpan', key=f'{slug}-form-submit', type='primary', width='stretch'):
            try:
                submit({**record, **values})
            except ServiceError as exc:
                st.error(str(exc))
                return
            flash('Data tersimpan.')
            st.rerun()

    _dialog()


def crud_page(user: dict, *, title: str, subtitle: str, entity: str, slug: str, defaults: dict,
              fields: Callable[[dict | None], list[dict]], load: Callable[[], list[dict]],
              save: Callable[..., int], remove: Callable[[int], None], headers: list, to_cells: Callable,
              create_perm: str = 'master.create', edit_perm: str = 'master.edit', delete_perm: str = 'delete') -> None:
    role = user['role']
    head = st.columns([5, 1], vertical_alignment='bottom')
    with head[0]:
        page_header(title, subtitle)
    if can(role, create_perm) and head[1].button('Tambah', icon=':material/add:', type='primary',
                                                  key=f'{slug}-add-button', width='stretch'):
        form_dialog(f'Tambah {entity}', fields(None), dict(defaults), lambda v: save(v), slug)
    records = load()
    with st.container(border=True):
        data_table(headers, [to_cells(r) for r in records], f'Belum ada data {entity.lower()}.', f'{slug}-table')
    allow_edit, allow_delete = can(role, edit_perm), can(role, delete_perm)
    if not records or not (allow_edit or allow_delete):
        return
    by_id = {r['id']: r for r in records}
    cols = st.columns([3, 1, 1], vertical_alignment='bottom')
    picked = cols[0].selectbox(f'Pilih {entity.lower()} untuk diubah / dihapus', list(by_id), index=None,
                               format_func=lambda i: by_id[i].get('name') or str(i), key=f'{slug}-pick',
                               placeholder='Pilih data...')
    if allow_edit and cols[1].button('Ubah', icon=':material/edit:', key=f'{slug}-edit-button',
                                     disabled=picked is None, width='stretch'):
        rec = by_id[picked]
        form_dialog(f'Ubah {entity}', fields(rec), rec, lambda v: save(v, rec['id']), slug)
    if allow_delete and cols[2].button('Hapus', icon=':material/delete:', key=f'{slug}-delete-button',
                                       disabled=picked is None, width='stretch'):
        rec = by_id[picked]
        confirm(f'Hapus {entity.lower()} "{rec.get("name")}"?', lambda: remove(rec['id']), f'{entity} dihapus.')
