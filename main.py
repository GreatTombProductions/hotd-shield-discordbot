import discord
import os
import pickle
from datetime import datetime, timedelta
from keep_alive import keep_alive

client = discord.Client()

try:
    with open ('shields.pkl', 'rb') as fp:
        shields = pickle.load(fp)
except:
    shields = []

def format_timedelta(td):
    minutes, seconds = divmod(td.seconds + td.days * 86400, 60)
    hours, minutes = divmod(minutes, 60)
    return '{:d}h:{:02d}m'.format(hours, minutes)

@client.event
async def on_ready():
    print('We have logged in as {0.user}'.format(client))

@client.event
async def on_message(message):
    global shields
    if message.author == client.user:
        return

    if message.content.startswith('!shield'):
        content = message.content.split(" ")

        if len(content) > 1:
            new_shield = True
            # add a shield
            user = message.author

            admin_mode = False
            if user.name == "AvatarOfNazarick":
                try:
                    float(content[1])
                except:
                    admin_mode = True

            if admin_mode:
                username = content[1]
                shield_length = content[2]
            else:
                shield_length = content[1]

            try:
                shield_length = float(shield_length)
            except:
                tosend = 'Shield length formatted incorrectly, try again. For example,to register an 8 hour shield: "!shield 8 Luggergue"'
                await message.channel.send(tosend)
                new_shield = False
                return

            if shield_length < 0 or shield_length > 72:
                tosend = 'Shield length must be between 0 and 72 hours. For example,to register an 8 hour shield: "!shield 8 Luggergue"'
                await message.channel.send(tosend)
                new_shield = False
                return

            if len(content) > 2 and not admin_mode:
                description = " ".join(content[2:])
            elif len(content) > 3 and admin_mode:
                description = " ".join(content[3:])
            else:
                description = ""

            start_time = datetime.now()

            if not admin_mode:
                if user.nick is None:
                    username = user.name
                else:
                    username = user.nick

            if new_shield:
                entry = {"user": username,
                         "amount": shield_length,
                         "description" : description,
                         "start_time": start_time,
                         "remaining_time": shield_length}
    
                shields = [shield for shield in shields if shield["user"] != entry["user"]]
                        
                shields.append(entry)
        # display current shields
        tosend = "Currently active shields:"

        valid_shields = []
        for i, shield in enumerate(shields):
            hours_active = datetime.now() - shield["start_time"]
            remaining_time = timedelta(hours=shield["amount"]) - hours_active

            if remaining_time > timedelta(0):
                valid_shields.append(i)
            
            remaining_time = format_timedelta(remaining_time)
            shield["remaining_time"] = remaining_time

        shields = [shields[i] for i in range(len(shields)) if i in valid_shields]

        if len(shields) == 0:
            tosend += ' none.\nTo register a shield, say "!shield time description" where time is a number between 0 and 72 representing hours. For example,to register an 8 hour shield: "!shield 8 Luggergue"'
            await message.channel.send(tosend)
            return

        shields = sorted(shields, key=lambda d: d['remaining_time'], reverse=True)

        for shield in shields:
            row = f"\n{shield['user']}, {shield['remaining_time']} remaining"
            if len(shield["description"]) > 0:
                row = row + f", {shield['description']}"

            tosend = tosend + row

        tosend = tosend + '\n\nRegister a new shield with "!shield time description" where time is a number between 0 and 72 representing hours. For example,to register an 8 hour shield: "!shield 8 Luggergue"'

        with open("shields.pkl", "wb") as fp:
            pickle.dump(shields, fp)

        await message.channel.send(tosend)
        return

keep_alive()
client.run(os.getenv('TOKEN'))