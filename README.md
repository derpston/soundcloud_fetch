# soundcloud_fetch
Takes a SoundCloud artist URL, fetches all the MP3 streams and applies ID3 tags.

## Features

* When interrupted, resumes fetching from the last file it attempted, so it can be run periodically to fetch new content.
* Attempts to automatically look up the public API key used on soundcloud.com
* Supports a user defined API key.

## Dependencies

* python-requests (for sensible HTTP fetching)
* The [Python soundcloud API wrapper](https://pypi.python.org/pypi/soundcloud)
* [mutagen](https://pypi.python.org/pypi/mutagen), for editing ID3 tags

## Getting a SoundCloud API key

* To be polite, you should [register for an API key/client id](http://soundcloud.com/you/apps)!
* If you are impolite, you can try to use the automatic client id detection feature by not specifying a --client-id option.
* If that fails, you can try to manually look up the client id the soundcloud frontend uses by using your browser's network debugging feature to watch the requests it makes when you load a soundcloud page, and look for a client_id value.

## Usage

```
$ python soundcloud_fetch.py 
usage: soundcloud_fetch.py [-h] [--client-id CLIENT_ID] url
soundcloud_fetch.py: error: too few arguments
```

Start ```soundcloud_fetch.py``` with a URL to a user's track listing page:

```
$ python soundcloud_fetch.py https://soundcloud.com/exampleuser
Attempting to fetch a public soundcloud client ID:
 * Fetching main page... HTTP 200, 16731 bytes
 * Locating app.js... found 1 URLs that may be app.js.
 * Fetching https://a-v2.sndcdn.com/assets/app-c90e6-744d103.js... HTTP 200, 628768 bytes
 * Searching for a client id... got one! 'deadbeef-example-client-id'
Resolving URL to user... user id: 123456
Fetching track list... got 2 tracks
Example_User_-_Track_One.mp3 exists, skipped.
Example_User_-_Track_Two does not exist.
 * Fetching streams URL... done
 * Fetching MP3... done, got 123456789 bytes
 * Setting ID3 tags... done!
All tracks processed.
```

