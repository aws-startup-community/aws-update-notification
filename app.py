from chalice import Chalice, Rate
from aws_lambda_powertools import Logger
import feedparser
import requests
import json
from bs4 import BeautifulSoup
from datetime import datetime, timedelta, timezone
import boto3

logger = Logger()

RATE_HOUR = 1
BOT_NAME = 'aws-update-notification'
RSS_URL = 'https://aws.amazon.com/about-aws/whats-new/recent/feed/'
CHANNEL_MAPPINGS = {
    'analytics': {
        'marchitecture': ['analytics'],
        'products': []
    },
    'containers': {
        'marchitecture': ['containers'],
        'products': ['amazon-ecs', 'amazon-eks', 'amazon-ecr', 'aws-app-mesh', 'aws-cloud-map', 'aws-copilot', 'aws-app-runner']
    },
    'frontend': {
        'marchitecture': [],
        'products': ['aws-amplify']
    },
    'iot': {
        'marchitecture': ['internet-of-things'],
        'products': []
    },
    'machine-learning':{
        'marchitecture': ['artificial-intelligence'],
        'products': ['sagemaker']
    },
}

def get_parameters(path='/'):
    params = {}
    ssm = boto3.client('ssm')
    res = ssm.get_parameters_by_path(Path=path)
    for parameter in res['Parameters']:
        key = parameter['Name'].replace(path, '')
        val = parameter['Value']
        params[key] = val
    return params

def gen_payload(entry, products, marchitecture, target='discord'):
    if len(entry.summary) > 0:
        translated_summary = translate.translate_text(
            Text=BeautifulSoup(entry.summary,"html.parser").get_text(),
            SourceLanguageCode='en',
            TargetLanguageCode='ja'
        )['TranslatedText']
    else:
        translated_summary = ''
    if target == 'discord':
        embeds = [
            {
                'title': entry.title,
                'description': translated_summary,
                'url': entry.link,
                'footer': {
                    'text': entry.updated
                },
                "fields": [
                    {
                        'name': "Product",
                        'value': ', '.join(products),
                        'inline': True
                    },
                    {
                        'name': 'Marchitecture',
                        'value': ', '.join(marchitecture),
                        'inline': True
                    },
                ]
            }
        ]
        payload = {'username': BOT_NAME, 'embeds': embeds}
    else:
        payload = {'content': entry.link}
    return payload

discord_webhooks = get_parameters(path='/startup-community/discord/webhooks/')

translate = boto3.client('translate')

app = Chalice(app_name='aws-update-notification')

# Automatically runs every 1 hour
@app.schedule(Rate(RATE_HOUR, unit=Rate.HOURS))
def check_news(event):
    event_time = datetime.strptime(event.time, '%Y-%m-%dT%H:%M:%S%z')
    try:
        feed = feedparser.parse(RSS_URL)
    except expression as e:
        logger.error(e)
    for entry in feed.entries:
        entry_date = datetime.strptime(entry.updated, '%a, %d %b %Y %H:%M:%S %z')
        if event_time - timedelta(hours=RATE_HOUR) <= entry_date < event_time and len(entry.tags) > 0:
            tag = entry.tags[0]
            products = []
            use_case = []
            marchitecture = []
            industry = []
            # "term": "marketing:marchitecture/networking-and-content-delivery,general:products/amazon-route-53" の様に入ってるのでバラす
            for term in tag.term.split(','):
                if term.startswith('general:products/'):
                    products.append(term.replace('general:products/', ''))
                elif term.startswith('general:use-case/'):
                    use_case.append(term.replace('general:use-case/', ''))
                elif term.startswith('marketing:marchitecture/'):
                    marchitecture.append(term.replace('marketing:marchitecture/', ''))
                elif term.startswith('marketing:industry/'):
                    industry.append(term.replace('marketing:industry/', ''))
                else:
                    logger.warn({
                        'msg': 'Unexpected tag',
                        'tag': tag.term,
                        'entry': entry,
                    })

            headers = {'Content-Type': 'application/json'}
            payload = gen_payload(entry, products, marchitecture, target='discord')

            # カテゴリ別
            post_flag = False
            for channel_name in CHANNEL_MAPPINGS.keys():
                marchitecture_intersection = set(marchitecture) & set(CHANNEL_MAPPINGS[channel_name]['marchitecture'])
                products_intersection = set(products) & set(CHANNEL_MAPPINGS[channel_name]['products'])
                if len(marchitecture_intersection) > 0 or len(products_intersection) > 0:
                    if channel_name in discord_webhooks:
                        webhook_url = discord_webhooks[channel_name]
                        res = requests.post(webhook_url, data=json.dumps(payload), headers=headers)
                        post_flag = True
                    else:
                        logger.error({
                            'msg': f'"{channel_name}" not in SSM Parameter Store',
                            'channel_name': channel_name,
                            'payload': payload,
                        })
            if not post_flag:
                if 'default' in discord_webhooks:
                    webhook_url = discord_webhooks['default']
                    res = requests.post(webhook_url, data=json.dumps(payload), headers=headers)
                else:
                    logger.error({
                        'msg': '"default" not in SSM Parameter Store',
                    })
    return {}
