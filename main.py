
from pyrogram import *
from pyrogram.types import (
    ReplyKeyboardMarkup,
    InlineKeyboardMarkup,
    InlineKeyboardButton)


import os
import sys
import time
import html
import httpx
try:
    import psutil
except BaseException:
    pass
import shutil
import logging
import asyncio
import aiofiles


# Helpers
try:
    import fetch_playlist
    import pytube_fetch
except ImportError as e:
    import Yt.fetch_playlist as fetch_playlist
    import Yt.pytube_fetch as pytube_fetch


def esml(x): return html.escape(str(x))


inMark = InlineKeyboardMarkup
inButton = InlineKeyboardButton

# Logging info
logger = logging.getLogger(__name__)
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO)


def debug(text, filename: str = ""):
    with open(f"debug{filename}.txt", "w", encoding="utf8")as f:
        f.write(str(text))


def clear():
    for i in os.listdir():
        if i.endswith(".session"):
            os.remove(i)


def delete_prev():
    for i in os.listdir():
        if i.split('.')[-1] in "mp4 mp4 mkv 3gp".split():
            os.remove(i)


# delete_prev()


admin = 5596148289
api_id = 10661093
api_hash = "ffa39e7d5836716e9a084233b828ae34"
key = "5877028651:AAFz5Fd_swxSZyqeCkY96hzlbkgL1J0E_C4"

# @ytgitaction
key = "5962713812:AAEdrzBgzEScRzh0iBdyAPl8DrM7GyDOUNQ"

key = "5919367026:AAERLPSPBCXPH0sDeBR14Dr6xbCMlNDq8JU"

bot = Client("Youtube1", api_id, api_hash, bot_token=key)


@bot.on_message(filters.command("start"))
async def start_command(c, m):
    debug(m)
    await m.reply("<b>Alive</b>")


# -------- Getting Server Details --------
def get_system_details():
    cpu = psutil.cpu_count()
    mem = dict(psutil.virtual_memory()._asdict())
    total, used, free = shutil.disk_usage("/")
    _ = 2**30
    all_m = f"{mem['total']/_:.2f}"
    use_m = f"{mem['used']/_:.2f}"
    all_d = f"{total / _:.2f}"
    use_d = f"{used / _:.2f}"
    left_d = f"{free/ _:.2f}"
    ug_d = esml(f"{used/total*100:.2f}")
    say = f"""\
CPU : <b>{cpu} Cores</b>
<b><u>       RAM      </u></b>
Total : <b>{all_m} GB</b>
Used  : <b>{use_m} GB</b>
Usage : <b>100/{esml(mem["percent"])} %</b>
<b><u>       DISK     </u></b>
Total : <b>{all_d} GB</b>
Used  : <b>{use_d} GB</b>
Free  : <b>{left_d} GB</b>
Usage : <b>100/{ug_d} %</b>
"""
    return say


@bot.on_message(filters.command("server"))
async def server_c(c, m):
    say = get_system_details()
    await m.reply(say)


@bot.on_message(filters.command(["down", "download"]))
async def custom_download(c, m):
    try:
        url = m.text.split()[1]
    except BaseException:
        await m.reply("<b>Please give url after /down</b>")
        return

    mes_id = str(m.id)

    x = await m.reply(f"""<b>Downloading...\nUrl: <a href="{url}">{url}</a></b>""")

    do = await pytube_fetch.async_download(url, mes_id, m=x)
    await x.edit_text("<b>Downloaded. Now uploading.</b>")
    filename = do.get("filename")
    await c.send_document(m.chat.id, open(filename, "rb"))

    os.remove(filename)


@bot.on_message(filters.command("ping"))
async def ping(c, m):
    s = time.time()
    x = await m.reply("<b>Checking...</b>")
    await x.edit_text(f"<b>Ping: {(time.time()-s)*1000:.2f} ms</b>")


async def download_other(link, message, quality, number, outof):
    yturl = link
    x = await message.edit_text(f"<b>Downloading {esml(link)}</b>...")
    edit_text = x.edit_text
    await edit_text("<b>Processing...</b>")
    loop = asyncio.get_running_loop()
    fn = f"{message.id}-{number}-{outof}.mp4"

    d = {
        "link": yturl,
        "quality": quality,
        "filename": fn,
        "message": message,
        "loop": asyncio.get_running_loop(),
        "stat": (number, outof)}

    try:
        got = await loop.run_in_executor(None, pytube_fetch.download_pytube, d)
        title = got.get("title")
    except Exception as e:
        print(e)
        try:
            pass  # os.remove(fn)
        except BaseException:
            pass
        await edit_text(f"<b>An error occurred.\nPlease try again</b>\n<pre>{esml(e)}</pre>")


async def get_playlist(c, m):
    text = m.text
    error = False
    try:
        quality = text.split()[1]
        say = f"Downloading the videos in {quality}"
    except IndexError as e:
        say = "Give the quality after playlust link"
        quality = "720p"
    except Exception as e:
        print(e)
        say = f"<b>Error!</b>\n<pre>{esml(e)}</pre>"
        error = True

    x = await m.reply(say)
    if error:
        return

    links = fetch_playlist.get_all_links(text.split()[0])

    if quality.isdecimal():
        quality = str(quality) + 'p'
    elif quality not in "720p 360p 144p":
        await x.edit_text("<b>Invalid quality </b>")
        return
    outof = len(links)
    for number, i in enumerate(links):
        video_id = pytube_fetch.get_the_video_id(i)
        url = f"https://youtube.com/watch?v={video_id}"
        # await x.edit_text(f"Downloading {url} in {quality}")
        await download_other(url, x, quality, number + 1, outof)
    await x.edit_text(f"Done All of {url}")


@bot.on_message(filters.text)
async def handle_it(c, m):
    text = m.text

    if m.outgoing:
        return
    if not text.lower().startswith("http"):
        await m.reply("<b>Maybe this isnt a link</b>")
        return
    if "playlist?list=" in text:
        await get_playlist(c, m)
        return

    x = await m.reply("<b>Processing...</b>")
    loop = asyncio.get_running_loop()
    data = await loop.run_in_executor(None, pytube_fetch.get_data_of_video, text)

    title = data.get("title")
    thumb = data.get("thumbnail")
    reses = data.get("resolutions")
    video_id = data.get("video_id")

    say = f"""
<b>{esml(title)}</b>
<a href="{thumb}"> </a>

<i>Select the desired format:</i>
	"""

    buttons = []

    for i in reses:
        a = [inButton(i, callback_data=f"video {video_id} {i}")]
        k = len(buttons) - 1
        if buttons and len(buttons[k]) == 1:
            buttons[k] += a
        else:
            buttons.append(a)
    buttons.append(
        [inButton("Audio 128kbps", callback_data=f"audio {video_id}")])

    await x.edit_text(say, reply_markup=inMark(buttons))


temp = {}


async def progress(current, total, client, message, start):
    pct = current / total * 100
    x = 1024**2
    a = f"""
<b>Uploaded {pct:.2f} % | {current/x:.2f} MB of {total/x:.2f} MB @ {current/x/(time.time()-start):.2f} MB/s </b>
"""
    print(a)
    if time.time() - temp[message.id] >= 2:
        await message.edit_text(a)
        temp[message.id] = time.time()

    # if (current * 100 / total) > 50:
        # client.stop_transmission()


@bot.on_callback_query()
async def answer(c: Client, cq):
    data = cq.data
    chat_id = cq.from_user.id
    mes_id = str(cq.message.id)

    async def edit_text(text):
        await cq.message.edit_text(str(text))

    if data.startswith("video"):
        data = data.split()
        quality = data[2]
        video_id = data[1]

        await cq.answer(
            f"{quality} Selected",
            show_alert=False)

        yturl = f"https://youtube.com/watch?v={video_id}"
        await edit_text("<b>Processing...</b>")
        loop = asyncio.get_running_loop()
        fn = f"{mes_id}.mp4"

        d = {
            "link": yturl,
            "quality": quality,
            "filename": fn,
            "message": cq.message,
            "loop": loop}

        try:
            got = await loop.run_in_executor(None, pytube_fetch.download_pytube, d)
            title = got.get("title")
        except Exception as e:
            try:
                os.remove(fn)
            except BaseException:
                pass
            await edit_text(f"<b>An error occurred.\nPlease try again</b>\n<pre>{esml(e)}</pre>")
            # await c.send_message(admin, f"<pre>{esml(e)}</pre>")

            return

        await edit_text(f"<b>Downloaded. Now uploading to Telegram.\nTime taken: {got.get('time_taken')} s</b>")
        print("Downloaded the file for", chat_id, title)

        filename = got.get("filename")

        s = time.time()
        temp[int(mes_id)] = s
        await c.send_document(chat_id, open(filename, "rb"), caption=title, file_name=f"{title}.mp4", progress=progress, progress_args=(c, cq.message, s))
        del temp[int(mes_id)]
        os.remove(filename)

        await edit_text(f"<b>Downloaded in <i>{got.get('time_taken')} s</i>.\nUploaded in <i>{int(time.time()-s)}</i> s</b>")

    elif data.startswith("audio"):
        data = data.split()
        video_id = data[1]

        await cq.answer(
            f"Audio 128kbps Selected",
            show_alert=False)

        yturl = f"https://youtube.com/watch?v={video_id}"
        await edit_text("<b>Processing...</b>")
        loop = asyncio.get_running_loop()
        fn = f"{mes_id}.mp3"

        d = {
            "link": yturl,
            "filename": fn,
            "message": cq.message,
            "loop": loop,
            "audio": True}

        try:
            got = await loop.run_in_executor(None, pytube_fetch.download_pytube, d)
            title = got.get("title")
        except Exception as e:
            try:
                os.remove(fn)
            except BaseException:
                pass
            await edit_text(f"<b>An error occurred.\nPlease try again</b>\n<pre>{esml(e)}</pre>")
            # await c.send_message(admin, f"<pre>{esml(e)}</pre>")

            return

        await edit_text(f"<b>Downloaded. Now uploading to Telegram.\nTime taken: {got.get('time_taken')} s</b>")
        print("Downloaded the file for", chat_id, title)

        filename = got.get("filename")

        s = time.time()
        temp[int(mes_id)] = s
        await c.send_document(chat_id, open(filename, "rb"), caption=title, file_name=f"{title}.mp3", progress=progress, progress_args=(c, cq.message, s))
        del temp[int(mes_id)]
        os.remove(filename)

        await edit_text(f"<b>Downloaded in <i>{got.get('time_taken')} s</i>.\nUploaded in <i>{int(time.time()-s)}</i> s</b>")


def run_main():
    bot.run()


if __name__ == "__main__":
    run_main()
