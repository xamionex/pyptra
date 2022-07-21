import json
from discord.ext import commands


def setup(bot):
    bot.add_cog(Configs(bot))


class Configs(commands.Cog, name="Configs"):
    """Configuration objects (no commands)."""
    COG_EMOJI = "⚙️"

    def __init__(self, ctx):
        paths = {"./data/afk.json": "afk",
                 "./data/global_perms.json": "global_perms",
                 "./data/reputation.json": "reputation",
                 "./data/settings.json": "settings"}
        for path, name in paths.items():
            with open(path, "r") as f:
                setattr(ctx, str(name), json.loads(f.read()))
                setattr(ctx, str(name) + "_path", path)

        ctx.rep_types = {"positive": "+ p plus ✅ 👍",
                         "negative": "- m minus ❌ 👎",
                         "informative": "ℹ️ ❓ stats s info i ?"}
        ctx.rep_type_positive = ctx.rep_types["positive"].split(" ")
        ctx.rep_type_negative = ctx.rep_types["negative"].split(" ")
        ctx.rep_type_informative = ctx.rep_types["informative"].split(" ")
        ctx.rep_type_combined = ctx.rep_type_positive + \
            ctx.rep_type_negative + ctx.rep_type_informative
        ctx.rep_type_list = {"positive": "Positive Reputation",
                             "negative": "Negative Reputation"}
        ctx.perms_list = {"blacklist": "Denies usage for bot",
                          "weird": "Allows -hug -kiss",
                          "ping": "Denies pinging user in -hug -kiss -pet",
                          "pet": "Allows petting users/images/emojis",
                          "hex": "Grants users to add colors to their name with a command",
                          "joke": "Allows using -fall -promote"}
        ctx.global_perms_list_false = {"wb_alert_dm": "Disables/Enables welcome back embed sending in DM instead",
                                       "afk_alert_dm": "Disables/Enables AFK alerts sending in DM instead"}
        ctx.global_perms_list_true = {"wb_alert": "Disables/Enables welcome back embed, overrides DM",
                                      "afk_alert": "Disables/Enables AFK alerts, overrides DM", }
        ctx.hug_gifs = ["https://media1.tenor.com/images/7e30687977c5db417e8424979c0dfa99/tenor.gif",
                        "https://media1.tenor.com/images/4d89d7f963b41a416ec8a55230dab31b/tenor.gif",
                        "https://media1.tenor.com/images/45b1dd9eaace572a65a305807cfaec9f/tenor.gif",
                        "https://media1.tenor.com/images/b4ba20e6cb49d8f8bae81d86e45e4dcc/tenor.gif",
                        "https://media1.tenor.com/images/949d3eb3f689fea42258a88fa171d4fc/tenor.gif",
                        "https://media1.tenor.com/images/72627a21fc298313f647306e6594553f/tenor.gif",
                        "https://media1.tenor.com/images/d3dca2dec335e5707e668b2f9813fde5/tenor.gif",
                        "https://media1.tenor.com/images/eee4e709aa896f71d36d24836038ed8a/tenor.gif",
                        "https://media1.tenor.com/images/b214bd5730fd2fdfaae989b0e2b5abb8/tenor.gif",
                        "https://media1.tenor.com/images/edea458dd2cbc76b17b7973a0c23685c/tenor.gif",
                        "https://media1.tenor.com/images/506aa95bbb0a71351bcaa753eaa2a45c/tenor.gif",
                        "https://media1.tenor.com/images/42922e87b3ec288b11f59ba7f3cc6393/tenor.gif",
                        "https://media1.tenor.com/images/bb841fad2c0e549c38d8ae15f4ef1209/tenor.gif",
                        "https://media1.tenor.com/images/234d471b1068bc25d435c607224454c9/tenor.gif",
                        "https://media1.tenor.com/images/de06f8f71eb9f7ac2aa363277bb15fee/tenor.gif"]
        ctx.purge_gifs = ["https://c.tenor.com/8wy7H4h5IVcAAAAd/asuka-langley-asuka.gif",
                          "https://c.tenor.com/OfqLXcy4EjwAAAAS/evangelion-lights.gif",
                          "https://c.tenor.com/ai947c7pFIMAAAAC/brick.gif",
                          "https://c.tenor.com/sLG8KOwLkukAAAAd/mgr-metal-gear-rising.gif",
                          "https://c.tenor.com/Ki3S5xrrY9wAAAAd/discord-discord-drama.gif",
                          "https://c.tenor.com/s0M5P7zXmuQAAAAC/metal-gear-rising-jetstream-sam.gif",
                          "https://c.tenor.com/poJ6qSHNhR0AAAAd/jetstream-sam-grass.gif",
                          "https://c.tenor.com/bnHxeEogbq8AAAAC/metal-gear-rising.gif",
                          "https://cdn.discordapp.com/attachments/920776187884732559/998236527714906172/PTRA_Purge.gif",
                          "https://cdn.discordapp.com/attachments/967897893413462027/998047629139259402/3Tt5.gif",
                          "https://c.tenor.com/giN2CZ60D70AAAAC/explosion-mushroom-cloud.gif"
                          ]
        ctx.hug_words = ["hugged",
                         "cuddled",
                         "embraced",
                         "squeezed",
                         "is holding onto",
                         "is caressing"]
        ctx.hug_words_bot = ["hug",
                             "cuddle",
                             "embrace",
                             "squeeze",
                             "hold onto",
                             "caress"]
        ctx.kiss_gifs = ["https://c.tenor.com/YTsHLAJdOT4AAAAC/anime-kiss.gif",
                         "https://c.tenor.com/wDYWzpOTKgQAAAAC/anime-kiss.gif",
                         "https://c.tenor.com/F02Ep3b2jJgAAAAC/cute-kawai.gif",
                         "https://c.tenor.com/Xc6y_eh0IcYAAAAd/anime-kiss.gif",
                         "https://c.tenor.com/sDOs4aMXC6gAAAAd/anime-sexy-kiss-anime-girl.gif",
                         "https://c.tenor.com/dp6A2wF5EKYAAAAC/anime-love.gif",
                         "https://c.tenor.com/OOwVQiBrXiMAAAAC/good-morning.gif",
                         "https://c.tenor.com/I8kWjuAtX-QAAAAC/anime-ano.gif",
                         "https://c.tenor.com/TWbZjCy8iN4AAAAC/girl-anime.gif"]
        ctx.kiss_words = ["kissed",
                          "smooched",
                          "embraced"]
        ctx.kiss_words_bot = ["kiss",
                              "smooch",
                              "embrace"]


def save(path, type, data):
    with open(path, type) as f:
        json.dump(data, f, indent=4, sort_keys=True)
