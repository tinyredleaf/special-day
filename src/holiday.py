import argparse
from datetime import datetime, timezone
from xml.etree import ElementTree as ET
import requests
import pandas as pd
from src import config

def get_time():
    utc_dt = datetime.now(timezone.utc)
    dt = utc_dt.astimezone()
    return dt

def get_response_status_code(root):
    status_code = '500'
    if root.tag != 'response':
        return status_code
    for code in root.iter('resultCode'):
        status_code = code.text
    return status_code

def get_holiday_info(year, month, operation):
    month_fill = '{0:02d}'.format(int(month))

    url = '/'.join([config.PUBLIC_DATA_DOMAIN, config.PUBLIC_DATA_HOLIDAY_URI,
    operation])
    params = {
        'solYear' : year,
        'solMonth' : month_fill,
        'ServiceKey' : config.PUBLIC_DATA_PORTAL_KEY,
        'numOfRows' : config.DEFAULT_NUM_PAGE
    }

    res = requests.get(url=url, params=params)
    return res

def parse_response(root, holiday_df):
    total_count = root.find('body/totalCount')
    if total_count is not None and (total_count.text > '0') :
        for item in root.findall('body/items/item'):
            res = {'date' : item.find('locdate').text,
                'name' : item.find('dateName').text,
                'type' : item.find('dateKind').text,
                'is_holiday' : item.find('isHoliday').text
            }
            holiday_df = holiday_df.append(res, ignore_index=True)
    return holiday_df

def run(year):
    holiday_df = pd.DataFrame(columns=['date', 'name', 'type', 'is_holiday'])
    operations = [config.PUBLIC_DATA_HOLIDAY_HOLIDAY_OP, config.PUBLIC_DATA_HOLIDAY_REST_OP,
                  config.PUBLIC_DATA_HOLIDAY_ANNIVERSARY_OP, config.PUBLIC_DATA_HOLIDAY_DIVISIOM_OP,
                  config.PUBLIC_DATA_HOLIDAY_SUNDRY_OP]

    for op in operations:
        for m in range(1, 13):
            res = get_holiday_info(year, m, op)
            root =ET.fromstring(res.content)
            if get_response_status_code(root) == '00':
                holiday_df = parse_response(root, holiday_df)

    holiday_df = holiday_df.drop_duplicates()
    holiday_df = holiday_df.sort_values(by=['date'], axis=0)
    holiday_df.to_csv('holiday_{}.csv'.format(year))

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--year', required=False, default=get_time().year)
    args = parser.parse_args()
    run(args.year)