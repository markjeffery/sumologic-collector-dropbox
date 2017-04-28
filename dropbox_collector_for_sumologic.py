#!/usr/bin/env python

import cmd
import locale
import os
import pprint
import shlex
import sys
import pdb
import json
import ConfigParser
from dropbox.rest import RESTClientObject, RESTResponse, SDK_VERSION, ErrorResponse

PY3 = sys.version_info[0] == 3

if PY3:
    from io import StringIO
else:
    from StringIO import StringIO

from dropbox import client, rest, session

class DropBoxAccess():
    def __init__(self):
        self.api_client = None
        self.config = ConfigParser.RawConfigParser()
        self.config.read('dropbox_collector_for_sumologic.ini')

        try:
            self.app_key = self.config.get('app_key','APP_KEY')
            self.app_secret = self.config.get('app_key','APP_SECRET')
        except (ConfigParser.NoOptionError, ConfigParser.NoSectionError):
            print("Config file does not have entries for App Key and App Secret")
            print("Check the installation instructions to generate them")
            return

        try:
            serialized_token = self.config.get('token','TOKEN')
            if serialized_token.startswith('oauth1'):
                access_key, access_secret = serialized_token[len('oauth1:'):].split(':', 1)
                sess = session.DropboxSession(self.app_key, self.app_secret)
                sess.set_token(access_key, access_secret)
                self.api_client = client.DropboxClient(sess)
            elif serialized_token.startswith('oauth2:'):
                access_token = serialized_token[len('oauth2:'):]
                self.api_client = client.DropboxClient(access_token)
            else:
                print("Malformed access token in ", (self.TOKEN_FILE,))
        except ConfigParser.NoSectionError:
            pass

    def do_log(self, action):
        """show auditlog"""
        if self.api_client is None:
            print("Please 'login' to execute this command\n")
            return
        if action == "test":
            body={'limit':10}
        else:
            body={'limit':1000}
        if action == "showlog":
            body['start_ts'] = 1418651258000 # Mon, 15 Dec 2014 13:47:38 GMT
            if self.config.has_option("cursor","cursor"):
                body['cursor'] = self.config.get("cursor","cursor")
        url, params, headers = self.api_client.request("/team/log/get_events", method="POST")
        headers['Content-Type'] = "application/json"
        bodytext = json.dumps(body)
        post_params = params
        try:
            rc = RESTClientObject()
            ret = rc.request(method = "POST", url = url, body=bodytext, headers = headers)
        except rest.ErrorResponse:
            print("Error:", sys.exc_info()[0])
            return

        if action == "showlog" and "cursor" in ret:
            if not self.config.has_section("cursor"):
                self.config.add_section("cursor")
            self.config.set("cursor","cursor",ret["cursor"])
        for k in ret["events"]:
            timestring = k["time"].replace("T"," ",1)
            timestring = timestring.replace("+00:00"," -0000",1)
            print(timestring + "," + json.dumps(k))
        with open('dropbox_collector_for_sumologic.ini', 'wb') as configfile:
            self.config.write(configfile)

    def do_login(self):
        """log in to a Dropbox account"""
        flow = client.DropboxOAuth2FlowNoRedirect(self.app_key, self.app_secret)
        authorize_url = flow.start()
        print("1. Go to: " + authorize_url + "\n")
        print("2. Click \"Allow\" (you might have to log in first).\n")
        print("3. Copy the authorization code.\n")
        code = raw_input("Enter the authorization code here: ").strip()

        try:
            access_token, user_id = flow.finish(code)
        except rest.ErrorResponse:
            print("Error:", sys.exc_info()[0])
            return

        if not self.config.has_section("token"):
            self.config.add_section("token")
        self.config.set("token","TOKEN",'oauth2:' + access_token)
        with open('dropbox_collector_for_sumologic.ini', 'wb') as configfile:
            self.config.write(configfile)
        self.api_client = client.DropboxClient(access_token)

def main():
    # TODO: Write up procedure for installing
    dba = DropBoxAccess()

    prog_name = sys.argv[0]
    args = sys.argv[1:]

    if len(args) == 0:
        dba.do_log("showlog")
        sys.exit(0)

    command = args[0]
    if command == 'login':
        # Implement do_login based on existing, but add APP_KEY & APP_SECRET
        dba.do_login()
    elif command == 'test':
        # Implement test, requesting 10 lines, but not storing position
        dba.do_log("test")
    elif command == 'showlog':
        # Show 1000 lines of log, storing position
        dba.do_log("showlog")
    else:
        sys.stderr.write("ERROR: Unknown command: %r\n" % command)
        sys.stderr.write("Run with no arguments for help.\n")
        sys.exit(1)

if __name__ == '__main__':
    main()
