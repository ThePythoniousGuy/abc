import googleapiclient.discovery
from urllib.parse import parse_qs, urlparse


YT_KEY = "AIzaSyAM4kPNhMkWRY7GMz7WFlk8gpGDseo57ns"


def get_all_links(play_list_url: str):
    query = parse_qs(urlparse(play_list_url).query, keep_blank_values=True)
    playlist_id = query["list"][0]

    print(f'Getting all links from {playlist_id}')
    youtube = googleapiclient.discovery.build(
        "youtube", "v3", developerKey=YT_KEY)

    request = youtube.playlistItems().list(
        part="snippet",
        playlistId=playlist_id,
        maxResults=50
    )
    response = request.execute()

    playlist_items = []
    while request:
        response = request.execute()
        playlist_items += response["items"]
        request = youtube.playlistItems().list_next(request, response)

    abc = [
        f'https://www.youtube.com/watch?v={t["snippet"]["resourceId"]["videoId"]}&list={playlist_id}&t=0s'
        for t in playlist_items
    ]

    return abc


url = """
https://youtube.com/playlist?list=PLzMcBGfZo4-lSq2IDrA6vpZEV92AmQfJK

""".strip()
if __name__ == "__main__":
    print(get_all_links(url))
