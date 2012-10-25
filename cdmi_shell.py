#!/usr/bin/env python
#
##############################
# CDMI shell version: 0.1.0  #
##############################
#
#  Copyright 2012 Mezeo Software
#
#  Licensed under the Apache License, Version 2.0 (the "License");
#  you may not use this file except in compliance with the License.
#  You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
#  Unless required by applicable law or agreed to in writing, software
#  distributed under the License is distributed on an "AS IS" BASIS,
#  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#  See the License for the specific language governing permissions and
#  limitations under the License.
#

import cmd
import sys
import requests
import json
import getpass
import optparse
import ConfigParser
import os

CONFIG_FILE = '~/.cdmirc'

print
print '/#`|#\|\/|^|^    (#|_  _ ||'
print '\_,|_/|  |_|_    _)| |(/_||'
print '==========================='

class cdmishell(cmd.Cmd):
    """CDMI CLI... """

    def __init__(self):
        self.intro = 'Welcome to CDMI shell... For help, type help or ? <ENTER>\n'
        self.dpath = '/cdmi'
        self.pathlist = {}
        self.pathlist['cpath'] = self.dpath
        self.prompt = 'cdmishell=> '

        parser = optparse.OptionParser("Usage: cdmi_shell")
        parser.add_option('-c', '--config', help="specify alternate config file (default='%s')" % CONFIG_FILE)
        parser.add_option('-i', '--id', help="specify the configuration to use")
        parser.set_defaults(config=CONFIG_FILE)
        opts, args = parser.parse_args()
        config = ConfigParser.ConfigParser()

        if opts.config.startswith('~'):
            opts.config = os.path.expanduser(opts.config)

        if os.path.isfile(opts.config) and opts.id:
            print "Using config file: %s" % opts.config
            print "Using ID: %s" % opts.id
            config.read(opts.config)
            try:
                self.url = config.get(opts.id, 'URL')
                self.username = config.get(opts.id, 'USER')
                self.password = config.get(opts.id, 'PASSWORD')
                self.__currentpath(self.dpath)
            except:
                print "Failed to parse config file.  Aborting."
                sys.exit(1)
        else:
            self.url = ''
            self.username = ''
            self.password = ''
            self.logged_in = False
            if self.logged_in is False:
                self.do_login()
            self.__currentpath(self.dpath)

        cmd.Cmd.__init__(self)

    def __makerequest(self, method, path, content_type=''):
        headers = {}
        headers['X-CDMI-Specification-Version'] = '1.0.1'

        if not content_type:
            headers['Content-Type'] = content_type

        if self.url:
            path = self.url + path
            if method == 'GET':
                request = requests.get(path, headers=headers, auth=(self.username, self.password), verify=False)

            if method == 'DELETE':
                request = requests.delete(path, headers=headers, auth=(self.username, self.password), verify=False)

            return (request)
        
    def __currentpath(self, path=''):
        if path:
            self.pathlist['opath'] = self.pathlist['cpath']
            self.pathlist['cpath'] = path
        return self.pathlist

    def __showobject(self, path, arg):
        request = self.__makerequest('GET', path)
        if request.status_code  == 200:
            keys = json.loads(request.content)
            if not arg:
                value = json.dumps(json.loads(request.content), sort_keys=True, indent=4)
            elif arg not in keys:
                value = "Key not found..."
            elif arg == 'metadata':
                value = json.dumps(keys[arg], sort_keys=True, indent=4)
            elif arg == 'exports':
                value = json.dumps(keys[arg], sort_keys=True, indent=4)
            elif arg == 'value':
                value = json.dumps(json.loads(keys[arg]), sort_keys=True, indent=4)
            else:
                value = keys[arg]

            return value

    def do_login(self, arg=None):
        "Login and get /cdmi"

        print
        self.url = raw_input("Enter URL: ")
        self.username = raw_input("Enter username: ")
        self.password = getpass.getpass("Enter password: ")

        print
        request = self.__makerequest('GET', self.dpath)

        if request.status_code >= 400:
            print "An HTTP/1.1 %s error occured during the login process..." % request.status_code
            self.logged_in = False
        else:
            print "Login succsessful...\n"
            self.logged_in = True
            self.__currentpath(self.dpath)
            self.prompt = "cdmi=> "

    def do_whoami(self,arg):
        "Print user and location..."
        print
        if self.logged_in == True:
            print "Logged in as..."
            print "User: %s " % self.username
            print "URL: %s " % self.url
        else:
            print "You are not logged in..."
         
        print

    def do_ls(self, arg):
        "Perform a unix style listing on the current path..."
        if self.url:
            cpath = self.__currentpath()
            if not arg:
                path = cpath['cpath']
            else:
                path = cpath['cpath'] + '/' + arg

            print
            print 'Listing: %s' % path

            request = self.__makerequest('GET', path)
            
            if request.status_code != 404:
                children = json.loads(request.content)
                if 'children' in children:
                    for value in children['children']:
                        print value
                else:
                    print "No child objects found. Try show..."
            else:
                print "No objects found..."
            print
        

    def do_cd(self, arg):
        "Change current path location..."
        if self.url:
            cpath = self.__currentpath()
            if '..' == arg:
                path = self.__showobject(cpath['cpath'], 'parentURI')
                npath = self.__currentpath(path)
                shellprompt = self.__showobject(path, 'objectName')
                self.prompt = '%s=> ' % shellprompt
            else:
                path = cpath['cpath'] + '/' + arg
                request = self.__makerequest('GET', path)
                if request.status_code == 200:
                    self.__currentpath(path)
                    self.prompt = '%s=> ' % arg
                else:
                    print "Path does not exist..."
                    print path
        

    def do_show(self, arg):
        "Pretty print the current path or an individual key..."
        print
        if self.url:
            args = arg.split()
            cpath = self.__currentpath()
            if len(args) > 1:
                path = cpath['cpath'] + '/' + args[0]
                results = self.__showobject(path, args[1])
                print results
            else:
                path = cpath['cpath'] 
                results = self.__showobject(path, arg)
                print results
       
        print

    def do_pwd(self, arg):
        "List current path location..."
        print
        if self.url:
            path = self.__currentpath()
            print path['cpath']
        
        print

    def do_tree(self, arg):
        "Display a tree like hiarchy..."
        if not arg:
            pwd = self.__currentpath()['cpath']
        else:
            pwd = arg

        request = self.__makerequest('GET', pwd)
        children = json.loads(request.content)['children']
        for child in children:
            print pwd + '/' + child
            if child.endswith('/'):
                self.do_tree(pwd + '/' + child[:-1])

    def do_quit(self, arg):
        "Exit the CDMI shell..."
        sys.exit(1)

    def do_EOF(self, line):
        "Accept ^D to exit..."
        return True

    # shortcuts
    do_q = do_quit
    do_sh = do_show
    do_who = do_whoami
    do_w = do_whoami

if __name__ == '__main__':
    cdmishell().cmdloop()

