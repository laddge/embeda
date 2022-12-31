import re
from urllib.parse import urljoin
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from typing import Optional
import requests
import lxml.html

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
async def api(url: Optional[str] = None):
    if not url:
        return "hello, world"
    try:
        r = requests.get(url, headers={"User-Agent": "Mozilla/5.0"}, timeout=10)
        if str(r.status_code)[0] != "2":
            raise Exception
        html = lxml.html.fromstring(r.text)
    except Exception:
        return {}

    if html.xpath('.//meta[@property="og:title"]/@content'):
        title = html.xpath('.//meta[@property="og:title"]/@content')[-1]
    elif html.xpath('.//meta[@property="twitter:title"]/@content'):
        title = html.xpath('.//meta[@property="twitter:title"]/@content')[-1]
    elif html.xpath(".//title/text()"):
        title = html.xpath(".//title/text()")[0]
    else:
        title = ""

    if html.xpath('.//meta[@property="og:description"]/@content'):
        description = html.xpath('.//meta[@property="og:description"]/@content')[-1]
    elif html.xpath('.//meta[@property="twitter:description"]/@content'):
        description = html.xpath('.//meta[@property="twitter:description"]/@content')[-1]
    elif html.xpath('.//meta[@name="description"]/@content'):
        description = html.xpath('.//meta[@name="description"]/@content')[0]
    else:
        description = ""

    if html.xpath('.//meta[@property="og:site_name"]/@content'):
        site_name = html.xpath('.//meta[@property="og:site_name"]/@content')[-1]
    else:
        site_name = ""

    if html.xpath('.//meta[@property="og:image"]/@content'):
        image = html.xpath('.//meta[@property="og:image"]/@content')[-1]
    elif html.xpath('.//meta[@property="twitter:image"]/@content'):
        image = html.xpath('.//meta[@property="twitter:image"]/@content')[-1]
    elif html.xpath('.//link[@rel="apple-touch-icon" or @rel="icon"]/@sizes'):
        size = max(
            [
                int(re.sub("x.*", "", s))
                for s in html.xpath(
                    './/link[@rel="apple-touch-icon" or @rel="icon"]/@sizes'
                )
            ]
        )
        image = html.xpath(
            './/link[(@rel="apple-touch-icon" or @rel="icon") and @sizes="'
            + str(size) + 'x' + str(size)
            + '"]/@href'
        )[0]
    elif html.xpath('.//link[@rel="shortcut icon"]/@href'):
        image = html.xpath('.//link[@rel="shortcut icon"]/@href')[0]
    else:
        image = ""

    if any([title, description, site_name, image]):
        return {
            "title": title,
            "description": description,
            "site_name": site_name,
            "image": urljoin(url, image),
        }
    else:
        return {}
