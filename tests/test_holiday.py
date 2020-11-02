import pytest
import pandas as pd
from xml.etree import ElementTree as ET
from src import *
from src.holiday import *

error_holiday_res = '''<OpenAPI_ServiceResponse>
        <cmmMsgHeader>
                <returnCode>500</returnCode>
                <errMsg>게이트웨이 내부 서비스 오류</errMsg>
        </cmmMsgHeader>
</OpenAPI_ServiceResponse>'''

right_holiday_res = '''
<response><header><resultCode>00</resultCode><resultMsg>NORMAL SERVICE.</resultMsg></header><body><items><item><dateKind>01</dateKind><dateName>1월1일</dateName><isHoliday>Y</isHoliday><locdate>20200101</locdate><seq>1</seq></item><item><dateKind>01</dateKind><dateName>설날</dateName><isHoliday>Y</isHoliday><locdate>20200124</locdate><seq>1</seq></item><item><dateKind>01</dateKind><dateName>설날</dateName><isHoliday>Y</isHoliday><locdate>20200125</locdate><seq>1</seq></item><item><dateKind>01</dateKind><dateName>설날</dateName><isHoliday>Y</isHoliday><locdate>20200126</locdate><seq>1</seq></item><item><dateKind>01</dateKind><dateName>설날</dateName><isHoliday>Y</isHoliday><locdate>20200127</locdate><seq>1</seq></item></items><numOfRows>100</numOfRows><pageNo>1</pageNo><totalCount>5</totalCount></body></response>'''

right_null_res = '''<response><header><resultCode>00</resultCode><resultMsg>NORMAL SERVICE.</resultMsg></header><body><items /><numOfRows>100</numOfRows><pageNo>1</pageNo><totalCount>0</totalCount></body></response>'''

def test_get_time():
    dt = get_time()
    assert isinstance(dt.year, int)
    assert isinstance(dt.month, int)

def test_get_response_status_code():
     err_root = ET.fromstring(error_holiday_res)
     assert get_response_status_code(err_root) == '500'

     right_root = ET.fromstring(right_holiday_res)
     assert get_response_status_code(right_root) == '00'

def test_get_holiday_info():
    assert all([config.PUBLIC_DATA_DOMAIN, config.PUBLIC_DATA_HOLIDAY_URI,
    config.PUBLIC_DATA_PORTAL_KEY, config.DEFAULT_NUM_PAGE])
    assert get_holiday_info(2020, 1, config.PUBLIC_DATA_HOLIDAY_HOLIDAY_OP).status_code == 200

def test_parse_response():
    holiday_df = pd.DataFrame(columns=['date', 'name', 'type', 'is_holiday'])
    holiday_df = parse_response(ET.fromstring(right_null_res), holiday_df)
    assert len(holiday_df) == 0

    holiday_df = parse_response(ET.fromstring(error_holiday_res), holiday_df)
    assert len(holiday_df) == 0

    holiday_df = parse_response(ET.fromstring(right_null_res), holiday_df)
    assert len(holiday_df) == int(ET.fromstring(right_null_res).find('body/totalCount').text)

def test_run():
    pass