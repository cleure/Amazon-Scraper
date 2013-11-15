
scraper = {
    'run_every': 3,     # Run every X Hours
    'workers': 4,       # Number of scraper processes to spawn
}

notifications = {
    'backend': ('smtp', {
        'host': 'smtp.gmail.com',                       # SMTP Host
        'from_addr': 'myemail@gmail.com',               # From Address
        'to_addr': 'myemail@gmail.com',                 # To Address
        'user': None,                                   # User (if login required)
        'password': None,                               # Password (if login required)
        'ssl': False,                                   # True for SSL
        'port': 25,                                     # SMTP Port
        'email_subject': 'Amazon Scraper Notification', # Email subject line
        'local_hostname': None,                         # FQDN of local host
        'keyfile': None,
        'certfile': None,
    }),
}
