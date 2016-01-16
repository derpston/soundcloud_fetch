import argparse
import soundcloud
import requests
import re
import os
import sys
import mutagen.mp3

def stdout(msg):
    """Small helper for writing to stdout and flushing it, intended to
make terminal output more compact and responsive."""
    sys.stdout.write(msg)
    sys.stdout.flush()

def find_client_id():
    """Fetches the soundcloud.com main page, looks for the 'app' js file
and tries to pull a client_id out of that. Returns None on failure or a
string client_id on success."""

    stdout("Attempting to fetch a public soundcloud client ID:\n")
    stdout(" * Fetching main page... ")
    response = requests.get("http://www.soundcloud.com")
    stdout("HTTP %d, %d bytes\n" % (response.status_code, len(response.content)))
    stdout(" * Locating app.js... ")
    app_js_urls = re.findall("\"(http.+?[^\"]+?/app-.+?js)", response.content)
    stdout("found %d URLs that may be app.js.\n" % len(app_js_urls))
    if len(app_js_urls) == 0:
        return None
    else:
        for url in app_js_urls:
            stdout(" * Fetching %s... " % url)
            response = requests.get(url)
            stdout("HTTP %d, %d bytes\n" % (response.status_code, len(response.content)))
            stdout(" * Searching for a client id... ")
            open("/tmp/appjs", "w").write(response.content)
            # Try to pick out the value for client_id, not including quotes,
            # anywhere in the JavaScript and do a little length sanity
            # checking on it.
            m = re.search("client_id:\"(.{16,128}?[^\"])\"", response.content)
            if m is None:
                stdout("failed!\n")
                return None
            else:
                client_id = m.group(1)
                stdout("got one! '%s'\n" % client_id)
                return client_id


parser = argparse.ArgumentParser()
parser.add_argument("url", action="store")
parser.add_argument("--client-id", action="store")
args = parser.parse_args()

if args.client_id is None:
    # If the user didn't specify a client_id, try to find one automatically.
    args.client_id = find_client_id()

if args.client_id is None:
    stdout("Failed to find a client ID automatically, please specify one with\n")
    stdout("the --client-id option. See README for details.")
    raise SystemExit(1)

client = soundcloud.Client(client_id=args.client_id)

stdout("Resolving URL to user... ")
resolver = client.get("/resolve?url=%s" % args.url)
user_id = resolver.obj['id']
stdout("user id: %d\n" % user_id)

stdout("Fetching track list... ")
tracks = client.get("/users/%d/tracks" % user_id)
stdout("got %d tracks\n" % len(tracks))

for track in tracks:
    filename = "%s - %s" % (track.obj['user']['username'], track.obj['title'])
    filename = re.sub(" ", "_", filename)
    filename = re.sub("[^A-Za-z0-9_ -]", "", filename)
    filename = re.sub("_+", "_", filename)
    filename = filename.strip("_")
    filename += ".mp3"
    stdout("%s " % filename)
    if os.path.exists(filename):
        stdout("exists, skipped.\n")
    else:
        stdout("does not exist.\n")
       
        stdout(" * Fetching streams URL... ")
        streams_url = "/i1/tracks/%d/streams" % track.obj['id']
        streams = client.get(streams_url)
        mp3_url = streams.obj['http_mp3_128_url']
        stdout("done\n")
        stdout(" * Fetching MP3... ")
        response = requests.get(mp3_url)
        if response.status_code == 200:
            stdout("done, got %d bytes\n" % len(response.content))
            open(filename, "w").write(response.content)
            stdout(" * Setting ID3 tags... ")
            mp3 = mutagen.mp3.EasyMP3(filename)
            mp3.tags = mutagen.easyid3.EasyID3()
            mp3.tags['artist'] = [track.obj['user']['username']]
            mp3.tags['title'] = [track.obj['title']]
            mp3.tags['album'] = ['soundcloud']
            mp3.save()
            stdout("done!\n")
        else:
            stdout("failed, got HTTP %d\n" % response.status_code)

stdout("All tracks processed.\n")
