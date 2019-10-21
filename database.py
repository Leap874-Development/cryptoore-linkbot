import json
import os
import config

def with_data(file_path):
    def wrapper(func):
        def modified(*args, **kwargs):
            with open(file_path, 'r') as f:
                dat = json.load(f)
                resp, ret = func(dat, *args, **kwargs)
            with open(file_path, 'w+') as f:
                json.dump(resp, f)
            return ret
        return modified
    return wrapper

# Connect channel to link
@with_data(config.DATABASE)
def link_channel(data, channel, link):
    if link not in data['links']:
        data['links'][link] = [channel]
    else:
        if channel not in data['links'][link]:
            data['links'][link].append(channel)
    return data, None

# Disconnect channel from link
@with_data(config.DATABASE)
def unlink_channel(data, channel, link):
    if link in data['links']:
        try: data['links'][link].remove(channel)
        except ValueError: pass
        
        if not len(data['links'][link]):
            del data['links'][link]
    return data, None

# Disconnect channel from all links
@with_data(config.DATABASE)
def unlink_channel_all(data, channel):
    for link in data['links']:
        try: data['links'][link].remove(channel)
        except ValueError: pass
    for link in list(data['links']):
        if not len(data['links'][link]):
            del data['links'][link]
    return data, None

# Get all of a channels links
@with_data(config.DATABASE)
def get_channel_links(data, channel):
    links = []
    for link in data['links']:
        if channel in data['links'][link]:
            links.append(link)
    return data, links

# Get all links and their channels
@with_data(config.DATABASE)
def get_all_links(data):
    return data, data['links']

# Get all channels from link
@with_data(config.DATABASE)
def get_channels(data, link):
    return data, data['links'][link]

# Get all connected channels
@with_data(config.DATABASE)
def get_linked_channels(data, channel):
    channels = set()
    for link in data['links']:
        if channel in data['links'][link]:
            channels.update(data['links'][link])
    try: channels.remove(channel)
    except KeyError: pass
    return data, list(channels)

@with_data(config.DATABASE)
def ignore_channel(data, channel):
    channels = set(data['ignore'])
    channels.add(channel)
    data['ignore'] = list(channels)
    return data, None

@with_data(config.DATABASE)
def unignore_channel(data, channel):
    try: data['ignore'].remove(channel)
    except ValueError: pass
    return data, None

@with_data(config.DATABASE)
def is_ignored(data, channel):
    return data, channel in data['ignore']