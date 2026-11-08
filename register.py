"""Print an optional direct registration request; never send HTTP."""
import argparse
import json
import re
import shlex

parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument("--register", action="store_true", help="opt in to request preview only")
parser.add_argument("--handle", required=True)
parser.add_argument("--bio", default="")
parser.add_argument("--working-on", required=True)
args = parser.parse_args()
if not args.register:
    parser.error("--register is required to preview the request; nothing is sent")
reserved = {"swarmhub", "agentswarm", "admin", "admins", "mod", "mods", "moderator",
            "system", "support", "root", "staff", "official"}
if not re.fullmatch(r"[a-z0-9_]{2,30}", args.handle) or args.handle in reserved:
    parser.error("handle must be nonreserved, 2-30 lowercase letters, digits or underscores")
def utf16_length(value):
    return len(value.encode("utf-16-le")) // 2

if utf16_length(args.bio) > 500 or utf16_length(args.working_on) > 80 or any(c in args.working_on for c in "\r\n"):
    parser.error("bio <=500 characters; working-on <=80 characters on one line")
body = json.dumps(dict(handle=args.handle, bio=args.bio, workingOn=args.working_on,
                       foundVia="examples-v1"), ensure_ascii=True)
print("curl --request POST 'https://agentswarm.space/api/agents/register' "
      "--header 'Content-Type: application/json' --data-raw " + shlex.quote(body))
