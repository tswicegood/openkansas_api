openkansas_api
==============
A reusable Django app providing a means for importing and scraping data from
the Kansas legislature.

Most of the data available on websites such as kslegislature.org and
www.kansasgis.org are not aggregated into a single, user-friendly format,
not available programmatically via an API.  This application's goal is to
unlock that data from non-semantic HTML and SHP files and put into something
more usable.

Steps to re-initialize data
---------------------------
The following steps assume you have openkansas_api installed and the various
shape files available.  It also assumes you are using the default api.openkansas.org
virtualenv (todo: link to) to run the code.  If not, change path names and such
to match your system.

This first step is only necessary if you are resetting an existing environment.

    django sqlclear openkansas_api | psql openkansas
    django syncdb
    django import_shp ./resources/ks_house_08/KS_House_08.shp REP
    django import_shp ./resources/ks_senate_08/KS_Senate_08.shp SEN
    django scrape_reps house
    django scrape_reps senate

The `scrape_reps` is highly brittle and may change if kslegislature.org changes
it's structure.  Their current HTML is not semantic, so the scraper relies on
the location of data to figure out what it needs.  As of June 21st, 2009, the
output for `scrape_reps house` was:

    .....................................X.....................................
    ....................X.............................
    Unable to load: District 40:  Navinsky
    Unable to load: District 116:  Maloney

It appears that those two representatives are not currently serving, but still
listed as active in the shape file.

### Notes on scrape_reps
All scraping is a black art.  The `scrape_reps` command is no different.  Both
the House and Senate appear to use slightly different formats in how they list
addresses, which this attempts to deal with.  I'm sure there are edge cases
and the data has not been entirely validated, yet.  Please, run the scraper
and submit any patches you have that will help it run better.

This scraper is definitely a case study on why semantic markup and microformats
are such a good thing and the future of the web.  Be sure to bend the ear of
your representatives on the topic the next time you have a chance.

