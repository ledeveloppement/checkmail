#!/usr/bin/env python3
# -*- coding: utf8 -*-
import imaplib
import os
import sys
import json
from email.parser import HeaderParser
COLOR=92
CONFIG_FILE=os.path.expanduser('~/.checkmail.conf.json')
try:
    with open(CONFIG_FILE,'r') as fh:
        config=json.load(fh)
except:
    print('edit config file first: {}'.format(CONFIG_FILE))
    sys.exit(1)
for server in config:
    for user in server['users']:
        m=imaplib.IMAP4_SSL(server['server'])
        pass_file,pass_start,pass_len=user['password'].split(':')
        with open(pass_file,'r') as fh:
            fh.seek(int(pass_start))
            password=fh.read(int(pass_len))
        m.login(user['login'],password)
        for mailbox in user['mailboxes']:
            m.select(mailbox)
            typ,data=m.uid('SEARCH',None,'UnSeen')
            str_id=data[0].decode('utf8')
            if len(str_id) == 0:
                n=0
            else:
                list_id=str_id.split(' ')
                n=len(list_id)
            if n > 0:
                s='\033[{color}m{login:30} {n:2} {link}\033[0m'
            else:
                s='{login:30} {n:2}'
            print(s.format(
                    login=user['login'],
                    n=n,
                    color=COLOR,
                    link=server['link'].format(login=user['login']),
                ))
            if n > 0:
                for uid in list_id:
                    typ,data=m.uid('FETCH',uid,'(BODY.PEEK[HEADER.FIELDS (DATE FROM SUBJECT)]])')
                    header_data = data[0][1].decode('utf8')
                    parser = HeaderParser()
                    msg = parser.parsestr(header_data)
                    print('\t{date}\n\t{sender}\n\t{subject}\n'.format(
                            date=msg['Date'],
                            sender=msg['From'],
                            subject=msg['Subject'],
                        ))
            m.close()
        m.logout()
