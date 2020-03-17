#!/usr/bin/env python3

import sys
import getopt
import datetime

'''The purpose of this file is to parse all flags given on the cmdline.
   Skipping to the bottom main function is where the control-flow begins.

'''
#TODO\s:
'''
1. Switch to argparse? Argparse enables the ability to output a specific help message
  rather than the entire help menu.
2. Reminder: Update help menu with getopts
3. Do we need the check that we are on linux now with this Python script version? Ask Teal.
'''

###Variables

# TODO -- I want to rework the way that I indicate an email is being sent... like an "(-e,--email)" flag?
'''
# Send e-mails
# Comment this out to temporally disable
SEND=1
'''

VARS={"TOEMAILS":[],"CCEMAILS":[],"BCCEMAILS":[],"FROMEMAIL":'',"SMTP":'',"USERNAME":'',"PASSWORD":'',"PRIORITY":"Normal","CERT":"cert.p12","CLIENTCERT":"cert.pem","PASSPHRASE":'',"WARNDAYS":"3","ZIPFILE":'',"VERBOSE":"1","NOW":datetime.datetime.now().strftime("%A, %B %d. %Y %I:%M%p"),"SUBJECT":'',"MESSAGE":'',"ATTACHMENTS":[]}

# Note, I did not use "toaddress",but rather the already existing "temails" as its equivalent (I think)
LOPTIONS={"-s":"--subject", "-m":"--message","-a":"--attachments", "-t":"--toemails", "-c":"--ccemails", "-b":"--bccemails", "-f":"--fromemail", "-S":"--smtp", "-u":"--username", "-p":"--password", "-P":"--priority", "-C":"--certificate", "-k":"--passphrase", "-z":"--zipfile", "-d":"--dryrun", "-V":"--verbose", "-h":"--help", "-v":"--version"}
# TODO -- long option naming like "bcc-emails" is non-sensical as it only takes one at a time...
# TODO -- add these somehow...or just reuse the original names
'''
TOADDRESSES=( "${TOEMAILS[@]}" )
TONAMES=( "${TOEMAILS[@]}" )
CCADDRESSES=( "${CCEMAILS[@]}" )
CCNAMES=( "${CCEMAILS[@]}" )
BCCADDRESSES=( "${BCCEMAILS[@]}" )
FROMADDRESS=$FROMEMAIL
FROMNAME=$FROMEMAIL
'''

# Output usage
# usage <program name>
def usage():
    print("Usage:  $1 <OPTION(S)>... -s <subject>\n"+
    "or:     $1 <OPTION>\n"+
    "One or more To, CC or BCC e-mail addresses are required. Send text messages by using the mobile providers e-mail to SMS or MMS gateway (https://en.wikipedia.org/wiki/SMS_gateway#Email_clients). All the options can also be set by opening the script in an editor and setting the variables at the top. See examples below.\n"+

    "Options:\n"+
        "-s <subject>    Subject\n"+
                            "Escape sequences are expanded. Supports Unicode characters.\n"+
        "-m <message>    Message body\n"+
                            "Escape sequences are expanded. Supports Unicode characters.\n"+
        "-a <attachment> Attachment filename\n"+
                            "Use multiple times for multiple attachments. Supports Unicode characters in filename.\n"+
        "-t <To address> To e-mail address\n"+
                            "Use multiple times for multiple To e-mail addresses.\n"+
        "-c <CC address> CC e-mail address\n"+
                            "Use multiple times for multiple CC e-mail addresses.\n"+
        "-b <BCC address>BCC e-mail address\n"+
                            "Use multiple times for multiple BCC e-mail addresses.\n"+
        "-f <From address>From e-mail address\n"+

        "-S <SMTP server>SMTP server\n"+
                            "Supported protocols: \"smtp\" and \"smtps\". Requires From e-mail address. Use \"smtp://localhost\" if running a mail server on this device.\n"+
        "-u <username>   SMTP server username\n"+
        "-p <password>   SMTP server password\n"+
        "-P <priority>   Priority\n"+
                            "Supported priorities: \"5 (Lowest)\", \"4 (Low)\", \"Normal\", \"2 (High)\" and \"1 (Highest)\". Requires SMTP server.\n"+
        "-C <certificate>S/MIME Certificate filename for digitally signing the e-mails\n"+
                            "It will ask you for the password the first time you run the script with this option. Requires SMTP server.\n"+
        "-k <passphrase> PGP secret key passphrase for digitally signing the e-mails with PGP/MIME\n"+
                            "Requires SMTP server.\n"+
        "-z <zipfile>    Compress attachment(s) with zip\n"+
        "-d              Dry run, do not send the e-mail\n"+
        "-V              Verbose, show the client-server communication\n"+
                            "Requires SMTP server.\n"+

        "-h              Display this help and exit\n"+
        "-v              Output version information and exit\n"+

    "Examples:\n"+
        "Send e-mail\n"+
        "$ $1 -s \"Example\" -t \"Example <example@example.com>\"\n"+

        "Send e-mail with message\n"+
        "$ $1 -s \"Example\" -m \"This is an example"'!'"\" -t \"Example <example@example.com>\"\n"+

        "Send e-mail with message and single attachment\n"+
        "$ $1 -s \"Example\" -m \"This is an example"'!'"\" -a example.txt -t \"Example <example@example.com>\"\n"+

        "Send e-mail with message and multiple attachments\n"+
        "$ $1 -s \"Example\" -m \"This is an example"'!'"\" -a example1.txt -a example2.txt -t \"Example <example@example.com>\"\n"+

        "Send e-mail to a CC address\n"+
        "$ $1 -s \"Example\" -t \"Example 1 <example1@example.com>\" -c \"Example 2 <example2@example.com>\"\n"+

        "Send e-mail with a From address\n"+
        "$ $1 -s \"Example\" -f \"Example <example@example.com>\" -t \"Example <example@example.com>\"\n"+

        "Send e-mail with an external SMTP server\n"+
        "$ $1 -s \"Example\" -f \"Example <example@example.com>\" -S \"smtps://mail.example.com\" -u \"example\" -p \"password\" -t \"Example <example@example.com>\"\n"+

        "Send high priority e-mail\n"+
        "$ $1 -s \"Example\" -f \"Example <example@example.com>\" -S \"smtps://mail.example.com\" -u \"example\" -p \"password\" -P \"1 (Highest)\" -t \"Example <example@example.com>\"\n"+

        "Send e-mail digitally signed with an S/MIME Certificate\n"+
        "$ $1 -s \"Example\" -f \"Example <example@example.com>\" -S \"smtps://mail.example.com\" -u \"example\" -p \"password\" -C \"cert.p12\" -t \"Example <example@example.com>\"\n"+

        "Send e-mail digitally signed with PGP/MIME"+ "$ $1 -s \"Example\" -f \"Example <example@example.com>\" -S \"smtps://mail.example.com\" -u \"example\" -p \"password\" -k \"passphrase\" -t \"Example <example@example.com>\""+")\n")

def assign(opts):
    '''assign the correct opts'''
    for opt, arg in opts:
        if opt in ("-a", "--attachments"):
            VARS["ATTACHMENTS"].append(arg)
        elif opt in ("-b", "--bccemails"):
            VARS["BCCEMAILS"].append(arg)
        elif opt in ("-c", "--ccemails"):
            VARS["CCEMAILS"].append(arg)
        elif opt in ("-d", "--dryrun"):
            pass # TODO
        elif opt in ("-f", "--fromemail"):
            VARS["FROMEMAIL"] = arg
        elif opt in ("-h", "--help"):
            usage()
            sys.exit(2)
        elif opt in ("-k", "--passphrase"):
            VARS["PASSPHRASE"]=arg
        elif opt in ("-m", "--message"):
            VARS["MESSAGE"]=arg
        elif opt in ("-p", "--password"):
            VARS["PASSWORD"]=arg
        elif opt in ("-s", "--subject"):
            VARS["SUBJECT"]=arg
        elif opt in ("-t", "--toemails"):
            VARS["TOEMAILS"].append(arg)
        elif opt in ("-u", "--username"):
            VARS["USERNAME"]= arg
        elif opt in ("-v", "--version"):
            print("Send Msg CLI 1.0\n")
            sys.exit(0)
        elif opt in ("-z", "--zipfile"):
            VARS["ZIPFILE"]= arg
        elif opt in ("-C", "--cert"):
            VARS["CERT"]= arg
        elif opt in ("-P", "--priority"):
            VARS["PRIORITY"]= arg
        elif opt in ("-S", "--smtp"):
            VARS["PRIORITY"]= arg
        elif opt in ("-V", "--VERBOSE"):
            VARS["VERBOSE"]= arg

def parse(argv):
    '''Find the correct variable to assign the opt to.'''
    # Parsing. Erroneous flags throw exception.
    try:
        # TODO -- "passphrase" does not match with variable 'k'. Why not "key"? Ask Teal
        opts, args = getopt.getopt(argv,"a:b:c:df:hk:m:p:s:t:u:vz:C:P:S:V",
                ["attachments=", "bccemails=", "ccemails=", "dryrun=", "fromemail=", "help=",
                    "passphrase=", "subject=", "toaddress=", "username=", "version=", "zipfile=",
                    "cert=", "priority=", "smtp=", "verbose="])
    except getopt.GetoptError:
        usage()
        sys.exit(2)
    assign(opts)
    #print(VARS)

def main(argv):
    parse(argv)

if __name__=="__main__":
    main(sys.argv[1:])
