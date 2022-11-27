import re
import json
import pandas as pd
import numpy as np
import requests

# 提取OCR导出文件中的地名
with open('loc_name_from_ocr.txt', 'r') as file:
    loc_name = file.read().replace('\n', '')
    file.close()
pattern = re.compile("[\u4e00-\u9fa5]+")
loc_list = pattern.findall(loc_name)

# 将地名和地理编码变为结构化文本
df = pd.DataFrame(loc_list, columns=['location_name'])
df.index = np.arange(1, len(df) + 1)

# 高德地图web API正地理编码查询


def geocode():
    # 高德地图web API正地理编码查询
    key = ''  # 在这里填写高德Web服务API KEY
    base = 'https://restapi.amap.com/v3/geocode/geo'
    location_list = []
    for i in loc_list:
        para = {'address': i, 'key': key, 'city': '北京'}
        try:
            reqs = requests.get(base, para)
            json_info = json.loads(reqs.text)
            loc = json_info['geocodes'][0]['location']
            location_list.append(loc)
        except:
            location_list.append('null')
    df['geocodes_location'] = location_list
    df.to_csv('raw.csv')
    return 'raw.csv'


geocode()

# 删除没有坐标的题目 + 添加缺失值
df = pd.read_csv('raw.csv')
df.set_index('location_name', inplace=True)
df.drop(['人儿', '油画', '剪贴', '彩墨', '邮', '缘', '东陵',
        '怀仁堂', '献花', '西市'], axis=0, inplace=True)
df.drop(labels='Unnamed: 0', axis=1, inplace=True)
df.at['故宫', 'geocodes_location'] = '116.397026,39.918058'  # 故宫博物院
df.at['象来街', 'geocodes_location'] = '116.365138,39.899030'  # 象来街招待所
# df.to_csv('cleaned.csv')

# 分开经纬度放入独立行
l = df['geocodes_location'].values.tolist()
# l = df['geocodes_location'].fillna('0,0').values.tolist()
# 考虑到可以将空缺值坐标改为0,0方便删除，但上文已经手动删除空缺值了。


def split_coords():
    x_list = []
    y_list = []
    for i in l:
        x = i.split(',')[0]
        y = i.split(',')[1]
        x_list.append(x)
        y_list.append(y)
    df['x'] = x_list
    df['y'] = y_list
    df.to_csv('cleaned_with_xy.csv')
    return 'cleaned_with_xy.csv'


split_coords()

# 计划出行路线
other_loc = {'name': ['北京大学人民医院白塔寺院区', '什刹海街道政务服务中心', '地安门桥', '帽儿胡同'], 'loc': ['116.366224,39.924753',
                                                                               '116.380275,39.93399'], 'note': ['出生地', '工作地', '1993年最后的北京行前往地安门桥下书店', '1993年最后的北京行提到想去朋友居住的胡同的帽子店']}
odf = pd.DataFrame(other_loc)

# 逆地理编码


def reverse_geocode():
    # 高德地图web API逆地理编码查询
    key = ''  # 在这里填写高德Web服务API KEY
    base = 'https://restapi.amap.com/v3/geocode/regeo?parameters'
    para = {'location': '116.361789261904747,39.933887761904771',
            'key': key, 'city': '北京'}
    reqs = requests.get(base, para)
    json_info = json.loads(reqs.text)
    return json_info


reverse_geocode()

# 逆地理编码结果包括 'building': {'name': '中国儿童中心少儿国学院', 'type': '科教文化服务;学校;学校'},
