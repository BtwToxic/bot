import asyncio
from pyrogram import Client, filters
from pyrogram.types import ChatJoinRequest

# ─────────────────────────────
# BOT CONFIG
# ─────────────────────────────
API_ID = 31682846              
API_HASH = "ee8f0b706749f918f59fc74a60bc0381"   
BOT_TOKEN = "8573758498:AAG33V_OV793ICVavWgg-KvINZYp89XK9kM"  

app = Client(
    "auto_accept_delay_bot",
    api_id=API_ID,
    api_hash=API_HASH,
    bot_token=BOT_TOKEN
)

# ─────────────────────────────
# DELAY STORAGE (PER GROUP)
# ─────────────────────────────
JOIN_DELAY = {}   # chat_id : seconds


# ─────────────────────────────
# ADMIN CHECK (LATEST SAFE METHOD)
# ─────────────────────────────
async def is_admin(client, chat_id, user_id):
    try:
        member = await client.get_chat_member(chat_id, user_id)
        return member.status in ("administrator", "creator")
    except:
        return False


# ─────────────────────────────
# /delay COMMAND (ADMINS ONLY)
# ─────────────────────────────
@app.on_message(filters.command("delay") & filters.group)
async def set_delay(client, message):
    if not message.from_user:
        return await message.reply_text(
            "❌ Anonymous admins are not supported.\n"
            "Please disable anonymous admin mode."
        )

    chat_id = message.chat.id
    user_id = message.from_user.id

    if not await is_admin(client, chat_id, user_id):
        return await message.reply_text(
            "❌ Only group admins can set the delay."
        )

    if len(message.command) != 2:
        return await message.reply_text(
            "❌ Usage:\n`/delay <minutes>`\nExample: `/delay 1`"
        )

    try:
        minutes = int(message.command[1])
        if minutes < 0 or minutes > 1440:
            raise ValueError
    except ValueError:
        return await message.reply_text(
            "❌ Delay must be between 0 and 1440 minutes."
        )

    JOIN_DELAY[chat_id] = minutes * 60

    if minutes == 0:
        await message.reply_text("✅ Join request delay has been **disabled**.")
    else:
        await message.reply_text(
            f"✅ Join request delay set to **{minutes} minute(s)**."
        )


# ─────────────────────────────
# AUTO ACCEPT JOIN REQUEST
# ─────────────────────────────
@app.on_chat_join_request()
async def auto_accept(client: Client, request: ChatJoinRequest):
    chat = request.chat
    user = request.from_user
    delay = JOIN_DELAY.get(chat.id, 0)

    # Delay before approval
    if delay > 0:
        await asyncio.sleep(delay)

    # Approve request
    try:
        await request.approve()
    except:
        return

    # Send DM (allowed by Telegram for join-request context)
    try:
        await client.send_message(
            user.id,
            f"✅ **Your join request has been approved!**\n\n"
            f"👥 Group: **{chat.title}**\n"
            f"⏱ Delay: {delay // 60} minute(s)\n\n"
            "🎉 Welcome!\n\n"
            "ℹ️ To receive future messages, you may /start the bot."
        )
    except:
        pass

    # Optional group welcome message
    try:
        await client.send_message(
            chat.id,
            f"👋 {user.mention} joined the group."
        )
    except:
        pass


print("🤖 Auto Accept + Delay Bot Started")
app.run()
