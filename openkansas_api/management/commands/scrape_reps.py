from django.core.management.base import BaseCommand
from django.contrib.gis.gdal import DataSource
from django.contrib.gis.utils import LayerMapping
from openkansas_api.models import Representative, Address, CapitalOffice, EmailAddress, Phone
from pyquery import PyQuery
import re
import sys
import os
import psycopg2

ROSTER_URLS = {
    'house': 'http://www.kslegislature.org/legsrv-house/searchHouse.do',
    'senate': 'http://www.kslegislature.org/legsrv-senate/searchSenate.do',
}


district_re = re.compile("^District (\d+)")
def extract_district(foo):
    for i in foo:
        matches = district_re.match(i)
        if not matches is None:
            return matches.groups()[0]

def return_failed_record(district, last_name):
    return "District #%s: %s" % (district, last_name)

def create_rep_doc(raw, roster_url):
    url = os.path.join(os.path.dirname(roster_url), raw.attrib['href'])
    return PyQuery(url=url)

def find_rep(raw, doc):
    last_name = raw.text_content().split(",")[0].strip()
    l = doc('center')[1].text_content().strip().split("\n")
    district = extract_district(l)

    try:
        return Representative.objects.with_district_and_last_name(district, last_name)[0]
    except IndexError:
        return return_failed_record(district, last_name)



def add_address_from_raw_data(raw_data, rep, model = Address):
    raw_data_list = raw_data.split("\n")
    city_zip = raw_data_list[1].split()
    if rep.type == "SEN":
        street_address = raw_data_list[0]
        city = raw_data_list[1].strip("Business Information")
        zipcode = 555555
    else:
        street_address, city, zipcode = raw_data_list[0], ' '.join(city_zip[0:-1]), city_zip[-1]
    address = model()
    address.street_address = street_address
    address.city = city.capitalize()
    address.zipcode = zipcode
    address.type = 'Home'
    address.representative = rep
    address.save()

def add_capital_office_email_and_committee(doc, rep):
    raw = doc("td:contains('Office')")[-1].text_content()
    # TODO: clean this up into something more elegant
    is_phone = is_office = is_email = False
    for foo in raw.strip().split():
        if is_office is True:
            is_office = "DONE"
            add_captial_office(rep, foo)
            continue
        
        if is_email is True:
            is_email = False
            add_official_email(rep, foo.strip("Committee"))
            continue

        if is_phone is True:
            is_phone = False
            add_official_phone(rep, foo)

        if foo == "Room:" and is_office != "DONE":
            is_office = True
            continue

        if foo == "Email:":
            is_email = True
            continue

        if foo == "Phone:":
            is_phone = True
            continue


    
def add_captial_office(rep, room):
    office = CapitalOffice()
    office.representative = rep
    office.room = room
    office.save()

def add_official_email(rep, email):
    email = EmailAddress.objects.create(
        representative = rep,
        email = email,
        type = "Official"
    )
    email.save()

def add_official_phone(rep, phone):
    if len(phone) == 8:
        phone = '785-' + phone
    p = Phone.objects.create(
        representative = rep,
        phone = phone,
        type = 'O',
    )
    p.save()
 
def scrape_info(raw, roster_url):

    doc = create_rep_doc(raw, roster_url)
    rep = find_rep(raw, doc)
    if rep.__class__.__name__ == 'str':
        return rep

    try:
        add_address_from_raw_data(doc("font[size=-1][color='BLACK']")[0].text_content().strip(), rep)
    except psycopg2.DataError:
        return return_failed_record(rep.district, rep.last_name)

    add_capital_office_email_and_committee(doc, rep)
    
    sys.stdout.write(".")
    sys.stdout.flush()


class Command(BaseCommand):
    def handle(self, *args, **kwargs):
        roster_url = ROSTER_URLS[args[0]]
        doc = PyQuery(url = roster_url)

        # we have to do this twice because they use presentation logic in
        # their classes and it's the most distinguishing feature to query
        # against
        l = [scrape_info(raw_entry, roster_url) for raw_entry in doc("tr .tanLine:first-child a")]
        l += [scrape_info(raw_entry, roster_url) for raw_entry in doc("tr .whiteLine:first-child a")]

        print ""
        for i in l:
            if i is not None:
                sys.stdout.write("Unable to load: %s\n" % i)


