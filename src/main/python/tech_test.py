import time
from xml.etree import ElementTree
import requests
import pandas as pd
import numpy as np
from tabulate import tabulate

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
    run_analysis([])
    import sys
    sys.exit(0)
    # for each artist in the payload response
    artist_id, artist_name = get_artist_id(input, request_headers)

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
    data = [['Take to the Skies', 'Enter Shikari', 324], ['Take to the Skies', 'Mothership', 455], ['Take to the Skies', 'Anything Can Happen in the Next Half Hour', 0], ['Take to the Skies', 'Labyrinth', 204], ['Take to the Skies', 'No Sssweat', 247], ['Take to the Skies', "Today Won't Go Down in History", 100], ['Take to the Skies', 'Reprise 1', None], ['Take to the Skies', 'Return to Energiser', 279], ['Take to the Skies', "Sorry You're Not a Winner", 0], ['Take to the Skies', 'Jonny Sniper', 229], ['Take to the Skies', 'Adieu', 95], ['Take to the Skies', 'OK, Time for Plan B', 0], ['Take to the Skies', 'Reprise 2', None], ['Common Dreads', 'Common Dreads', 110], ['Common Dreads', 'Solidarity', 160], ['Common Dreads', 'Step Up', 276], ['Common Dreads', 'Juggernauts', 451], ['Common Dreads', 'Wall', 361], ['Common Dreads', 'Zzzonked', 186], ['Common Dreads', 'Havoc A', 57], ['Common Dreads', 'No Sleep Tonight', 408], ['Common Dreads', 'Gap in the Fence', 250], ['Common Dreads', 'Havoc B', 79], ['Common Dreads', 'Antwerpen', 186], ['Common Dreads', 'The Jester', 242], ['Common Dreads', 'Halcyon', 1], ['Common Dreads', 'Hectic', 308], ['Common Dreads', 'Fanfare for the Conscious Man', 256], ['A Flash Flood of Colour', 'System…', None], ['A Flash Flood of Colour', '…Meltdown', None], ['A Flash Flood of Colour', 'Sssnakepit', 348], ['A Flash Flood of Colour', 'Search Party', 257], ['A Flash Flood of Colour', 'Arguing With Thermometers', 347], ['A Flash Flood of Colour', 'Stalemate', 271], ['A Flash Flood of Colour', 'Gandhi Mate, Gandhi', 434], ['A Flash Flood of Colour', 'Warm Smiles Do Not Make You Welcome Here', 236], ['A Flash Flood of Colour', 'Pack of Thieves', 245], ['A Flash Flood of Colour', 'Hello Tyrannosaurus, Meet Tyrannicide', 32], ['A Flash Flood of Colour', 'Constellations', 397], ['A Flash Flood of Colour', 'Quelle Surprise', 298], ['A Flash Flood of Colour', 'Destabilise', 352], ['A Flash Flood of Colour', 'Quelle Surprise (Rout VIP mix)', 298], ['A Flash Flood of Colour', 'Intro/Destabilise (live From the Electric Ballroom Oct 2011)', None], ['A Flash Flood of Colour', 'Sssnakepit (live From the Electric Ballroom Oct 2011)', 348], ['A Flash Flood of Colour', 'Quelle Surprise (live From the Electric Ballroom Oct 2011)', 298], ['A Flash Flood of Colour', 'OK, Time for Plan B (live From the Electric Ballroom Oct 2011)', 0], ['The Mindsweep', 'The Appeal & The Mindsweep I', 346], ['The Mindsweep', 'The One True Colour', 338], ['The Mindsweep', 'Anaesthetist', 256], ['The Mindsweep', 'The Last Garrison', 337], ['The Mindsweep', 'Never Let Go of the Microscope', 254], ['The Mindsweep', 'Myopia', 283], ['The Mindsweep', 'Torn Apart', 249], ['The Mindsweep', 'Interlude', 1], ['The Mindsweep', 'The Bank of England', 123], ['The Mindsweep', 'There’s a Price on Your Head', None], ['The Mindsweep', 'Dear Future Historians…', None], ['The Mindsweep', 'The Appeal & The Mindsweep II', 153], ['The Mindsweep', 'Slipshod', 186], ['The Mindsweep', 'The Paddington Frisk', 148], ['The Mindsweep', 'Rat Race', 311], ['The Mindsweep', 'Radiate', 370], ['The Spark', 'The Spark', 1], ['The Spark', 'The Sights', 337], ['The Spark', 'Live Outside', 335], ['The Spark', 'Take My Country Back', 330], ['The Spark', 'Airfield', 318], ['The Spark', 'Rabble Rouser', 367], ['The Spark', 'Shinrin‐yoku', None], ['The Spark', 'Undercover Agents', 335], ['The Spark', 'The Revolt of the Atoms', 266], ['The Spark', 'An Ode to Lost Jigsaw Pieces (In Two Movements)', 318], ['The Spark', 'The Embers', 1], ['The Zone', 'The Feast (demo)', 0], ['The Zone', "Kickin' Back on the Surface of Your Cheek (edit)", 110], ['The Zone', 'Keep It on Ice', 281], ['The Zone', 'Adieu (Routron 5000 remix)', 95], ['The Zone', 'Sorry You’re Not a Winner (live)', None], ['The Zone', 'Mothership (demo)', 217], ['The Zone', 'Acid Nation', 159], ['The Zone', 'Enter Shikari (demo)', 324], ['Tribalism', 'Tribalism', 394], ['Tribalism', 'Thumper', 397], ['Tribalism', 'All Eyes on the Saint', 239], ['Tribalism', 'We Can Breathe in Space', 0], ['Tribalism', 'Insomnia (live)', 303], ['Tribalism', 'Juggernauts (Nero remix)', 451], ['Tribalism', 'No Sleep Tonight (The Qemists remix)', 408], ['Tribalism', 'Wall (High Contrast remix)', 361], ['Tribalism', 'No Sleep Tonight (Mistabishi remix)', 408], ['Tribalism', "Juggernauts (Blue Bear's True Tiger remix)", 451], ['Tribalism', 'No Sleep Tonight (Rout remix)', 408], ['Tribalism', 'No Sleep Tonight (LightsGoBlue remix)', 408], ['Tribalism', 'Havoc A (live)', 57], ['Tribalism', 'Labyrinth (live)', 204], ['Tribalism', 'Hectic (live)', 308], ['Live at Milton Keynes: Bootleg Series, Vol. 1', 'Enter Shikari', 324], ['Live at Milton Keynes: Bootleg Series, Vol. 1', 'The Feast', 451], ['Live at Milton Keynes: Bootleg Series, Vol. 1', 'Return to Energiser', 279], ['Live at Milton Keynes: Bootleg Series, Vol. 1', 'Anything Can Happen in the Next Half Hour…', None], ['Live at Milton Keynes: Bootleg Series, Vol. 1', 'Labyrinth', 204], ['Live at Milton Keynes: Bootleg Series, Vol. 1', 'No Sssweat', 247], ['Live at Milton Keynes: Bootleg Series, Vol. 1', 'Interlude', 1], ['Live at Milton Keynes: Bootleg Series, Vol. 1', 'Sorry, You’re Not a Winner', None], ['Live at Milton Keynes: Bootleg Series, Vol. 1', 'Mothership', 455], ['Live at Milton Keynes: Bootleg Series, Vol. 1', 'OK, Time for Plan B', 0], ['Live at Rock City 2009', 'Common Dreads / Solidarity', None], ['Live at Rock City 2009', 'Step Up', 276], ['Live at Rock City 2009', 'The Feast', 451], ['Live at Rock City 2009', 'Mothership', 455], ['Live at Rock City 2009', 'Zzzonked', 186], ['Live at Rock City 2009', 'Havoc A', 57], ['Live at Rock City 2009', 'No Sleep Tonight', 408], ['Live at Rock City 2009', 'Gap in the Fence', 250], ['Live at Rock City 2009', 'Havoc B', 79], ['Live at Rock City 2009', 'Labyrinth', 204], ['Live at Rock City 2009', 'No Ssweat', None], ['Live at Rock City 2009', 'Hectic', 308], ['Live at Rock City 2009', 'Enter Shikari', 324], ['Live at Rock City 2009', 'Fanfare for the Conscious Man', 256], ['Live at Rock City 2009', 'Juggernauts', 451], ['Live from Planet Earth: Bootleg Series, Volume 3', 'Intro', 91], ['Live from Planet Earth: Bootleg Series, Volume 3', 'Solidarity', 160], ['Live from Planet Earth: Bootleg Series, Volume 3', 'Motherstep/Mothership', None], ['Live from Planet Earth: Bootleg Series, Volume 3', 'Zzzonked', 186], ['Live from Planet Earth: Bootleg Series, Volume 3', 'Havoc A', 57], ['Live from Planet Earth: Bootleg Series, Volume 3', 'No Sssweat', 247], ['Live from Planet Earth: Bootleg Series, Volume 3', 'The Feast', 451], ['Live from Planet Earth: Bootleg Series, Volume 3', 'Hectic', 308], ['Live from Planet Earth: Bootleg Series, Volume 3', 'Destabilise', 352], ['Live from Planet Earth: Bootleg Series, Volume 3', 'Gap in the Fence', 250], ['Live from Planet Earth: Bootleg Series, Volume 3', 'Wall', 361], ['Live from Planet Earth: Bootleg Series, Volume 3', 'Labyrinth', 204], ['Live from Planet Earth: Bootleg Series, Volume 3', 'The Jester', 242], ['Live from Planet Earth: Bootleg Series, Volume 3', 'Juggernauts', 451], ['Live from Planet Earth: Bootleg Series, Volume 3', 'Sorry You’re Not a Winner', None], ['Live from Planet Earth: Bootleg Series, Volume 3', 'Intro', 91], ['Live from Planet Earth: Bootleg Series, Volume 3', 'Solidarity', 160], ['Live from Planet Earth: Bootleg Series, Volume 3', 'Motherstep/Mothership', None], ['Live from Planet Earth: Bootleg Series, Volume 3', 'Zzzonked', 186], ['Live from Planet Earth: Bootleg Series, Volume 3', 'Havoc A', 57], ['Live from Planet Earth: Bootleg Series, Volume 3', 'No Sssweat', 247], ['Live from Planet Earth: Bootleg Series, Volume 3', 'The Feast', 451], ['Live from Planet Earth: Bootleg Series, Volume 3', 'Hectic', 308], ['Live from Planet Earth: Bootleg Series, Volume 3', 'Destabilise', 352], ['Live from Planet Earth: Bootleg Series, Volume 3', 'Gap in the Fence', 250], ['Live from Planet Earth: Bootleg Series, Volume 3', 'Wall', 361], ['Live from Planet Earth: Bootleg Series, Volume 3', 'Labyrinth', 204], ['Live from Planet Earth: Bootleg Series, Volume 3', 'The Jester', 242], ['Live from Planet Earth: Bootleg Series, Volume 3', 'Juggernauts', 451], ['Live from Planet Earth: Bootleg Series, Volume 3', 'Sorry You’re Not a Winner', None], ['Live from Planet Earth: Bootleg Series, Volume 3', 'Solidarity / Step Up', None], ['Live from Planet Earth: Bootleg Series, Volume 3', 'Motherstep/Mothership', None], ['Live from Planet Earth: Bootleg Series, Volume 3', 'Zzzonked / Havoc A', None], ['Live from Planet Earth: Bootleg Series, Volume 3', 'No Sleep Tonight', 408], ['Live from Planet Earth: Bootleg Series, Volume 3', 'Kickin’ Back on the Surface of Your Cheek', None], ['Live from Planet Earth: Bootleg Series, Volume 3', 'Labyrinth', 204], ['Live from Planet Earth: Bootleg Series, Volume 3', 'Anything Can Happen in the Next Half Hour', 0], ['Live from Planet Earth: Bootleg Series, Volume 3', 'The Jester', 242], ['Live from Planet Earth: Bootleg Series, Volume 3', 'Hectic', 308], ['Live from Planet Earth: Bootleg Series, Volume 3', 'Return to Energiser', 279], ['Live from Planet Earth: Bootleg Series, Volume 3', 'No Sssweat', 247], ['Live from Planet Earth: Bootleg Series, Volume 3', 'Sorry You’re Not a Winner', None], ['Live from Planet Earth: Bootleg Series, Volume 3', 'Juggernauts', 451], ['Live from Planet Earth: Bootleg Series, Volume 3', 'OK, Time for Plan B', 0], ['Live from Planet Earth: Bootleg Series, Volume 3', 'Solidarity', 160], ['Live from Planet Earth: Bootleg Series, Volume 3', 'Motherstep/Mothership', None], ['Live from Planet Earth: Bootleg Series, Volume 3', 'The Jester', 242], ['Live from Planet Earth: Bootleg Series, Volume 3', 'Zzzonked', 186], ['Live from Planet Earth: Bootleg Series, Volume 3', 'Havoc A', 57], ['Live from Planet Earth: Bootleg Series, Volume 3', 'Enter Shikari', 324], ['Live from Planet Earth: Bootleg Series, Volume 3', 'Juggernauts', 451], ['Live from Planet Earth: Bootleg Series, Volume 3', 'Fanfare for the Conscious Man', 256], ['Live from Planet Earth: Bootleg Series, Volume 3', 'Solidarity', 160], ['Live from Planet Earth: Bootleg Series, Volume 3', 'No Sssweat', 247], ['Live from Planet Earth: Bootleg Series, Volume 3', 'Step Up', 276], ['Live from Planet Earth: Bootleg Series, Volume 3', 'Havoc B', 79], ['Live from Planet Earth: Bootleg Series, Volume 3', 'Mothership', 455], ['Live from Planet Earth: Bootleg Series, Volume 3', 'The Jester', 242], ['Live from Planet Earth: Bootleg Series, Volume 3', 'Juggernauts', 451], ['Live from Planet Earth: Bootleg Series, Volume 3', 'Sorry You’re Not a Winner', None], ['Live from Planet Earth: Bootleg Series, Volume 3', 'Enter Shikari', 324], ['Live in London W6. March 2012: Bootleg Series, Vol. 4', 'System / Meltdown (live From the Hammersmith Apollo)', None], ['Live in London W6. March 2012: Bootleg Series, Vol. 4', 'The Feast (live From the Hammersmith Apollo)', 451], ['Live in London W6. March 2012: Bootleg Series, Vol. 4', 'Gandhi Mate, Gandhi (live From the Hammersmith Apollo)', 434], ['Live in London W6. March 2012: Bootleg Series, Vol. 4', 'Quelle Surprise (live From the Hammersmith Apollo)', 298], ['Live in London W6. March 2012: Bootleg Series, Vol. 4', 'Hello Tyrannosaurus, Meet Tyrannicide (live From the Hammersmith Apollo)', 32], ['Live in London W6. March 2012: Bootleg Series, Vol. 4', 'Stalemate (live From the Hammersmith Apollo)', 271], ['Live in London W6. March 2012: Bootleg Series, Vol. 4', 'Enter Shikari (live From the Hammersmith Apollo)', 324], ['Live in London W6. March 2012: Bootleg Series, Vol. 4', 'Return to Energiser (live From the Hammersmith Apollo)', 279], ['Live in London W6. March 2012: Bootleg Series, Vol. 4', 'Sssnakepit (live From the Hammersmith Apollo)', 348], ['Live in the Barrowland: Bootleg Series Vol. 5', 'System…', None], ['Live in the Barrowland: Bootleg Series Vol. 5', '…Meltdown', None], ['Live in the Barrowland: Bootleg Series Vol. 5', 'Sssnakepit (alternative version)', 348], ['Live in the Barrowland: Bootleg Series Vol. 5', 'Antwerpen', 186], ['Live in the Barrowland: Bootleg Series Vol. 5', 'Gandhi Mate, Gandhi', 434], ['Live in the Barrowland: Bootleg Series Vol. 5', 'Labyrinth', 204], ['Live in the Barrowland: Bootleg Series Vol. 5', 'Destabilise', 352], ['Live in the Barrowland: Bootleg Series Vol. 5', 'Return to Energiser', 279], ['Live in the Barrowland: Bootleg Series Vol. 5', 'Warm Smiles Do Not Make You Welcome Here', 236], ['Live in the Barrowland: Bootleg Series Vol. 5', 'Gap in the Fence', 250], ['Live in the Barrowland: Bootleg Series Vol. 5', 'Juggernauts', 451], ['Live in the Barrowland: Bootleg Series Vol. 5', 'Arguing With Thermometers', 347], ['Live in the Barrowland: Bootleg Series Vol. 5', 'Mothership', 455], ['Live in the Barrowland: Bootleg Series Vol. 5', 'Constellations', 397], ['Live in the Barrowland: Bootleg Series Vol. 5', 'Pack of Thieves', 245], ['Live in the Barrowland: Bootleg Series Vol. 5', 'Zzzonked', 186], ['Live at Alexandra Palace', 'Intro / Solidarity', None], ['Live at Alexandra Palace', 'Sorry You’re Not a Winner', None], ['Live at Alexandra Palace', 'The One True Colour', 338], ['Live at Alexandra Palace', 'The Last Garrison / No Sleep Tonight', None], ['Live at Alexandra Palace', 'Destabilise', 352], ['Live at Alexandra Palace', 'Radiate', 370], ['Live at Alexandra Palace', 'Slipshod / The Jester', None], ['Live at Alexandra Palace', 'Price On Your Head (inc. Danny Byrd remix)', None], ['Live at Alexandra Palace', 'Dear Future Historians', None], ['Live at Alexandra Palace', 'Arguing With Thermometers', 347], ['Live at Alexandra Palace', 'Gandhi Mate, Gandhi', 434], ['Live at Alexandra Palace', 'Torn Apart', 249], ['Live at Alexandra Palace', 'Mothership', 455], ['Live at Alexandra Palace', 'Redshift', 268], ['Live at Alexandra Palace', 'Anaesthetist (inc. Reso remix)', 256], ['Live at Alexandra Palace', 'The Appeal & The Mindesweep II', None], ['Take to the Skies: Live in Moscow. May 2017', 'Stand Your Ground (Live In Moscow. May 2017)', None], ['Take to the Skies: Live in Moscow. May 2017', 'Enter Shikari (Live In Moscow. May 2017)', 324], ['Take to the Skies: Live in Moscow. May 2017', 'Mothership (Live In Moscow. May 2017)', 455], ['Take to the Skies: Live in Moscow. May 2017', 'Anything Can Happen In The Next Half Hour (Live In Moscow. May 2017)', 0], ['Take to the Skies: Live in Moscow. May 2017', 'Interlude 1 (Live In Moscow. May 2017)', 42], ['Take to the Skies: Live in Moscow. May 2017', 'Labyrinth (Live In Moscow. May 2017)', 204], ['Take to the Skies: Live in Moscow. May 2017', 'Hoodwinker (Live In Moscow. May 2017)', 284], ['Take to the Skies: Live in Moscow. May 2017', "Sorry You're Not A Winner (Live In Moscow. May 2017)", 0], ['Take to the Skies: Live in Moscow. May 2017', 'Juggernauts (Live In Moscow. May 2017)', 451], ['Take to the Skies: Live in Moscow. May 2017', 'No Sweat (Live In Moscow. May 2017)', None], ['Take to the Skies: Live in Moscow. May 2017', "Today Won't Go Down In History (Live In Moscow. May 2017)", 100], ['Take to the Skies: Live in Moscow. May 2017', 'Anaesthetist (Live In Moscow. May 2017)', 256], ['Take to the Skies: Live in Moscow. May 2017', 'Return To Energiser (Live In Moscow. May 2017)', 279], ['Take to the Skies: Live in Moscow. May 2017', 'Jonny Sniper (Live In Moscow. May 2017)', 229], ['Take to the Skies: Live in Moscow. May 2017', 'Adieu (Live In Moscow. May 2017)', 95], ['Take to the Skies: Live in Moscow. May 2017', 'Redshift (Live In Moscow. May 2017)', 268], ['Take to the Skies: Live in Moscow. May 2017', 'Ok Time For A Plan B (Live In Moscow. May 2017)', None], ['Take to the Skies: Live in Moscow. May 2017', 'Appeal 2 (Live In Moscow. May 2017)', None], ['The Mindsweep: Hospitalised', 'The Appeal & The Mindsweep I (Metrik remix)', 346], ['The Mindsweep: Hospitalised', 'The One True Colour (Keeno remix)', 338], ['The Mindsweep: Hospitalised', 'Anaesthetist (Reso remix)', 256], ['The Mindsweep: Hospitalised', 'The Last Garrison (S.P.Y. remix)', 337], ['The Mindsweep: Hospitalised', 'Never Let Go of the Microscope (Etherwood remix)', 254], ['The Mindsweep: Hospitalised', 'Myopia (Bop remix)', 283], ['The Mindsweep: Hospitalised', 'Torn Apart (Hugh Hardie remix)', 249], ['The Mindsweep: Hospitalised', 'Interlude (The Erised remix)', 1], ['The Mindsweep: Hospitalised', 'The Bank of England (Lynx remix)', 123], ['The Mindsweep: Hospitalised', 'There’s a Price on Your Head (Danny Byrd remix)', None], ['The Mindsweep: Hospitalised', 'Dear Future Historians (London Elektricity remix)', None], ['The Mindsweep: Hospitalised', 'The Appeal & The Mindsweep II (Krakota remix)', 153]]
    df = pd.DataFrame(data, columns =['album', 'song', 'word_count'])

    avg_word_count = df['word_count'].mean()
    print('avg_word_count: ', avg_word_count)

    # Album Stats
    albums = df.groupby('album').agg([np.min, np.max, np.mean, np.std])
    print(tabulate(albums, headers='keys', tablefmt='psql'))


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
            time.sleep(0.5)
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
        elif "error" in response.text:
            print(response.text)
            time.sleep(2)
        else:
            return response

    raise ConnectionError('Multiple 429 Errors: ', url)


if __name__ == '__main__':
    #todo handle command line args here e.g. argparse
    input = 'Enter Shikari'
    print('input: ', input)
    main(input)
