from cogs.etc.config import (
    AUTHORID,
    dbBase,
    EMBED_ST,
    COLOR_RED,
    COLOR_GREEN,
    PROJECT_NAME,
    TOKEN,
    PREFIX,
    ESCAPE,
    LOG_SERVER,
    LOG_CHANNEL,
    WHITELIST_RANKS,
    whitelist,
    current_timestamp,
    status_query,
    fetch_whitelist,
    SHARDS,
    URBAN_KEY
)

import logging
import logging.config
from utils.checker import filler
logging.config.fileConfig('../../../discord/logging.conf')


def define_global_vars(bot):
    bot.authorid = AUTHORID
    bot.dbBase = dbBase
    bot.embed_st = EMBED_ST
    bot.color_green = COLOR_GREEN
    bot.color_red = COLOR_RED
    bot.project_name = PROJECT_NAME
    bot.token = TOKEN
    bot.prefix = PREFIX
    bot.escape = ESCAPE
    bot.log_server = LOG_SERVER
    bot.log_channel = LOG_CHANNEL
    bot.whitelist_ranks = WHITELIST_RANKS
    bot.whitelist = whitelist
    bot.current_timestamp = current_timestamp
    bot.status_query = status_query
    bot.fetch_whitelist = fetch_whitelist
    bot.logger = logging.getLogger('MrPython')
    bot.server_settings = None
    bot.set_filler = filler
    # Newly added
    bot.cur_shards = SHARDS
    bot.urban_key = URBAN_KEY

    return bot
