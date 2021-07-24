# AffiliateBot2.0

This is an updated version that runs via Docker and is easier to maintain.

---

This bot functions as a scanner for Affiliate base content within submissions and comments.

It is based on the bot we use at https://www.reddit.com/r/GameDeals for reporting spam and other content, while it is not the exact same bot, I will keep this updated with most of the features we use.

The bot does not require any form of subreddit moderator permissions and will report submissions and comments in the following format `Bot Report: REASON`.

When a Submission or a Comment is submitted within the chosen subreddit, the bot will extract all the URL's check the URL and also check the content of the linked sites to check for Affiliate based information and Report the Submission or Comment based on it's findings, it is not always 100% correct and still requires manual interaction before you make you choice to remove or approve.

If you need any help to configure, or hosting the bot you are welcome to contact me directly on [reddit](https://www.reddit.com/user/dgc1980/).

---

# Options for hosting

[Gullo's Hosting](https://hosting.gullo.me/pricing) - Cheap OpenVZ NAT Based VPS using a Shared IPv4 between other members recommended 512MB server but will worth with 256MB (upgrading to Docker for newer versions of bot 512MB required)

* use coupon `LEB-NAT-256MB` or `LEB-NAT-512MB` depending on your choice to take about 40% off the price

[Boomer.host](https://my.boomer.host/order.php?step=1&productGroup=4&product=7) - Cheap OpenVZ Based VPS with its own IPv4 - USD4.99 per year. fairly new host not many reviews I have started using one for testing

[VirMach](https://virmach.com/special-offers/) Cheap KVM Based VPS with cheap prices and dedicated IPv4 - I currently use a 1GB system here for my production bots and are highly recommended



---
I have no affiliate links in the above links and not getting paid to promote any of the above providers and they are just my personal recommendations, you are free to use anyone you wish

---

# Installation

Recommended Linux Distro is either Debian 9+ or Ubuntu 18.04+

installation of Docker CE

```
curl -sSL https://get.docker.com/ | CHANNEL=stable sh
systemctl enable docker.service
systemctl start docker.service
apt install -y docker-compose
```

enter a directory for the bot to run in and store its data

`mkdir AffiliateBot`

`cd AffiliateBot`

create a `docker-compose.yml` file

`nano -w docker-compose.yml`

and enter the following information

```
version: '2.3'
services:
  affiliatebot2.0:
    image: dgc1980/affiliatebot2.0:latest
    environment:
      REDDIT_USER: YOUR_REDDIT_BOT_USERNAME
      REDDIT_PASS: YOUR_REDDIT_BOT_PASS
      REDDIT_CID: YOURCLIENTID
      REDDIT_SECRET: YOURSECRET
      REDDIT_SUBREDDIT: SubReddit
      # Check comment anchors for match [https://to.link/address](https://to.link/address) to see if they are hiding links
      CONFIG_CHECKANCHOR: 1
      # this will only check the base domain for both results, DomainOnly or All
      CONFIG_ANCHORMATCH: DomainOnly
    volumes:
      - ./affilliatebot2.0:/app/config
    restart: always
```

the username and pass are what you have signed up with

for the Client ID and Secret please visit https://www.reddit.com/prefs/apps

create a new app as script, then use the information from that for your configuration above

once you have completed the above load the docker container with the following

`docker-compose up`

you will see that it will automatically download the required configuration for affiliate filtering press CTRL+C to stop the bot

edit your `affilliatebot2.0/affiliatedata.txt` and such with additional information if required then restart the bot detached

`docker-compose up -d`

if you wish to stop the bot in the future use

`docker-compose down`
