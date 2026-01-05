import asyncio
from pyrogram import Client, filters
from pyrogram.types import ChatJoinRequest
from pyrogram.errors import UserIsBlocked, PeerIdInvalid

# ─────────────────────────────
# BOT CONFIG (AS YOU REQUESTED)
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
# DELAY STORAGE
# ─────────────────────────────
JOIN_DELAY = {}  # chat_id : seconds


# ─────────────────────────────
# ADMIN CHECK (FIXED – NO FALSE ERRORS)
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
            "❌ Anonymous admins are not supported."
        )

    if not await is_admin(client, message.chat.id, message.from_user.id):
        return await message.reply_text(
            "❌ Only group admins can set the delay."
        )

    if len(message.command) != 2:
        return await message.reply_text(
            "Usage: /delay <minutes>\nExample: /delay 1"
        )

    try:
        minutes = int(message.command[1])
        if minutes < 0 or minutes > 1440:
            raise ValueError
    except ValueError:
        return await message.reply_text(
            "Delay must be between 0 and 1440 minutes."
        )

    JOIN_DELAY[message.chat.id] = minutes * 60

    if minutes == 0:
        await message.reply_text("✅ Join request delay disabled.")
    else:
        await message.reply_text(
            f"✅ Join request delay set to {minutes} minute(s)."
        )


# ─────────────────────────────
# AUTO ACCEPT JOIN REQUEST (FIXED)
# ─────────────────────────────
@app.on_chat_join_request()
async def auto_accept(client: Client, request: ChatJoinRequest):
    chat = request.chat
    user = request.from_user
    delay = JOIN_DELAY.get(chat.id, 0)

    # Delay
    if delay > 0:
        await asyncio.sleep(delay)

    # ALWAYS approve request
    try:
        await request.approve()
    except:
        return

    # Message text (same as your screenshot)
    text = (
        "✅ **Your request has been accepted successfully!**\n\n"
        f"👥 Group: **{chat.title}**\n"
        f"⏱ Delay: {delay // 60} minute(s)\n\n"
        "🎉 Welcome!"
    )

    # Try DM
    try:
        await client.send_message(user.id, text)

    except (UserIsBlocked, PeerIdInvalid):
        # Bot is blocked → Telegram will show system notification automatically
        pass

    except:
        pass

    # Group fallback message (optional but useful)
    try:
        await client.send_message(
            chat.id,
            f"👋 {user.mention} joined the group.\n"
            "ℹ️ Please unblock the bot to receive welcome messages."
        )
    except:
        pass


print("🤖 Auto Accept + Delay Bot Started")
app.run()
