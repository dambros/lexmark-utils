# -*- coding: utf-8 -*-

import glob
import logging.config
import os
import re
import subprocess
from xml.dom.minidom import parseString

import click
import dicttoxml

import config


@click.group()
def cli():
    """
    Requires ImageMagick installed!

    Script responsible for merging scanned tif files into a single pdf one
    and link the appropriate properties to its pdf, by transforming it into
    a xml.

           file_merger.py merge -c CONVERT_PATH

       For detailed help, try this:

           file_merger.py merge --help
       """
    pass


@cli.command()
@click.option(
    '--convert-path', '-c',
    default='/usr/local/bin/convert',
    help='ImageMagick\'s convert path',
    type=click.Path()
)
def merge(convert_path):
    """
    Merge files and generates XML. Example usage:

    file_merger.py merge --convert-path /opt/convert
    """

    logger.info('Iniciando execução...')
    tif_path = get_path(config.MFP_FOLDER_PATH, 'tif')
    tif_files = glob.glob(tif_path)
    properties_path = get_path(config.MFP_FOLDER_PATH, 'properties')
    properties_files = glob.glob(properties_path)

    if tif_files and properties_files:
        convert_files(convert_path, tif_files, properties_files)

    logger.info('Execução finalizada!')


def convert_files(convert_path, tif_files, properties_files):
    clean_tif_files = [os.path.basename(x) for x in tif_files]
    tif_filenames = get_unique_filenames_without_pages(clean_tif_files)
    for tif in tif_filenames:
        props = get_props(properties_files, tif)
        page_count = get_current_page_count(clean_tif_files, tif)

        if not props or page_count != int(props[1]['NumPages']):
            r = re.compile(f'.*{tif}_[0-9]*.tif')
            tif_files = [x for x in tif_files if not r.match(x)]

            if props:
                properties_path = props[0]
                r = re.compile(properties_path)
                properties_files = [x for x in properties_files if
                                    not r.match(x)]
        else:
            generate_xml(properties_files, tif)
            docs_pattern = f'{tif}_*.tif'
            new_filename = f'{config.OCR_FOLDER_PATH}/{tif}.pdf'
            cmd = [convert_path, docs_pattern, new_filename]
            subprocess.call(cmd, cwd=config.MFP_FOLDER_PATH, shell=False)

    delete_files(tif_files)
    delete_files(properties_files)


def get_current_page_count(docs, name):
    r = re.compile(f'{name}_[0-9]*.tif')
    result = list(filter(r.match, docs))
    return len(result)


def get_props(properties_files, name):
    for properties_file in properties_files:
        props = load_properties(properties_file)
        if props['PageFilenameBase'] == name:
            return properties_file, props
    return None


def generate_xml(properties_files, name):
    for properties_file in properties_files:
        props = load_properties(properties_file)
        if props['PageFilenameBase'] == name:
            xml = dicttoxml.dicttoxml(props, attr_type=False)
            dom = parseString(xml)
            filename = f'{config.OCR_FOLDER_PATH}/{name}.xml'
            write_file(filename, dom.toprettyxml())
            return


def write_file(filename, content):
    with open(filename, 'w') as file:
        file.write(content)
        file.close()


def delete_files(file_path_list):
    for file in file_path_list:
        if os.path.isfile(file):
            os.remove(file)
        else:
            logger.warning("Error: %s file not found" % file)


def get_path(folder, extension):
    path = f'{folder}/*.{extension}'
    return path


def get_unique_filenames_without_pages(files):
    name_pattern = '_[^_]+$'
    filenames = set()
    for file in files:
        name = re.sub(name_pattern, '', file)
        filenames.add(name)

    return filenames


def load_properties(filepath, sep='=', comment_char='#'):
    props = {}
    with open(filepath, "rt") as f:
        for line in f:
            l = line.strip()
            if l and not l.startswith(comment_char):
                key_value = l.split(sep)
                key = key_value[0].strip()
                value = sep.join(key_value[1:]).strip().strip('"')
                props[key] = value
    return props


if __name__ == "__main__":
    logging.config.fileConfig(config.LOG_CONFIG_PATH)
    logger = logging.getLogger(os.path.basename(__file__))
    cli()
