"""API to Sodexo."""
import datetime

import aiohttp
import logging
import json
from bs4 import BeautifulSoup

from .const import LOGIN_URL, LUNCH_PASS_SELECTOR, ECO_PASS_SELECTOR, GIFT_PASS_SELECTOR
from .lib import AccountDetails, parse_html

_LOGGER = logging.getLogger(__name__)
_LOGGER.setLevel(logging.DEBUG)


class SodexoAPI:
    """Interfaces to https://sodexo4you.be/"""
    
    def __init__(self, websession):
        self.websession = websession
        self.json = None

    async def login(self, username, password):
        """Issue LOGIN request."""
        try:
            _LOGGER.debug("Logging in...")
            async with self.websession.get(
                LOGIN_URL, 
            ) as res:
                if res.status == 200 and res.content_type == "text/html":
                    text = await res.text()
                    soup = BeautifulSoup(text, 'html.parser')
                    xsrfToken = soup.select_one('#account-login > input[type=hidden]:nth-child(3)')
                    payload = {'op': 'Se connecter', 'name': username, 'pass': password, 'form_id': 'user_login_block', 'form_build_id': xsrfToken}
                async with self.websession.post(
                        LOGIN_URL,
                        data=payload
                ) as loggedPage:
                    text = await loggedPage.text()
                    return 'ok';
                raise Exception("Could not retrieve token for user, login failed")
        except aiohttp.ClientError as err:
            _LOGGER.exception(err)
    
    async def getAccountDetails(self) -> AccountDetails:
        """Issue ACCOUNT DETAILS requests."""
        try:
            _LOGGER.debug("Getting account details...")
            async with self.websession.get(
                LOGIN_URL,
            ) as res:
                if res.status == 200 and res.content_type == "text/html":
                    html = await res.text()
                    soup = BeautifulSoup(html, 'html.parser')

                    lunch = float(soup.select_one(LUNCH_PASS_SELECTOR).text.replace(' €', ''))
                    eco = float(soup.select_one(ECO_PASS_SELECTOR).text.replace(' €', ''))
                    gift = float(soup.select_one(GIFT_PASS_SELECTOR).text.replace(' €', ''))
                    return AccountDetails(lunch, eco, gift, datetime.datetime.now().strftime("%d/%m/%Y %H:%M"));
                raise Exception("Could not retrieve account information from API")
        except aiohttp.ClientError as err:
            _LOGGER.exception(err)