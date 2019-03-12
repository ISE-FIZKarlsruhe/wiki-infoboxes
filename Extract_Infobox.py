import re
import mwparserfromhell
import pandas as pd
import fileinput
import argparse

parser = argparse.ArgumentParser(
    description='Extract infoboxes from articles and create csv file with infobox entities '
                'which contain a link + csv file which counts entites')
parser.add_argument('-xml_path', help='Path to xml dump')
parser.add_argument('-info_path', help='Path to infobox file')
parser.add_argument('-comp', help='Path to result file which contains all counter information')
args = parser.parse_args()

wikixml_path = args.xml_path
infobox_path = args.info_path
comp_path = args.comp

def open_wiki_articles(input_path):
    article = ""
    article_list = []
    input = fileinput.FileInput(input_path)
    for line in input:
        while line:
            article += line
            if '</page>' in line:
                article_list.append(article)
                article = ""
    return article_list


def extract_title(article):
    re_title = re.search(r'<title>.*?</title>', article)
    group_title = re_title.group()
    title = group_title.replace('<', '>').split('>')
    return title[2]


def parse_infobox(infobox, title, infofile):
    '''
    parses each infobox.
    :param infobox: the infobox in string form the article
    :param title: the title of the article
    :param infofile: the file in which the result should be written
    :return:
    '''
    infobox_value_counter = 0
    link_counter = 0
    amount_info_values = 0
    entity_list = {}
    infobox_dic = {}
    name = ""
    value = ""

    print('-- Processing article : ' + title)
    amount_info_values = len(infobox[0].params)
    for i in range(0, amount_info_values):
        # counts all infobox names with content (not only those which contain a link)
        if re.match('[^\\n]', str(infobox[0].params[
                                      i].value)) is not None:
            infobox_value_counter += 1
        if '[[' in infobox[0].params[i].value:
            link_counter += 1
            # clear name and value
            name = str(infobox[0].params[i].name)
            value = str(infobox[0].params[i].value)
            name = name.replace('\n', ' ')
            value = value.replace('\n', ' ')
            entity_list.update({name: value})
    infobox_dic.update({title: entity_list})
    infofile.write(str(infobox_dic) + '\n')
    return title, amount_info_values, infobox_value_counter, link_counter


def create_infobox_dic(wikiarticle_path, infobox_path, comp_path):
    '''
    This files runs through all the articles from wikipedia to extract each infobox. The infobox will be written to a file
    in a dictionary format.
    :param wikiarticle_path: the path to the files which contains the wikipedia articles
    :param infobox_path: the path to the location where the file with the infoboxes should be saved
    :param comp_path: the path to the location where the file with the numbers should be saved
    :return:
    '''
    df = pd.DataFrame(
        columns=['article', 'amount_properties', 'amount_entities', 'amount_links', 'amount_link_article_match'])
    article = ""
    infobox_file = open(infobox_path, 'w+')
    print('-- Extracting infoboxes')
    for line in fileinput.input(wikiarticle_path,
                                openhook=fileinput.hook_compressed):  # hook_compressed hook_encoded('cp65001')
        article += line
        if '</page>' in line:
            # start processing infobox
            infobox = mwparserfromhell.parse(article).filter_templates(matches='Infobox .*')
            article_title = extract_title(article)
            if infobox:
                title, counter1, counter2, counter3 = parse_infobox(infobox, article_title, infobox_file)
                df = df.append(
                    {'article': title, 'amount_properties': counter1,
                     'amount_entities': counter2,
                     'amount_links': counter3}, ignore_index=True)
            # end of processing infobox
            article = ""
    df.to_csv(comp_path, sep=';', index=False)
    print('-- Infoboxes extracted and saved in infobox_file')
    return df

