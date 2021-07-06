import pandas as pd
from re import findall
from string import ascii_uppercase, digits

# Set pandas settings
pd.set_option('display.max_rows', None)
pd.set_option('display.max_columns', None)
pd.set_option('display.width', None)
pd.set_option('display.max_colwidth', None)
# pd.options.mode.chained_assignment = None


def get_dataframe(url_path):
    """
            The get_dataframe parses the entire table and balance date from given source.

            Parameters:
                url_path (str): The source url.

            Returns:
                dataframe (pandas.DataFrame instance): Current dataframe.
                balance_date (pandas._libs.tslibs.timestamps.Timestamp instance): The balance sheet date.
    """
    tables_list = pd.read_html(url_path,
                               flavor=['html5lib'],
                               index_col=0,
                               parse_dates=True,
                               thousands='.',
                               decimal=',',
                               displayed_only=False
                               )
    entire_df = tables_list[0]
    non_empty_index = entire_df.index.dropna()
    dataframe = entire_df.loc[non_empty_index]
    # parse dates
    long_str = dataframe.iloc[0].name
    dates = (findall(r'31\.12\.\d{4}\b', long_str))
    balance_date = pd.to_datetime(sorted(dates)[0], format='%d.%m.%Y') + pd.offsets.Day(1) - pd.offsets.Second(1)
    dataframe.drop(index=dataframe.iloc[0].name, inplace=True)
    return dataframe, balance_date


def format_columns(dataframe):
    """
            The format_columns formats the columns in the dataframe and removes unnecessary columns.

            Parameters:
                dataframe (pandas.DataFrame instance): Current dataframe.

            Returns:
                dataframe (pandas.DataFrame instance): Current dataframe.
    """
    # try to find the same index fields that can be dropped
    dataframe = dataframe.transpose()
    indexes = dataframe.index
    m_indexes_list = []
    for m_index in indexes:
        m_index = pd.array(m_index)
        m_indexes_list.append(m_index)
    num_items = len(m_indexes_list)
    template_array = m_indexes_list[0]
    try:
        array_sum = m_indexes_list[0] + m_indexes_list[1]
    except Exception as exception:
        print(exception)
    col_to_drop_list = []
    for i in range(len(template_array)):
        if array_sum[i] == template_array[i] * num_items:
            col_to_drop_list.append(i)
    # and drop them
    # dataframe = dataframe.swaplevel(0, 1, axis='index')
    dataframe = dataframe.droplevel(col_to_drop_list)
    dataframe = dataframe.reset_index()
    dataframe = dataframe.transpose()
    dataframe = dataframe.reset_index()
    return dataframe


def data_to_float(dataframe):
    """
            The data_to_float  converts all numeric values in the balance sheet item fields from object type
            to float type.
            I use this it because something going wrong with pandas.

            Parameters:
                dataframe (pandas.DataFrame instance): Current dataframe.

            Returns:
                dataframe (pandas.DataFrame instance): Current dataframe.
    """
    # I use this func because pd.to_numeric(), df.apply() and df.astype() does not work:(
    float_df = pd.DataFrame()
    for label, content in dataframe.items():
        float_content = []
        for value in content:
            try:
                value = float(value)
            except:
                value = value
            float_content.append(value)
        float_df[label] = float_content
    float_df = float_df.reset_index()
    float_df = float_df.drop(float_df.columns[0], axis=1)
    return float_df


def teur_to_eur(dataframe):
    """
            The teur_to_eur converts thousands of EUR into EUR.

            Parameters:
                dataframe (pandas.DataFrame instance): Current dataframe.

            Returns:
                dataframe (pandas.DataFrame instance): Current dataframe.
    """
    # locating titles
    df_date_currency = dataframe.iloc[0:2]
    # locating TEURO
    teur_cols = []
    for col in df_date_currency:
        if df_date_currency[col].str.contains(r'\b[T|t][E|e][U|u][R|r][O|o]?[\.]?[\d]?\b').any():
            teur_cols.append(col)
    for column in teur_cols:
        eur_values_list = []
        teuro_column = dataframe[column].values
        for value in teuro_column:
            if type(value) == float:
                eur_values_list.append(value * 1000)
            else:
                eur_values_list.append(value)
        dataframe[column] = eur_values_list
    return dataframe


def rename_columns(dataframe, balance_d, previous_d):
    """
            The rename_columns renames the date and currency columns.

            Parameters:
                dataframe (pandas.DataFrame instance): Current dataframe.
                balance_d (pandas._libs.tslibs.timestamps.Timestamp instance): Current balance date.
                previous_d (pandas._libs.tslibs.timestamps.Timestamp instance): Previous balance date.

            Returns:
                dataframe (pandas.DataFrame instance): Current dataframe.
    """
    dataframe = dataframe.drop(labels=[1], axis=0)
    for col in dataframe:
        dataframe[col] = dataframe[col].replace(regex={r'\b[T|t]?[E|e][U|u][R|r][O|o]?\.?[\d]?\b': '',
                                                       'level_0': 'titles'})
    dataframe.columns = dataframe.iloc[0]
    dataframe = dataframe.drop(dataframe.index[0])
    dataframe = dataframe.groupby(level=0, axis=1, sort=False).sum()
    try:
        dataframe.drop(labels=[''], axis=1, inplace=True)
    except:
        pass
    dataframe.rename(columns={dataframe.columns[1]: balance_d.strftime('%d.%m.%Y'),
                              dataframe.columns[2]: previous_d.strftime('%d.%m.%Y')
                              },
                     inplace=True)
    dataframe.reset_index(inplace=True)
    dataframe.drop(labels=['index'], axis=1, inplace=True)
    return dataframe


def separate_balance(dataframe):
    """
            The separate_balance separates and formats assets and liabilities.

            Parameters:
                dataframe (pandas.DataFrame instance): Current dataframe.

            Returns:
                df_asset (pandas.DataFrame instance): Current assets dataframe.
                df_liab (pandas.DataFrame instance): Current liabilities dataframe.
    """
    # separate assets and liabilities
    titles = dataframe.titles.str.lower()
    sum_rows = titles.str.contains(r'summe aktiva')
    sum_rows = titles.loc[sum_rows].keys()
    try:
        df_asset = dataframe.iloc[:sum_rows[0]]
        df_liab = dataframe.iloc[sum_rows[0] + 1: -1]
    except IndexError:
        liab_title = titles.str.contains(r'passiv')
        liab_title = titles.loc[liab_title].keys()
        df_asset = dataframe.iloc[:liab_title[0]]
        df_liab = dataframe.iloc[liab_title[0] + 1: -1]
    type_asset_rows = df_asset['titles'].where(df_asset['titles'] == 'Aktiva').dropna()
    df_asset = df_asset.drop(labels=type_asset_rows.index, axis=0)
    type_liab_rows = df_liab['titles'].where(df_liab['titles'] == 'Passiva').dropna()
    df_liab = df_liab.drop(labels=type_liab_rows.index, axis=0)
    return df_asset, df_liab


def structure_balance(dataframe, balance_type):
    """
            The structure_balance sets the desired shape of the table
            and sets the sum values for each balance division.

            Parameters:
                dataframe (pandas.DataFrame instance): Current dataframe.
                balance_type (str): The balance type. Should be either Aktiva or Passiva.

            Returns:
                df_struct (pandas.DataFrame instance): Current dataframe.
    """
    # structure dataframe
    division_markers = set(('. '.join(ascii_uppercase[0:8]) + '.').split())
    roman_nums = ['I', 'II', 'III', 'IV', 'V', 'VI', 'VII', 'VIII', 'IX', 'X']
    subdivision_markers = list(('. '.join(roman_nums) + '.').split())
    article_markers = set(('. '.join(digits) + '.').split())
    paragraphs = dataframe.titles.str.partition(expand=False)
    balance_date = dataframe.columns[1]
    balance_date_values = dataframe[balance_date].to_list()
    previous_date = dataframe.columns[2]
    previous_date_values = dataframe[previous_date].to_list()
    struct = {'type': [balance_type for i in range(len(balance_date_values))],
              'division': [None for i in range(len(balance_date_values))],
              'subdivision': [None for i in range(len(balance_date_values))],
              'article': [None for i in range(len(balance_date_values))],
              'line': [None for i in range(len(balance_date_values))],
              balance_date: balance_date_values,
              previous_date: previous_date_values}
    i = 0
    for row, content in paragraphs.iteritems():
        if content[0] in division_markers:
            div_row = row
            div = dataframe.at[div_row, 'titles']
            struct['division'][i] = div
        elif content[0] in subdivision_markers:
            subdiv_row = row
            subdiv = dataframe.at[subdiv_row, 'titles']
            struct['subdivision'][i] = subdiv
            try:
                struct['division'][i] = div
            except UnboundLocalError:
                pass
        elif content[0] in article_markers:
            art_row = row
            art = dataframe.at[art_row, 'titles']
            struct['article'][i] = art
            try:
                struct['division'][i] = div
            except UnboundLocalError:
                pass
            try:
                struct['subdivision'][i] = subdiv
            except UnboundLocalError:
                pass
        else:
            line_row = row
            line = dataframe.at[line_row, 'titles']
            struct['line'][i] = line
            try:
                struct['division'][i] = div
            except UnboundLocalError:
                pass
            try:
                struct['subdivision'][i] = subdiv
            except UnboundLocalError:
                pass
            try:
                struct['article'][i] = art
            except UnboundLocalError:
                pass
        i += 1
    # set the sum values for each division
    df_struct = pd.DataFrame.from_dict(struct)
    for div, num in df_struct.division.value_counts().iteritems():
        if num > 1:
            div_rows = df_struct.division.str.count(div)
            div_rows = div_rows.where(div_rows > 0).dropna().index.to_list()
            div_sum_row = div_rows.pop(0)
            b_d_sum = df_struct.filter(items=div_rows, axis=0)[balance_date].sum()
            p_d_sum = df_struct.filter(items=div_rows, axis=0)[previous_date].sum()
            df_struct.at[div_sum_row, balance_date] = round(b_d_sum, 2)
            df_struct.at[div_sum_row, previous_date] = round(p_d_sum, 2)
    return df_struct


def parse_balance(url):
    """
            The parse_balance performs all steps to gather the financial background from url into a dataframe.

            Parameters:
                url (pandas.DataFrame instance): Source url.

            Returns:
                df (pandas.DataFrame instance): Current dataframe.
    """
    df, current_date = get_dataframe(url)
    previous_date = current_date - pd.offsets.MonthEnd(12)
    df = format_columns(df)
    df = data_to_float(df)
    df = teur_to_eur(df)
    df = rename_columns(df, current_date, previous_date)
    asset_df, liab_df = separate_balance(df)
    asset_df = structure_balance(asset_df, 'Aktiva')
    liab_df = structure_balance(liab_df, 'Passiva')
    df = asset_df.append(liab_df)
    df.attrs['url'] = url
    return df


if __name__ == '__main__':
    pass
