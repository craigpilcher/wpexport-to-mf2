# wpexport-to-mf2
Transform a WordPress XML export into a [microformats2](http://microformats.org/wiki/microformats2) dictionary

## How it works
This library takes WordPress XML-RPC input, and creates a dictionary of ActivityStream2 data to feed to granary for processing to microformats. Very much a work in progress.

## Usage

    python3 wp-to-mf2.py blogurl userid password

where userid and password are the credentials of your WordPress user.

## Dependencies

Currently using [Python Wordpress XMLRPC](https://github.com/maxcutler/python-wordpress-xmlrpc), as well as [Granary](https://granary.io)
