import Extract_Infobox
import pandas as pd
import datetime
import re
import argparse
import time

# get articles (as concatenated string) from the triple file matching with the infobox article name
def get_article_triple_file(article_name, t_file):
    t_file.seek(0)
    article_as_string = ""
    article_name = article_name.replace(' ', '_')
    t_line = t_file.readline()
    while t_line:
        if article_name in t_line:
            article_as_string += t_line
            t_line = t_file.readline()
        elif article_as_string:
            break
        else:
            t_line = t_file.readline()
    return article_as_string


# parser = argparse.ArgumentParser()
# parser.add_argument('-xml', help='test')
# parser.add_argument('-c', '--crawler', help='triple file path')
# parser.add_argument('-info', help='Path to infobox file 697898 9')
# parser.add_argument('-comp', help='Path to result file which contains all counter information 897987897')
# parser.add_argument('-r', '--result', help='result file')
# args = parser.parse_args()

wikixml_path = '../../wikipedia20180401/wikipart_5/enwiki_1000069.xml' # args.xml
infobox_path = '../../infoboxes/infobox_file/res/2501_infobox_1000069.txt' # args.info
wikitriple_path = '../../wikipedia20180401/RES_1000069/wiki_triples.txt' # args.crawler
result_path = '../../infoboxes/result_infoboxes/res/2501_result_1000069.csv' # args.result
comp_path = '../../infoboxes/comp_infoboxes/res/2501_comp_1000069.csv' # args.comp

start = time.time()
'''
start running this script: it starts with extracting the infoboxes from the articles (in Extract_Infobox.create_infobox_dic)
and gives back a file, which contains the infobox information about each article.
In the following script the file with the infobox information from the previous method is compared with the file from last
semester which contains all links from each article. The matches of both files will be written to a result file.
Furthermore another csv file is written which contains the counters for the articles to compute the statistics.
'''

df_comp = Extract_Infobox.create_infobox_dic(wikixml_path, infobox_path, comp_path)
with open(wikitriple_path) as triple_f:  # , encoding='cp65001'
    with open(infobox_path) as infobox_f:
        df = pd.DataFrame(columns=['Article', 'Infobox_property', 'Link',
                                   'Sentence'])  # contains articles with infoboxes, and those entities which are links and were found in the article as links
        print('-- Start to compare the Infoboxes')
        # iterate through infoboxes
        infobox_f_line = infobox_f.readline()
        while infobox_f_line:
            article = list(eval(infobox_f_line).keys())[0]  # get first article of the infoboxes
            article_from_triple = get_article_triple_file(article,
                                                          triple_f)  # continue only if article could be found in the triple file
            # print('-- Processing infobox: ' + article)
            value_link_match_counter = 0
            if article_from_triple:
                infobox_value_list = list(eval(infobox_f_line)[article])
                while infobox_value_list:
                    plain_infobox_value = eval(infobox_f_line)[article][
                        infobox_value_list[0]]  # first infobox entity value out of list
                    entities_re = re.findall(r'(\[\[.*?\]\])',
                                             plain_infobox_value)  # get entity out of infobox entity value
                    #  if several entities are combined in one infobox entity value
                    for infobox_entity in entities_re:
                        infobox_entity = infobox_entity.replace('[[', '').replace(']]', '')
                        if "|" in infobox_entity:  # if shadowing
                            infobox_entity = re.match(r'(.*?)(\|)', infobox_entity)
                            infobox_entity = infobox_entity.group().replace('|', '')
                        # infobox_entity_undsco = re.sub(r"(.)([A-Z])", r"\1_\2", infobox_entity)
                        infobox_entity_undsco = infobox_entity.replace(' ', '_')
                        print('-- Processing infobox: ' + article + ' with entity: ' + infobox_entity_undsco)
                        try:
                            match_re = re.search(r'(<.*/' + infobox_entity_undsco + '>).*', article_from_triple, # replace with if string in string ? - but how dealing with lower and upper case
                                             re.IGNORECASE)
                        except re.error as err:
                            print('ERROR: ' + str(err))
                            print('ERROR PATTERN: ' + str(err.pattern))
                            print('ERROR INDEX POSITION: ' + str(err.pos))
                        if match_re:
                            value_link_match_counter += 1
                            match = match_re.group()
                            df = df.append({'Article': article, 'Infobox_property': infobox_value_list[0],
                                            'Link': infobox_entity_undsco.replace('_', ' '),
                                            'Sentence': match.replace('>', '/').split('/')[10]},
                                           ignore_index=True)
                    infobox_value_list.pop(0)
            index_co = df_comp.index[df_comp['article'] == article].tolist()[0]
            df_comp.loc[index_co, 'amount_link_article_match'] = value_link_match_counter
            infobox_f_line = infobox_f.readline()
df.to_csv(result_path, sep=';', index=False)
df_comp.to_csv(comp_path, sep=';', index=False)
