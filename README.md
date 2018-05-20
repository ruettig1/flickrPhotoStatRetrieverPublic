# flickrPhotoStatRetriever
Development to retrieve statistics from photos from flickr based on ID.

# Requirements
pip install requirements.txt

# Running instructions
python flickrStatRetriever.py <input_file.txt> <output_file.csv> <mode>

mode specifies what mode to write the output file (either 'append' or 'overwrite')

# Input
file containing filenames for downloaded files (here it is imageList.txt)

# Output
<output_file.csv> which contains all pertinent data acquired from flickr/googlemaps

# Schema
This table describes the data in each row in the output CSV file

Name | Description
------------ | -------------
filename | name of file for photos
photo_id | unique Flickr photo id
date_posted | posting date of this photo
date_taken | taken date of this photo
photo_latitude | geotagged latitude coordinate of this photo
photo_longitude | geotagged longitude coordinate of this photo
photo_comments | number of comments underneath photo
photo_views | number of views for this photo
photo_favorites | number of favorites on this photo
user_id | Flickr user id  of poster
user_ispro | 0 if user is not pro, 1 if user is pro
user_latitude | user's latitude
user_longitude | user's longitude
user_firstdatetaken | timestamp of first photo taken by user
user_firstdateposted | timestamp of first photo posted by user to Flickr
user_photocount | number of photos posted by user


# TODO
* Use pandas to calculate distributions of interesting metrics
