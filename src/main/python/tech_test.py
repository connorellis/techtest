import sys
import json
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

    artist_releases = get_artist_releases(artist_id, request_headers)

    for release in artist_releases:
        print(release)
        for track in release['tracklist']:
            print(track)
            test = lyricsovh_api_base_url + '/{0}/{1}'.format(artist_name, track)
            test = lyricsovh_api_base_url + '/{0}/{1}'.format('Coldplay', 'Adventure of a Lifetime')
            print(test)
            lyrics = make_api_request(test, request_headers).json()['lyrics']
            print(str(lyrics.split[' '].length()))
            sys.exit()


def get_artist_id(input, headers):

    artists_api = '{0}/artist/?query=artist:{1}'.format(musicbrainz_api_base_url, input)

    matching_artists_xml = make_api_request(artists_api, headers).text
    #matching_artists_xml = '<?xml version="1.0" encoding="UTF-8" standalone="yes"?><metadata created="2019-12-07T16:16:20.462Z" xmlns="http://musicbrainz.org/ns/mmd-2.0#" xmlns:ns2="http://musicbrainz.org/ns/ext#-2.0"><artist-list count="2" offset="0"><artist id="cc197bad-dc9c-440d-a5b5-d52ba2e14234" type="Group" type-id="e431f5f6-b5d2-343d-8b36-72607fffb74b" ns2:score="100"><name>Coldplay</name><sort-name>Coldplay</sort-name><country>GB</country><area id="8a754a16-0027-3a29-b6d7-2b40ea0481ed" type="Country" type-id="06dd0ae4-8c74-30bb-b43d-95dcedf961de"><name>United Kingdom</name><sort-name>United Kingdom</sort-name><life-span><ended>false</ended></life-span></area><begin-area id="f03d09b3-39dc-4083-afd6-159e3f0d462f" type="City" type-id="6fd8f29a-3d0a-32fc-980d-ea697b69da78"><name>London</name><sort-name>London</sort-name><life-span><ended>false</ended></life-span></begin-area><isni-list><isni>000000011551394X</isni></isni-list><life-span><begin>1996-09</begin><ended>false</ended></life-span><alias-list><alias sort-name="Cold Play" type="Search hint" type-id="1937e404-b981-3cb7-8151-4c86ebfc8d8e">Cold Play</alias><alias sort-name="Coldplay, The" type="Artist name" type-id="894afba6-2816-3c24-8072-eadb66bd04bc" end-date="1998">The Coldplay</alias></alias-list><tag-list><tag count="2"><name>rock</name></tag><tag count="7"><name>pop</name></tag><tag count="16"><name>alternative rock</name></tag><tag count="8"><name>british</name></tag><tag count="1"><name>uk</name></tag><tag count="0"><name>britannique</name></tag><tag count="0"><name>britpop</name></tag><tag count="3"><name>pop rock</name></tag><tag count="0"><name>piano pop</name></tag><tag count="1"><name>piano rock</name></tag><tag count="0"><name>english</name></tag><tag count="0"><name>parlophone</name></tag><tag count="0"><name>rock and indie</name></tag><tag count="0"><name>ambient pop</name></tag><tag count="0"><name>pop/rock</name></tag><tag count="0"><name>chapel</name></tag><tag count="0"><name>post-britpop</name></tag></tag-list></artist><artist id="62c54a75-265f-4e13-ad0a-0fb001559a2e" type="Group" type-id="e431f5f6-b5d2-343d-8b36-72607fffb74b" ns2:score="60"><name>Viva La Coldplay</name><sort-name>Viva La Coldplay</sort-name><country>GB</country><area id="8a754a16-0027-3a29-b6d7-2b40ea0481ed" type="Country" type-id="06dd0ae4-8c74-30bb-b43d-95dcedf961de"><name>United Kingdom</name><sort-name>United Kingdom</sort-name><life-span><ended>false</ended></life-span></area><life-span><begin>2006</begin><ended>false</ended></life-span></artist></artist-list></metadata>'
    matching_artists_root = ElementTree.fromstring(matching_artists_xml)

    near_matches = []
    artist_id = None
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


'''
            for country in artist.findall('artist'):
                rank = country.find('rank').text
                name = country.get('name')
                print(name, rank)
'''


def get_artist_releases(artist_mbid, headers):

    releases_api = '{0}/release?artist={1}&type=album'.format(musicbrainz_api_base_url, artist_mbid)
    #releases_api = '{0}/release?artist={1}'.format(musicbrainz_api_base_url, artist_mbid)

    release_list_xml = make_api_request(releases_api, headers).text
    #release_groups_api = '{0}/release-group?artist={1}&type=album'.format(musicbrainz_api_base_url, artist_mbid)

    release_list_root = ElementTree.fromstring(release_list_xml)

    release_list = []
    for release in release_list_root.findall('ns:release-list/ns:release', musicbrainz_ns):

        # get the musicbrainz id of the release
        release_id = release.attrib['id']
        release_title = release.find('ns:title', musicbrainz_ns).text
        print('Release title: ', release_title)

        tracklist = get_release_tracks(release_id, headers)

        release_list.append({"release_id": release_id,
                             "release_title": release_title,
                             "tracklist": tracklist})

    return release_list

def get_release_tracks(release_mbid, headers):

    releases_api = '{0}/release/{1}?inc=recordings'.format(musicbrainz_api_base_url, release_mbid)

    release_list_xml = make_api_request(releases_api, headers).text
    #release_list_xml = '<metadata xmlns="http://musicbrainz.org/ns/mmd-2.0#"><release id="8e602038-c0f2-3c2d-9068-a1a3daca493d"><title>Parachutes</title><status id="4e304316-386d-3409-af2e-78857eec5cfe">Official</status><quality>high</quality><packaging id="ec27701a-4a22-37f4-bfac-6616e0f9750a">Jewel Case</packaging><text-representation><language>eng</language><script>Latn</script></text-representation><date>2000-07-10</date><country>GB</country><release-event-list count="1"><release-event><date>2000-07-10</date><area id="8a754a16-0027-3a29-b6d7-2b40ea0481ed"><name>United Kingdom</name><sort-name>United Kingdom</sort-name><iso-3166-1-code-list><iso-3166-1-code>GB</iso-3166-1-code></iso-3166-1-code-list></area></release-event></release-event-list><barcode>724352778324</barcode><asin>B00004U9MS</asin><cover-art-archive><artwork>true</artwork><count>3</count><front>true</front><back>true</back></cover-art-archive><medium-list count="1"><medium><position>1</position><format id="9712d52a-4509-3d4b-a1a2-67c88c643e31">CD</format><track-list count="10" offset="0"><track id="021eeb14-9f28-40dc-867f-7f1241c0a382"><position>1</position><number>1</number><length>139000</length><recording id="fb81a071-9c63-4e8c-ab60-77403e81c01d"><title>Don’t Panic</title><length>136906</length></recording></track><track id="a82cfc99-5b9b-40a9-9292-d28628e04537"><position>2</position><number>2</number><length>301000</length><recording id="71557258-6534-4b56-8007-3903ace2d869"><title>Shiver</title><length>299693</length></recording></track><track id="34eda33c-e647-44e9-8772-829bd0ef040e"><position>3</position><number>3</number><length>320000</length><recording id="50369905-68ca-48d2-912d-b37330ff7dc3"><title>Spies</title><length>318773</length></recording></track><track id="79a88b4d-9e9b-4eaa-b198-6af0b80c9782"><position>4</position><number>4</number><length>228000</length><recording id="22d49305-4e35-4a69-8638-05ac5f734065"><title>Sparks</title><length>227093</length></recording></track><track id="399b93dc-ae9c-4a71-ada4-ca9006308926"><position>5</position><number>5</number><length>271000</length><recording id="729cf505-94eb-4fbe-bc76-cbae44cff091"><title>Yellow</title><length>269200</length></recording></track><track id="371a8b6e-62b2-4321-9e1b-f4bfbd0d961e"><position>6</position><number>6</number><length>272000</length><recording id="1aa7ebc0-25ee-47b2-8efd-6074307c5b14"><title>Trouble</title><length>270906</length></recording></track><track id="f0871f62-7a29-4792-931e-258bc2ba14cf"><position>7</position><number>7</number><length>47000</length><recording id="3451489e-ea50-4e4e-9043-df1e30ce37b5"><title>Parachutes</title><length>46200</length></recording></track><track id="8d19ac73-22f8-4ff4-b556-edfa43cd1cba"><position>8</position><number>8</number><length>256000</length><recording id="94909689-459c-4d15-8e31-678854c48f22"><title>High Speed</title><length>254360</length></recording></track><track id="4f6a4f8e-67c5-4a26-84aa-e5ac89b93af3"><position>9</position><number>9</number><length>251000</length><recording id="7e52d1a9-6c02-4f2e-b30e-dc22ef219f3f"><title>We Never Change</title><length>249400</length></recording></track><track id="5aba3420-6272-41c4-b443-fb6cf94b7a1a"><position>10</position><number>10</number><length>434000</length><recording id="78485fd1-136d-4f2b-ae93-d9815d828e26"><title>Everything’s Not Lost / Life Is for Living</title><length>436066</length></recording></track></track-list></medium></medium-list></release></metadata>'

    release_list_root = ElementTree.fromstring(release_list_xml)

    track_list = []
    for track in release_list_root.findall('ns:release/ns:medium-list/ns:medium/ns:track-list/ns:track', musicbrainz_ns):
        track_title = track.find('ns:recording/ns:title', musicbrainz_ns).text
        track_list.append(track_title)

    return(track_list)


def make_api_request(url, headers):

    # try API 3 times in case of 429 error
    for x in range(1, 3):

        # Error handling for request exceptions
        try:
            # https://wiki.musicbrainz.org/XML_Web_Service/Rate_Limiting
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
            print('429 Error: ', url)
        else:
            return response

    raise ConnectionError('Multiple 429 Errors: ', url)


if __name__ == '__main__':
    #todo handle command line args here e.g. argparse
    input = 'Judee Sill'
    print('input: ', input)
    main(input)
