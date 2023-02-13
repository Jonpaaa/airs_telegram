import os
import logging
from functools import wraps
from telegram import Update, InputFile, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Updater, CallbackQueryHandler, filters, MessageHandler, ApplicationBuilder, CommandHandler, ContextTypes
from config import TOKEN

import datetime
import time
from airs_scripts import e6b, holds, checkWx, notamRead, plateFetch, flightPlan, aipFetch


logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO)


def log_command(func):
    @wraps(func)
    async def wrapper(*args, **kwargs):
        start_time = time.time()
        update = args[0]
        user = update.message.from_user.username
        full_name = update.message.from_user.full_name
        logging.info(f"command FROM {user}, {full_name} at {start_time}")
        result = await func(*args, **kwargs)
        response_time = time.time() - start_time
        logging.info(f"Response TO {user}, {full_name} in {response_time}")
        return result
    return wrapper

"""
___________STATUS AND HELP SECTION__________
    This is the section used to check the bot's status and get help.
"""

utc_Raw = datetime.datetime.utcnow()
utc = utc_Raw.strftime('%H%M')
@log_command
###Start and Help
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await context.bot.send_message(chat_id=update.effective_chat.id, text=f"TIME: {utc}Z\nACTIVE")

@log_command
async def help(update: Update, context: ContextTypes.DEFAULT_TYPE):
    args = context.args

    commands = [
        ("/start", ""),
        ("/e6b", "[TAS], [TRK], [W], [V], (opt)[DIST]"),
        ("/hold", "[TRK], [RAD], [STD?], (opt)[P]"),
        ("/notam", "[ICAO code]"),
        ("/wx", "[ICAO code]"),
        ("/aip", "[Alpha-2 code]"),
        ("/plates", "[ICAO code]")
    ]

    verbose = [
    "Starts bot and gives status information",
    "Returns HDG, GS and *Time [DIST]",
    "Returns sector information, and *Picture [p]",
    "Returns NOTAMs for Aerodrome",
    "Returns METAR and TAF for Aerodrome",
    "Returns link and info on AIP for country",
    "Returns Jeppesen plates for Aerodrome"
    ]

    if len(args) == 0:
        message = "List of commands:\n"
        for command in commands:
            message += f"{command[0]} {command[1]}\n"
        await context.bot.send_message(chat_id=update.effective_chat.id, text=message)
        return
    elif len(args) == 1:
        if args[0] == "-v":
            message = "Invalid option.\n\nFor more information, use `/help [command] -v`"
            await context.bot.send_message(chat_id=update.effective_chat.id, text=message)
            return
        else:
            command = [c for c in commands if c[0] == f"/{args[0]}"]
            if not command:
                message = "Invalid command.\n\nFor a list of commands, use `/help`"
                await context.bot.send_message(chat_id=update.effective_chat.id, text=message)
                return
            else:
                message = f"{command[0][0]} {command[0][1]}"
                await context.bot.send_message(chat_id=update.effective_chat.id, text=message)
                return
    elif len(args) == 2:
        if args[1] != "-v":
            message = "Invalid option.\n\nFor more information, use `/help [command] -v`"
            await context.bot.send_message(chat_id=update.effective_chat.id, text=message)
            return
        else:
            command = [c for c in commands if c[0] == f"/{args[0]}"]
            if not command:
                message = "Invalid command.\n\nFor a list of commands, use `/help`"
                await context.bot.send_message(chat_id=update.effective_chat.id, text=message)
                return
            else:
                index = commands.index(command[0])
                message = f"{command[0][0]} {command[0][1]}\n\nDescription:\n{verbose[index]}"
                await context.bot.send_message(chat_id=update.effective_chat.id, text=message)
                return
    else:
        message = "Only able to send information on one command at a time"
        await context.bot.send_message(chat_id=update.effective_chat.id, text=message)
        return
### E6B
@log_command
async def nav_Calc(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # Extract the TAS, track, W/V from the user's message
    args = context.args
    if len(args) not in [4, 5]:
        await context.bot.send_message(chat_id=update.effective_chat.id, text="Incorrect number of arguments. Please provide TAS, TRK, W, V, opt [DIST].")
        return

    true_Airspeed, track, wind, wind_v = map(int, args[:4])
    distance = int(args[4]) if len(args) == 5 else 0
    try:
        true_Airspeed, track, wind, wind_v = int(true_Airspeed), int(track), int(wind), int(wind_v)
        if distance:
            distance = int(distance)

        
    except ValueError:
        await context.bot.send_message(chat_id=update.effective_chat.id, text="Inputs must be integers.")
        return

    # Call the e6b_calc function and store the 3 returned values
    hdg, gs, *hhmm_parts = e6b.e6b_calc(true_Airspeed, track, wind, wind_v, distance)
    # Construct the message to send to the user
    hhmm = f"ETA: {hhmm_parts[0]}" if hhmm_parts else ""
    message = f"TAS: {true_Airspeed} | TRK: {track} | W/V: {wind}/{wind_v}\n\nHDG: {hdg}\nGS: {gs}\n{hhmm}"
    # Send the message to the user
    await context.bot.send_message(chat_id=update.effective_chat.id, text=message)



### HOLD
@log_command
async def hold(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # Extract the track, radial, and if it's a standard pattern from the user's message, and the optional image argument
    args = context.args
    if len(args) != 3 and len(args) != 4:
        await context.bot.send_message(chat_id=update.effective_chat.id, text="Incorrect number of arguments. Please provide trk, rad, std, and (optional) image.")
        return
    trk, rad, std = args[:3]
    try:
        trk, rad = int(trk), int(rad)
    except ValueError:
        await context.bot.send_message(chat_id=update.effective_chat.id, text="trk and rad must be integers.")
        return
    if not isinstance(std, str):
        await context.bot.send_message(chat_id=update.effective_chat.id, text="std must be a string.")
        return
    # Call the calculate function and store the 4 returned values
    holdPic, toFlag, sector, instruction, directToTeardrop, directToParallel, parallelToTeardrop = holds.calculate(trk, rad, std)
    # Check if the user requested the image
    if len(args) == 4 and args[3] == "p":
        # Save the image to a file
        holdPic.save("hold.png")
        # Send the image to the user
        with open("hold.png", "rb") as f:
            await context.bot.send_photo(chat_id=update.effective_chat.id, photo=f)
    # Construct the message to send to the user
    message = f"TRK: {trk} | RAD: {rad}\n\n⬆ TO STN: {toFlag}\nSector: {sector}, {instruction}\nS3 Direct: {directToTeardrop} - {directToParallel}\nS2 Parallel: {directToParallel} - {parallelToTeardrop}\nS1 Teardrop: {parallelToTeardrop} - {directToTeardrop}"
    # Send the message to the user
    await context.bot.send_message(chat_id=update.effective_chat.id, text=message)


"""
___________FLIGHT PLANNING SECTION__________
    This is the section used for retrieval of useful information before a flight, with potential costs. External API's are used to retrieve data.
"""

### FLIGHT PLAN DB
@log_command
async def gen_fp(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # Extract the DEP & DEST from the user's message
    args = context.args
    if len(args) != 2:
        await context.bot.send_message(chat_id=update.effective_chat.id, text="Incorrect number of arguments. Please input DEP & DEST.")
        return
    dep, dest = args  
    # Call the flightplan function
    plan = await flightPlan.flightPlan(dep, dest)
    # Construct the message to send to the user
    message = ""
    for i, node in enumerate(plan):
        message += f"Ident: {node['ident']}\nType: {node['type']}\nLat: {node['lat']}\nLon: {node['lon']}\nAlt: {node['alt']}\nVia: {node['via']}\n"
        if i != len(plan) - 1:
            message += f"TRK(M): {node['track_mag']}\nTRK(T): {node['track_true']}\nDIST: {node['dist']}\n\n"
        else:
            message += "\n"

    messages = [message[i:i+4096] for i in range(0, len(message), 4096)]

    for message in messages:
        await context.bot.send_message(chat_id=update.effective_chat.id, text=message)

### NOTAM
@log_command
async def check_notam(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # Extract the region code from the user's message
    args = context.args
    if len(args) != 1:
        await context.bot.send_message(chat_id=update.effective_chat.id, text="Incorrect number of arguments. Please input a valid NOTAM region.")
        return
    fir = args[0]
    FIR = fir.strip()
    if not isinstance(FIR, str):
        await context.bot.send_message(chat_id=update.effective_chat.id, text="Please input a valid NOTAM region.")
        return
    # Call the notam function
    NOTAM = notamRead.notam(FIR)
    # Construct the message to send to the user
    messages = [NOTAM[i:i+4096] for i in range(0, len(NOTAM), 4096)]
    # Send the message to the user
    for message in messages:
        await context.bot.send_message(chat_id=update.effective_chat.id, text=message)

### WEATHER
@log_command
async def check_wx(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # Extract the ICAO code from the user's message
    args = context.args
    if len(args) != 1:
        await context.bot.send_message(chat_id=update.effective_chat.id, text="Incorrect number of arguments. Please input a valid ICAO Code.")
        return
    ad = args[0]
    AD = ad.strip()
    if not isinstance(AD, str):
        await context.bot.send_message(chat_id=update.effective_chat.id, text="Please input a valid ICAO code.")
        return
    # Call the wx function
    METAR, TAF = checkWx.wx(AD)
    # Construct the message to send to the user
    message = f"{METAR}\n{TAF}"
    # Send the message to the user
    await context.bot.send_message(chat_id=update.effective_chat.id, text=message)

### AIP
@log_command
async def aip_fetch(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # Extract the args from the user's message
    args = context.args
    if len(args) != 1:
        await context.bot.send_message(chat_id=update.effective_chat.id, text="Invalid number of arguments. Please enter a 2-letter code.")
        return
    country = args[0]
    COUNTRY = country.strip().upper()
    if not isinstance(COUNTRY, str) or len(COUNTRY) != 2:
        await context.bot.send_message(chat_id=update.effective_chat.id, text="Invalid code. Please enter a 2-letter code.")
        return
    # Call the function
    aip = aipFetch.get_eaip_by_alpha_code(COUNTRY)
    if aip is None:
        await context.bot.send_message(chat_id=update.effective_chat.id, text="No information found for " + COUNTRY)
        return
    # Construct the message to send to the user
    message = f"Information for {list(aip.values())[1]}:\n"
    message += f"Status: {aip['status']}\n"
    message += f"Access: {aip['access']}\n"
    message += f"URL: {aip['url']}"
    # Send the message to the user
    await context.bot.send_message(chat_id=update.effective_chat.id, text=message)

### JEPPESEN PLATES
@log_command
async def plates_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # Extract the args from the user's message
    plate = context.args
    if len(plate) != 1:
        await context.bot.send_message(chat_id=update.effective_chat.id, text="Invalid number of arguments. Please enter a 4-letter code.")
        return
    plate_code = plate[0]
    if len(plate_code) != 4:
        await context.bot.send_message(chat_id=update.effective_chat.id, text="Invalid code. Please enter a 4-letter code.")
        return
    # Call the function
    pdf_path = plateFetch.get_pdf_path(plate_code)
    if pdf_path is None:
        await context.bot.send_message(chat_id=update.effective_chat.id, text="No matching file found.")
        return

    # Send the file to the user
    with open(pdf_path, 'rb') as f:
        pdf_file = f.read()

    await context.bot.send_document(chat_id=update.effective_chat.id, document=InputFile(pdf_file, filename=f'{plate}.pdf'))    


if __name__ == '__main__':
    print ('AIRS has started')
    application = ApplicationBuilder().token(TOKEN).build()
    
    start_handler = CommandHandler('start', start)
    application.add_handler(start_handler)
    
    help_handler = CommandHandler('help', help)
    application.add_handler(help_handler)

    navCalc_handler = CommandHandler('e6b', nav_Calc)
    application.add_handler(navCalc_handler)    

    hold_handler = CommandHandler('hold', hold)
    application.add_handler(hold_handler)

    fp_handler = CommandHandler('fp', gen_fp)
    application.add_handler(fp_handler)

    notam_handler = CommandHandler('notam', check_notam)
    application.add_handler(notam_handler)

    wx_handler = CommandHandler('wx', check_wx)
    application.add_handler(wx_handler)

    aip_handler = CommandHandler('aip', aip_fetch)
    application.add_handler(aip_handler)

    plates_handler = CommandHandler('plates', plates_handler)
    application.add_handler(plates_handler)

    application.run_polling()


