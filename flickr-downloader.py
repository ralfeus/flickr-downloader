#!/usr/bin/env python3
import flickrapi
import webbrowser
import piexif
import piexif.helper
import urllib
from datetime import datetime
import pathlib
import os
import os.path
import time
from apiCallsWatcher import apiCallsWatcher

flickr_api = u'c5a20c77aebfbee22ed5835711fa6647'
flickr_secret = u'7fcc2669c1a4e730'

def savePicture(url, dateTaken, albums):
    #timeTaken = datetime.strptime(dateTaken, '%Y-%m-%d %H:%M:%S')
    dstDir = '/mnt/sandlet/Temp/Flickr/' + dateTaken[0:4] + '/'+ dateTaken[5:7] 
    dstFile = dstDir + '/' + dateTaken.replace(':', '') + '.jpg'
    
    pathlib.Path(dstDir).mkdir(parents = True, exist_ok = True)
    urllib.request.urlretrieve(url, dstFile)
    try:
        exif = piexif.load(dstFile)
        exif['Exif'][piexif.ExifIFD.UserComment] = piexif.helper.UserComment.dump(albums, piexif.helper.UserComment.UNICODE)
    #exif['0th'][40094] = piexif.helper.UserComment.dump(albums, piexif.helper.UserComment.UNICODE)
    #print(exif)
        exifBytes = piexif.dump(exif)
        piexif.insert(exifBytes, dstFile)
    except ValueError:
        print(url, "ValueError during EXIF modification")

flickr = flickrapi.FlickrAPI(flickr_api, flickr_secret)

flickr_photos_search = apiCallsWatcher.makeCall(flickr.photos.search)
flickr_photos_getAllContexts = apiCallsWatcher.makeCall(flickr.photos.getAllContexts)

if not flickr.token_valid(perms='read'):

    # Get a request token
    flickr.get_request_token(oauth_callback='oob')

    # Open a browser at the authentication URL. Do this however
    # you want, as long as the user visits that URL.
    authorize_url = flickr.auth_url(perms='read')
    webbrowser.open_new_tab(authorize_url)

    # Get the verifier code from the user. Do this however you
    # want, as long as the user gives the application the code.
    verifier = str(input('Verifier code: '))

    # Trade the request token for an access token
    flickr.get_access_token(verifier)

response = flickr_photos_search(user_id='me', per_page = 500, extras='date_taken,url_o')
pages = int(response[0].attrib['pages'])
#print(pages)
for page in range(2, pages + 2):
    print('Page', page - 1, 'of', pages)
    photoNum = 1
    for photo in response.getiterator('photo'):
        print("\tPage", page - 1, 'of', pages, ', photo', photoNum, 'of 500')
        photoNum += 1
        photoUrl = photo.get('url_o')
        if os.path.exists('/tmp/flickr'):
            f = open('/tmp/flickr', 'r')
            downloadedUrls = f.readlines()
            f.close()
            isDownloaded = False
            for url in downloadedUrls:
                if url.strip() == photoUrl:
                    isDownloaded = True
                    break
            if isDownloaded:
                continue

        #response = flickr.photos.getAllContexts(photo_id = '34981313174')
        response = flickr_photos_getAllContexts(photo_id = photo.get('id'))
        albums = []
        for context in response.getiterator('set'):
            albums.append(context.get('title'))
        #print("\t", ';'.join(albums))
        savePicture(photo.get('url_o'), photo.get('datetaken'), ';'.join(albums))
        with open('/tmp/flickr', 'a') as f:
            print(photo.get('url_o'), file = f)
        #exit()
    response = flickr_photos_search(user_id = 'me', page = page, per_page = 500, extras = 'date_taken,url_o')
