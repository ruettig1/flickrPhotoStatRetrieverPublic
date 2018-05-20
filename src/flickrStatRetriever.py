import flickrapi
from flickrapi import FlickrAPI
import datetime as datetime
import csv
import argparse
import googlemaps
import time
import sys
import config
import requests

#globals
gmaps_key = 'redacted'
public_key = 'redacted'
secret_key = 'redacted'
flickr = FlickrAPI(public_key, secret_key, format='parsed-json')
gmaps = googlemaps.Client(key=gmaps_key)

#methods
def convertTimestamp(unix_timestamp):
    if unix_timestamp != 'null' or date_posted != 'empty':
        return datetime.datetime.fromtimestamp(int(unix_timestamp)).strftime('%Y-%m-%d %H:%M:%S')
    return unix_timestamp

def createCSV(records_list, file_name, mode):
    if mode == 'append':
        write_mode = 'a'
    if mode == 'overwrite':
        write_mode = "w"
    with open(file_name, write_mode) as f:
        writer = csv.writer(f)
        writer.writerows(records_list)

def createRedoList(redo_list):
    with open("./results/redo.txt", "w") as f:
        f.write(''.join(redo_list))

def parseImageList(file_name):
    f = open(file_name)
    img_list = []
    img_list = [line for line in f]
    f.close()
    return img_list

def retrieveUserCoordinates(location):
    lat_long = []
    if location != '':
        location_dict = gmaps.geocode(location)[0]
        lat_long.append(location_dict['geometry'].get('location', {}).get('lat', ''))
        lat_long.append(location_dict['geometry'].get('location', {}).get('lng', ''))
        return lat_long
    else:
        return(['', ''])

def parsePhotoInfo(photo_dict, favorites_dict):

    photo_info = []

    photo_info.append(photo_dict['photo'].get('dates', {}).get('taken', ''))
    photo_info.append(convertTimestamp(photo_dict['photo'].get('dates', {}).get('posted', '')))
    photo_info.append(photo_dict['photo'].get('location', {}).get('latitude', ''))
    photo_info.append(photo_dict['photo'].get('location', {}).get('longitude', ''))
    photo_info.append(photo_dict['photo'].get('comments', {}).get('_content', ''))
    photo_info.append(photo_dict['photo'].get('views', ''))
    photo_info.append(favorites_dict['photo'].get('total', ''))

    return photo_info

def parseUserInfo(user_dict):

    user_info = []
    user_info.append(user_dict['person'].get('id', ''))
    user_info.append(user_dict['person'].get('ispro', ''))
    user_location = user_dict['person'].get('location', {}).get('_content', '')
    user_info.extend(retrieveUserCoordinates(user_location))
    user_info.append(user_dict['person']['photos'].get('firstdatetaken', {}).get('_content', ''))
    user_info.append(convertTimestamp(user_dict['person']['photos'].get('firstdate', {}).get('_content', '')))
    user_info.append(str(user_dict['person']['photos'].get('count', {}).get('_content', '')))

    return user_info

def createRecord(photo_id, flickr_photo_id, user_info, photo_info):
    record = []
    record.append(photo_id.strip())
    record.append(flickr_photo_id)
    record.extend(photo_info)
    record.extend(user_info)
    return record


def main(input_file, output_file, mode):
    img_list = parseImageList(input_file)

    record_list = []
    reject_list = []
    redo_list = []

    if mode != 'append':
        record_list.append(config.record_schema)
        reject_list.append(config.reject_schema)

    counter = 1;

    for photo_id in img_list:
        print("Processing image {} out of {}".format(counter, len(img_list)))
        counter = counter+1
        record = []
        reject = []
        photo_info = []
        user_info = []
        flickr_photo_id = photo_id.partition('_')[0]
        try:
            photo_dict = flickr.photos.getInfo(api_key = public_key, photo_id=flickr_photo_id)
            favorites_dict = flickr.photos.getFavorites(api_key = public_key, photo_id=flickr_photo_id)
            photo_info = parsePhotoInfo(photo_dict, favorites_dict)
            user_dict = flickr.people.getinfo(api_key = public_key, user_id = photo_dict['photo']['owner']['nsid'])
            user_info = parseUserInfo(user_dict)
        except flickrapi.exceptions.FlickrError as e:
            if e.code == None:
                redo_list.append(photo_id)
                continue
            else:
                if not photo_info:
                    photo_info = ['']*7
                if not user_info:
                    user_info = ['']*7
                reject.append(photo_id.rstrip())
                reject.append(photo_id.partition('_')[0])
                reject.append(e.code)
                reject_list.append(reject)
        except requests.exceptions.ConnectionError as e:
            redo_list.append(photo_id)
            continue
        except googlemaps.exceptions.Timeout as e:
            redo_list.append(photo_id)
            continue
        except:
            print("Unexpected error:", sys.exc_info()[0])
            if not photo_info:
                photo_info = ['']*7
            if not user_info:
                user_info = ['']*7
            reject.append(photo_id.rstrip())
            reject.append(photo_id.partition('_')[0])
            reject.append('x')
            reject_list.append(reject)

        record_list.append(createRecord(photo_id, flickr_photo_id, user_info, photo_info))

    createRedoList(redo_list)
    createCSV(record_list, output_file, mode)
    createCSV(reject_list, './results/reject.csv', mode)

if __name__ == "__main__":

    parser = argparse.ArgumentParser(description='Application to retrieve social media statistics from the Flickr API')

    parser.add_argument('f',
                        help='Input file to be processed')

    parser.add_argument('o',
                        help='File output is to be written to')

    parser.add_argument('m',
                        help='Mode for output file (append or overwrite)')

    args = parser.parse_args()

    if(args.f):
        print("Input file is %s" % args.f)
    else:
        print("NO INPUT FILE")
        exit()

    if(args.o):
        print("Output file is %s" % args.o)
    else:
        print("NO OUTPUT FILE")
        exit()

    if(args.m):
        print("Output file mode is %s" % args.o)
    else:
        print("NO OUTPUT MODE")
        exit()

    main(args.f, args.o, args.m)
