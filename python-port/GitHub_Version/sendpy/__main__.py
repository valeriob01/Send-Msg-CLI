#!/usr/bin/env python

import sys
import os
import re
import getopt
import datetime, time
import subprocess
import codecs
import atexit
from shutil import which

from send import sendEmail
import usage
import configuration

'''Copyright © Daniel Connelly

   The purpose of this file is to
   1. parse all flags given on the cmdline.
   2. do checks to see if those files are valid
   3. handle escape characters appropriately
'''
# TODO -- delete after Regex test...these are the Firefox values
# values trakc what the value should be and index is used to find what that value should be
red = "\033[31m"
green = "\033[32m"
reset = '\033[0m'
index = 0
firefox_values = [
  [green + "VALID" + reset],
  [green + "VALID" + reset],
  [green + "VALID" + reset],
  [green + "VALID" + reset],
  [green + "VALID" + reset],
  [green + "VALID" + reset],
  [green + "VALID" + reset],
  [green + "VALID" + reset],
  [red + "TYPE_MISMATCH" + reset],

  [red + "TYPE_MISMATCH" + reset],
  [green + "VALID" + reset],
  [green + "VALID" + reset],
  [green + "VALID" + reset],
  [red + "TYPE_MISMATCH" + reset],

  [green + "VALID" + reset],
  [green + "VALID" + reset],
  [red + "TYPE_MISMATCH" + reset],
  [red + "TYPE_MISMATCH" + reset],
  [green + "VALID" + reset],
  [red + "TYPE_MISMATCH" + reset],
  [red + "TYPE_MISMATCH" + reset],
  [green + "VALID" + reset],
  [green + "VALID" + reset],
  [green + "VALID" + reset],
  [green + "VALID" + reset],
  [green + "VALID" + reset],
  [green + "VALID" + reset],
  [green + "VALID" + reset],
  [green + "VALID" + reset],
  [red + "TYPE_MISMATCH" + reset],
  [green + "VALID" + reset],
  [green + "VALID" + reset],
  [green + "VALID" + reset],

  [red + "TYPE_MISMATCH" + reset],
  [red + "TYPE_MISMATCH, True" + reset],

  [green + "VALID" + reset],
  [green + "VALID" + reset],
  [green + "VALID" + reset],
  [green + "VALID" + reset],
  [red + "TYPE_MISMATCH, BAD_INPUT" + reset],
  [red + "TYPE_MISMATCH, BAD_INPUT" + reset],
  [red + "TYPE_MISMATCH, BAD_INPUT" + reset],
  [red + "TYPE_MISMATCH, BAD_INPUT" + reset],

  [red + "TYPE_MISMATCH, BAD_INPUT" + reset],
  [red + "TYPE_MISMATCH, BAD_INPUT" + reset],
  [red + "TYPE_MISMATCH, BAD_INPUT" + reset],
  [red + "TYPE_MISMATCH, BAD_INPUT" + reset],

  [green + "VALID" + reset],
  [red + "TYPE_MISMATCH" + reset],
  [red + "TYPE_MISMATCH" + reset],
  [red + "TYPE_MISMATCH" + reset],
  [green + "VALID" + reset],
  [red + "TYPE_MISMATCH" + reset],
  [red + "TYPE_MISMATCH" + reset],
  [red + "TYPE_MISMATCH" + reset],
  [green + "VALID" + reset],
]

chromium_values = [
["something@something.com", "something@something.com", "expectValid"],
["someone@localhost.localdomain", "someone@localhost.localdomain", "expectValid"],
["someone@127.0.0.1", "someone@127.0.0.1", "expectValid"],
["a@b.b", "a@b.b", "expectValid"],
["a/b@domain.com", "a/b@domain.com", "expectValid"],
["{}@domain.com", "{}@domain.com", "expectValid"],
["m*'!%@something.sa", "m*'!%@something.sa", "expectValid"],
["tu!!7n7.ad##0!!!@company.ca", "tu!!7n7.ad##0!!!@company.ca", "expectValid"],
["%@com.com", "%@com.com", "expectValid"],
["!#$%&'*+/=?^_`{|}~.-@com.com", "!#$%&'*+/=?^_`{|}~.-@com.com", "expectValid"],
[".wooly@example.com", ".wooly@example.com", "expectValid"],
["wo..oly@example.com", "wo..oly@example.com", "expectValid"],
["someone@do-ma-in.com", "someone@do-ma-in.com", "expectValid"],
["somebody@example", "somebody@example", "expectValid"],
["\u000Aa@p.com\u000A", "a@p.com", "expectValid"],
["\u000Da@p.com\u000D", "a@p.com", "expectValid"],
["a\u000A@p.com", "a@p.com", "expectValid"],
["a\u000D@p.com", "a@p.com", "expectValid"],
["", "", "expectValid"],
[" ", "", "expectValid"],
[" a@p.com", "a@p.com", "expectValid"],
["a@p.com ", "a@p.com", "expectValid"],
[" a@p.com ", "a@p.com", "expectValid"],
["\u0020a@p.com\u0020", "a@p.com", "expectValid"],
["\u0009a@p.com\u0009", "a@p.com", "expectValid"],
["\u000Ca@p.com\u000C", "a@p.com", "expectValid"],

["invalid:email@example.com", "invalid:email@example.com", "expectInvalid"],
["@somewhere.com", "@somewhere.com", "expectInvalid"],
["example.com", "example.com", "expectInvalid"],
["@@example.com", "@@example.com", "expectInvalid"],
["a space@example.com", "a space@example.com", "expectInvalid"],
["something@ex..ample.com", "something@ex..ample.com", "expectInvalid"],
["a\b@c", "a\b@c", "expectInvalid"],
["someone@somewhere.com.", "someone@somewhere.com.", "expectInvalid"],
["\"\"test\blah\"\"@example.com", "\"\"test\blah\"\"@example.com", "expectInvalid"],
["\"testblah\"@example.com", "\"testblah\"@example.com", "expectInvalid"],
["someone@somewhere.com@", "someone@somewhere.com@", "expectInvalid"],
["someone@somewhere_com", "someone@somewhere_com", "expectInvalid"],
["someone@some:where.com", "someone@some:where.com", "expectInvalid"],
[".", ".", "expectInvalid"],
["F/s/f/a@feo+re.com", "F/s/f/a@feo+re.com", "expectInvalid"],
["some+long+email+address@some+host-weird-/looking.com", "some+long+email+address@some+host-weird-/looking.com", "expectInvalid"],
["a @p.com", "a @p.com", "expectInvalid"],
["a\u0020@p.com", "a\u0020@p.com", "expectInvalid"],
["a\u0009@p.com", "a\u0009@p.com", "expectInvalid"],
["a\u000B@p.com", "a\u000B@p.com", "expectInvalid"],
["a\u000C@p.com", "a\u000C@p.com", "expectInvalid"],
["a\u2003@p.com", "a\u2003@p.com", "expectInvalid"],
["a\u3000@p.com", "a\u3000@p.com", "expectInvalid"],
["ddjk-s-jk@asl-.com", "ddjk-s-jk@asl-.com", "expectInvalid"],
["someone@do-.com", "someone@do-.com", "expectInvalid"],
["somebody@-p.com", "somebody@-p.com", "expectInvalid"],
["somebody@-.com", "somebody@-.com", "expectInvalid"],

["something@something.com", "something@something.com", "expectValid"],
["someone@localhost.localdomain", "someone@localhost.localdomain", "expectValid"],
["someone@127.0.0.1", "someone@127.0.0.1", "expectValid"],
["a@b.b", "a@b.b", "expectValid"],
["a/b@domain.com", "a/b@domain.com", "expectValid"],
["{}@domain.com", "{}@domain.com", "expectValid"],
["m*'!%@something.sa", "m*'!%@something.sa", "expectValid"],
["tu!!7n7.ad##0!!!@company.ca", "tu!!7n7.ad##0!!!@company.ca", "expectValid"],
["%@com.com", "%@com.com", "expectValid"],
["!#$%&'*+/=?^_`{|}~.-@com.com", "!#$%&'*+/=?^_`{|}~.-@com.com", "expectValid"],
[".wooly@example.com", ".wooly@example.com", "expectValid"],
["wo..oly@example.com", "wo..oly@example.com", "expectValid"],
["someone@do-ma-in.com", "someone@do-ma-in.com", "expectValid"],
["somebody@example", "somebody@example", "expectValid"],
["\u0020a@p.com\u0020", "a@p.com", "expectValid"],
["\u0009a@p.com\u0009", "a@p.com", "expectValid"],
["\u000Aa@p.com\u000A", "a@p.com", "expectValid"],
["\u000Ca@p.com\u000C", "a@p.com", "expectValid"],
["\u000Da@p.com\u000D", "a@p.com", "expectValid"],
["a\u000A@p.com", "a@p.com", "expectValid"],
["a\u000D@p.com", "a@p.com", "expectValid"],
["", "", "expectValid"],
[" ", "", "expectValid"],
[" a@p.com", "a@p.com", "expectValid"],
["a@p.com ", "a@p.com", "expectValid"],
[" a@p.com ", "a@p.com", "expectValid"],

["invalid:email@example.com", "invalid:email@example.com", "expectInvalid"],
["@somewhere.com", "@somewhere.com", "expectInvalid"],
["example.com", "example.com", "expectInvalid"],
["@@example.com", "@@example.com", "expectInvalid"],
["a space@example.com", "a space@example.com", "expectInvalid"],
["something@ex..ample.com", "something@ex..ample.com", "expectInvalid"],
["a\b@c", "a\b@c", "expectInvalid"],
["someone@somewhere.com.", "someone@somewhere.com.", "expectInvalid"],
["\"\"test\blah\"\"@example.com", "\"\"test\blah\"\"@example.com", "expectInvalid"],
["\"testblah\"@example.com", "\"testblah\"@example.com", "expectInvalid"],
["someone@somewhere.com@", "someone@somewhere.com@", "expectInvalid"],
["someone@somewhere_com", "someone@somewhere_com", "expectInvalid"],
["someone@some:where.com", "someone@some:where.com", "expectInvalid"],
[".", ".", "expectInvalid"],
["F/s/f/a@feo+re.com", "F/s/f/a@feo+re.com", "expectInvalid"],
["some+long+email+address@some+host-weird-/looking.com", "some+long+email+address@some+host-weird-/looking.com", "expectInvalid"],
["\u000Ba@p.com\u000B", "\u000Ba@p.com\u000B", "expectInvalid"],
["\u2003a@p.com\u2003", "\u2003a@p.com\u2003", "expectInvalid"],
["\u3000a@p.com\u3000", "\u3000a@p.com\u3000", "expectInvalid"],
["a @p.com", "a @p.com", "expectInvalid"],
["a\u0020@p.com", "a\u0020@p.com", "expectInvalid"],
["a\u0009@p.com", "a\u0009@p.com", "expectInvalid"],
["a\u000B@p.com", "a\u000B@p.com", "expectInvalid"],
["a\u000C@p.com", "a\u000C@p.com", "expectInvalid"],
["a\u2003@p.com", "a\u2003@p.com", "expectInvalid"],
["a\u3000@p.com", "a\u3000@p.com", "expectInvalid"],
["ddjk-s-jk@asl-.com", "ddjk-s-jk@asl-.com", "expectInvalid"],
["someone@do-.com", "someone@do-.com", "expectInvalid"],
["somebody@-p.com", "somebody@-p.com", "expectInvalid"],
["somebody@-.com", "somebody@-.com", "expectInvalid"],

["someone@somewhere.com,john@doe.com,a@b.c,a/b@c.c,ualla@ualla.127", "someone@somewhere.com,john@doe.com,a@b.c,a/b@c.c,ualla@ualla.127", "expectValid"],
["tu!!7n7.ad##0!!!@company.ca,F/s/f/a@feo-re.com,m*'@a.b", "tu!!7n7.ad##0!!!@company.ca,F/s/f/a@feo-re.com,m*'@a.b", "expectValid"],
[" a@p.com,b@p.com", "a@p.com,b@p.com", "expectValid"],
["a@p.com ,b@p.com", "a@p.com,b@p.com", "expectValid"],
["a@p.com, b@p.com", "a@p.com,b@p.com", "expectValid"],
["a@p.com,b@p.com ", "a@p.com,b@p.com", "expectValid"],
["   a@p.com   ,   b@p.com   ", "a@p.com,b@p.com", "expectValid"],
["\u0020a@p.com\u0020,\u0020b@p.com\u0020", "a@p.com,b@p.com", "expectValid"],
["\u0009a@p.com\u0009,\u0009b@p.com\u0009", "a@p.com,b@p.com", "expectValid"],
["\u000Aa@p.com\u000A,\u000Ab@p.com\u000A", "a@p.com,b@p.com", "expectValid"],
["\u000Ca@p.com\u000C,\u000Cb@p.com\u000C", "a@p.com,b@p.com", "expectValid"],
["\u000Da@p.com\u000D,\u000Db@p.com\u000D", "a@p.com,b@p.com", "expectValid"],

["someone@somewhere.com,john@doe..com,a@b,a/b@c,ualla@ualla.127", "someone@somewhere.com,john@doe..com,a@b,a/b@c,ualla@ualla.127", "expectInvalid"],
["some+long+email+address@some+host:weird-/looking.com,F/s/f/a@feo+re.com,,m*'@'!%", "some+long+email+address@some+host:weird-/looking.com,F/s/f/a@feo+re.com,,m*'@'!%", "expectInvalid"],
["   a @p.com   ,   b@p.com   ", "a @p.com,b@p.com", "expectInvalid"],
["   a@p.com   ,   b @p.com   ", "a@p.com,b @p.com", "expectInvalid"],
["\u000Ba@p.com\u000B,\u000Bb@p.com\u000B", "\u000Ba@p.com\u000B,\u000Bb@p.com\u000B", "expectInvalid"],
["\u2003a@p.com\u2003,\u2003b@p.com\u2003", "\u2003a@p.com\u2003,\u2003b@p.com\u2003", "expectInvalid"],
["\u3000a@p.com\u3000,\u3000b@p.com\u3000", "\u3000a@p.com\u3000,\u3000b@p.com\u3000", "expectInvalid"],
[",,", ",,", "expectInvalid"],
[" ,,", ",,", "expectInvalid"],
[", ,", ",,", "expectInvalid"],
[",, ", ",,", "expectInvalid"],
["  ,  ,  ", ",,", "expectInvalid"],
["\u0020,\u0020,\u0020", ",,", "expectInvalid"],
["\u0009,\u0009,\u0009", ",,", "expectInvalid"],
["\u000A,\u000A,\u000A", ",,", "expectInvalid"],
["\u000B,\u000B,\u000B", "\u000B,\u000B,\u000B", "expectInvalid"],
["\u000C,\u000C,\u000C", ",,", "expectInvalid"],
["\u000D,\u000D,\u000D", ",,", "expectInvalid"],
["\u2003,\u2003,\u2003", "\u2003,\u2003,\u2003", "expectInvalid"],
["\u3000,\u3000,\u3000", "\u3000,\u3000,\u3000", "expectInvalid"]]

''' each debug matches up with the empty new line (e.g., 128).
debug("Valid single addresses when 'multiple' attribute is not set."],
debug("Invalid single addresses when 'multiple' attribute is not set."],
debug("Valid single addresses when 'multiple' attribute is set."],
debug("Invalid single addresses when 'multiple' attribute is set."],
debug("Valid multiple addresses when 'multiple' attribute is set."],
debug("Invalid multiple addresses when 'multiple' attribute is set."],
'''
chromium_validity = []
with open("chromium.txt", "r") as f1:
    for line in f1:
        if "expectValid" in line:
            chromium_validity.append(green + line.strip('\n') + reset)
        else:
            chromium_validity.append(red + line.strip('\n') + reset)

# Default Variables

VARS={"TOEMAILS":[],
        "CCEMAILS":[],
        "BCCEMAILS":[],
        "FROMEMAIL":'',
        "SMTP":'',
        "USERNAME":'',
        "PASSWORD":'',
        "FROMADDRESS":'',
        "PRIORITY":'',
        "PORT":0,
        "CERT":'',
        "CLIENTCERT":'cert.pem',
        "PASSPHRASE":'',
        "WARNDAYS":3,
        "ZIPFILE":'',
        "VERBOSE":False,
        "NOW":time.strftime("%b %d %H:%M:%S %Y %Z", time.gmtime()),
        "SUBJECT":'',
        "MESSAGE":'',
        "ATTACHMENTS":[],
        "SMIME": '',
        "PGP": '',
        "DRYRUN": False,
        "TIME": 0,
        "NOTIFY": '',
        "LANGUAGE": False,
        "TLS": False,
        "STARTTLS": False}

# Stores default SMTP server, username, password if `--config` option is set.
CONFIG_FILE="~/.sendpy.ini"

# ESCAPE_SEQUENCE_RE and decode_escapes credit -- https://stackoverflow.com/a/24519338/8651748 and Teal Dulcet
ESCAPE_SEQUENCE_RE = re.compile(r'''(\\U[0-9a-fA-F]{8}|\\u[0-9a-fA-F]{4}|\\x[0-9a-fA-F]{2}|\\[0-7]{1,3}|\\N\{[^}]+\}|\\[\\'"abfnrtv])''')

def zero_pad(message):
    '''zero_pad escape characters (u and U and x) that are < 4 numbers long, since python doesn't support this'''
    new_message = ""
    start_index = 0 # what we begin at for each iteration through our loop
    len_message = len(message)
    RE = re.compile('^[0-9a-fA-F]$') # matches any hexadecimal char
    while start_index < len_message:
        new_message += message[start_index]
        if start_index +1 != len_message and message[start_index] == "\\" and (message[start_index+1] == "u" or message[start_index+1] == "U" or message[start_index+1] == "x"):
            esc_char = message[start_index+1] # u, U, or x
            if esc_char == 'u':
                zero_pad = 4 # amount of zeroes to add
            elif esc_char == 'U':
                zero_pad = 8
            else: # x
                zero_pad = 2
            count = 0 # track number of escape characters to zero pad
            new_message += esc_char
            start_index +=2 # skip past escaped escape character
            for j in range(start_index, len_message):
                if count > zero_pad:
                    start_index+= zero_pad # avoid re-checking the unicode/x string.
                    break
                if re.match(RE, message[j]): # reach the end/beginning of new unicode/x string:
                    count+=1
                else:
                    # Zero pad
                    new_message += "0" * (zero_pad-count)

                    # add back in characters
                    for k in range(0, count):
                        new_message+=message[start_index]
                        start_index += 1
                    start_index -= 1 # for back-to-back escape sequences
                    break
        start_index += 1
    return new_message

def decode_escapes(s):
    def decode_match(match):
        return codecs.decode(match.group(0), 'unicode-escape')

    return ESCAPE_SEQUENCE_RE.sub(decode_match, s)

def error_exit(condition, err):
    '''print an error and exit when one occurs'''
    if condition:
        sys.stderr.write(err)
        sys.exit(1)

def assign(opts):
    '''assign the correct values to the correct opts'''
    for opt, arg in opts:
        if opt in ("-a", "--attachments"):
            if not arg or not (os.path.exists(arg) and os.access(arg, os.R_OK)): # [-r ..] in bash
                error_exit(True, f'Error: Cannot read {arg} file.')
            VARS["ATTACHMENTS"].append(arg)
        elif opt in ("-b", "--bcc"):
            VARS["BCCEMAILS"].append(arg)
        elif opt in ("-c", "--cc"):
            VARS["CCEMAILS"].append(arg)
        elif opt in ("-d", "--dryrun"):
            VARS["DRYRUN"] = True
        elif opt in ("-e", "--examples"):
            usage.examples()
            sys.exit(0)
        elif opt in ("-f", "--from"):
            if not VARS["FROMEMAIL"]:
                VARS["FROMEMAIL"] = arg
            else:
                error_exit(True, "Only one 'from' address must be specified as.")
        elif opt in ("-g", "--gateways"):
            usage.carriers()
            sys.exit(0)
        elif opt in ("-h", "--help"):
            usage.usage()
            sys.exit(0)
        elif opt in ("-k", "--passphrase"):
            VARS["PASSPHRASE"]=arg
        elif opt in ("-l", "--language"):
            VARS["LANGUAGE"]=True
        elif opt in ("-m", "--message"):
            if VARS["NOTIFY"] != '':
                print("Warning: Output from the program named in the `-n, --notify` flag will be sent in addition to the message indicated in the `-m, -message` flag.")
                VARS["MESSAGE"] +="\n"
            VARS["MESSAGE"] += decode_escapes(zero_pad(arg))
        elif opt in ("--message-file"):
            if VARS["MESSAGE"] != '':
                VARS["MESSAGE"] +="\n"
            expanded_file = os.path.expanduser(arg)
            if expanded_file == '-':
                VARS["MESSAGE"] += decode_escapes(zero_pad(sys.stdin.read()))
            elif os.path.exists(expanded_file) and os.access(expanded_file, os.R_OK):
                with open (expanded_file, "r") as f1:
                    VARS["MESSAGE"] += decode_escapes(zero_pad(f1.read()))
            else:
                error_exit(True, "Error: \"" + expanded_file + "\" file does not exist.")
        elif opt in ("-n", "--notify"):
            if VARS["MESSAGE"] != '':
                VARS["MESSAGE"] +="\n"
            p = subprocess.Popen(arg, shell=True, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
            stdout  = p.communicate()[0].decode()
            VARS["MESSAGE"] += decode_escapes(zero_pad(f'\n**OUTPUT**\n{stdout}\n**EXIT CODE**\n{p.returncode}'))
        elif opt in ("-p", "--password"):
            VARS["PASSWORD"]=arg
        elif opt in ("--config"):
            configuration.config_email()
            print("Configuration file successfully set\n")
            sys.exit(0)
        elif opt in ("-s", "--subject"):
            VARS["SUBJECT"] = decode_escapes(zero_pad(arg))
        elif opt in ("--starttls"):
            VARS["STARTTLS"] = True
        elif opt in ("-t", "--to"):
            VARS["TOEMAILS"].append(arg)
        elif opt in ("--tls"):
            VARS["TLS"] = True
        elif opt in ("-u", "--username"):
            VARS["USERNAME"]= arg
        elif opt in ("-v", "--version"):
            print("Send Msg CLI 1.0\n")
            sys.exit(0)
        elif opt in ("-z", "--zipfile"):
            if arg.endswith('.zip'):
                VARS["ZIPFILE"]= arg
            else:
                VARS["ZIPFILE"]= arg+".zip"
        elif opt in ("-C", "--cert"):
            VARS["CERT"]= arg
        elif opt in ("--smtpservers"):
            usage.servers()
            sys.exit(0)
        elif opt in ("-T", "--time"):
            VARS["TIME"] = arg
        elif opt in ("-P", "--priority"):
            VARS["PRIORITY"]= arg
        elif opt in ("-S", "--smtp"):
            res = arg.split(":")
            if len(res) == 2:
                VARS["SMTP"] = res[0]
                VARS["PORT"] = int(res[1])
            elif len(res) > 2:
                error_exit(True, "Extraneous input into -S or --smtp.")
            else:
                VARS["SMTP"] = res[0]
        elif opt in ("-V", "--verbose"):
            VARS["VERBOSE"]= True

def configuration_assignment():
    '''If a user decides, they may work from a configuration if the user does not specify a necessary
       flag (e.g., -u). If the config file is empty, an error will be thrown.
    '''
    # make file with appropriate fields if file does not exist
    if not VARS["SMTP"] or not VARS["FROMEMAIL"] or not VARS["USERNAME"]:
        if not os.path.exists(os.path.expanduser(CONFIG_FILE)):
            error_exit(True, "Error: SMTP server, From, Username or Password fields not set in config file and not typed on CMDline. Please include the -S, -f, or -u, flags or use the following command to set the config file: `sendpy --config`")
        else:
            print("SMTP server, From, or Username fields not typed on CMDline. \n\nAttempting to send msg with configuration file credentials...\n")
            VARS["SMTP"], VARS["PORT"], VARS["FROMEMAIL"], VARS["USERNAME"], VARS["PASSWORD"] = configuration.return_config()

def parse_assign(argv):
    '''Find the correct variable to assign the arg/opt to.'''
    try:
        opts, args = getopt.getopt(argv,"a:b:c:def:ghk:lm:n:p:rs:t:u:vz:C:P:S:T:V",
                ["attachments=", "bcc=", "cc=", "cert=", "config", "dryrun", "examples", "from=", "gateways",
                    "help", "language", "message=", "message-file=", "notify", "passphrase=", "password=", "priority=", "smtp=", "starttls",
                    "smtpservers", "subject=", "time", "to=", "tls", "username=", "verbose", "version", "zipfile="])
    except getopt.GetoptError:
        usage.usage()
        sys.exit(2)
    assign(opts)
    if VARS["TLS"] and VARS["STARTTLS"]:
        error_exit(True, "Cannot specify both --tls and --starttls option. Please choose one and try again.")

# modified from source: https://stackoverflow.com/questions/5194057/better-way-to-convert-file-sizes-in-python
def convert_bytes(size, byte_type):
    '''Calculates how large an attachment in two ways -- iB and B'''
    byte_array = ['Bytes', 'K', 'M', 'G', 'T', 'P', 'E', 'Z', 'Y']
    div_size = 1024.0 if byte_type == "i" else 1000.0
    import locale

    for x in byte_array:
        if size < div_size:
            locale.setlocale(locale.LC_ALL, '')
            unit = x + ('' if x == 'Bytes' else ('i' if byte_type == 'i' else '') + 'B')
            return f'{size:,.1f}{unit}'
        size /= div_size

    return size

# user codeskyblue from: https://stackoverflow.com/questions/19103052/python-string-formatting-columns-in-line
def format_attachment_output(rows):
    '''Spaces the printing of attachments based on largest length. A replacement for the column cmd.
       Also used for printing out our help menus found in usage.py.
    '''
    lens = []
    for col in zip(*rows):
        lens.append(max([len(v) for v in col]))
    format = "  ".join(["{:<" + str(l) + "}" for l in lens])
    for row in rows:
        print(format.format(*row).strip('\n'))

def attachment_work():
    '''Zips files to send in msg if user specifies the '-z' flag. Will also calculate size of attachments
       and warn user if size is large. Will also strip the path and just use the basename (filename).
    '''
    if VARS["ATTACHMENTS"]:
        TOTAL=0
        rows = []

        zip_file = VARS["ZIPFILE"]
        if zip_file:
            if os.path.exists(zip_file):
                error_exit(True, f'Error: File {zip_file} already exists.')

            import zipfile
            with zipfile.ZipFile(zip_file, 'w') as myzip:
                for attachment in VARS["ATTACHMENTS"]:
                    myzip.write(attachment, os.path.basename(attachment))
            atexit.register(lambda x: os.remove(x), zip_file)
            VARS["ATTACHMENTS"] = [zip_file]

        # printing in a nice row; checking if total attachment size is >= 25 MB
        for attachment in VARS["ATTACHMENTS"]:
            SIZE=os.path.getsize(attachment)
            TOTAL +=int(SIZE)
            if SIZE < 1000:
                rows.append((os.path.basename(attachment), convert_bytes(int(SIZE), "i"), ""))
            else:
                rows.append((os.path.basename(attachment), convert_bytes(int(SIZE), "i"), "("+convert_bytes(int(SIZE), "b")+")"))

        rows.append(("\nTotal Size:", " " + convert_bytes(int(TOTAL),"i"), " " + "("+convert_bytes(int(TOTAL),"b")+")"))
        print("Attachments:")
        format_attachment_output(rows)

        if TOTAL >= 26214400:
            print("Warning: The total size of all attachments is greater than or equal to 25 MiB. The message may be rejected by your or the recipient's mail server. You may want to upload large files to an external storage service, such as Firefox Send: https://send.firefox.com or transfer.sh: https://transfer.sh\n")

def email_work():
    '''Check for valid email addresses.
       Split 'From' e-mail address into name (if one is given) and email: "Example <example@example.com>" -> "Example", "example@example.com".
       Credit for a superior regex goes to Teal Dulcet.
    '''
    if not VARS["TOEMAILS"] and not VARS["BCCEMAILS"]:
        error_exit(True, "No 'To' or 'BCC' email supplied. Please enter one or both.")

    #FROMADDRESS = VARS["FROMEMAIL"] # TODO -- delete when regex is solved.
    #RE=re.compile(r'(?:\"?([^\"]*)\"?\s)?[%<a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.>]+')

    # ***Teal's code***
    ## This is the 1st regex he developed from the messages.
    VARS["FROMADDRESS"] = VARS["FROMEMAIL"]

    ## This is the 2nd regex he developed (and after we added a lot more test cases).
    RE=re.compile(r'^(.{1,64}@[\w.-]{4,254})|((.*) *<(.{1,64}@[\w.-]{4,254})>)$')
    RE1=re.compile(r'^.{6,254}$')
    RE2=re.compile(r'^.{1,64}@')
    RE3=re.compile(r'^(([^@"(),:;<>\[\\\].\s]|\\[^():;<>.])+|"([^"\\]|\\.)+")(\.(([^@"(),:;<>\[\\\].\s]|\\[^():;<>.])+|"([^"\\]|\\.)+"))*@((xn--)?[^\W_]([\w-]{0,61}[^\W_])?\.)+(xn--)?[^\W\d_]{2,63}$')
    global index # TODO -- firefox delet

    # Check if the email is valid.
    try:
        for i in range(0, len(VARS["TOEMAILS"])):
            result = RE.match(VARS["TOEMAILS"][i])
            if not result:
                error_exit(True, "Error: \""+VARS["TOEMAILS"][i]+"\" is not a valid e-mail address.")

        for i in range(0, len(VARS["CCEMAILS"])):
            result = RE.match(VARS["CCEMAILS"][i])
            if not result:
                error_exit(True, "Error: \""+VARS["CCEMAILS"][i]+"\" is not a valid e-mail address.")

        for i in range(0, len(VARS["BCCEMAILS"])):
            result = RE.match(VARS["BCCEMAILS"][i])
            if not result:
                error_exit(True, "Error: \""+VARS["BCCEMAILS"][i]+"\" is not a valid e-mail address.")

        if VARS["FROMADDRESS"]:
            result = RE.match(VARS["FROMADDRESS"])
            if result:
                VARS["FROMADDRESS"] = result.group(1) if result.group(1) else result.group(4)
            #if not RE1.match(VARS["FROMADDRESS"]) or not RE2.match(VARS["FROMADDRESS"]): # TODO -- restore after  after regex testing is done.
            if not RE1.match(VARS["FROMADDRESS"]) or not RE2.match(VARS["FROMADDRESS"]) or not RE3.match(VARS["FROMADDRESS"]):
                #print("Error: \""+VARS["FROMADDRESS"]+"\" is not a valid e-mail address.") # TODO -- delete
                #print(red + "Error: \""+reset + VARS["FROMADDRESS"]+"\" is not a valid e-mail address. Should be " + firefox_values[index][0]) # TODO -- firefox version...delete
                print(red + "Error: \""+reset + VARS["FROMADDRESS"]+"\" is not a valid e-mail address. Should be " + chromium_validity[index]) # TODO -- chromium version...delete
                index +=1
                return
                error_exit(True, "Error: \""+VARS["FROMADDRESS"]+"\" is not a valid e-mail address.") # restore after regex testing is done.
            else:
                #print("Valid: \""+VARS["FROMADDRESS"]+"\".") # TODO -- delete
                #print(green + "Valid: \""+reset+VARS["FROMADDRESS"]+"\". Should be " + firefox_values[index][0]) # TODO -- firefox version...delete
                print(green + "Valid: \""+reset+VARS["FROMADDRESS"]+"\". Should be " + chromium_validity[index]) # TODO -- chromium version...delete
                index +=1
                return
        else:
            error_exit(True, "Error: Must specify FROM e-mail address.")

    except Exception as error:
        print(error)
        sys.exit(1)

def cert_checks():
    '''Creates the .pem certificate (defined in VARS["CLIENTCERT"]; e.g., cert.pem) with certificate \
       located in VARS["CERT"] (read in from CMDLINE using -C, or --cert)
    '''
    if VARS["CERT"]:
        if which("openssl") is None:
            error_exit(True, "Error: OpenSSL not found on PATH. Please download OpenSSL and/or add it to the PATH. You need this to sign a message with S/MIME.")

        if not os.path.exists(VARS["CERT"]) and not os.access(VARS["CERT"], os.R_OK) and not os.path.exists(VARS["CLIENTCERT"]):
            error_exit(True, "Error: \""+VARS["CERT"]+"\" certificate file does not exist.")

        if not os.path.exists(VARS["CLIENTCERT"]):
            print("Saving the client certificate from \""+VARS["CERT"]+"\" to \""+VARS["CLIENTCERT"]+"\"")
            print("Please enter the password when prompted.\n")
            subprocess.check_output("openssl pkcs12 -in \""+VARS["CERT"]+"\" -out \""+VARS["CLIENTCERT"]+"\" -clcerts -nodes",shell=True).decode().strip("\n")

        aissuer=subprocess.check_output("openssl x509 -in \""+VARS["CLIENTCERT"]+"\" -noout -issuer -nameopt multiline,-align,-esc_msb,utf8,-space_eq", shell=True).decode().strip("\n")
        date=subprocess.check_output("openssl x509 -in \""+VARS["CLIENTCERT"] + "\" -noout -enddate", shell=True).decode().strip("\r\n")

        if aissuer:
            for line in aissuer.split("commonName="):
                issuer=line
        else:
            issuer=''

        split = date.split("notAfter=")
        if split:
            for line in split:
                date=line
        else:
            error_exit(True, "No expiration date found in cert.pem file. You may try re-creating the file by deleting it and running this script again.")

        p=subprocess.Popen("openssl x509 -in \"" + VARS["CLIENTCERT"] + "\" -noout -checkend 0", stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
        p.communicate()

        if p != 0:
            sec = int(time.mktime(datetime.datetime.strptime(date, "%b %d %H:%M:%S %Y %Z").timetuple()) - time.mktime(datetime.datetime.strptime(VARS["NOW"], "%b %d %H:%M:%S %Y %Z").timetuple()))
            if sec / 86400 < VARS["WARNDAYS"]:
                if issuer:
                    print(f'Warning: The S/MIME Certificate from \"{issuer}\" expires in less than ' + str(VARS["WARNDAYS"])+ f' days {date}')
                else:
                    print(f'Warning: The S/MIME Certificate expires in less than ' + str(VARS["WARNDAYS"])+ f' days {date}')

        else:
            error = f'Error: The S/MIME Certificate from \"{issuer}\" expired {date}' if issuer else f'Error: The S/MIME Certificate expired {date}'
            error_exit(True, error)

def passphrase_checks():
    '''Does a number of checks if a user indicated they watn to sign with a GPG key to utilize PGP/MIME'''
    if VARS["PASSPHRASE"]:
        if which("gpg") is None:
            error_exit(True, "Error: GPG not found. You need this to sign a message with PGP/MIME")

        # Work from a config file
        if VARS["PASSPHRASE"].lower() == "config":
            VARS["PASSPHRASE"] = configuration.config_pgp()

        # create file to be written out, then schedule it to be removed if an exit occurs
        with open("temp_message", "w") as f1:
            f1.write(" ")
        atexit.register(lambda x: os.remove(x), 'temp_message')

        # check if GPG key exists
        p = subprocess.Popen("gpg --pinentry-mode loopback --batch -o - -ab -u \""+VARS["FROMADDRESS"]+"\" --passphrase-fd 0 temp_message", shell=True, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        stdout = p.communicate(bytes(VARS["PASSPHRASE"], "utf-8"))[0].decode()
        if p.returncode != 0:
            error_exit(True, "Error: A PGP key pair does not yet exist for \""+VARS["FROMADDRESS"]+"\" or the passphrase was incorrect.")

        # check if GPG key will expire soon or has expired
        date=subprocess.check_output("gpg -k --with-colons \""+VARS["FROMADDRESS"]+"\"", shell=True).decode().strip("\n")
        for line in date.split("\n"):
            if "pub" in line:
                date = line.split(":")[6]
                break

        if date:
            sec = int(date) - int(time.mktime(datetime.datetime.strptime(VARS["NOW"], "%b %d %H:%M:%S %Y %Z").timetuple()))
            fingerprint=subprocess.check_output("gpg --fingerprint --with-colons \""+VARS["FROMADDRESS"]+"\"", shell=True).decode().strip("\n")
            for line in fingerprint.split("\n"):
                if "fpr" in line:
                    fingerprint = line.split(":")[9]
                    break

            readable_date = datetime.datetime.fromtimestamp(int(date)).strftime("%b %d %H:%M:%S %Y %Z")
            if sec > 0:
                if sec / 86400 < VARS["WARNDAYS"]:
                    print(f'Warning: The PGP key pair for \"' + VARS["FROMADDRESS"] + f'\" with fingerprint {fingerprint} expires in less than ' + str(VARS["WARNDAYS"]) + f' days {readable_date}.\n')
            else:
                error_exit(True,f'Error: The PGP key pair for \"' + VARS["FROMADDRESS"] + f'\" with fingerprint {fingerprint} expired {readable_date}')

    if VARS["CERT"] and VARS["PASSPHRASE"]:
        print("Warning: You cannot digitally sign the e-mails with both an S/MIME Certificate and PGP/MIME. S/MIME will be used.\n")

def main(argv):
    # testing
    # TODO -- delete this testing structure
    #with open("valid.txt", "r") as f1: # test valid e-mail addresses
    #with open("invalid.txt", "r") as f1: # test invalid e-mail addresses
    with open("firefox.txt", "r") as f1: # test invalid e-mail addresses
        try:
            #for line in f1:
                #VARS["FROMEMAIL"] = line.strip('\n')
            for line in chromium_values:
                length = len(line)
                VARS["FROMEMAIL"] = line[0].strip('\n')

                # parsing/assignment
                parse_assign(argv)
                configuration_assignment() # use default configuration if nothing was put on the CMDline

                # email/email checks
                email_work()
                attachment_work()

                # signing/signing checks
                cert_checks()
                passphrase_checks()

                # sending
                sendEmail(VARS, VARS["PORT"])
        except Exception as error:
            print(error)
            print("EXCEPTION CAUGHT")

if __name__=="__main__":
    if len(sys.argv) == 1:
        usage.usage()
        sys.exit(1)
    main(sys.argv[1:])
