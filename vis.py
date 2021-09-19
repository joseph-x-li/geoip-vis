import sqlite3
import pandas as pd
import plotly.express as px
from geoip import runapi, loadgeoipdata, CACHELOCATION


def parsedb(file):
    """
    This function parses the database file and returns pandas DF
    """
    conn = sqlite3.connect(file)
    df = pd.read_sql_query("SELECT * FROM andrewafs", conn)
    return df


def truncatedate(df):
    """
    truncate date column to nearest day
    """
    df['date'] = pd.to_datetime(df['date'])
    df['date'] = df['date'].dt.date
    return df


def collatedate(df):
    """
    collate data by date, return a dictionary
    """
    df = df.groupby(['date']).agg(list)
    return df


def unique(df):
    """
    drop duplicate rows
    """
    df = df.drop_duplicates()
    return df


df = parsedb("/Users/elizabethxu/Desktop/andrewafs.db")
df = truncatedate(df)
df = unique(df)
df = collatedate(df)
df = df.drop(columns=['andrewid'])

get_geo = False
if get_geo:
    allips = df['ipaddr'].tolist()
    flattened_ips = [item for sublist in allips for item in sublist]
    unique_ips = list(set(flattened_ips))
    runapi(unique_ips)

geodata = loadgeoipdata(CACHELOCATION)


def ip2geo(ipaddrs):
    """
    map list of ips to either state if in USA, or None otherwise
    """
    retval = []
    for ip in ipaddrs:
        try:
            if geodata[ip]['country_name'] == 'United States':
                retval.append(geodata[ip]['region_code'])
            # else:
            #     retval.append(None)
        except KeyError:
            continue
            # retval.append(None)

    return retval


df = df.assign(geoip=df['ipaddr'].map(ip2geo))
df = df.drop(columns=['ipaddr'])
stcodes = ['AL', 'AK', 'AZ', 'AR', 'CA', 'CO', 'CT', 'DE', 'DC', 'FL', 'GA', 'HI', 'ID', 'IL', 'IN', 'IA', 'KS', 'KY', 'LA', 'ME', 'MD', 'MA', 'MI', 'MN', 'MS', 'MO', 'MT', 'NE', 'NV', 'NH', 'NJ', 'NM', 'NY', 'NC', 'ND', 'OH', 'OK', 'OR', 'PA', 'RI', 'SC', 'SD', 'TN', 'TX', 'UT', 'VT', 'VA', 'WA', 'WV', 'WI', 'WY']
stcodesWOPA = ['AL', 'AK', 'AZ', 'AR', 'CA', 'CO', 'CT', 'DE', 'DC', 'FL', 'GA', 'HI', 'ID', 'IL', 'IN', 'IA', 'KS', 'KY', 'LA', 'ME', 'MD', 'MA', 'MI', 'MN', 'MS', 'MO', 'MT', 'NE', 'NV', 'NH', 'NJ', 'NM', 'NY', 'NC', 'ND', 'OH', 'OK', 'OR', 'RI', 'SC', 'SD', 'TN', 'TX', 'UT', 'VT', 'VA', 'WA', 'WV', 'WI', 'WY']

# add columns using stcodes as column names
for stcode in stcodes:
    df[stcode] = 0
print(len(stcodes))

# for each row, take the geoip column and add 1 to the corresponding column
for index, row in df.iterrows():
    for stcode in row['geoip']:
        df.at[index, stcode] += 1

df = df.drop(columns=['geoip', 'PA'])
df['date'] = pd.to_datetime(df.index)
df['date'] = df['date'].apply(lambda x: str(x))

df = pd.melt(df, id_vars=['date'], value_vars=stcodesWOPA, var_name='statecode', value_name='count')


# Generate a animated graph using choropleth. Animate over index. use usa map, color red. plot state counts.
fig = px.choropleth(
    df, 
    locations='statecode', 
    color='count',
    animation_frame='date',
    color_continuous_scale='blues',
    range_color=(0, 20),
    scope='usa',
    title='CMU AFS Usage',
    locationmode='USA-states',
)

fig.show()