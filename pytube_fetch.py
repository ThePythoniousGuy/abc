from pytube import YouTube
import httpx
import time
import os
import aiofiles
import asyncio
import functools

down_ses = httpx.AsyncClient(timeout=77 * 60, verify=False)


def debug(text, filename: str = ""):
    with open(f"debug{filename}.txt", "w", encoding="utf8")as f:
        f.write(str(text))


def get_data_of_video(link):
    yt = YouTube(link)
    streams = yt.streams
    title = yt.title
    thumb = yt.thumbnail_url
    reses = tuple(i.resolution for i in streams.filter(progressive=True))
    audio = streams.get_audio_only()

    return {
        "title": title,
        "thumbnail": thumb,
        "resolutions": reses,
        "video_id": get_the_video_id(link)
    }


# def find_download_link(data:tuple or list):
# try:
# link, quality = data
# except:
# link = data[0]
# quality = None
#
# yt = YouTube(link)
# streams = yt.streams
# title = yt.title
# thumb = yt.thumbnail_url
#
# if quality:
# video = streams.filter(progressive=True, resolution=quality)[0]
# else:
# video = streams.filter(progressive=True)[-1]
#
# return {
# "url": video.url,
# "title": title,
# "thumbnail": thumb,
# "format": "mp4",
# "video":video
# }


temp = {}


def on_progress(
        vid,
        chunk,
        bytes_remaining,
        start,
        message=None,
        loop=None,
        stat=None):
    total = vid.filesize
    dnd = total - bytes_remaining
    pct = dnd / total * 100
    x = 1024**2
    if stat:
        current = f"{stat[0]} out of {stat[1]}"
    else:
        current = ""
    a = f"""
<b>Downloaded {pct:.2f} %
{dnd/x:.2f} MB of {total/x:.2f} MB @ {dnd/x/(time.time()-start):.2f} MB/s

{current}
</b>
    """.strip()

    if not message:
        print(a)
    else:
        try:
            if message:
                if time.time() - temp[message.id] >= 2:
                    loop.run_until_complete(message.edit_text(a))
                    temp[message.id] = time.time()
                    print(time.time())
        except RuntimeError as tf:
            pass
        except Exception as e:
            print(e)


def download_pytube(data):
    link = data.get("link")
    quality = data.get("quality")
    message = data.get("message")
    filename = data.get("filename")
    loop = data.get("loop")
    isaudio = data.get("audio")
    stat = data.get("stat")
    ft = time.time()
    prog = functools.partial(
        on_progress,
        start=ft,
        message=message,
        loop=loop,
        stat=stat)

    yt = YouTube(link, on_progress_callback=prog)
    streams = yt.streams
    title = yt.title
    thumb = yt.thumbnail_url

    if quality:
        video = streams.filter(progressive=True, resolution=quality)[0]
    else:
        video = streams.filter(progressive=True)[-1]

    audio = streams.get_audio_only()

    st = time.time()
    if message:
        temp[message.id] = st
    if isaudio:
        audio.download(filename=filename)
    else:
        video.download(filename=filename)

    del temp[message.id]

    return {
        "ok": True,
        "message": " File has been downloaded",
        "filename": filename,
        "time_taken": int(
            time.time() - ft),
        "title": title}


d = {
    "link": "http://www.youtube.com/watch?v=jZURhuJjMqs",
    "quality": "720p",
    "filename": "abc.mp4"}
# download_pytube(d)


def get_the_video_id(url: str):
    url = url.replace('https://', '').replace('http://', '').split('/')[1]
    if '&list' in url:
        url = url[url.find("v=") + 2: url.find('&list')]
        return url
    elif "watch?v=" in url:
        url = url[url.find("v=") + 2:]
        return url

    return url


# download_pytube(d)

# get_data_of_video("http://www.youtube.com/watch?v=OlV2vgkopBA")


async def async_download(url, name="10110", fo="", m=None):
    try:
        async with down_ses.stream("GET", url) as r:
            if not fo:
                fo = r.headers["content-type"].split('/')[1]
            for x in " ~`|√π♪÷×{}£$℅^°=[]\\<>,.@#৳%&*-+()!\"':;/?":
                name = name.replace(x, '_')
            name = name.replace('___', '_').replace('__', '_')

            filename = f"{name}.{fo}"
            total = int(r.headers["content-length"])
            st = time.time()
            ft = time.time()
            async with aiofiles.open(filename, "wb") as file:
                async for chunk in r.aiter_bytes():
                    await file.write(chunk)
                    dnd = r.num_bytes_downloaded
                    cu = time.time()

                    if cu - st >= 2:
                        j = 1000**2
                        a = f"<b>Downloaded {dnd/j:.2f} MB of {total/j:.2f} MB  @ {dnd/j/(cu-ft):.2f} MB/s</b>"
                        if not m:
                            print(a)
                        if m:
                            await m.edit_text(a)
                        st = time.time()
        return {
            "ok": True,
            "message": " File has been downloaded",
            "filename": filename,
            "size": total,
            "time_taken": int(
                time.time() - ft)}

    except httpx.RemoteProtocolError as e:
        return {
            "ok": False,
            "message": "Server closed connection unexpectedly",
            "error": str(e)}

    except Exception as e:
        return {"ok": False, "message": "Some error occurred", "error": str(e)}


async def main():
    a = find_download_link("https://youtu.be/v3uPtNMXsvI")

    x = await async_download(a.get("url"), a.get("title"), "mp4")
    print(x)


if __name__ == "__main__":
    # asyncio.run(main())
    # os.system("pip freeze > requirements.txt")
    pass
