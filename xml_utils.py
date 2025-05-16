from xml.etree import ElementTree as ET
import html
import streamlit as st


def format_response(response):
    try:
        escaped = response.replace("&", "&amp;")
        wrapped = f"<root>{escaped}</root>"
        root = ET.fromstring(wrapped)
        return root
    except ET.ParseError as e:
        st.error(f"XML Parsing failed: {e}")
        return None


def extract_xml(root):
    for company in root.findall('company'):
        row = {
            'Name': html.unescape(company.findtext('name')),
            'Employee Announcements and Recognition': company.findtext('recog_score'),
            'Company Events': company.findtext('events_score'),
            'Company and Mission': company.findtext('mission_score'),
            'Presentation': company.findtext('pres_score'),
            'Industry Trends and Market News': company.findtext('trends_score'),
            'Comment': company.findtext('comment').strip()
        }
        return row
