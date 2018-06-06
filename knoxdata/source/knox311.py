import io
import re
import datetime as dt
from collections import defaultdict

import requests_cache
from requests_html import HTML
import pandas as pd

from PyPDF2 import PdfFileReader
from PyPDF2.utils import PdfReadError


def get_knox311_dataframes():
    data = get_knox311_data()

    requests_dict_frames = {
        'dates': 'date',
        'public': 'requests.Public Service.0',
        'public_on_time': 'requests.Public Service.1',
        'solid_waste': 'requests.Solid Waste.0',
        'solid_waste_on_time': 'requests.Solid Waste.1',
        'traffic': 'requests.Traffic.0',
        'traffic_on_time': 'requests.Traffic.1',
        'civil': 'requests.Civil.0',
        'civil_on_time': 'requests.Civil.1',
        'storm_water': 'requests.Storm water.0',
        'storm_water_on_time': 'requests.Storm water.1',
        'building_inspections_zoning': 'requests.Building Inspections / Zoning.0',
        'building_inspections_zoning_on_time': 'requests.Building Inspections / Zoning.1',
        'building_inspections': 'requests.Building Inspections.0',
        'building_inspections_on_time': 'requests.Building Inspections.1',
        'zoning': 'requests.Zoning.0',
        'zoning_on_time': 'requests.Zoning.1',
        'municiple_court': 'requests.Municipal Court.0',
        'municiple_court_on_time': 'requests.Municipal Court.1',
        'codes_enforcement': 'requests.Codes Enforcement.0',
        'codes_enforcement_on_time': 'requests.Codes Enforcement.1',
        'parks_and_recreation': 'requests.Parks & Recreation.0',
        'parks_and_recreation_on_time': 'requests.Parks & Recreation.1',
        'total_service_requests': 'requests.Total Service Requests.0',
        'total_service_requests_on_time': 'requests.Total Service Requests.1',
    }

    services_dict_frames = {
        'dates': 'date',
        'codes_enforcement_lot_complaint': 'services.Codes Enforcement: Lot Complaint.0',
        'codes_enforcement_lot_complaint_days': 'services.Codes Enforcement: Lot Complaint.1',
        'solid_waste_missed_trash_pickup': 'services.Solid Waste: Missed Trash Pickup.0',
        'solid_waste_missed_trash_pickup_days': 'services.Solid Waste: Missed Trash Pickup.1',
        'municipal_court': 'services.Municipal Court.0',
        'municipal_court_days': 'services.Municipal Court.1',
        'kub_referral': 'services.KUB Referral.0',
        'kub_referral_days': 'services.KUB Referral.1',
        'abandoned_vehicle': 'services.Abandoned Vehicle.0',
        'abandoned_vehicle_days': 'services.Abandoned Vehicle.1',
        'trash_recycling_cart_issue': 'services.Trash / Recycling Cart Issues.0',
        'trash_recycling_cart_issue_days': 'services.Trash / Recycling Cart Issues.1',
        'courtesy_box_dumpster': 'services.Courtesy Box / Dumpster.0',
        'courtesy_box_dumpster_days': 'services.Courtesy Box / Dumpster.1',
        'abandoned_junk_vehicle': 'services.Abandoned / Junk Vehicle.0',
        'abandoned_junk_vehicle_days': 'services.Abandoned / Junk Vehicle.1',
        'dead_animal_pickup': 'services.Dead Animal Pick up.0',
        'dead_animal_pickup_days': 'services.Dead Animal Pick up.1',
        'public_service_courtesy_box_dumpster_request': 'services.Public Service: Courtesy Box Dumpster Request.0',
        'public_service_courtesy_box_dumpster_request_days': 'services.Public Service: Courtesy Box Dumpster Request.1',
        'codes_enforcement_structure_complaint': 'services.Codes Enforcement: Structure Complaint.0',
        'codes_enforcement_structure_complaint_days': 'services.Codes Enforcement: Structure Complaint.1',
        'codes_enforcement_abandoned_junk_vehicle': 'services.Codes Enforcement: Abandoned / Junk Vehicle.0',
        'codes_enforcement_abandoned_junk_vehicle_days': 'services.Codes Enforcement: Abandoned / Junk Vehicle.1',
        'traffic_engineering_parking_investigation': 'services.Traffic Engineering: Parking Investigation.0',
        'traffic_engineering_parking_investigation_days': 'services.Traffic Engineering: Parking Investigation.1',
        'public_service_brush_pickup_request': 'services.Public Service: Brush Pickup Request.0',
        'public_service_brush_pickup_request_days': 'services.Public Service: Brush Pickup Request.1',
        'public_service_tree_limb_removal': 'services.Public Service: Tree Limb Removal.0',
        'public_service_tree_limb_removal_days': 'services.Public Service: Tree Limb Removal.1',
    }

    statistics_dict_frames = {
        'dates': 'date',
        'end_of_month_open_requests': 'open_requests.open',
        'number_of_calls': 'statistics.Number of Calls.0',
        'average_answer_time': 'statistics.Average Answer Time.0',
        'service_quality': 'statistics.Grade of Service \( Calls answered in 20 sec or less \).0'
    }

    return {
        'requests': convert_to_pandas_frame(data, requests_dict_frames),
        'services': convert_to_pandas_frame(data, services_dict_frames),
        'statistics': convert_to_pandas_frame(data, statistics_dict_frames),
    }


def convert_to_pandas_frame(data, dict_frames):
    data_columns = defaultdict(list)
    for d in data:
        if isinstance(d['date'], dt.date):
            for key in dict_frames:
                subkey = d
                subkeys = dict_frames[key].split('.')
                for k in subkeys:
                    if k == '0':
                        if len(subkey) == 0:
                            subkey = None
                        else:
                            subkey = subkey[0]
                    elif k == '1':
                        if len(subkey) == 0:
                            subkey = None
                        else:
                            subkey = subkey[1]
                    else:
                        if subkey is not None:
                            subkey = subkey.get(k)
                data_columns[key].append(subkey)
    df = pd.DataFrame.from_dict(data_columns)
    return df.set_index('dates')

def get_knox311_data():
    BASE_URL = 'http://knoxvilletn.gov'
    cached_session = requests_cache.CachedSession()

    data = []
    for pdf_link in get_home_page_pdf_links(
            base_url=BASE_URL, session=cached_session):
        parsed_data = parse_pdf(pdf_link, session=cached_session)
        if parsed_data:
            data.append(parsed_data)
    return data


def get_home_page_pdf_links(base_url, session):
    page_home = f'{base_url}/government/city_departments_offices/311/performance_measures/'
    response = session.get(page_home)
    html = HTML(html=response.text)
    links = set()
    for a in html.find('table tbody a[href]'):
        for link in a.links:
            links.add(base_url + link)
    return links


def parse_pdf(absolute_link, session):
    response = session.get(absolute_link)
    try:
        pdf = PdfFileReader(io.BytesIO(response.content))
    except PdfReadError:
        print(f'unable to read pdf {absolute_link} --- skipping')
        return None
    full_text = ""
    for i in range(pdf.getNumPages()):
        full_text += pdf.getPage(i).extractText()

    # pdf is very messy (removing whitespace)
    full_text = full_text.replace('\n', '')
    full_text = full_text.replace('\t', '')
    #full_text = full_text.replace(' ', '')

    return {
        'url': absolute_link,
        'text': full_text,
        **extract_year_month(full_text),
        **extract_open_requests(full_text),
        **extract_table_rows(full_text)
    }


def extract_year_month(text):
    year_month_regex = r'City of Knoxville 311 Service Requests Œ? (\S+ \S* \d+)'
    matches = re.search(year_month_regex.replace(r' ', r'\s*'), text)
    if matches is None: raise ValueError(text)
    if 'Quarter' in matches.group(1):
        return {'date': matches.group(1)}
    return {'date': dt.datetime.strptime(matches.group(1), '%B %Y').date()}


def extract_open_requests(text):
    open_requests_regex = r'As of (\d+)/(\d+)/(\d+) there are still (\d+) total service'
    matches = re.search(open_requests_regex.replace(r' ', r'\s+'), text)
    if matches is None: return {}
    month, day, year, open_requests = matches.groups()
    return {
        'open_requests': {
            'asof': dt.date(month=int(month), day=int(day), year=int(year)),
            'open': int(open_requests)
        }
    }


def parse_field(text, name, fields):
    fields_regex = [name.replace(' ', '\s*')] + [field[1] for field in fields]
    matches = re.search(r'\s*'.join(fields_regex), text)
    if matches is None: return []
    return [field[0](value) for field, value in zip(fields, matches.groups())]


def extract_table_rows(text):
    int_field = (int, r'(\d+)')
    float_field = (float, r'(\d+\.?\d*)')
    percent_field = (float, r'(\d*\.?\d*)\s*%')
    def parse_comma_int(s):
        return int(s.replace(',', ''))
    comma_int_field = (parse_comma_int, r'(\d+,?\d*)')
    requests_fields = (
        (r'Public Service', (int_field, percent_field)),
        (r'Solid Waste', (int_field, percent_field)),
        (r'Traffic', (int_field, percent_field)),
        (r'Civil', (int_field, percent_field)),
        (r'Storm water', (int_field, percent_field)),
        (r'Building Inspections / Zoning', (int_field, percent_field)),
        (r'Building Inspections', (int_field, percent_field)),
        (r'Zoning', (int_field, percent_field)),
        (r'Municipal Court', (int_field, percent_field)),
        (r'Codes Enforcement', (int_field, percent_field)),
        (r'Parks & Recreation', (int_field, percent_field)),
        (r'Total Service Requests', (comma_int_field, percent_field))
    )

    top_5_service_fields = (
        (r'Codes Enforcement: Lot Complaint', (int_field, float_field)),
        (r'Solid Waste: Missed Trash Pickup', (int_field, float_field)),
        (r'Municipal Court', (int_field, float_field)),
        (r'KUB Referral', (int_field, float_field)),
        (r'Abandoned Vehicle', (int_field, float_field)),
        (r'Trash / Recycling Cart Issues', (int_field, float_field)),
        (r'Courtesy Box / Dumpster', (int_field, float_field)),
        (r'Abandoned / Junk Vehicle', (int_field, float_field)),
        (r'Dead Animal Pick up', (int_field, float_field)),
        (r'Public Service: Courtesy Box Dumpster Request', (int_field, float_field)),
        (r'Codes Enforcement: Structure Complaint', (int_field, float_field)),
        (r'Codes Enforcement: Abandoned / Junk Vehicle', (int_field, float_field)),
        (r'Traffic Engineering: Parking Investigation', (int_field, float_field)),
        (r'Public Service: Brush Pickup Request', (int_field, float_field)),
        (r'Public Service: Tree Limb Removal', (int_field, float_field)),
    )

    statistics_fields = (
        (r'Number of Calls', (comma_int_field,)),
        (r'Average Answer Time', (int_field,)),
        (r'Grade of Service \( Calls answered in 20 sec or less \)', (percent_field,))
    )

    return {
        'requests': {field[0]: parse_field(text, *field) for field in requests_fields},
        'services': {field[0]: parse_field(text, *field) for field in top_5_service_fields},
        'statistics': {field[0]: parse_field(text, *field) for field in statistics_fields},
    }
