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
                          "gif": "Allows making gifs of users/images/emojis",
                          "hex": "Grants users to add colors to their name with a command",
                          "joke": "Allows using -fall -promote"}
        ctx.perm_ignore_invert = ["blacklist", "hex", "ping"]
        ctx.perms_list_deny_change = ["ping", "blacklist"]
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
        ctx.discord_experiments = {
            "ANIMATED_BANNER": "Ability to upload an animated [banner image](https://support.discord.com/hc/en-us/articles/360028716472-Server-Banner-Background-Invite-Splash-Image) that will display above the channel list.",
            "ANIMATED_ICON": "Ability to upload an animated icon, similar to animated profile pictures for Nitro members. Displays on hover and invite links on desktop, and plays constantly on mobile.",
            "AUTO_MODERATION": "Ability to enable AutoMod.",
            "BANNER": "Ability to set a [banner image](https://support.discord.com/hc/en-us/articles/360028716472-Server-Banner-Background-Invite-Splash-Image) that will display above the channel list. ",
            "BOOSTING_TIERS_EXPERIMENT_MEDIUM_GUILD": "No information is available for this yet",
            "BOOSTING_TIERS_EXPERIMENT_SMALL_GUILD": "No information is available for this yet",
            "BOT_DEVELOPER_EARLY_ACCESS": "Enables early access features for bot and library developers.",
            "COMMUNITY": "[Gain access to Server Discovery, Insights, Community Server News, and Announcement Channels](https://support.discord.com/hc/en-us/articles/360035969312-Public-Server-Guidelines).",
            "CREATOR_MONETIZABLE": "No information is available for this yet",
            "CREATOR_MONETIZABLE_DISABLED": "No information is available for this yet",
            "DISCOVERABLE_DISABLED": "Guild is permanently removed from Discovery by Discord.",
            "DISCOVERABLE": "Visible in Server Discovery.",
            "ENABLED_DISCOVERABLE_BEFORE": "Given to servers that have enabled Discovery at any point.",
            "EXPOSED_TO_ACTIVITIES_WTP_EXPERIMENT": "Given to servers that are in the `2021-11_activities_baseline_engagement_bundle` experiment",
            "GUILD_HOME_TEST": "Gives the guild access to the Home feature",
            "HAD_EARLY_ACTIVITIES_ACCESS": "Server previously had access to voice channel activities and can bypass the boost level requirement",
            "HAS_DIRECTORY_ENTRY": "Guild is in a directory channel.",
            "HUB": "[Student Hubs](https://dis.gd/studenthubs) contain a directory channel that let you find school-related, student-run servers for your school or university.",
            "INTERNAL_EMPLOYEE_ONLY": "Restricts the guild so that only users with the staff flag can join.",
            "INVITE_SPLASH": "Ability to set a background image that will display on all invite links.",
            "MEMBER_PROFILES": "Allows members to customize their avatar, banner and bio for that server.",
            "MEMBER_VERIFICATION_GATE_ENABLED": "Has member verification gate enabled, requiring new users to pass the verification gate before interacting with the server.",
            "MORE_EMOJI": "Adds 150 extra emoji slots to each category (normal and animated emoji). Not used in server boosting.",
            "MORE_STICKERS": "Adds 60 total sticker slots no matter how many it had before. Not used in server boosting.",
            "NEWS": "Ability to create and use [~~news~~ announcement channels](https://support.discord.com/hc/en-us/articles/360028384531-Channel-Following-FAQ) which can be followed, and shows the Announcements analytics tab in the guild settings.",
            "NEW_THREAD_PERMISSIONS": "Guild has [new thread permissions](https://support.discord.com/hc/en-us/articles/4403205878423-Threads-FAQ#h_01FDGC4JW2D665Y230KPKWQZPN).",
            "PARTNERED": "Partner badge near the server name and in mutual server lists.",
            "PREMIUM_TIER_3_OVERRIDE": "Forces the server to server boosting level 3",
            "PREVIEW_ENABLED": "Allows a user to view the server without passing membership gating.",
            "PRIVATE_THREADS": "Ability to create private threads",
            "RELAY_ENABLED": "Shards connections to the guild to different nodes that relay information between each other.",
            "ROLE_ICONS": "Ability to set an image or emoji as a role icon.",
            "ROLE_SUBSCRIPTIONS_ENABLED": "Ability to view and manage role subscriptions.",
            "ROLE_SUBSCRIPTIONS_AVAILABLE_FOR_PURCHASE": "Allows servers members to purchase role subscriptions.",
            "TEXT_IN_VOICE_ENABLED": "Show a chat button inside voice channels that opens a dedicated text channel in a sidebar similar to thread view.",
            "THREADS_ENABLED_TESTING": "Used by bot developers to test their bots with threads in guilds with 5 or less members and a bot. ~~Also gives the premium thread features.~~",
            "THREADS_ENABLED": "Enabled threads early access.",
            "THREAD_DEFAULT_AUTO_ARCHIVE_DURATION": "Unknown, presumably used for testing changes to the thread default auto archive duration.",
            "TICKETED_EVENTS_ENABLED": "Ability to view and manage ticketed events.",
            "VANITY_URL": "Ability to set a vanity URL (custom discord.gg invite link).",
            "VERIFIED": "Verification checkmark near the server name and in mutual server lists.",
            "VIP_REGIONS": "~~Ability to use special voice regions with better stability: US East VIP, US West VIP, and Amsterdam VIP.~~ Deprecated, replaced with 384kbps max bitrate",
            "WELCOME_SCREEN_ENABLED": "Has welcome screen enabled, a modal shown to new joiners that features different channels, and a short description of the guild",
            "CHANNEL_BANNER": "Ability to set a channel banner that will display above the Channel Information sidebar.",
            "COMMERCE": "Ability to create and use [store channels](https://discord.com/developers/docs/game-and-server-management/special-channels#store-channels).",
            "EXPOSED_TO_BOOSTING_TIERS_EXPERIMENT": "No information is available for this yet",
            "PUBLIC_DISABLED": "Deprecated in favor of `COMMUNITY`",
            "PUBLIC": "Deprecated in favor of `COMMUNITY`",
            "SEVEN_DAY_THREAD_ARCHIVE": "Ability to use seven-day archive time for threads.",
            "THREE_DAY_THREAD_ARCHIVE": "Ability to use three-day archive time for threads.",
            "FEATURABLE": "Previously used to control which servers were displayed under the \"Featured\" category in Discovery",
            "FORCE_RELAY": "Shards connections to the guild to different nodes that relay information between each other.",
            "LURKABLE": "N/A",
            "MEMBER_LIST_DISABLED": "Created for the Fortnite server blackout event on Oct 13, 2019, when viewing the member list it would show \"There's nothing to see here.\".",
            "MONETIZATION_ENABLED": "Allows the server to set a team in dev portal to cash out ticketed stage payouts"
        }


def save(path, type, data):
    with open(path, type) as f:
        json.dump(data, f, indent=4, sort_keys=True)
