import time
from xml.etree import ElementTree
import requests

lyricsovh_api_base_url = "https://api.lyrics.ovh/v1"
musicbrainz_api_base_url = "https://musicbrainz.org/ws/2"
# xml namespaces for api
musicbrainz_ns = {'ns': 'http://musicbrainz.org/ns/mmd-2.0#',
                  'ns2': 'http://musicbrainz.org/ns/ext#-2.0'}

#todo rename input
def main(input):
    request_headers = {'method': 'GET',
                       'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko)'
                                     ' Chrome/74.0.3729.157 Safari/537.36'
                       }

    # for each artist in the payload response
    artist_id, artist_name = get_artist_id(input, request_headers)
    # print(artist_id,artist_name)
    # artist_id = 'cc197bad-dc9c-440d-a5b5-d52ba2e14234'

    tracklists = get_artist_release_groups(artist_id, request_headers)

    # this list will contain the combinations release_name, track_name, lyric_count for analysis
    dataset = []

    # for each release, for each track in tracklist
    for release in tracklists.keys():
        for track in tracklists[release]:
            lyrics_api = lyricsovh_api_base_url + '/{0}/{1}'.format(artist_name, track)

            try:
                lyrics = make_api_request(lyrics_api, request_headers).json()['lyrics']
                number_of_words = len(lyrics.split())
            except ConnectionError:
                # if we can't get the lyrics then set the data point to None (we might be able to fill it in later)
                number_of_words = None
                print("unable to get lyrics at url 404: ", lyrics_api)

            dataset.append([release, track, number_of_words])

    run_analysis(dataset)


def run_analysis(data):
    print(data)


def get_artist_id(input, headers):

    artists_api = '{0}/artist/?query=artist:{1}'.format(musicbrainz_api_base_url, input)

    matching_artists_xml = make_api_request(artists_api, headers).text
    matching_artists_root = ElementTree.fromstring(matching_artists_xml)

    near_matches = []
    artist_id = None
    artist_name = None
    #todo add testing for 1 exact match
    for artist in matching_artists_root.findall('ns:artist-list/ns:artist', musicbrainz_ns):

        # get the musicbrainz id of the artist and the name
        artist_name = artist.find('ns:name', musicbrainz_ns).text

        # if we find a matching artist then break loop
        if artist_name.lower() == input.lower():

            artist_id = artist.attrib['id']
            print('Artist Found!')
            break

        # else add near match to list to report back to user
        else:
            near_matches.append(artist_name)

    if not artist_id:
        print("Artist not found!")
        print("Did you mean one of the following? {0}".format(', '.join(near_matches)))
        raise AssertionError("Artist not found!")

    return artist_id, artist_name


def get_artist_release_groups(artist_mbid, headers):

    """
    https://musicbrainz.org/doc/Development/XML_Web_Service/Version_2
    need to perform browse style requests as linked entity requests are limited to 25 items
    using release-group entity as this is closest to an album

    Todo: if I had more time I would use a paging class to page through the results rather than use limit=100
    """
    release_group_api = '{0}/release-group?artist={1}&type=album&limit=100'.format(musicbrainz_api_base_url, artist_mbid)

    release_list_group_xml = make_api_request(release_group_api, headers).text
    release_list_group_root = ElementTree.fromstring(release_list_group_xml)

    release_list = {}
    for release in release_list_group_root.findall('ns:release-group-list/ns:release-group', musicbrainz_ns):

        # get the musicbrainz id of the release
        release_gp_id = release.attrib['id']
        release_title = release.find('ns:title', musicbrainz_ns).text

        # check this is a unique release name e.g. not a re-release
        if release_list.get(release_title):
            continue

        # Function returns an official release or None if none found
        release_id = get_official_release_id(release_gp_id, headers)

        # check we hae a valid release_id
        if not release_id:
            print(release_title, " has no official release")
            continue

        print('Release title: ', release_title)

        # get tracklist for release
        tracklist = get_release_tracks(release_id, headers)

        release_list[release_title] = tracklist

    return release_list


def get_official_release_id(artist_rg_mbid, headers):

    releases_api = '{0}/release?release-group={1}&'.format(musicbrainz_api_base_url, artist_rg_mbid)

    release_list_xml = make_api_request(releases_api, headers).text
    release_list_root = ElementTree.fromstring(release_list_xml)

    for release in release_list_root.findall('ns:release-list/ns:release', musicbrainz_ns):

        # make sure it is an official release
        release_status = release.find('ns:status', musicbrainz_ns)

        if release_status is None:
            continue

        if release_status.text == 'Official':
            return release.attrib['id']

    return None


def get_release_tracks(release_mbid, headers):

    releases_api = '{0}/release/{1}?inc=recordings'.format(musicbrainz_api_base_url, release_mbid)

    release_list_xml = make_api_request(releases_api, headers).text

    release_list_root = None
    try:
        release_list_root = ElementTree.fromstring(release_list_xml)
    except:
        print("unable to parse response")
        print(release_list_xml)

    track_list = []
    for track in release_list_root.findall('ns:release/ns:medium-list/ns:medium/ns:track-list/ns:track', musicbrainz_ns):
        track_title = track.find('ns:recording/ns:title', musicbrainz_ns).text
        track_list.append(track_title)

    return track_list


def make_api_request(url, headers):

    # try API 3 times in case of 429 error
    for x in range(1, 3):

        # Error handling for request exceptions
        try:
            time.sleep(1)
            response = requests.get(url, headers=headers)

        except requests.exceptions.HTTPError as err:
            raise requests.exceptions.HTTPError("Http Error: ", err)
        except requests.exceptions.ConnectionError as err:
            raise requests.exceptions.ConnectionError("Error Connecting: ", err)
        except requests.exceptions.Timeout as err:
            raise requests.exceptions.Timeout("Http Timeout: ", err)
        except requests.exceptions.RequestException as err:
            raise requests.exceptions.RequestException("Request Exception: ", err)

        if response.status_code == 404:
            raise ConnectionError('404 Error: ', url)
        elif response.status_code == 429:
            # https://wiki.musicbrainz.org/XML_Web_Service/Rate_Limiting
            time.sleep(1)
        else:
            return response

    raise ConnectionError('Multiple 429 Errors: ', url)


if __name__ == '__main__':
    #todo handle command line args here e.g. argparse
    input = 'Judee Sill'
    print('input: ', input)
    main(input)
