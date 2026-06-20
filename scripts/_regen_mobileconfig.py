import uuid

ACCOUNTS = [
    ("Alan Woodyard",               "alan@alanwoodyard.com",                "eD!No4U1z3yT4q1VhxMb"),
    ("Hello - AW.com",              "hello@alanwoodyard.com",               "nKJLZrQDoqDeSg4IJn!f"),
    ("Alan - Sail Southern",        "alan@sailsouthern.com",                "ZYCNSHFaDaYm!hFvH0sb"),
    ("Info - Sail Southern",        "info@sailsouthern.com",                "7jNcgUa!ixyHqbKTi1EQ"),
    ("Alan - Layline Digital",      "alan@laylinedigital.com",              "78eXo0JzPYYK!NvJCEy8"),
    ("Info - Layline Digital",      "info@laylinedigital.com",              "nwoHcS!5ra4tXx7i3uH9"),
    ("Alan - AW.net",               "alan@alanwoodyard.net",                "mSKGpm57cNtO!TecXckG"),
    ("Admin - AW.net",              "admin@alanwoodyard.net",               "vvub1GqzT2PeBWku4!Ju"),
    ("Alan - AW.photo",             "alan@alanwoodyard.photo",              "BFe!EoC5nkHgdileiskZ"),
    ("Alan - Awoo Design",          "alan@awoo.design",                     "U!qoTutu5HjVGY970IiO"),
    ("Hello - Awoo Design",         "hello@awoo.design",                    "xPrneiXP1dADaL!8GF1X"),
    ("Alan - Curb Appeal",          "alan@curbappealdigital.com",           "tnFQ747BwHlg9!zLqlRi"),
    ("Info - Curb Appeal",          "info@curbappealdigital.com",           "Y!0BlI9PsTldh80HpDf4"),
    ("Admin - Curb Appeal",         "admin@curbappealdigital.com",          "pu3A!QoIG9BboLOqV0N6"),
    ("Post Modern Cereal",          "postmoderncereal@postmoderncereal.com","zxp5N7od3!37WbXWoq85"),
    ("Info - Post Modern Cereal",   "info@postmoderncereal.com",            "WdG2OxSK3bek7PWlb!Ox"),
]

IMAP_HOST, IMAP_PORT = "mail.alanwoodyard.com", 993
SMTP_HOST, SMTP_PORT = "mail.alanwoodyard.com", 587

ACCOUNT_TPL = """        <dict>
            <key>EmailAccountDescription</key>
            <string>{display}</string>
            <key>EmailAccountName</key>
            <string>Alan Woodyard</string>
            <key>EmailAccountType</key>
            <string>EmailTypeIMAP</string>
            <key>EmailAddress</key>
            <string>{email}</string>
            <key>IncomingMailServerAuthentication</key>
            <string>EmailAuthPassword</string>
            <key>IncomingMailServerHostName</key>
            <string>{imap_host}</string>
            <key>IncomingMailServerPortNumber</key>
            <integer>{imap_port}</integer>
            <key>IncomingMailServerUseSSL</key>
            <true/>
            <key>IncomingMailServerUsername</key>
            <string>{email}</string>
            <key>IncomingPassword</key>
            <string>{password}</string>
            <key>OutgoingMailServerAuthentication</key>
            <string>EmailAuthPassword</string>
            <key>OutgoingMailServerHostName</key>
            <string>{smtp_host}</string>
            <key>OutgoingMailServerPortNumber</key>
            <integer>{smtp_port}</integer>
            <key>OutgoingMailServerUseSSL</key>
            <false/>
            <key>OutgoingMailServerUsername</key>
            <string>{email}</string>
            <key>OutgoingPassword</key>
            <string>{password}</string>
            <key>PayloadDescription</key>
            <string>Stax Mail - {email}</string>
            <key>PayloadDisplayName</key>
            <string>{email}</string>
            <key>PayloadIdentifier</key>
            <string>com.staxmail.email.{uid}</string>
            <key>PayloadType</key>
            <string>com.apple.mail.managed</string>
            <key>PayloadUUID</key>
            <string>{puuid}</string>
            <key>PayloadVersion</key>
            <integer>1</integer>
            <key>SMIMEEnabled</key>
            <false/>
        </dict>
"""

out = """<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN"
  "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>PayloadContent</key>
    <array>
"""

for display, email, pw in ACCOUNTS:
    uid = email.replace("@", ".").replace(".", "-")
    out += ACCOUNT_TPL.format(
        display=display, email=email, password=pw,
        imap_host=IMAP_HOST, imap_port=IMAP_PORT,
        smtp_host=SMTP_HOST, smtp_port=SMTP_PORT,
        uid=uid, puuid=str(uuid.uuid4()).upper()
    )

out += """    </array>
    <key>PayloadDescription</key>
    <string>Stax Mail - all primary accounts</string>
    <key>PayloadDisplayName</key>
    <string>Stax Mail Accounts</string>
    <key>PayloadIdentifier</key>
    <string>com.staxmail.profile.primary</string>
    <key>PayloadOrganization</key>
    <string>Stax</string>
    <key>PayloadRemovalDisallowed</key>
    <false/>
    <key>PayloadType</key>
    <string>Configuration</string>
    <key>PayloadUUID</key>
    <string>{profile_uuid}</string>
    <key>PayloadVersion</key>
    <integer>1</integer>
</dict>
</plist>
""".format(profile_uuid=str(uuid.uuid4()).upper())

path = r"C:\Users\aewoo\Desktop\Claude Code Workspace\Quick Script\stax-mail-accounts.mobileconfig"
with open(path, "w", encoding="utf-8") as f:
    f.write(out)
print("Done:", path)
