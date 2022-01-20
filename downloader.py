from pytube import YouTube, Playlist
import os


def download(url, path):
    yt = YouTube(url)
    yt.streams\
        .filter(progressive=True, file_extension='mp4')\
        .order_by('resolution')\
        .desc().first().download(path)


def download_many(urls, path):
    for url in urls:
        download(url, path)


def download_playlist(url, path):
    playlist = Playlist(url)

    for video in playlist.video_urls:
        download(video, path)


if __name__ == '__main__':
    _url = input('Enter the url: ')

    download_path = './input'

    if not os.path.exists(download_path):
        os.mkdir(download_path)

    if _url.lower().__contains__('list'):
        download_playlist(_url, download_path)
    else:
        _urls = _url.split(';')

        download_many(_urls, download_path)
