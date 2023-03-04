from telegram.ext import *
from telegram import *
import logging
import time
import telegram
import threading
import flask
import html
import psutil
import shutil
import httpx


# MDC EXPORT -> ROBOTER403
key = "5656447564:AAFr26Wb7lzWQe8XUA_EbGtdhBFwakOOUuU"

# Hello Cat
key = "5364216031:AAGEGh15w8-HDTRh5gRi1KxAV6eo1RkgRms"

#ptb
key = "5898931098:AAGrI-4q-9_OshOAolbAWnsYPJiQnnGrCU4"

# Logging what's happening
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO)


def mark2(text): return telegram.helpers.escape_markdown(str(text), 2)


def esml(x): return html.escape(str(x))


HTTPX_CLIENT = {"client": httpx.AsyncClient()}


# -------------- Re usable code ------------

async def ping(u, c):
    up = u.effective_message
    s = time.perf_counter()
    m = await up.reply_text("<b>Checking...</b>", quote=True)
    e = time.perf_counter()
    try:
        await m.edit_text(f"<b>Ping: {(e-s)*1000:.2f} ms</b>")
    except Exception as e:
        print(e)


async def send(u, c):
    up = u.effective_message
    user = u.effective_user.id
    await c.bot.sendDocument(user, open("input.mp4"))
    await c.bot.sendDocument(user, open("input.mp4"))


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
<b>---  VPS  ---</b>
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


async def server_c(u, c):
    user_id = u.effective_user.id
    chat_id = u.effective_chat.id
    say = get_system_details()
    await c.bot.sendMessage(chat_id, say)


async def contact(u, c):
    say = f"""\
Give your Feedback and Suggestions in <b>@RoboterBotsChat</b>

Channel: <b>@RoboterBots</b>
Developer: <b>@Roboter403</b>
    """
    await u.effective_message.reply_text(say)


async def info(u, c):
    user_id = u.effective_user.id
    chat_id = u.effective_chat.id
    fn = esml(u.effective_user.first_name)
    ln = esml(u.effective_user.last_name)
    un = u.effective_user.username
    ulink = f"""
<a href="{f'tg://user?id={user_id}'if not un else f't.me/{un}'}">{fn}</a>
            """.strip()
    un = esml(un)
    date = esml(u.effective_message.date)
    profile_photos = await c.bot.get_user_profile_photos(user_id)

    say = f"""
👆🏻<u><b>Your Profile Photo</b></u> 👌🏻

<b>User ID     :</b> <code>{user_id}</code>
<b>Chat ID     :</b> <code>{chat_id}</code>
<b>First Name :</b> <i>{fn}</i>
<b>Last Name  :</b> <i>{ln}</i>
<b>Username   : @{un}</b>
<b>User Link  :</b> {ulink}
<b>Date       : {date[:-6]}
Time Zone   : +00:00 UTC</b>

<i>To copy your User ID, just tap on it.</i>
    """
    pps = profile_photos["photos"]

    if pps != []:
        one = pps[0][-1]["file_id"]
        await c.bot.sendPhoto(chat_id, one, caption=say)
    else:
        await c.bot.sendMessage(chat_id, say[40:])


async def start_commmand(update, context) -> None:
    msg = "Hello there!\nThis is the start command."
    await update.effective_message.reply_text(msg)


async def cute_cats(update, context) -> None:
    chatid = update.effective_chat.id
    endpoint = "https://api.thecatapi.com/v1/images/search"
    client = HTTPX_CLIENT.get("client")
    try:
        r = (await client.get(endpoint)).json()[0]["url"]
        # print(r)
        await context.bot.sendPhoto(chatid, r)
    except Exception as e:
        print(e)
        HTTPX_CLIENT["client"] = httpx.AsyncClient()


# Keep alive
app = flask.Flask('')
bbb = time.time()
@app.route('/')
def home(
): return f"Alive on the mercy of Allah (SWT)<b><b>Alive for {(bbb-time.time())/60/60:.2f} hours"
def run(): app.run(host='0.0.0.0', port=8080)
def keep_alive(): t = threading.Thread(target=run); t.start()


def main():
    df = Defaults(parse_mode=constants.ParseMode.HTML)
    app = ApplicationBuilder().token(key).defaults(df).connection_pool_size(
        333).write_timeout(100).read_timeout(100).build()

    # Command Handlers...
    start_h = CommandHandler("start", start_commmand, block=False)

    cat_h = CommandHandler("cat", cute_cats, block=False)
    app.add_handler(start_h)
    app.add_handler(cat_h)
    app.add_handler(CommandHandler("ping", ping, block=False))
    app.add_handler(CommandHandler("server", server_c, block=False))
    app.add_handler(CommandHandler("info", info, block=False))
    app.add_handler(CommandHandler("send", send, block=False))
    app.add_handler(CommandHandler("contact", contact, block=False))

    app.run_polling()


if __name__ == "__main__":
    # keep_alive()
    main()
