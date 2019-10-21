import discord
import typing
from discord.ext import commands

import config
import secrets
import database

bot = commands.Bot(command_prefix=config.PREFIX)
bot.remove_command('help')

def parse_channel(mention):
    try:
        cid = mention.lstrip('<#')
        cid = int(cid.rstrip('>'))
        return bot.get_channel(cid)
    except Exception as e:
        return None

async def forward_msg(channel, msg):
    embed=discord.Embed(title=msg.content, color=config.EMBED_COLOR)
    embed.set_author(name=msg.author.name, icon_url=msg.author.avatar_url)
    embed.set_footer(text='%s#%s' % (msg.guild.name, msg.channel.name))
    if len(msg.attachments):
        embed.set_image(url=msg.attachments[0].url)
    await channel.send(embed=embed)

async def on_ready():
    guild_names = ', '.join([ a.name for a in bot.guilds ])
    print('ForwardBot v%s online and logged in as %s' % (config.VERSION, bot.user))
    print('Connected to %s guild(s): %s' % (len(bot.guilds), guild_names))
    print('Now awaiting messages...')

async def on_message(msg):
    if msg.author == bot.user: return

    if not database.is_ignored(msg.channel.id):
        channels = database.get_linked_channels(msg.channel.id)
        for chan_id in channels:
            chan = bot.get_channel(chan_id)
            await forward_msg(chan, msg)

@bot.command()
@commands.has_permissions(administrator=True)
async def link(ctx, link):
    database.link_channel(ctx.message.channel.id, link)
    await ctx.send('Channel linked to `%s`' % link)

@bot.command()
@commands.has_permissions(administrator=True)
async def unlink(ctx, link):
    if link == 'all':
        await ctx.send('Keyword `all` is not allowed as a link name')
        return
    try:
        chans = database.get_channels(link)
    except KeyError:
        await ctx.send('Link `%s` does not exist' % link)
        return
    if ctx.message.channel.id in chans:
        database.unlink_channel(ctx.message.channel.id, link)
        await ctx.send('Channel unlinked from `%s`' % link)
    else:
        await ctx.send('Channel was not linked to `%s`, nothing changed' % link)

@bot.command()
@commands.has_permissions(manage_channels=True)
async def inspect(ctx, link=None):
    channel = parse_channel(link)
    if link == 'all':
        links = database.get_all_links()
        msg = 'Found %s link(s):\n' % len(links)
        for link in links: msg += '⇒ `%s` (%s linked)\n' % (link, len(links[link]))
        if len(links): await ctx.send(msg)
        else: await ctx.send('No links found, see `%shelp` for command reference' % config.PREFIX)
    elif channel:
        links = database.get_channel_links(channel.id)
        links = [ '`%s`' % a for a in links ]
        if len(links): await ctx.send('%s is linked to: %s' % (channel.mention, ', '.join(links)))
        else: await ctx.send('%s has no links' % channel.mention)
    elif link:
        try:
            channels = database.get_channels(link)
            channels = [ bot.get_channel(a).mention for a in channels ]
            await ctx.send('`%s` is connected to: %s' % (link, ', '.join(channels)))
        except KeyError:
            await ctx.send('Link `%s` does not exist' % link)
    else:
        links = database.get_channel_links(ctx.message.channel.id)
        links = [ '`%s`' % a for a in links ]
        if len(links): await ctx.send('This channel is linked to: %s' % ', '.join(links))
        else: await ctx.send('This channel has no links')

@bot.command()
@commands.has_permissions(manage_channels=True)
async def ignore(ctx):
    database.ignore_channel(ctx.message.channel.id)
    await ctx.send('Channel ignored')

@bot.command()
@commands.has_permissions(manage_channels=True)
async def unignore(ctx):
    database.unignore_channel(ctx.message.channel.id)
    await ctx.send('Channel unignored')

@bot.command()
@commands.has_permissions(manage_channels=True)
async def help(ctx):
    embed=discord.Embed(title='LinkBot Help', color=config.EMBED_COLOR)
    embed.add_field(name='>inspect', value='shows links to current channel', inline=False)
    embed.add_field(name='>inspect #channel', value='shows links to #channel', inline=False)
    embed.add_field(name='>inspect linkName', value='shows channels connected to linkName', inline=False)
    embed.add_field(name='>link linkName', value='links channel to linkName', inline=False)
    embed.add_field(name='>unlink linkName', value='unlinks channel from linkName', inline=False)
    embed.add_field(name='>ignore', value='ignores all messages from this channel', inline=False)
    embed.add_field(name='>unignore', value='stops ignoring messages from this channel', inline=False)
    embed.add_field(name='>help', value='shows this message', inline=True)
    await ctx.send(embed=embed)

bot.add_listener(on_ready)
bot.add_listener(on_message)
bot.run(secrets.BOT_TOKEN)
