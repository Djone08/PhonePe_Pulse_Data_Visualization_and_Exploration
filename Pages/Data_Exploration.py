import pandas as pd
import numpy as np
import streamlit as st
from Main import set_creds
import plotly.express as px


def px_bar(df: pd.DataFrame, x: str, y: str, labels: dict):
    fig = px.bar(df, x=x, y=y, title=labels[x],
                 color_discrete_sequence=['rebeccapurple'], labels=labels)
    fig.update_layout(xaxis_showgrid=True)
    st.plotly_chart(fig)


def px_map(df: pd.DataFrame, x: str, y: str, labels: dict):
    url = 'https://gist.githubusercontent.com/jbrobst/56c13bbbf9d97d187fea01ca62ea5112/raw/e388c4cae20aa53cb5090210a42ebb9b765c0a36/india_states.geojson'
    fig = px.choropleth(df, geojson=url, locations=y, featureidkey='properties.ST_NM',
                        color=x, color_continuous_scale='purp',
                        hover_name=y, title=labels[x],
                        fitbounds='locations', labels=labels)
    fig.update_geos(visible=False)
    st.plotly_chart(fig)


def px_pie(df: pd.DataFrame, x: str, y: str, labels: dict):
    fig = px.pie(df, names=y, values=x, hover_name=y, title=labels[x], hole=0.5,
                 color_discrete_sequence=np.array(px.colors.get_colorscale('purp'))[::-1, 1], labels=labels)
    st.plotly_chart(fig)


def px_line(df: pd.DataFrame, x: str, y: str, labels: dict):
    fig = px.line(df, x=x, y=y, markers=True, labels=labels)
    st.plotly_chart(fig)


def plotter(_df: pd.DataFrame, group: str, group_label: str, graphs: list, **cols):
    df = _df.groupby(group)[[*cols.keys()]].sum()
    labels = cols | {group: group_label}
    df.reset_index(inplace=True)
    st_cols = st.columns(1 if len(cols.keys()) == 1 else 2)
    _i = 0
    for col in cols:
        plot_tabs = st_cols[_i % 2].tabs(graphs)
        for i, g in enumerate(graphs):
            with plot_tabs[i]:
                if g == 'Bar Chart':
                    px_bar(df, col, group, labels)
                elif g == 'Map':
                    px_map(df, col, group, labels)
                elif g == 'Pie Chart':
                    px_pie(df, col, group, labels)
                elif g == 'Line Chart':
                    px_line(df, group, col, labels)
        _i += 1


def get_year(_min_yr: int, _max_yr: int, key: str) -> str:
    _year = st.slider('**Select the Year**', _min_yr, _max_yr, _min_yr, key=f'{key}_year')
    year_condition = f'year={_year}'
    return year_condition


def get_quarter(_q_list: list, key: str) -> str:
    q_dict = {1: 'I Quarter', 2: 'II Quarter', 3: 'III Quarter', 4: 'IV Quarter'}
    q_col = st.columns([.2, .2, .2, .2, .2])
    q_check = [q_col[x - 1].checkbox(q_dict[x], x in _q_list, disabled=x not in _q_list,
                                     key=f'{x}_{key}_quarter') for x in q_dict]
    _quarter = tuple(np.array([*q_dict.keys()])[q_check])
    if len(_quarter) == len(_q_list):
        return 'quarter'
    elif any(q_check):
        return f'quarter={_quarter[0]}' if sum(q_check) == 1 else f'quarter in {_quarter!r}'
    else:
        return ''


def get_vars(table_name: str, key: str,
             _year: bool | None = True,
             _quarters: bool | None = True,
             _state: bool | None = True):
    if _year:
        df = db.fetch_data(f'select distinct year from {table_name}')
        _year = get_year(df.year.min(), df.year.max(), key)
        yield (_year)
    if _quarters:
        q_list = db.fetch_data(f'''select distinct quarter from {table_name}
        where {_year}''').quarter.to_list()
        _quarters = get_quarter(q_list, key)
        yield (_quarters)
    if _state:
        s_list = db.fetch_data(f'''select distinct state from {table_name}
        where {year} and {_quarters}''').state.to_list()
        _state = st.selectbox('**Select the State**', ['All'] + s_list, index=0, key=f'{key}_state')
        yield (_state)
    return


db = set_creds()

tab1, tab2, tab3 = st.tabs(['Aggregated Data', 'Map Data', 'Top Data'])

with tab1:
    method = st.radio('**Select the Analysis Method**', horizontal=True, key='agg',
                      options=['Insurance Analysis', 'Transaction Analysis', 'User Analysis'])

    if method == 'Insurance Analysis':
        year, quarters = get_vars('aggregated_insurance', 'agg_i', _state=False)

        if quarters:
            _q_df = db.fetch_data(f'''select * from aggregated_insurance
            where {year} and {quarters}''')
            plotter(_q_df, 'state', 'State', ['Bar Chart', 'Map'],
                    trans_count='Transaction Count', trans_amount='Transaction Amount')
        else:
            st.error('Select Some Quarter to see Results', icon='🚨')

    elif method == 'Transaction Analysis':
        year, quarters, state = get_vars('aggregated_transaction', 'agg_t')

        if quarters:
            if state == 'All':
                _q_df = db.fetch_data(f'''select * from aggregated_transaction
                where {year} and {quarters}''')
                plotter(_q_df, 'state', 'State', ['Bar Chart', 'Map'],
                        trans_count='Transaction Count', trans_amount='Transaction Amount')
            else:
                _s_df = db.fetch_data(f'''select * from aggregated_transaction
                where {year} and {quarters} and state={state!r}''')
                plotter(_s_df, 'trans_type', 'Transaction Type', ['Bar Chart'],
                        trans_count='Transaction Count', trans_amount='Transaction Amount')
        else:
            st.error('Select Some Quarter to see Results', icon='🚨')

    elif method == 'User Analysis':
        year, quarters, state = get_vars('aggregated_user', 'agg_u')

        if quarters:
            if state == 'All':
                _q_df = db.fetch_data(f'''select * from aggregated_user
                where {year} and {quarters}''')
                plotter(_q_df, 'user_brand', 'Device Brand', ['Pie Chart', 'Bar Chart'],
                        user_count='User Count')
            else:
                _s_df = db.fetch_data(f'''select * from aggregated_user
                where {year} and {quarters} and state={state!r}''')
                plotter(_s_df, 'user_brand', 'Device Brand', ['Pie Chart', 'Line Chart'],
                        user_count='User Count')
        else:
            st.error('Select Some Quarter to see Results', icon='🚨')

with tab2:
    method_map = st.radio('**Select the Analysis Method**', horizontal=True, key='map',
                          options=['Insurance Analysis', 'Transaction Analysis', 'User Analysis'])

    if method_map == 'Insurance Analysis':
        year, quarters, state = get_vars('map_insurance', 'map_i')

        if quarters:
            if state == 'All':
                _q_df = db.fetch_data(f'''select * from map_insurance
                where {year} and {quarters}''')
                plotter(_q_df, 'state', 'State', ['Bar Chart', 'Map'],
                        trans_count='Transaction Count', trans_amount='Transaction Amount')
            else:
                _s_df = db.fetch_data(f'''select * from map_insurance
                where {year} and {quarters} and state={state!r}''')
                plotter(_s_df, 'district', 'District', ['Bar Chart', 'Pie Chart'],
                        trans_count='Transaction Count', trans_amount='Transaction Amount')
        else:
            st.error('Select Some Quarter to see Results', icon='🚨')

    elif method_map == 'Transaction Analysis':
        year, quarters, state = get_vars('map_transaction', 'map_t')

        if quarters:
            if state == 'All':
                _q_df = db.fetch_data(f'''select * from map_transaction
                where {year} and {quarters}''')
                plotter(_q_df, 'state', 'State', ['Bar Chart', 'Map'],
                        trans_count='Transaction Count', trans_amount='Transaction Amount')
            else:
                _s_df = db.fetch_data(f'''select * from map_transaction
                where {year} and {quarters} and state={state!r}''')
                plotter(_s_df, 'district', 'District', ['Bar Chart', 'Pie Chart'],
                        trans_count='Transaction Count', trans_amount='Transaction Amount')
        else:
            st.error('Select Some Quarter to see Results', icon='🚨')

    elif method_map == 'User Analysis':
        year, quarters, state = get_vars('map_user', 'map_u')

        if quarters:
            if state == 'All':
                _q_df = db.fetch_data(f'''select * from map_user
                where {year} and {quarters}''')
                plotter(_q_df, 'state', 'State', ['Line Chart', 'Map'],
                        user_count='User Count', user_opens='Apps Opened')
            else:
                _s_df = db.fetch_data(f'''select * from map_user
                where {year} and {quarters} and state={state!r}''')
                plotter(_s_df, 'district', 'District', ['Bar Chart', 'Pie Chart'],
                        user_count='User Count', user_opens='Apps Opened')
        else:
            st.error('Select Some Quarter to see Results', icon='🚨')

with tab3:
    method_top = st.radio('**Select the Analysis Method**', horizontal=True, key='top',
                          options=['Insurance Analysis', 'Transaction Analysis', 'User Analysis'])

    if method_top == 'Insurance Analysis':
        year, quarters = get_vars('top_insurance', 'top_i', _state=False)

        if quarters:
            _q_df = db.fetch_data(f'''select * from top_insurance
            where {year} and {quarters}''')
            plotter(_q_df, 'state', 'State', ['Bar Chart', 'Map'],
                    trans_count='Transaction Count', trans_amount='Transaction Amount')
        else:
            st.error('Select Some Quarter to see Results', icon='🚨')

    elif method_top == 'Transaction Analysis':
        year, quarters = get_vars('top_transaction', 'top_t', _state=False)

        if quarters:
            _q_df = db.fetch_data(f'''select * from top_transaction
            where {year} and {quarters}''')
            plotter(_q_df, 'state', 'State', ['Bar Chart', 'Map'],
                    trans_count='Transaction Count', trans_amount='Transaction Amount')
        else:
            st.error('Select Some Quarter to see Results', icon='🚨')

    elif method_top == 'User Analysis':
        year, quarters, state = get_vars('top_user', 'top_u')
        if quarters:
            if state == 'All':
                _q_df = db.fetch_data(f'''select * from top_user
                where {year} and {quarters}''')
                plotter(_q_df, 'state', 'State', ['Line Chart', 'Map'],
                        user_count='User Count')
            else:
                _s_df = db.fetch_data(f'''select * from top_user
                where {year} and {quarters} and state={state!r} and entity_type="district"''')
                plotter(_s_df, 'entity_name', 'District', ['Line Chart', 'Pie Chart'],
                        user_count='User Count')
                _s_df = db.fetch_data(f'''select * from top_user
                where {year} and {quarters} and state={state!r} and entity_type="pincode"''')
                _s_df.entity_name = _s_df.entity_name.apply(lambda x: f'📍{x}')
                plotter(_s_df, 'entity_name', 'Pincode', ['Line Chart', 'Pie Chart'],
                        user_count='User Count')

        else:
            st.error('Select Some Quarter to see Results', icon='🚨')
