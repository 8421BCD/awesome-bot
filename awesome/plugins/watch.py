import random
from dataclasses import dataclass
from typing import Dict

import nonebot
import nonebot.permission as perm
from awesome import ac_filter
from awesome import bayes_filter
from nonebot import on_natural_language, NLPSession, IntentCommand


@dataclass
class Record:
    last_msg: str
    last_user_id: int
    repeat_count: int = 0


records: Dict[str, Record] = {}


@on_natural_language(only_to_me=False, permission=perm.GROUP)
async def _(session: NLPSession):
    group_id = session.event.group_id
    user_id = session.event.user_id
    msg = session.msg
    record = records.get(group_id)
    ac_match = ac_filter.trie.iter(msg)
    bayes_match = bayes_filter.check(msg)
    if len(list(ac_match)) or bayes_match:
        bot = nonebot.get_bot()
        try:
            await bot.delete_msg(**session.event)
        except:
            pass
        return IntentCommand(90.0, 'filter', current_arg=str(user_id))
    if record is None or msg != record.last_msg:
        record = Record(msg, user_id, repeat_count=1)
        records[group_id] = record
        return
    if record.last_user_id == user_id:
        return
    record.last_user_id = user_id
    record.repeat_count += 1
    if record.repeat_count == 2:
        return IntentCommand(
            90.0,
            'repeater',
            args={'delay': random.randint(5, 20) / 10, 'message': msg}
        )
