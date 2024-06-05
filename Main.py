from functools import wraps
import pandas as pd
from typing import Literal, Callable
import sqlite3
import mysql.connector as db
import streamlit as st


class DataBase(object):
    def __init__(self, db_type: Literal['sqlite', 'mysql'] | None = 'sqlite', host: str | None = None,
                 user: str | None = None, password: str | None = None, port: int | None = None,
                 schema: str | None = None, data_base_path: str | None = None):
        self.db_type = db_type

        if self.db_type == 'mysql':
            self.db = db.connect(host=host, user=user, password=password, port=port)
        elif self.db_type == 'sqlite':
            self.db_path = data_base_path or 'database.db'
            self.db = sqlite3.connect(self.db_path)

        self.cur = self.db.cursor()
        if self.db_type == 'mysql':
            self.cur.execute(f'create database if not exists {schema}')
            self.cur.execute(f'use {schema}')
        self.cur.close()

    @staticmethod
    def with_cursor(func: Callable) -> Callable:
        @wraps(func)
        def wrapper_func(self, *args, **kwargs):
            if self.db_type == 'sqlite':
                self.db = sqlite3.connect(self.db_path)
            self.cur = self.db.cursor()
            if self.db_type == 'sqlite':
                self.cur.execute('pragma foreign_keys = 1')
            value = func(self, *args, **kwargs)
            self.cur.close()
            if self.db_type == 'sqlite':
                self.db.close()
            return value
        return wrapper_func

    def insert_data(self, _table_name: str, **kwargs):
        _data = tuple(x for x in kwargs.values())
        _cols = ','.join(x for x in kwargs)
        if self.db_type == 'sqlite':
            _data_filler = ('?,' * len(_data))[:-1]
            self.cur.execute(f'insert into {_table_name} ({_cols}) values ({_data_filler})', _data)
        elif self.db_type == 'mysql':
            self.cur.execute(f'insert into {_table_name} ({_cols}) values {_data}')
        self.db.commit()

    def update_data(self, _table_name: str, **kwargs):
        if self.db_type == 'sqlite':
            _data = list(kwargs.values())
            _data_filler = ','.join([f'{x}=?' for x in kwargs if x != 'id'])
            self.cur.execute(f'update {_table_name} set {_data_filler} where id = {_data[0]!r}', _data[1:])
        elif self.db_type == 'mysql':
            _data = [f'{a}={b!r}' for a, b in zip(kwargs.keys(), kwargs.values())]
            self.cur.execute(f'update {_table_name} set {",".join(_data[1:])} where {_data[0]}')
        self.db.commit()

    @with_cursor
    def fetch_data(self, query: str):
        self.cur.execute(query)
        data = self.cur.fetchall()
        cols = [x[0] for x in self.cur.description]
        return pd.DataFrame(data, columns=cols)

    @with_cursor
    def execute(self, query: str):
        self.cur.execute(query)
        self.db.commit()


def set_creds() -> DataBase:
    st.session_state['db_creds'] = st.session_state.get('db_creds') or dict(st.secrets.PulseDataBase)
    _db = st.session_state.get('db') or DataBase(**st.session_state.db_creds)
    st.session_state['db'] = _db
    return _db


if __name__ == '__main__':
    db = set_creds()
    '''
    # :violet[Data Visualization and Exploration]
    ## :violet[A User-Friendly Tool Using Streamlit and Plotly]
    
    
    ### :violet[Domain :] Fintech
    ### :violet[Technologies used :] Github Cloning, Python, Pandas, MySQL, mysql-connector-python,
    ### Streamlit, and Plotly.
    ### :violet[Overview :] In this .streamlit web app you can visualize the phonepe pulse data 
    ### and gain lot of insights on transactions, number of users, top 10 state, district, pincode 
    ### and which brand has most number of users and so on. Bar charts, Pie charts and Geo map visualization 
    ### are used to get some insights.'''
