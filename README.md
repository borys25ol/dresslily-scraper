Dreslily Scraper
====================

Local install
-------------

Setup and activate a python3 virtualenv via your preferred method. e.g. and install production requirements:


    $ make ve
  
For remove virtualenv:


    $ make clean

Use docker for install Splash:

    https://splash.readthedocs.io/en/stable/install.html



Scrapy process
======================

Run ``scrapy crawl`` from spider folder:


    $ scrapy crawl {spider-name}

Result CSV files stored:

    $ cd crawl/results && ls -l

  
 