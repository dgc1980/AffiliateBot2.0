import sqlite3

import time
import praw
import prawcore
import requests

import logging
import re
import os
import datetime

import schedule

from numpy import loadtxt

reddit_cid = os.environ['REDDIT_CID']
reddit_secret = os.environ['REDDIT_SECRET']

reddit_user = os.environ['REDDIT_USER']
reddit_pass = os.environ['REDDIT_PASS']

reddit_subreddit = os.environ['REDDIT_SUBREDDIT']

CHECKANCHOR = os.environ['CONFIG_CHECKANCHOR']
ANCHORMATCH = os.environ['CONFIG_ANCHORMATCH']


web_useragent = 'python:AffiliateBot:2.0 (by dgc1980)'


reddit = praw.Reddit(client_id=reddit_cid,
                     client_secret=reddit_secret,
                     password=reddit_pass,
                     user_agent=web_useragent,
                     username=reddit_user)
subreddit = reddit.subreddit(reddit_subreddit)



apppath='/app/config/'

logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s %(name)-12s %(levelname)-8s %(message)s',
                    datefmt='%m-%d %H:%M',
                    filename=apppath+'affiliatebot.log',
                    filemode='a')

console = logging.StreamHandler()
console.setLevel(logging.INFO)
formatter = logging.Formatter('%(name)-12s: %(levelname)-8s %(message)s')
console.setFormatter(formatter)
logging.getLogger('').addHandler(console)
os.environ['TZ'] = 'America/Los_Angeles'


def download(url, file_name):
    with open(file_name, "wb") as file:
        response = requests.get(url)
        file.write(response.content)



logging.info("Loading Affiliate Data" )
if not os.path.isfile(apppath+"affiliatedata.txt"):
  logging.info("Not Found!! - downloading base template" )
  url = 'https://gist.githubusercontent.com/dgc1980/fb0a166623c6d326fcaf69ac19a0866c/raw/affiliatedata.txt'
  download(url, apppath+"affiliatedata.txt")
AffiliateData = loadtxt(apppath+"affiliatedata.txt", comments="#", delimiter=",", unpack=False ,dtype='str', ndmin = 1)

logging.info("Loading Whitelist Data" )
if not os.path.isfile(apppath+"whitelist.txt"):
  logging.info("Not Found!! - downloading base template" )
  url = 'https://gist.githubusercontent.com/dgc1980/a79838cba5672ec4e197ed35f092307f/raw/whitelist.txt'
  download(url, apppath+"whitelist.txt")
Whitelist = loadtxt(apppath+"whitelist.txt", comments="#", delimiter=",", unpack=False,dtype='str', ndmin = 1)

logging.info("Loading Greylist Data" )
if not os.path.isfile(apppath+"greylist.txt"):
  logging.info("Not Found!! - downloading base template" )
  url = 'https://gist.githubusercontent.com/dgc1980/a56db0cc6052e9952b2079806b025a04/raw/greylist.txt'
  download(url, apppath+"greylist.txt")
Greylist = loadtxt(apppath+"greylist.txt", comments="#", delimiter=",", unpack=False, dtype='str', ndmin = 1)

logging.info("Loading IgnoreURL Data" )
if not os.path.isfile(apppath+"ignoreurls.txt"):
  logging.info("Not Found!! - downloading base template" )
  url = 'https://gist.githubusercontent.com/dgc1980/f9d35c91621026d992ef2fcf11242838/raw/ignoreurls.txt'
  download(url, apppath+"ignoreurls.txt")
URLignores = loadtxt(apppath+"ignoreurls.txt", comments="#", delimiter=",", unpack=False, dtype='str', ndmin = 1)


f = open(apppath+"submissionids.txt","a+")
f.close()
f = open(apppath+"commentids.txt","a+")
f.close()

def checkanchors( comment ):
  anchors = re.findall('\[(\S+)\]\((\S+)\)', comment)
  for anchor in anchors:
    if ANCHORMATCH == 'DomainOnly':
      if any(s in anchor[0] for s in ['.co','.com','.net', '.io', '.org', '.gg']):
        if getdomain( anchor[0] ):
          if getdomain(anchor[0]) != getdomain(anchor[1]):
            return True


def submissionID(postid):
    f = open(apppath+"submissionids.txt","a+")
    f.write(postid + "\n")
    f.close()

def commentID(postid):
    f = open(apppath+"commentids.txt","a+")
    f.write(postid + "\n")
    f.close()

def getdomain( url ):
    match1 = re.search("(?:https?:\/\/)?(?:www\.)?([\w\-\.]+)", url)
    if match1:
      return match1.group(1)
    return None




def check_url( url ):
    if re.search("(?:https?:\/\/)?(?:www\.)?([\w\-\.]+)\/", url) is not None:
        forceload = False
        for uignore in URLignore:
            if uignore in url.lower():
                return = True
        for greylist in Greylist:
            if greylist in url.lower():
                forceload = True
        if getdomain(url) not in Whitelist or forceload:
            logging.info("checking url " + url)
            try:
                r = requests.get(url)
                if r.history:
                    for reqs in r.history:
                        print("redirects  " + reqs.url)
                        for affdata in AffiliateData:
                            if re.search(affdata, reqs.url.lower() ) is not None:
                                return( "Found Generic Affiliate Information In Redirect" )
                    print("redirects  " + r.url)
                    for affdata in AffiliateData:
                        if re.search(affdata, r.url.lower() ) is not None:
                            return( "Found Generic Affiliate Information In Redirect" )


                if re.search("amzn.to|amazon\.co.*tag=|amazon\.com\/.*asin", r.text.lower()) is not None:
                    return( "Amazon Affailiates Found" )
                if re.search("(amzn_assoc_tracking_id|amazon-adsystem.com)", r.text.lower()) is not None:
                    return( "Amazon Ads found, may be spam" )
                if re.search("shopify.com|wix.com", r.text.lower()) is not None:
                    return( "Wix/Shopify Found check if legit store" )
                for affdata in AffiliateData:
                    if re.search(affdata, r.text ) is not None:
                        return( "Found Generic Affiliate Information" )
                return
            except:
                logging.info("error checking " + url)





def check_comment(comment):
    commentID(comment.id)
    urls = re.findall('(?:(?:https?):\/\/)?[\w/\-?=%.]+\.[\w/\-?=%.]+', comment.body)
    if len(urls) == 0:
        logging.debug("NO LINK FOUND skipping: " + comment.id)
        return
    # remove duplicate URLs
    unique_urls = []
    for url in urls:
        if url in unique_urls:
            continue
        else:
            unique_urls.append(url)

    if CHECKANCHOR == 1:
        if checkanchors( comment.body ):
            logging.info("Reporting " + comment.id + " for Found Mismatched Anchor/Link" )
            comment.report( "Affiliate Bot: " + "Found Mismatched Anchor/Link" )
            return

    for url in unique_urls:
        urlcheck = check_url( url )
        if urlcheck:
            logging.info("Reporting " + comment.id + " for " + urlcheck )
            comment.report( "Affiliate Bot: " + urlcheck )
            return





def check_post(submission):
    submissionID(submission.id)
    if submission.is_self:
        urls = re.findall('(?:(?:https?):\/\/)?[\w/\-?=%.]+\.[\w/\-?=%.]+', submission.selftext)
        if len(urls) == 0:
            logging.debug("NO LINK FOUND skipping: " + submission.title)
            return
    # remove duplicate URLs
        unique_urls = []
        for url in urls:
          if url in unique_urls:
            continue
          else:
            unique_urls.append(url)
        for url in unique_urls:
            urlcheck = check_url( url )
            if urlcheck:
                submission.report( "Affiliate Bot: " + urlcheck )
                return

    if not submission.is_self:
        url = submission.url
        urlcheck = check_url( url )
        if urlcheck:
            submission.report( urlcheck )
            return

logging.info("bot initialized...." )

while True:
  try:
    logging.debug("checking submissions")
    for post in subreddit.stream.submissions(pause_after=-1):
        if post is None:
            break
        if post.id in open(apppath+'submissionids.txt').read():
          continue
        check_post(post)
    logging.debug("checking comments")
    for cmt in subreddit.stream.comments(pause_after=-1):
        if cmt is None:
            break
        if cmt.id in open(apppath+'commentids.txt').read():
          continue
        check_comment(cmt)
  except (prawcore.exceptions.RequestException, prawcore.exceptions.ResponseException):
    logging.info("Error connecting to reddit servers. Retrying in 30 seconds...")
    time.sleep(30)



