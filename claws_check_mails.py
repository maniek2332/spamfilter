#!/usr/bin/env python
# -*- coding: utf-8 -*-

import gtk
from clawsmail import Folder, get_folderview_selected_folder, move_messages
import requests

current_folder = get_folderview_selected_folder()
trash = Folder('trash')
if current_folder:
    messages = current_folder.get_messages()
    new_messages = [m for m in messages if m.is_new() or m.is_unread()]

    spam_messages = []
    for msg in new_messages:
        with open(msg.FilePath, 'rb') as fh:
            content = fh.read()
        res = requests.put('http://127.0.0.1:2220/', content)
        if res.status_code == 221:
            spam_messages.append(msg)

    move_messages(spam_messages, trash)

    mdialog = gtk.MessageDialog(
        message_format="%d out of %d messages was recognized as spam" %
        (len(spam_messages), len(new_messages))
    )
    mdialog.show()

