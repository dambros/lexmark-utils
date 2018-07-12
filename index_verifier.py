# -*- coding: utf-8 -*-

import logging.config
import os
import urllib.parse
from collections import defaultdict

import click
import requests

import config

ES_SEARCH_SUFFIX = '/api/{}/search'
SEARCH_SUFFIX = '/spa/#/viewer/{};id={};q={}'
DB_PATTERN = '{document_id} -- {query}'


@click.group()
def cli():
    """
        Script responsible for checking if a new hit was found for the list of
        words previously registered and warn users about it.

            index_verifier.py check

        For detailed help, try this:

            index_verifier.py check --help
    """
    pass


@cli.command()
def check():
    """
    Check EasySearch for hits on the words registered and send emails in case
    something new is found.

    Edit config.py to specify all the required configurations for this script.
    """

    logger.info('Iniciando execução...')
    lines = get_search_words()
    es_url = f'{config.ES_BASE_URL}{ES_SEARCH_SUFFIX.format(config.COLETA)}'

    new_docs = defaultdict(list)
    for line in lines:
        payload = {
            'query': {
                'value': [line]
            }
        }

        r = requests.post(es_url, json=payload)
        if r.status_code != 200:
            raise Exception(f'Problem while POST to Easysearch: {r.reason}')

        content = r.json()
        if content['totalDocs'] > 0:
            documents = content['documents']
            for document in documents:
                value = DB_PATTERN.format(document_id=document['id'],
                                          query=line)
                if not check_message_already_sent(value):
                    new_docs[line].append(document)

    if new_docs:
        send_notification(new_docs)

    logger.info('Execução finalizada!')


def get_search_words():
    return [line.rstrip('\n') for line in open(config.SEARCH_WORD_PATH)]


def check_message_already_sent(value):
    if os.path.isfile(config.DB_PATH):
        with open(config.DB_PATH, 'r') as f:
            documents = f.read().splitlines()
            if value in documents:
                return True

    with open(config.DB_PATH, 'a') as f:
        f.write(f'{value}\n')

    return False


def send_notification(documents):
    requests.post(
        config.MAILGUN_API,
        auth=('api', config.MAILGUN_API_KEY),
        data={'from': config.MAILGUN_FROM,
              'to': config.RECIPIENT_LIST,
              'subject': 'Novas entradas encontradas!',
              'html': build_email_message(documents)})


def build_email_message(documents):
    li_pattern = '<li><a target="_blank" href="{}">{}</a></li>'

    with open('./res/templates/list.html') as l, open(
            './res/templates/template.html') as t:
        list_template = l.read()
        template = t.read()

    li_templates = []
    for query, items in documents.items():
        encoded_query = urllib.parse.quote_plus(query)

        li = []
        for item in items:
            link = config.ES_BASE_URL + SEARCH_SUFFIX.format(
                config.COLETA, item['id'], encoded_query)

            for field in item['fields']:
                if field['name'] == 'Nome do arquivo':
                    li_item = li_pattern.format(link, field['value'])
                    li.append(li_item)
                    break

        li_str = ''.join(li)
        li_templates.append(
            list_template.format(query=query, link_list=li_str))

    lists = ''.join(li_templates)
    return template.format(query_list=lists)


if __name__ == "__main__":
    logging.config.fileConfig(config.LOG_CONFIG_PATH)
    logger = logging.getLogger(os.path.basename(__file__))
    cli()
