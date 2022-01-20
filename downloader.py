from pytube import YouTube


def download(url, path):
    yt = YouTube(url)
    yt.streams\
        .filter(progressive=True, file_extension='mp4')\
        .order_by('resolution')\
        .desc().first().download(path)


if __name__ == '__main__':
    _url = input('Enter the url: ')

    download(_url, './input/')
