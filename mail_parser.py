#!/usr/bin/env python
# -*- coding: utf-8 -*-

import re
import sys
import quopri
import encodings
import base64
from pprint import pprint
from HTMLParser import HTMLParser

import pandas as pd
from requests.structures import CaseInsensitiveDict

from utils import LOG, memory


RE_HEADER = re.compile(r'^[A-Za-z-]+[:]')
RE_CHARSET = re.compile(r'charset\s*=\s*["]?([^";]+)', re.I)
RE_HEADER_BOUNDARY = re.compile(r'boundary\s*=\s*["]?([^";]+)', re.I)
RE_BASE64 = re.compile('(?:(?:[a-zA-Z0-9+/=]+)[\n]?)+')
HTML_STATS_TAGS = {'b', 'i', 'font', 'center'}
HTML_PARSER_IGNORE_TAGS = {'br', 'hr', 'img'}


HTMLStats = lambda: pd.Series(
    index=(['tags_count', 'errors_count'] +
           ['cov_' + tag for tag in HTML_STATS_TAGS]),
    dtype='int64',
    data=0
)

EmailStats = lambda: pd.Series(
    index=['attached_images', 'charset_errors'],
    dtype='int64',
    data=0
)


def base64_partial_decode(body):
    rem = RE_BASE64.match(body)
    decoded = base64.decodestring(rem.group(0))
    body, repl_count = RE_BASE64.subn(decoded, body, 1)
    return body


@memory.cache
def parse_mails(files_list):
    mails = []
    for fname in files_list:
        with open(fname, 'rb') as fh:
            content = fh.read()
        mp = MessageParser(fname, content)
        mails.append(mp)
    mails = pd.DataFrame([m.as_series() for m in mails])
    return mails


def parse_mail_string(content):
    mp = MessageParser('<SINGLE>', content)
    mails = pd.DataFrame([mp.as_series()])
    return mails


class StatsHTMLParser(HTMLParser):
    def reset(self):
        HTMLParser.reset(self)
        self.stats = HTMLStats()
        self.tag_stack = []
        self.text_list = []

    @property
    def text(self):
        return "\n".join(self.text_list)

    def handle_starttag(self, tag, attrs):
        if tag in HTML_PARSER_IGNORE_TAGS:
            return
        self.tag_stack.insert(0, tag)
        self.stats['tags_count'] += 1

    def handle_endtag(self, tag):
        if tag in HTML_PARSER_IGNORE_TAGS:
            return
        if self.tag_stack and tag == self.tag_stack[0]:
            del self.tag_stack[0]
        else:
            LOG.debug("Invalid closing tag at %r", self.getpos())
            if tag in self.tag_stack:
                idx = self.tag_stack.index(tag)
                del self.tag_stack[:idx + 1]
                self.stats['errors_count'] += idx + 1

    def handle_data(self, data):
        text = data.strip()
        if self.tag_stack and self.tag_stack[0] in ('script', 'style'):
            return
        if text:
            self.text_list.append(text)

            for tag in (set(self.tag_stack) & HTML_STATS_TAGS):
                self.stats['cov_' + tag] += len(text)


def validate_charset(charset):
    return charset and encodings.search_function(charset) is not None


class MessageParser(object):
    def __init__(self, name, content, init_headers={}):
        self.name = name
        self.content = content

        self.headers = CaseInsensitiveDict(init_headers)
        self.html_stats = HTMLStats()
        self.email_stats = EmailStats()

        self.head, self.body = self.content.split('\n\n', 1)
        self._parse_headers()
        self._decode_body()

    @property
    def subject(self):
        return self.headers['Subject']

    @property
    def mime_type(self):
        if 'Content-Type' in self.headers:
            content_type = self.headers['Content-Type']
            mime_type = content_type.split(';', 1)[0]
            mime_type = mime_type.strip().lower()
            return mime_type

    @property
    def charset(self):
        if 'Content-Type' in self.headers:
            content_type = self.headers['Content-Type']
            rem = RE_CHARSET.search(content_type)
            if rem:
                charset = rem.group(1).lower()
                return charset

    @property
    def is_multipart(self):
        if self.mime_type and self.mime_type.startswith('multipart/'):
            return True
        else:
            return False

    def _get_boundary(self):
        if 'Content-Type' in self.headers:
            content_type = self.headers['Content-Type']
            rem = RE_HEADER_BOUNDARY.search(content_type)
            if rem:
                return rem.group(1)

    def _parse_headers(self):
        lines = self.head.split('\n')

        # Drop the "From..." line
        while lines and not RE_HEADER.match(lines[0]):
            del lines[0]
        while lines:
            line = self._get_header_line(lines)
            key, value = line.split(':', 1)
            key, value = key.strip(), value.strip()
            self.headers[key] = value

    def _get_header_line(self, lines):
        line_parts = [lines.pop(0)]
        while lines and (lines[0].startswith('\t') or
                         lines[0].startswith(' ')):
            line_parts.append(lines.pop(0))

        line = " ".join([part.strip() for part in line_parts])
        return line

    def _decode_body(self):
        if self.mime_type and (self.mime_type.startswith('image/') or
                               self.mime_type.startswith('application/')):
            LOG.info("Body marked as image, skipping body")
            self.email_stats['attached_images'] += 1
            self.body = ""
            return

        if self.is_multipart:
            LOG.debug("Detected multipart/* content-type")
            self._decode_multipart_body()
        else:
            self._decode_single_body()

    def _decode_single_body(self):
        self.body = self.body.strip()
        cte = self.headers.get('Content-Transfer-Encoding', '').lower()
        if 'quoted-printable' in cte:
            LOG.debug("Detected quoted-printable encoding, decoding")
            self.body = quopri.decodestring(self.body)
        if 'base64' in cte:
            LOG.debug("Detected base64 encoding, decoding")
            try:
                self.body = base64.decodestring(self.body)
            except base64.binascii.Error:
                LOG.info("base64 decoder failed, trying partial decoding")
                self.body = base64_partial_decode(self.body)

        LOG.debug("Detected charset: %s", self.charset)
        try:
            self.body = self.body.decode(
                validate_charset(self.charset) and self.charset or 'ascii',
                'strict'
            )
        except UnicodeDecodeError:
            LOG.info('Error during strict decoding')
            self.email_stats['charset_errors'] = 1
            self.body = self.body.decode(
                validate_charset(self.charset) and self.charset or 'ascii',
                'ignore'
            )

        if self._guess_html():
            LOG.debug("Message recognized as HTML")
            self._parse_html()
        else:
            LOG.debug("Message recognized as plaintext")

    def _decode_multipart_body(self):
        boundary = self._get_boundary()
        if not boundary:
            LOG.warn("Message detected as multipart but boundary "
                     "declaration was not found")
            return

        start_bnd = '\n' + '--' + boundary + '\n'
        end_bnd = '\n' + '--' + boundary + '--' + '\n'

        self.body = '\n' + self.body  # for string matching purpose

        try:
            start_index = self.body.index(start_bnd) + len(start_bnd)
        except ValueError:
            LOG.warn("Cannot find boundaries in body, "
                     "treating as single message")
            self._decode_single_body()
            return

        end_index = self.body.rfind(end_bnd)
        if end_index < 0:
            end_index = None

        content = self.body[start_index:end_index]

        parts = content.split(start_bnd)

        messages = [MessageParser(self.name, msg_content, self.headers)
                    for msg_content in parts]
        self.body = "\n".join([msg.body for msg in messages])
        for msg in messages:
            self.email_stats += msg.email_stats
            self.html_stats += msg.html_stats

    def _guess_html(self):
        if self.mime_type and self.mime_type == 'text/html':
            return True
        else:
            return False

    def _parse_html(self):
        parser = StatsHTMLParser()
        parser.feed(self.body)
        parser.close()
        self.body = parser.text
        self.html_stats = parser.stats

    def as_series(self):
        s = pd.Series({'plain_body': self.body})
        s_headers = pd.Series(dict(self.headers))
        s_headers.index = s_headers.index.map(lambda h: 'h_' + h.lower())
        s = (s
             .append(s_headers, True)
             .append(self.email_stats, True)
             .append(self.html_stats, True)
             )
        s.name = self.name
        return s


if __name__ == '__main__':
    for mail_path in sys.argv[1:]:
        with open(mail_path, 'rb') as fh:
            content = fh.read()
        mp = MessageParser(mail_path, content)
        print "=============="
        print "Message headers"
        print
        pprint(dict(mp.headers))
        print "=============="
        print
        print "=============="
        print "Message body"
        print
        print mp.body
        print "=============="
        print
        print "=============="
        print "Message HTML stats"
        print
        pprint(mp.html_stats)
        print "=============="
        print
        print "=============="
        print "Message stats"
        print
        pprint(mp.email_stats)
        print "Text length: %d" % len(mp.body)
        print "=============="
