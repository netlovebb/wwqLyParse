#!/usr/bin/env python3.5
# -*- coding: utf-8 -*-
# author wwqgtxx <wwqgtxx@gmail.com>
import subprocess
import logging
import json

# encoding list to fix encoding BUG on windows
fix_encoding = [
    'UTF-8',
    'cp936',
    'cp950',
]


# try to decode, to fix encoding BUG on windows
def try_decode(raw, no_error=False):
    fix_list = fix_encoding
    rest = fix_list
    while len(rest) > 0:
        one = rest[0]
        rest = rest[1:]
        try:
            out = raw.decode(one)
            return out
        except Exception as e:
            if len(rest) < 1:
                if no_error:
                    out = raw.decode(one, 'ignore')
                    return out
                else:
                    raise e


# try parse json
def try_parse_json(raw_text):
    while True:
        try:
            info = json.loads(raw_text)
            return info
        except Exception as e:
            try:
                rest = '{' + raw_text.split('{', 1)[1]
            except IndexError:
                raise e
            if rest == raw_text:
                raise
            raw_text = rest


def run_subprocess(args, timeout=None, need_stderr=True, **kwargs):
    pipe = subprocess.PIPE
    logging.debug(args)
    p = subprocess.Popen(args, stdout=pipe, stderr=pipe if need_stderr else None, shell=False, **kwargs)
    try:
        stdout, stderr = p.communicate(timeout=timeout)
    except subprocess.TimeoutExpired:
        logging.debug("Timeout!!! kill %s" % p)
        p.kill()
        stdout, stderr = p.communicate()
    else:
        # try to decode
        stdout = try_decode(stdout)
        stderr = try_decode(stderr) if need_stderr else None
        # print(stdout)
        return stdout, stderr


from . import asyncio


async def async_run_subprocess(args, timeout=None, need_stderr=True, **kwargs):
    pipe = subprocess.PIPE
    logging.debug(args)
    # args = subprocess.list2cmdline(args)
    p = await asyncio.create_subprocess_exec(*args, stdout=pipe, stderr=pipe if need_stderr else None, **kwargs)
    try:
        stdout, stderr = await asyncio.wait_for(p.communicate(), timeout=timeout)
    except asyncio.TimeoutError:
        raise asyncio.CancelledError
    else:
        # try to decode
        stdout = try_decode(stdout)
        stderr = try_decode(stderr) if need_stderr else None
        # print(stdout)
        return stdout, stderr
    finally:
        try:
            p.terminate()
            logging.debug("Timeout!!! kill %s" % p)
        except:
            pass


def safe_print(text):
    print((str(text)).encode('gbk', 'ignore').decode('gbk'))
