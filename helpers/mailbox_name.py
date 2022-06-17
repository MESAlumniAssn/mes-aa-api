import os

mailbox_mapping = {
    os.getenv("PRESIDENT_EMAIL"): "President",
    "vp@mesalumniassociation.com": "Vice President",
    "secretary@mesalumniassociation.com": "Secretary",
    "jointsecy@mesalumniassociation.com": "Joint Secretary",
    os.getenv("TREASURER_EMAIL"): "Treasurer",
    "mcmembers@mesalumniassociation.com": "MC Members",
    os.getenv("CONTACT_EMAIL"): "Contact",
}
