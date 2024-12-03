#!/usr/bin/env python3

import re
import os
import pdfx 
import lxml
import requests
import time
import random
import logging
import argparse
from bs4 import BeautifulSoup
import pandas as pd


# used fns
def coerce_into_string(a_list: list, a_string: str = ' ') -> str:
    text = [element.text for element in a_list]
    return a_string.join(text).strip().replace('\n \n', ', ')


def remove_nwln(a_text: str, a_string: str = '', repla: str ='') -> str:
    return a_string.join(a_text).replace('\n', repla)


def detect_body(url: str) -> str:
    bodyRegx = re.compile(r'senate|house')
    return bodyRegx.search(url).group().title()


def xml_parse_append(xml_data: bytes, curr_url: str, a_dataframe: pd.DataFrame) -> pd.DataFrame:


    try: # get xml schema
        table = BeautifulSoup(xml_data, 'xml').find('MEMBINFO')


        # extract elements 
        name = table.find('DISP_NAME').text
        body = detect_body(curr_url)
        party = table.find('PARTY').text
        leg_exp = coerce_into_string(table.find_all('LEG_EXP'))
        education = coerce_into_string(table.find_all('EDUCATION'))
        occupation = coerce_into_string(table.find_all('OCCUPATION'))
        committees = coerce_into_string(table.find_all('CMTE_NAME'))
        organizations_info = remove_nwln(table.find('ORG_INFO').text, repla = ' ')
        personal_info = remove_nwln(table.find('PERS_INFO').text, repla = ' ')


        # Adding extracted elements to rows in table
        curr_row = {
                'Legislator': name, 
                'Body': body,
                'Party': party,
                'LegislativeExp': leg_exp,
                'Education': education,
                'Occupations': occupation,
                'Commitees': committees,
                'Organizations': organizations_info,
                'Personal': personal_info,
                'url': curr_url
            }


        print(f'Now appending: {curr_row}')


    except AttributeError as err:


        print(str(err))
        print(f'Failed to scrappe {curr_url}. Filling rows as NA.')
        curr_row = {
                'Legislator': 'NA', 
                'Body': 'NA',
                'Party': 'NA',
                'LegislativeExp': 'NA',
                'Education': 'NA',
                'Occupations': 'NA',
                'Commitees': 'NA',
                'Organizations': 'NA',
                'Personal': 'NA',
                'url': curr_url
                }
        pass


    except Exception as err:
        logging.exception(err)
        pass


    a_dataframe = pd.concat([a_dataframe, pd.DataFrame([curr_row])], ignore_index=True)
    return a_dataframe    
    

def main() -> None:
    inpt = os.path.join(*args.input)
    outp = os.path.join(*args.output)


    # get links from pdf
    pdf = pdfx.PDFx(f'{inpt}')


    # list
    urls = pdf.get_references_as_dict()['url']


    # get rid of diferent-structured pages
    discard = ['https://ltgovhosemann.ms.gov/', 'https://www.legislature.ms.gov/legislators/senators/', 'https://www.legislature.ms.gov/legislators/representatives/']


    urls = list(filter(lambda url: url not in discard, urls))


    if args.save_list:
        with open('links.txt', 'w') as file:
            file.write(' \n'.join(urls))
            file.close()

    
    # set up request
    user = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36'}


    # init dataframe
    data = pd.DataFrame(columns=['Legislator', 'Body', 'Party', 'LegislativeExp', 'Education', 'Occupations', 'Commitees', 'Organizations', 'Personal'])


    for index, url in enumerate(urls):
        

        print(f'Scrapping {index+1} of {len(urls)} urls')     
        xml_data = requests.get(url, headers = user).content
        data = xml_parse_append(xml_data, url, data)
        randomly_await = random.randint(3,14)
        print(f"Ok. Now sleeping for {randomly_await} secs.")
        time.sleep(randomly_await)


    print('Done.')


    # save
    data.to_csv(f'{outp}')


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='A script to scrape MS Legislature bio data')
    parser.add_argument('-in', '--input', nargs='+', help='A pdf file containing the links to scrape.')
    parser.add_argument('-o', '--output', type=str, nargs='+', help='Name and path of the output file. Must be a csv file.')
    parser.add_argument('-s', '--save-list', type=bool, nargs='?', default=True, help='Save txt list of urls, default behavior.')
    args = parser.parse_args()
    main()


