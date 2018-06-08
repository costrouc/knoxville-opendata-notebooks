import datetime as dt
import json

import requests
import pandas as pd



QUERY_STRING = {
    "modes": [{"id": 1}],
    "endDate": 1528430400000,
    "centerLon": -83.9207392,
    "pageSize": None,
    "limitBy": 500,
    "analytics": [
        {"width": 0, "id": 3, "position": 1, "height": 0},
        {"width": 0, "id": 50,"position": 2, "height": 0},
        {"width": 0, "id": 59, "position": 3, "height": 0},
        {"width": 0, "id": 74, "position": 4, "height": 0}
    ],
    "dataRelation": "Primary",
    "gridStatStamp": None,
    "pageStart": None,
    "keywordOption": "notes",
    "zoom": 10,
    "filters": [],
    "viewAttributeVersion": 0,
    "viewIteration": 55,
    "polygon": {
        "valid": True,
        "minLon": -84.9015264772217,
        "maxLat": 36.390817111448854,
        "centroid": {
            "x": -83.92099669206544,
            "y": 35.96455923637623,
            "class": "com.bairinc.raids.model.dataview.polygon.RaidsPolygon$Point"
        },
        "minLat": 35.53830136130361,
        "centerLon": -83.92099669206544,
        "maxLon": -82.9404669069092,
        "alias": "box",
        "centerLat": 35.96455923637623,
        "draw": False
    },
    "sortingClause": [
        {
            "pos": 0,
            "attribute": {
                "mode": {
                    "classificationGroupName": None,
                    "display": "Event",
                    "relational": False,
                    "id": 1,
                    "customClassificationProcessor": False
                },
                "viewId": "view62",
                "displayName": "Date",
                "dataViewName": "Date",
                "id": 62,
                "hpccWildCardSupport": False,
                "derived": False
            },
            "order": False
        },
        {
            "pos": 1,
            "attribute": {
                "mode": {
                    "classificationGroupName": None,
                    "display": "Offenders",
                    "relational": False,
                    "id": 3,
                    "customClassificationProcessor": False
                },
                "viewId": "view509",
                "displayName": "First Name",
                "dataViewName": "First Name",
                "id": 509,
                "hpccWildCardSupport": False,
                "derived": False
            },
            "order": False
        }
    ],
    "dataViewName": "grid",
    "singleMode": None,
    "centerLat": 35.9606384,
    "page": [
        {
            "mode": {
                "classificationGroupName": None,
                "customClassificationProcessor": False,
                "display": "Event",
                "id": 1,
                "relational": False
            },
            "page": 1,
            "pageCount": 0,
            "pageSize": 500,
            "recordCount": 0
        },
        {
            "mode": {
                "classificationGroupName": None,
                "customClassificationProcessor": False,
                "display": "Offenders",
                "id": 3,
                "relational": False
            },
            "page": 0,
            "pageCount": 0,
            "pageSize": 1,
            "recordCount": 0
        }
    ],
    "user": {
        "firstName": None,
        "lastName": None,
        "roles": [
            {
                "productId": None,
                "name": "user"
            }
        ],
        "dataProviderId": -1,
        "userID": -1,
        "email": "public@communitycrimemap.com",
        "singleSignOnEntityId": None
    },
    "filterIterator": {},
    "startDate": 1528257600000,
    "classfications": [
        {"mode": {"id": 1}, "id": 8},
        {"mode": {"id": 1}, "id": 20},
        {"mode": {"id": 1}, "id": 27},
        {"mode": {"id": 1}, "id": 26},
        {"mode": {"id": 1}, "id": 18},
        {"mode": {"id": 1}, "id": 9},
        {"mode": {"id": 1}, "id": 2},
        {"mode": {"id": 1}, "id": 10},
        {"mode": {"id": 1}, "id": 11},
        {"mode": {"id": 1}, "id": 17},
        {"mode": {"id": 1}, "id": 19},
        {"mode": {"id": 1}, "id": 3},
        {"mode": {"id": 1}, "id": 22},
        {"mode": {"id": 1}, "id": 21},
        {"mode": {"id": 1}, "id": 13},
        {"mode": {"id": 1}, "id": 1},
        {"mode": {"id": 1}, "id": 16},
        {"mode": {"id": 1}, "id": 6},
        {"mode": {"id": 1}, "id": 7},
        {"mode": {"id": 1}, "id": 4},
        {"mode": {"id": 1}, "id": 5},
        {"mode": {"id": 1}, "id": 14},
        {"mode": {"id": 1}, "id": 12},
        {"mode": {"id": 1}, "id": 15},
        {"mode": {"id": 1}, "id": 23},
        {"mode": {"id": 1}, "id": 24},
        {"mode": {"id": 1}, "id": 25}
    ],
    "primary": True
}


def get_and_write_crime_dateframes(years=10):
    craweled_dates = {}
    session = requests.session()
    session.get('http://communitycrimemap.com/?address=Knoxville,TN') # initialize cookies

    for i in range(years * 365):
        start_date = dt.date.today() - dt.timedelta(days=i)
        if start_date in craweled_dates:
            continue
        craweled_dates[start_date] = crawl_crime_page_for_date(start_date, session)

    view_map = {
        'view34': 'incident',
        'view35': 'crime',
        'view36': 'location',
        'view62': 'datetime',
        'view82': 'latitude',
        'view81': 'longitude',
        'view96': 'address',
        'view85': 'accuracy',
        'view86': 'image',
        'view84': 'agency',
        'view182': 'date',
    }
    df = pd.concat(list(craweled_dates.values())).rename(columns=view_map)
    df['date'] = pd.to_datetime(df['date'], format="%m/%d/%Y")
    df['datetime'] = pd.to_datetime(df['datetime'], format="%b %d, %Y %I:%M %p")
    df.drop('image', axis=1, inplace=True)
    df.to_csv('../data/crime/crime.csv')
    return df


def crawl_crime_page_for_date(start_date, session):
    def datetime_to_intsec(datetime):
        return int((datetime - dt.date(year=1970, month=1, day=1)).total_seconds() * 1000)

    QUERY_STRING['startDate'] = datetime_to_intsec(start_date)
    QUERY_STRING['endDate'] = datetime_to_intsec(start_date + dt.timedelta(days=1))
    data = []

    # crawl initial page
    QUERY_STRING['page'][0]['page'] = 0
    QUERY_STRING['page'][0]['pageSize'] = 20

    response = session.post(
        'http://communitycrimemap.com/Protected/RAIDS/Data/DataGrid.serv',
        data={'dataView': json.dumps(QUERY_STRING)},
        headers={'content-type': 'application/x-www-form-urlencoded'}
    )
    response_data = response.json()
    data.extend(response_data['dataEvents'])
    total_num_records = response_data['totalRecordCount']

    for i in range(21, total_num_records, 20):
        QUERY_STRING['page'][0]['page'] = i
        response = session.post(
            'http://communitycrimemap.com/Protected/RAIDS/Data/DataGrid.serv',
            data={'dataView': json.dumps(QUERY_STRING)},
            headers={'content-type': 'application/x-www-form-urlencoded'}
        )
        response_data = response.json()
        data.extend(response_data['dataEvents'])

    df = pd.DataFrame(data)
    return df.set_index('view34')
