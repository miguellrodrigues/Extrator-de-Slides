from pytube import YouTube
import os


def download(url, path):
    yt = YouTube(url)
    yt.streams\
        .filter(progressive=True, file_extension='mp4')\
        .order_by('resolution')\
        .desc().first().download(path)


if __name__ == '__main__':
    _url = input('Enter the url: ')

    download_path = './input'

    if not os.path.exists(download_path):
        os.mkdir(download_path)

    download(_url, download_path)
