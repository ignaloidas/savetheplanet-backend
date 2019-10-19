import base64
import datetime
import itertools
import json
import netrc
import ssl
import sys
from urllib.parse import urlparse
from urllib.request import urlopen, Request, build_opener, HTTPCookieProcessor
from urllib.error import HTTPError, URLError

CMR_URL = "https://cmr.earthdata.nasa.gov"
URS_URL = "https://urs.earthdata.nasa.gov"
CMR_PAGE_SIZE = 2000
CMR_FILE_URL = (
    "{0}/search/granules.json?provider=NSIDC_ECS"
    "&sort_key[]=start_date&sort_key[]=producer_granule_id"
    "&scroll=true&page_size={1}".format(CMR_URL, CMR_PAGE_SIZE)
)


def build_version_query_params(version):
    desired_pad_length = 3
    if len(version) > desired_pad_length:
        print('Version string too long: "{0}"'.format(version))
        quit()

    version = str(int(version))  # Strip off any leading zeros
    query_params = ""

    while len(version) <= desired_pad_length:
        padded_version = version.zfill(desired_pad_length)
        query_params += "&version={0}".format(padded_version)
        desired_pad_length -= 1
    return query_params


def build_cmr_query_url(
    short_name, version, time_start, time_end, polygon=None, filename_filter=None
):
    params = "&short_name={0}".format(short_name)
    params += build_version_query_params(version)
    params += "&temporal[]={0},{1}".format(time_start, time_end)
    if polygon:
        params += "&polygon={0}".format(polygon)
    if filename_filter:
        params += "&producer_granule_id[]={0}&options[producer_granule_id][pattern]=true".format(
            filename_filter
        )
    return CMR_FILE_URL + params


def cmr_filter_urls(search_results):
    """Select only the desired data files from CMR response."""
    if "feed" not in search_results or "entry" not in search_results["feed"]:
        return []

    entries = [e["links"] for e in search_results["feed"]["entry"] if "links" in e]
    # Flatten "entries" to a simple list of links
    links = list(itertools.chain(*entries))

    urls = []
    unique_filenames = set()
    for link in links:
        if "href" not in link:
            # Exclude links with nothing to download
            continue
        if "inherited" in link and link["inherited"] is True:
            # Why are we excluding these links?
            continue
        if "rel" in link and "data#" not in link["rel"]:
            # Exclude links which are not classified by CMR as "data" or "metadata"
            continue

        if "title" in link and "opendap" in link["title"].lower():
            # Exclude OPeNDAP links--they are responsible for many duplicates
            # This is a hack; when the metadata is updated to properly identify
            # non-datapool links, we should be able to do this in a non-hack way
            continue

        filename = link["href"].split("/")[-1]
        if filename in unique_filenames:
            # Exclude links with duplicate filenames (they would overwrite)
            continue
        unique_filenames.add(filename)

        urls.append(link["href"])

    return urls


def cmr_search(short_name, version, time_start, time_end, polygon="", filename_filter=""):
    """Perform a scrolling CMR query for files matching input criteria."""
    cmr_query_url = build_cmr_query_url(
        short_name=short_name,
        version=version,
        time_start=time_start,
        time_end=time_end,
        polygon=polygon,
        filename_filter=filename_filter,
    )
    print("Querying for data:\n\t{0}\n".format(cmr_query_url))

    cmr_scroll_id = None
    ctx = ssl.create_default_context()
    ctx.check_hostname = False
    ctx.verify_mode = ssl.CERT_NONE

    try:
        urls = []
        while True:
            req = Request(cmr_query_url)
            if cmr_scroll_id:
                req.add_header("cmr-scroll-id", cmr_scroll_id)
            response = urlopen(req, context=ctx)
            if not cmr_scroll_id:
                # Python 2 and 3 have different case for the http headers
                headers = {k.lower(): v for k, v in dict(response.info()).items()}
                cmr_scroll_id = headers["cmr-scroll-id"]
                hits = int(headers["cmr-hits"])
                if hits > 0:
                    print("Found {0} matches.".format(hits))
                else:
                    print("Found no matches.")
            search_page = response.read()
            search_page = json.loads(search_page.decode("utf-8"))
            url_scroll_results = cmr_filter_urls(search_page)
            if not url_scroll_results:
                break
            if hits > CMR_PAGE_SIZE:
                print(".", end="")
                sys.stdout.flush()
            urls += url_scroll_results

        if hits > CMR_PAGE_SIZE:
            print()
        return urls
    except KeyboardInterrupt:
        quit()


def get_credentials(url, username, password):

    credentials = "{0}:{1}".format(username, password)
    credentials = base64.b64encode(credentials.encode("ascii")).decode("ascii")

    if url:
        req = Request(url)
        req.add_header("Authorization", "Basic {0}".format(credentials))
        opener = build_opener(HTTPCookieProcessor())
        opener.open(req)

    return credentials


def cmr_download(urls, username, password):
    """Download files from list of urls."""
    if not urls:
        return

    url_count = len(urls)
    print("Downloading {0} files...".format(url_count))
    credentials = None

    for index, url in enumerate(urls, start=1):
        if not credentials and urlparse(url).scheme == "https":
            credentials = get_credentials(url, username, password)

        filename = url.split("/")[-1]
        print("{0}/{1}: {2}".format(str(index).zfill(len(str(url_count))), url_count, filename))

        try:
            # In Python 3 we could eliminate the opener and just do 2 lines:
            # resp = requests.get(url, auth=(username, password))
            # open(filename, 'wb').write(resp.content)
            req = Request(url)
            if credentials:
                req.add_header("Authorization", "Basic {0}".format(credentials))
            opener = build_opener(HTTPCookieProcessor())
            data = opener.open(req).read()
            open(filename, "wb").write(data)
        except HTTPError as e:
            print("HTTP error {0}, {1}".format(e.code, e.reason))
        except URLError as e:
            print("URL error: {0}".format(e.reason))
        except IOError:
            raise
        except KeyboardInterrupt:
            quit()


def download_laser_data(
    time_start, time_end, short_name
):  # potentially add a way to select a polygon?
    username = "skielaforplanet"
    password = "skielaIgnas1"
    version = "001"
    polygon = "6.87052703409168,45.75950180667454,7.908980475880933,45.873216937619354,8.040406028586762,46.141137467117474,7.590759691992182,46.15150619813348,6.87052703409168,45.75950180667454"
    filename_filter = "*"

    urls = cmr_search(
        short_name, version, time_start, time_end, polygon=polygon, filename_filter=filename_filter
    )
    print(urls)
    return cmr_download(urls, username, password)


time_start = "2001-01-01T00:00:00Z"
time_end = datetime.datetime.now().isoformat()
short_name_photon = "ATL06"
short_name_ice = "ATL03"
download_laser_data(time_start, time_end, short_name_ice)
