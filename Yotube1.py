import requests
import csv
from urllib.parse import quote
import isodate

def get_channel_videos(channel_id, api_key):
    base_url = "https://www.googleapis.com/youtube/v3"
    encoded_channel_id = quote(channel_id)
    endpoint = f"{base_url}/search?key={api_key}&channelId={encoded_channel_id}&part=snippet,id&order=date&maxResults=20"

    response = requests.get(endpoint)
    if response.status_code == 200:
        return response.json()
    else:
        print(f"Error: Unable to fetch channel videos (status code {response.status_code})")
        print(response.text)
        return None

def get_video_details(video_id, api_key):
    base_url = "https://www.googleapis.com/youtube/v3"
    endpoint = f"{base_url}/videos?id={video_id}&key={api_key}&part=contentDetails,statistics"

    response = requests.get(endpoint)
    if response.status_code == 200:
        video_data = response.json()
        duration = video_data['items'][0]['contentDetails']['duration']
        view_count = int(video_data['items'][0]['statistics']['viewCount'])
        return duration, view_count
    else:
        print(f"Error: Unable to fetch video details (status code {response.status_code})")
        return None, None

def export_to_csv(videos, api_key, file_name):
    video_data_list = []

    for video in videos['items']:
        title = video['snippet']['title']
        video_id = video['id']['videoId']
        video_url = f"https://www.youtube.com/watch?v={video_id}"
        thumbnail_url = video['snippet']['thumbnails']['high']['url']
        duration_iso, view_count = get_video_details(video_id, api_key)
        if duration_iso is not None:
            duration_seconds = isodate.parse_duration(duration_iso).total_seconds()
        else:
            duration_seconds = None
        video_data_list.append([title, video_id, video_url, thumbnail_url, duration_seconds, view_count])

    sorted_video_data_list = sorted(video_data_list, key=lambda x: x[5], reverse=True)

    with open(file_name, 'w', encoding='utf-8', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(['Title', 'Video ID', 'URL', 'Thumbnail URL', 'Duration (seconds)', 'View Count'])

        for video_data in sorted_video_data_list:
            writer.writerow(video_data)

print("Please enter your YouTube API key:")
api_key = input().strip()

print("Please enter the YouTube channel ID:")
channel_id = input().strip()

output_file = "channel_videos.csv"

channel_videos = get_channel_videos(channel_id, api_key)

if channel_videos:
    export_to_csv(channel_videos, api_key, output_file)
    print(f"Video information exported to {output_file}")
