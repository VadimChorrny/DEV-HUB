#----------------------------------------------+
#                 Variables                    |
#----------------------------------------------+
owner_ids = [
    301295716066787332
]

perms_tr = {
    "create_instant_invite": "Создавать приглашения",
    "kick_members": "Кикать участников",
    "ban_members": "Банить участников",
    "administrator": "Администратор",
    "manage_channels": "Управлять каналами",
    "manage_guild": "Управлять сервером",
    "add_reactions": "Добавлять реакции",
    "view_audit_log": "Просматривать журнал аудита",
    "priority_speaker": "Приоритетный режим",
    "stream": "Видео",
    "read_messages": "Читать сообщения",
    "view_channel": "Видеть канал",
    "send_messages": "Отправлять сообщения",
    "send_tts_messages": "Отправлять TTS сообщения",
    "manage_messages": "Управлять сообщениями",
    "embed_links": "Встраивать ссылки",
    "attach_files": "Прикреплять файлы",
    "read_message_history": "Просматривать историю сообщений",
    "mention_everyone": "Упоминать everyone / here",
    "external_emojis": "Использовать внешние эмодзи",
    "view_guild_insights": "View server insights",
    "connect": "Подключаться",
    "speak": "Говорить",
    "mute_members": "Выключать микрофон у участников",
    "deafen_members": "Заглушать участников",
    "move_members": "Перемещать участников",
    "use_voice_activation": "Использовать режим рации",
    "change_nickname": "Изменять никнейм",
    "manage_nicknames": "Управлять никнеймами",
    "manage_roles": "Управлять ролями",
    "manage_permissions": "Управлять правами",
    "manage_webhooks": "Управлять вебхуками",
    "manage_emojis": "Управлять эмодзи"
}

bad_arg_tr = {
    "user": "пользователь не был найден",
    "member": "участник не был найден",
    "role": "роль не была найдена",
    "channel": "канал не был найден"
}

#----------------------------------------------+
#                 Functions                    |
#----------------------------------------------+
def error_msg(_type):
    _type = _type.lower()
    return "не удалось найти нужную информацию" if _type not in bad_arg_tr else bad_arg_tr[_type]


def display_perms(missing_perms):
    out = ""
    for perm in missing_perms:
        out += f"> {perms_tr[perm]}\n"
    return out


def vis_aliases(aliases):
    if aliases not in [None, []]:
        out = "**Синонимы:** "
        for a in aliases:
            out += f"`{a}`, "
        return out[:-2]
    else:
        return ""


def carve_int(string):
    digits = [str(i) for i in range(10)]
    out = ""
    for s in string:
        if s in digits:
            out += s
        elif out != "":
            break
    return int(out) if out != "" else None


def is_int(string):
    try:
        int(string)
        return True
    except ValueError:
        return False


def get_field(_dict, *key_wrods, default=None):
    if _dict is not None:
        for kw in key_wrods:
            if kw in _dict:
                _dict = _dict[kw]
            else:
                _dict = None
                break
    return default if _dict is None else _dict


def find_alias(dict_of_aliases, search):
    out, search = None, search.lower()
    for key in dict_of_aliases:
        aliases = dict_of_aliases[key]
        aliases.append(key)
        for al in aliases:
            if al.startswith(search):
                out = key
                break
        if out is not None:
            break
    return out


def antiformat(text):
    alph = "qwertyuiopasdfghjklzxcvbnm1234567890 \n\t"
    out = ""
    for s in text:
        if s.lower() not in alph:
            out += "\\" + s
        else:
            out += s
    return out


def has_permissions(member, perm_array):
    perms_owned = dict(member.guild_permissions)
    total_needed = len(perm_array)
    for perm in perm_array:
        if perms_owned[perm]:
            total_needed -= 1
    return total_needed == 0


async def get_message(channel, msg_id):
    try:
        return await channel.fetch_message(msg_id)
    except Exception:
        return None


class detect:
    @staticmethod
    def member(guild, search):
        ID = carve_int(search)
        if ID is None:
            ID = 0
        member = guild.get_member(ID)
        if member is None:
            member = guild.get_member_named(search)
        return member
    
    @staticmethod
    def channel(guild, search):
        ID = carve_int(search)
        if ID is None:
            ID = 0
        channel = guild.get_channel(ID)
        if channel is None:
            for c in guild.channels:
                if c.name == search:
                    channel = c
                    break
        return channel
    
    @staticmethod
    def role(guild, search):
        ID = carve_int(search)
        if ID is None:
            ID = 0
        role = guild.get_role(ID)
        if role is None:
            for r in guild.roles:
                if r.name == search:
                    role = r
                    break
        return role
    
    @staticmethod
    def user(search, client):
        ID = carve_int(search)
        user = None
        if ID is not None:
            user = client.get_user(ID)
        return user


# The end