from email.policy import strict
from posixpath import split
from pdfquery import PDFQuery
import re
from collections import defaultdict
import PyPDF2
import os
import sys
import datetime
from dateutil import parser

from pdfminer.pdfinterp import PDFResourceManager, PDFPageInterpreter
from pdfminer.converter import TextConverter
from pdfminer.layout import LAParams
from pdfminer.pdfpage import PDFPage
from pdfminer.pdfinterp import resolve1
from pdfminer.pdfparser import PDFParser
from pdfminer.pdfdocument import PDFDocument
from pdfminer.pdfpage import PDFTextExtractionNotAllowed
from pdfminer.pdfdevice import PDFDevice
from pdfminer.converter import PDFPageAggregator
import pdfminer
from io import StringIO
import regex
import pandas as pd

##########################################
# Need to throw error messages for debugging purposes. Split the __init__ try
# into multiple with error msgs.
##########################################

#########################
# Error classes


class PDFQuerryLoadError(Exception):
    pass


class AcctSearcherInitError(Exception):
    pass


#########################

class acct_searcher:
    def __init__(self, filename=None, bank=None):
        """

        :param filename: 
        :bank from          
                            "Ameritrade",                            
                            "Asset Mark Combined",
                            "Asset Mark Combined Holdings",
                            "Bok Financial",
                            "Bok Holdings",
                            "Bok Transactions",
                            "Comerica",
                            "Delaware Trust",
                            "Delaware Trust Multi",
                            "First Midwest",
                            "Fifth Third Bank",
                            "Ford",
                            "Honda Funds Held",
                            "Raymond James",
                            "Raymond James Combined",
                            "Raymond James Holdings",
                            "Raymond James Transactions",
                            "Regions",
                            "Reinsurance Max",
                            "Summit Wealth",
                            "SunTrust",
                            "Suntrust Reduced",
                            "SunTrust Holdings",
                            "SunTrust Transactions",
                            "Truist",
                            "Truist Reduced",
                            "Truist Holdings",
                            "Truist Transactions",
                            "UBS",
                            "UMB Bank",
                            "US Bank",
                            "US Bank Holdings",
                            "US Bank Transactions",
                            "Wells Fargo",
                            "Whitney Bank",
                            "Wilmington Trust"

        """
        if filename is not None and bank is not None:
            if not os.path.exists(filename):
                raise FileNotFoundError(f'File ({filename}) is not found.')

            try:

                self.filename = filename
                self.load_profiles()
                self.bank = bank
                self.text = ''
                if self.bank not in self.profiles:
                    raise Exception(f'Bank {self.bank} profile is not available. ')

            except:
                print(f'Failed to initialize class with specified parameters bank = {bank}, filename = {filename}, error {sys.exc_info()[0]}')

    def load_profiles(self):
        self.profiles = {
                            "Ameritrade",
                            "Asset Mark Combined",
                            "Asset Mark Combined Holdings",                            
                            "Bok Financial",
                            "Bok Holdings",
                            "Bok Transactions",
                            "Comerica",
                            "Delaware Trust",
                            "Delaware Trust Multi",
                            "First Midwest",
                            "Fifth Third Bank",
                            "Ford",
                            "Honda Funds Held",
                            "Raymond James",
                            "Raymond James Combined",
                            "Raymond James Holdings",
                            "Raymond James Transactions",
                            "Regions",
                            "Reinsurance Max",
                            "Summit Wealth",
                            "SunTrust",
                            "Suntrust Reduced",
                            "SunTrust Holdings",
                            "SunTrust Transactions",
                            "Truist",
                            "Truist Reduced",
                            "Truist Holdings",
                            "Truist Transactions",
                            "UBS",
                            "UMB",
                            "UMB Bank",
                            "US Bank",
                            "US Bank Holdings",
                            "US Bank Transactions",
                            "Wells Fargo",
                            "Whitney Bank",
                            "Wilmington Trust"
                         }

    def convert_pdf_to_txt(self, page_num_list=None):
        try:
            with open(self.filename, 'rb') as f:
                if page_num_list == None:
                    parser = PDFParser(f)
                    doc = PDFDocument(parser)
                    parser.set_document(doc)
                    pages = resolve1(doc.catalog['Pages'])
                    numpages = pages.get('Count', 0)
                    page_num_list = list(range(numpages))

                output = StringIO()
                manager = PDFResourceManager()
                converter = TextConverter(manager, output, laparams=LAParams())
                interpreter = PDFPageInterpreter(manager, converter)

                for page_content in PDFPage.get_pages(f, page_num_list):#range(numpages)):
                    interpreter.process_page(page_content)
                
                converter.close()
                text = output.getvalue()
                output.close()
                text = repr(text)
                # print(text)
            return text
        except:
            return None   

    def convert_pdf_to_txt_with_page(self):
        with open(self.filename, 'rb') as f:

            parser = PDFParser(f)
            doc = PDFDocument(parser)
            parser.set_document(doc)
            pages = resolve1(doc.catalog['Pages'])
            numpages = pages.get('Count', 0)
            page_num_list = list(range(numpages))

            text_by_page = [{'text':'', 'page':-1}]*len(page_num_list) # pre-initialize to speed things up

            output = StringIO()
            manager = PDFResourceManager()
            converter = TextConverter(manager, output,laparams=LAParams())
            interpreter = PDFPageInterpreter(manager, converter)

            for ii,page_content in enumerate(PDFPage.get_pages(f, range(numpages))):#range(numpages)):
                interpreter.process_page(page_content)
                text = output.getvalue()
                text_by_page[ii] = {'text':repr(text), 'page':ii}
                output.truncate(0)
                output.seek(0)

            output.close()
            converter.close()
        return text_by_page


    def convert_pdf_to_txt_PDFQuery(self, page_list = None, PDFQueryObj = None):

        text = []
        if PDFQueryObj is None:
            PDFQueryObj = PDFQuery(self.filename)
        if page_list == None:
            page_list = range(PDFQueryObj.doc.catalog['Pages'].resolve()['Count'])

        for page in page_list:
            PDFQueryObj.load(page)
            root = PDFQueryObj.tree.getroot()
            text_ = [node.text for node in root.iter() if node.text is not None]
            if text_ == []:  # no text found on page -> go to next page
                continue
            else:
                text += text_
        PDFQueryObj.file.close()
        return text

    def convert_pdf_to_txt_PDFQuery_with_page_pos(self, page_list = None, PDFQueryObj = None):

        text = []
        if PDFQueryObj is None:
            PDFQueryObj = PDFQuery(self.filename)
        if page_list == None:
            page_list = range(PDFQueryObj.doc.catalog['Pages'].resolve()['Count'])

        for page in page_list:
            PDFQueryObj.load(page)
            root = PDFQueryObj.tree.getroot()
            for node in root.iter():
                if node.text:
    #                 print(node)
                    text += [{'text':node.text, 'bbox':list(node.layout.bbox), 'page': page}]# for node in root.iter() if node.text is not None]_
        PDFQueryObj.file.close()
        return text

    def convert_pdf_to_text_pypdf2(self):
        """extracts just page 0 currently"""
        try:
            with open(self.filename, mode='rb') as f:
                reader = PyPDF2.PdfFileReader(f)
                page = reader.getPage(0)
                text = page.extractText()
            return text
        except:
            return None

    def convert_pdfminer_w_position(self):
    # Open a PDF file.
    # with open('./HCIC 1117 Re 01.23.2020 Cession Statement.pdf', 'rb') as fp:
        with open(self.filename, 'rb') as fp:
        # fp = open('/Users/me/Downloads/test.pdf', 'rb')

            # Create a PDF parser object associated with the file object.
            parser = PDFParser(fp)

            # Create a PDF document object that stores the document structure.
            # Password for initialization as 2nd parameter
            document = PDFDocument(parser)

            # Check if the document allows text extraction. If not, abort.
            if not document.is_extractable:
                raise PDFTextExtractionNotAllowed

            # Create a PDF resource manager object that stores shared resources.
            rsrcmgr = PDFResourceManager()

            # Create a PDF device object.
            device = PDFDevice(rsrcmgr)

            # BEGIN LAYOUT ANALYSIS
            # Set parameters for analysis.
            laparams = LAParams()

            # Create a PDF page aggregator object.
            device = PDFPageAggregator(rsrcmgr, laparams=laparams)

            # Create a PDF interpreter object.
            interpreter = PDFPageInterpreter(rsrcmgr, device)

            def parse_obj(lt_objs, ii):
                elts = []
                parsedElts = []
                # loop over the object list
                for obj in lt_objs:

                    # if it's a textbox, print text and location
                    if isinstance(obj, pdfminer.layout.LTTextBoxHorizontal):
                        ###This commented out code is to use the PDFScraper class if desired at some later point
    #                     print("%6d, %6d, %s" % (obj.bbox[0], obj.bbox[1], obj.get_text().replace("\n","_")))
    #                     new_elt = text_elt.text_elt()
    #                     new_elt.text = obj.get_text().strip()
    #                     new_elt.bbox = [obj.bbox[0], obj.bbox[1], obj.bbox[2], obj.bbox[3]]
    #                     new_elt.x0=new_elt.bbox[0]
    #                     new_elt.x1=new_elt.bbox[2]
    #                     new_elt.y0 = new_elt.bbox[1]
    #                     new_elt.y1 = new_elt.bbox[3]
    #                     new_elt.page = ii
    #                     elts += [new_elt]
                        obj.page = ii
                        parsedElts += [obj]
                        # {'text':obj.get_text().strip(), 'x0':obj.bbox[0], 'x1':obj.bbox[2], 'y0':obj.bbox[1], 'y1':obj.bbox[3], 'page':ii}]

                    # if it's a container, recurse
                    elif isinstance(obj, pdfminer.layout.LTFigure):
                        parse_obj(obj._objs, ii)

                return elts, parsedElts
    #         all_text_elts = []
            all_pdfminer_elts = []
            # loop over all pages in the document
            for ii, page in enumerate(PDFPage.create_pages(document)):

                # read the page into a layout object
                interpreter.process_page(page)
                layout = device.get_result()

                # extract text from this object
                parsed_objs = parse_obj(layout._objs, ii)
    #             all_text_elts += parsed_objs[0]
                all_pdfminer_elts += parsed_objs[1]
        return  all_pdfminer_elts #,all_text_elts

    def convert_pdf_to_text_with_page_pypdf2(self):
        file_contents = []
        contents = ''
        with open(self.filename, 'rb') as pdffile:
            pdfReader = PyPDF2.PdfFileReader(pdffile)
            count = pdfReader.numPages
            
            for i in range(count):
                page = pdfReader.getPage(i)
                page_contents = page.extractText() 
                contents += page_contents
                file_contents += [{'page':i, 'text':page_contents}]

        return file_contents, contents, count

    def combine_pages(self, results_list):
        
        # _res = [a for a in results_list if a['acct_no'] is not None]
        _res = [a for a in results_list if a['acct_no'] is not None or a['company_name'] is not None]
        temp = [[a['acct_no'], a['company_name'], a['date1'], a['date2'], a['_date1'], a['_date2'], []] for a in _res]
        unique = []
        for a in temp:
            if a in unique:
                pass
            else:
                unique +=  [a]

        for uelt in unique:
            for elt in _res:
                if elt['acct_no'] == uelt[0] and elt['company_name'] == uelt[1] and elt['date1']== uelt[2] and elt['date2'] == uelt[3]:
                    uelt[6]+= [elt['page']]
        unique_dict = [{'acct_no': a[0], 'company_name':a[1], 'date1': a[2], 'date2': a[3], '_date1': a[4], '_date2': a[5],'page':a[6]} for a in unique]
        return unique_dict


    def remove_ltd(self, string):
        to_replace = re.compile('(LTD|LTD\.|Limited)$', re.IGNORECASE)
        company = re.sub(to_replace, '', string.strip()).strip()

        last_word = company.split(' ')[-1]
        if last_word.lower() in ['l','lt', 'ltd','ltd.']:
            company = ' '.join(company.split(' ')[:-1]).strip()
        if company[-1] in [',','.']:
            company = company[:-1]
        return company
        

    # def remove_ltd(self, string):
        
    #     if re.search(r'LTD(.){0,1}$',string, re.IGNORECASE):
    #         company = re.sub(re.compile('LTD(.){0,1}$', re.IGNORECASE), '', string).strip()
    #         if company[-1] in [',','.']:
    #             company = company[:-1]
    #         return company
    #     else:
    #         return string

    def format_date_as_string(self, year, month):
        if month < 10:
            month_str = '0'+str(month)
        else:
            month_str = str(month)
        year_str = str(year)
        return year_str+'_'+month_str

    def get_eom_from_year_month(self, year, month):
        last_day_list = [31,30,29,28]
        for day in last_day_list:
            try:
                newdate = datetime.date(year, month, day)
                return newdate
            except:
                pass
        return None



    # This is currently not in TK's list of banks but leaving code here anyway.
    def Key_Private_Bank(self):
        return_list = []

        try:
            self.text = self.convert_pdf_to_txt([1])
            for page in self.text:
                try:
                    split_text = [line.strip() for line in page['text'].split('\\n') if line.strip() != '']

                    acct_regex = re.compile(r'(?<=242-)[0-9]{3,10}')
                    date_regex = re.compile(r'[0-9]{2}/[0-9]{2}/[0-9]{4}')

                    dates = [a for a in split_text if re.search(date_regex, a)]
                    _acct = [a for a in split_text if re.search(acct_regex, a)][0]

                    acct = re.findall(acct_regex, _acct)[0]
                    dates = [parser.parse(a) for a in dates]
                    if dates[0]<dates[1]:
                        _date1 = dates[0]
                        _date2 = dates[1]
                    else:
                        _date1=dates[1]
                        _date2=dates[0]
                    date1 = self.format_date_as_string(_date1.year, _date1.month)
                    date2 = self.format_date_as_string(_date2.year, _date2.month)
                    return_list += [{'acct_no':acct, 'company_name': None, 'date1':date1, 'date2': date2, '_date1':_date1, '_date2':_date2, 'page':page}]
                except:
                    pass
            df = pd.DataFrame(return_list).fillna('None')\
                .groupby(['acct_no','company_name','date1','date2','_date1','_date2'])['page']\
                .apply(list)\
                .to_frame()\
                .reset_index()\
                .applymap(lambda x: None if x == 'None' else x)
            # print(df)      
            df_dict = df.to_dict('records')
            return df_dict

        except:
            return None 


    def Reinsurance_Max(self):
        return_list = []

        try:
            self.text = self.convert_pdf_to_txt_with_page()
            # print(self.text)
            for page in self.text:
                try:
                    split_text = [line.strip() for line in page['text'].split('\\n') if line.strip() != '']
                    
                    _acct = [a.strip() for a in split_text if re.search('[0-9a-z]{3}-[0-9a-z]{6}', a, re.IGNORECASE)][0]
                    acct = re.search('[0-9a-z]{3}-[0-9a-z]{6}', _acct, re.IGNORECASE).group(0)
                    
                
                    _dates = re.search(r'(?<=PERIOD)\s(\D{3,9}\s*[0-9]{1,2},\s*20[0-9]{2})\s*to\s*(\D{3,9}\s*[0-9]{1,2},\s*20[0-9]{2})', page['text'], re.IGNORECASE)
                    _date1 = parser.parse(_dates.group(1))
                    _date2 = parser.parse(_dates.group(2))
                    date1 = self.format_date_as_string(_date1.year, _date1.month)
                    date2 = self.format_date_as_string(_date2.year, _date2.month)
                    # print(_dates, _date1, _date2)
            
                    return_list += [{'acct_no':acct, 'company_name':None, 'date1': date1, 'date2':date2, '_date1':_date1, '_date2':_date2,'page':page['page']}]
                except:
                    pass
            df = pd.DataFrame(return_list).fillna('None')\
                .groupby(['acct_no','company_name','date1','date2','_date1','_date2'])['page']\
                .apply(list)\
                .to_frame()\
                .reset_index()\
                .applymap(lambda x: None if x == 'None' else x)
            # print(df)      
            df_dict = df.to_dict('records')

            return df_dict
        except:
            return None

    # This is currently not in TK's list of banks but leaving code here anyway.
    def First_Bank_of_Tennessee(self):
        try:
            return_list = []
            self.text = self.convert_pdf_to_txt_with_page()
            for page in self.text:
                try:
                    split_text = [line.strip() for line in page['text'].split('\\n') if line.strip() != '']
                    _acct = [a.strip() for a in split_text if re.search('[0-9]{10}', a, re.IGNORECASE)][0]
                    acct = re.search('[0-9]{10}', _acct, re.IGNORECASE).group(0)

                    _dates = [a for a in split_text if re.search(r'statement:\s*\D{3,9}\s*[0-9]{1,2},\s*20[0-9]{2}', a, re.IGNORECASE)]
                    _date_list = [a.split(":")[1].strip() for a in _dates]
                    _date1 = parser.parse(_date_list[0])
                    _date2 = parser.parse(_date_list[1])

                    if _date1 > _date2:
                        temp_date = _date1
                        _date1 = _date2
                        _date2 = temp_date

                    date1 = self.format_date_as_string(_date1.year, _date1.month)
                    date2 = self.format_date_as_string(_date2.year, _date2.month)
                    return_list += [{'acct_no':acct, 'company_name':None, 'date1': date1, 'date2':date2, '_date1':_date1, '_date2':_date2,'page':page['page']}]
                except:
                    pass
            df = pd.DataFrame(return_list).fillna('None')\
                .groupby(['acct_no','company_name','date1','date2','_date1','_date2'])['page']\
                .apply(list)\
                .to_frame()\
                .reset_index()\
                .applymap(lambda x: None if x == 'None' else x)
            # print(df)      
            df_dict = df.to_dict('records')

            return df_dict

        except:
            return None

    def Wells_Fargo(self):
        return_list = []
        self.text,_,_ = self.convert_pdf_to_text_with_page_pypdf2()
        try:
            for page in self.text:
                try:
                    text = page['text']#.replace('\\n','')
                    dateregex = regex.compile(r'(?<=ending|-)\s*(JANUARY|February|March|April|May|June|July|August|September|October|November|December)\s*[0-9]{1,2},\s*20[0-9]{2}', re.IGNORECASE)
                    dates = regex.findall(dateregex, text)
                    _date1 = parser.parse(dates[0])
                    _date2 = parser.parse(dates[0])
                    acct = regex.findall(r'[0-9]{4}-[0-9]{4}', text)[0]
                    date1 = self.format_date_as_string(_date1.year, _date1.month)
                    date2 = self.format_date_as_string(_date2.year, _date2.month)
                    return_list += [{'acct_no':acct, 'company_name':None, 'date1': date1, 'date2':date2, '_date1':_date1, '_date2':_date2,'page':page['page']}]
                except:
                    pass
            #need to fill None with place holder then back to None for TK
            df = pd.DataFrame(return_list).fillna('None')\
                .groupby(['acct_no','company_name','date1','date2','_date1','_date2'])['page']\
                .apply(list)\
                .to_frame()\
                .reset_index()\
                .applymap(lambda x: None if x == 'None' else x)
            df_dict = df.to_dict('records')

            return df_dict

        except:
            return None



    def Bok_Financial(self):
        try:
            self.text = self.convert_pdf_to_txt_with_page()
            return_list = []
            for page in self.text:
                try:
                    split_text = [line.strip() for line in page['text'].split('\\n') if line.strip() != '']
                
                    _acct = [a.strip() for a in split_text if re.search('\s*account\s*(number){0,1}:\s*([0-9]){2}-([0-9]){4}-([a-zA-Z]{0,1}[0-9]{1,2})-([0-9]){1}\s*', a, re.IGNORECASE)][0]
                    acct = re.search('([0-9]){2}-([0-9]){4}-([a-zA-Z]{0,1}[0-9]{1,2})-([0-9]){1}', _acct).group(0)
                    
                    _dates = [a for a in split_text if re.search(r'Statement\s*Period:\s*[0-9]{1,2}/[0-9]{1,2}/[0-9]{2}\s*through\s*[0-9]{1,2}/[0-9]{1,2}/[0-9]{2}', a, re.IGNORECASE)][0].strip()
                    
                    date_list = re.findall(r'[0-9]{1,2}/[0-9]{1,2}/[0-9]{2}', _dates)
                    _date1 = parser.parse(date_list[0])
                    _date2 = parser.parse(date_list[1])
                    date1 = self.format_date_as_string(_date1.year, _date1.month)
                    date2 = self.format_date_as_string(_date2.year, _date2.month)
                
                    return_list += [{'acct_no':acct, 'company_name':None, 'date1': date1, 'date2':date2, '_date1':_date1, '_date2':_date2,'page':page['page']}]
                except:
                    pass
            #need to fill None with place holder then back to None for TK
            df = pd.DataFrame(return_list).fillna('None')\
                .groupby(['acct_no','company_name','date1','date2','_date1','_date2'])['page']\
                .apply(list)\
                .to_frame()\
                .reset_index()\
                .applymap(lambda x: None if x == 'None' else x)
            # print(df)      
            df_dict = df.to_dict('records')

            return df_dict
        except:
            pass

    def Bok_Holdings_Transactions_Split(self):
        results = self.convert_pdf_to_txt_PDFQuery_with_page_pos()
        holdings_pages = set()
        transactions_pages = set()
        holdings_key_words = set(['assetandliabilitypositions'])
        transaction_key_words = set(['receipts','income','purchases','sales'])
        
        for page in list(set([a['page'] for a in results])):
            page_elts = [a for a in results if a['page'] == page]
            sorted_page_top = sorted(page_elts, key = lambda x: (-x['bbox'][1]))[:6]#, x['bbox'][0]))[:6]
            sorted_page_top_reduced = set([a['text'].strip().lower().replace(' ','') for a in sorted_page_top])
        
            if holdings_key_words.intersection(sorted_page_top_reduced) != set():
                # print(f'{page} holdings page')
                holdings_pages.add(page)
        
            elif transaction_key_words.intersection(sorted_page_top_reduced) != set():
                # print(f'{page} transactions page')
                transactions_pages.add(page)
        
        return {'transactions':transactions_pages, 'holdings':holdings_pages}

    def Bok_Holdings(self):
        try:
            acct_split = self.Bok_Financial()
            transactions_holdings_split = self.Bok_Holdings_Transactions_Split()
            holdings_pages = transactions_holdings_split['holdings']

            for acct in acct_split:
                acct['page'] = list(holdings_pages.intersection(set(acct['page'])))
            
            return_list =  None if [a for a in acct_split if a['page'] != []] == [] else [a for a in acct_split if a['page'] != []]
            return return_list
        except:
            return None

    def Bok_Transactions(self):
        try:
            acct_split = self.Bok_Financial()
            transactions_holdings_split = self.Bok_Holdings_Transactions_Split()
            transactions_pages = transactions_holdings_split['transactions']

            for acct in acct_split:
                acct['page'] = list(transactions_pages.intersection(set(acct['page'])))
            
            return_list =  None if [a for a in acct_split if a['page'] != []] == [] else [a for a in acct_split if a['page'] != []]
            return return_list
        except:
            return None


    def Regions(self):
        return_list = []
        try:
            self.text = self.convert_pdf_to_txt_with_page()
            
            for page in self.text:
                try:
                    split_text = [line.strip() for line in page['text'].split('\\n') if line.strip() != '']
                    # print(split_text)
                    
                    try: # old format
                        acct = [a.strip() for a in split_text if re.match('\s*([0-9]){10}\s*(?=ASI)', a, re.IGNORECASE).group(1)][0]
                        _dates = [a for a in split_text if re.search(r'\s*[0-9]{1,2}/[0-9]{1,2}/20[0-9]{2}\s*THROUGH\s*[0-9]{1,2}/[0-9]{1,2}/20[0-9]{2}', a, re.IGNORECASE)][0].strip()
                        _date2 = re.findall(r'[0-9]{1,2}/[0-9]{1,2}/20[0-9]{2}', _dates)[1].strip()
                    except: # new format - added new format that didn't sep with white spaces and would be parsed incorrectly
                        acct = re.findall(r'[0-9]{10}\s*(?=ASI)', split_text[0], re.IGNORECASE)[0]
                        # acct = re.findall('[0-9]{10}', _acct)[0]
                        _dates = [a for a in split_text if re.search(re.compile(r'(?<=-)\s*\D{3,9}\s*[0-9]{1,2}\s*,\s*20[0-9]{2}'),a)][0].strip()
                        _date2 = re.findall(re.compile(r'(?<=-)\s*\D{3,9}\s*[0-9]{1,2}\s*,\s*20[0-9]{2}'), _dates)[0].strip()
                        _day=re.search(r'(\D{3,9})(\s*[0-9]{1,2}\s*,\s*)(20[0-9]{2})', _date2).group(2)
                        _month=re.search(r'(\D{3,9})(\s*[0-9]{1,2}\s*,\s*)(20[0-9]{2})', _date2).group(1)
                        _year=re.search(r'(\D{3,9})(\s*[0-9]{1,2}\s*,\s*)(20[0-9]{2})', _date2).group(3)
                        _date2 = _month.strip()+' '+_day.strip()+' '+_year.strip()

                    # _date1 = parser.parse(date_list[0])
                    _date2 = parser.parse(_date2)

                    # date1 = self.format_date_as_string(_date1.year, _date1.month)
                    date2 = self.format_date_as_string(_date2.year, _date2.month)


                    return_list +=  [{'acct_no':acct, 'company_name':None, 'date1': None, 'date2':date2, '_date1':None, '_date2':_date2,'page':page['page']}]
                except:
                    pass
            df = pd.DataFrame(return_list).fillna('None')\
                .groupby(['acct_no','company_name','date1','date2','_date1','_date2'])['page']\
                .apply(list)\
                .to_frame()\
                .reset_index()\
                .applymap(lambda x: None if x == 'None' else x)
            # print(df)      
            df_dict = df.to_dict('records')

            return df_dict

        except:
            return None

    # This is currently not in TK's list of banks but leaving code here anyway.
    def Peoples_United_Bank(self):
        return_list = []

        try:
            self.text = self.convert_pdf_to_txt_with_page()
            for page in self.text:
                try:
                    split_text = [line.strip() for line in page['text'].split('\\n') if line.strip() != '']
                
                    _acct = [a.strip() for a in split_text if re.search('([a-zA-Z0-9]){2}-([a-zA-Z0-9]){4}-([a-zA-Z0-9]){2}-([a-zA-Z0-9]){1}', a, re.IGNORECASE)][0]
                    acct = re.search('([a-zA-Z0-9]){2}-([a-zA-Z0-9]){4}-([a-zA-Z0-9]){2}-([a-zA-Z0-9]){1}', _acct, re.IGNORECASE).group(0).strip()
                
                    _dates = [a for a in split_text if re.search(r'FROM\s*[0-9]{1,2}/[0-9]{1,2}/[0-9]{2}\s*THROUGH\s*[0-9]{1,2}/[0-9]{1,2}/[0-9]{2}', a, re.IGNORECASE)][0].strip()
                    date_list = re.findall(r'[0-9]{1,2}/[0-9]{1,2}/[0-9]{2}', _dates)
                
                    _date1 = parser.parse(date_list[0])
                    _date2 = parser.parse(date_list[1])
                
                    date1 = self.format_date_as_string(_date1.year, _date1.month)
                    date2 = self.format_date_as_string(_date2.year, _date2.month)
                
                    return_list +=  [{'acct_no':acct, 'company_name':None, 'date1': date1, 'date2':date2, '_date1':_date1, '_date2':_date2,'page':page['page']}]
                except:
                    pass
                df = pd.DataFrame(return_list).fillna('None')\
                    .groupby(['acct_no','company_name','date1','date2','_date1','_date2'])['page']\
                    .apply(list)\
                    .to_frame()\
                    .reset_index()\
                    .applymap(lambda x: None if x == 'None' else x)
                # print(df)      
                df_dict = df.to_dict('records')

            return df_dict
        except:
            return None

    def First_Midwest(self):

        return_list = []

        try:
            self.text = self.convert_pdf_to_txt_with_page()
            for page in self.text:
                try:
                    date_regex = regex.compile('((January|February|March|April|May|June|July|August|September|October|November|December)\s*[0-9]{1,2}\s*,\s*20[0-9]{2}\s*-\s*(January|February|March|April|May|June|July|August|September|October|November|December)\s*[0-9]{1,2}\s*,\s*20[0-9]{2})', regex.IGNORECASE)

                    acct_regex = regex.compile('([0-9]{2}-[0-9]{4}-[0-9]{2}-[0-9]{1})')

                    split_text = [line.strip() for line in page['text'].split('\\n') if line.strip() != '']
                    # print(split_text)
                    acct = [acct_regex.search(a).group(0).strip() for a in split_text if acct_regex.search(a)][0]

                    # dates = [a for a in split_text if re.search(r'[0-9]{1,2}/[0-9]{1,2}/[0-9]{2}\s*-\s*[0-9]{1,2}/[0-9]{1,2}/[0-9]{2}', a, re.IGNORECASE)][0].strip()
                    dates = [a for a in split_text if regex.search(date_regex, a)][0].strip()
                    date_list = dates.split("-")
                    _date1 = parser.parse(date_list[0].strip())
                    _date2 = parser.parse(date_list[1].strip())
                    date1 = self.format_date_as_string(_date1.year, _date1.month)
                    date2 = self.format_date_as_string(_date2.year, _date2.month)
                    return_list += [{'acct_no':acct, 'company_name':None, 'date1': date1, 'date2':date2, '_date1':_date1, '_date2':_date2,'page':page['page']}]
                except:
                    pass
            df = pd.DataFrame(return_list).fillna('None')\
                .groupby(['acct_no','company_name','date1','date2','_date1','_date2'])['page']\
                .apply(list)\
                .to_frame()\
                .reset_index()\
                .applymap(lambda x: None if x == 'None' else x)
            # print(df)      
            # print(max(df.iloc[0]['page']))
            # print(list(range(max(df.loc[0]['page'])+1)))
            df.at[0,'page'] = list(range(max(df.loc[0]['page'])+1))
            df_dict = df.to_dict('records')

            return df_dict

        except:
            return None

    def Fifth_Third_Bank(self):
        return_list = []
        try:   
            self.text,_,_ = self.convert_pdf_to_text_with_page_pypdf2()
            if ''.join([a['text'].strip() for a in self.text]).strip() == '':
                self.text = self.convert_pdf_to_txt_with_page()

            for page in self.text:
                try:    
                    acct_regex = regex.compile(r'(?<=Investment\s*Account\s*)[0-9]{2}-[0-9]{2}-[0-9]{3}-[0-9]{7}', regex.IGNORECASE)
                    date_regex = regex.compile(r'[0-9]{1,2}/[0-9]{1,2}/20[0-9]{2}\s*-\s*[0-9]{1,2}/[0-9]{1,2}/20[0-9]{2}')
                    acct = regex.search(acct_regex, page['text']).group(0) # for elt in page['text'] if regex.search(acct_regex, elt)][0]
                    dates = regex.search(date_regex, page['text']).group(0) # for elt in split_text if regex.search(date_regex, elt)][0] # [regex.search(acct_regex, line).group(0) for line in split_text if regex.search(acct_regex, line)]
                    date_list = dates.split(" - ")
                    _date1 = parser.parse(date_list[0])
                    _date2 = parser.parse(date_list[1])
                    date1 = self.format_date_as_string(_date1.year, _date1.month)
                    date2 = self.format_date_as_string(_date2.year, _date2.month)

                    return_list +=  [{'acct_no':acct, 'company_name':None, 'date1': date1, 'date2':date2, '_date1':_date1, '_date2':_date2,'page':page['page']}]
                except:
                    pass
            df = pd.DataFrame(return_list).fillna('None')\
                .groupby(['acct_no','company_name','date1','date2','_date1','_date2'])['page']\
                .apply(list)\
                .to_frame()\
                .reset_index()\
                .applymap(lambda x: None if x == 'None' else x)
            # print(df)      
            df_dict = df.to_dict('records')

            return df_dict

        except:
            return None



    def Honda_Funds_Held(self):
        return_list = []
        try:
            self.text = self.convert_pdf_to_txt_with_page()
            for page in self.text:
                try:
                    split_text = [line.strip() for line in page['text'].split('\\n') if line.strip() != '']
                    _company1 = [a for a in split_text if re.search('I[0-9]{4}', a)][0]
                    _company2 = _company1.split("-")[0].strip()
                    # company_name = self.remove_ltd(_company2)
                    company_name = _company2.strip()

                    acct = _company1.split("-")[1].strip()

                    date = [a for a in split_text if re.search('For\s*Month\s*Ending\s*', a, re.IGNORECASE)][0]
                    _date2 = re.sub(re.compile('For\s*Month\s*Ending\s*', re.IGNORECASE),'', date)
                    _date2 = parser.parse(_date2)
                    date2 = self.format_date_as_string(_date2.year, _date2.month)
                    # print(acct, date2)
                    return_list += [{'acct_no':acct, 'company_name':company_name, 'date1': None, 'date2':date2, '_date1':None, '_date2':_date2,'page':page['page']}]
                except:
                    pass

            df = pd.DataFrame(return_list).fillna('None')\
                .groupby(['acct_no','company_name','date1','date2','_date1','_date2'])['page']\
                .apply(list)\
                .to_frame()\
                .reset_index()\
                .applymap(lambda x: None if x == 'None' else x)
            # print(df)      
            df_dict = df.to_dict('records')

            return df_dict
        except:
            return None


    def Ameritrade(self):
        # try:
                    
        return_list = []
        page_list = range(PDFQuery(self.filename).doc.catalog['Pages'].resolve()['Count'])
        for page in page_list: # looping over pages to actually load to try and speed it up a bit
            try:
                _split_text = self.convert_pdf_to_txt_PDFQuery(page_list=[page])
                split_text = [a for a in _split_text if a != '']
                _acct = [a for a in split_text if re.search('Account\s*[0-9]{3}-[0-9]{6}', a, re.IGNORECASE)][0].strip()
                acct = re.sub(re.compile(r'Account\s+', re.IGNORECASE), '', _acct)

                _date = [a for a in split_text if re.search('Reporting\s*Period:\s*', a, re.IGNORECASE)][0].strip()
                date = re.sub(re.compile('Reporting\s*Period:\s*', re.IGNORECASE),'',_date).strip()
                _date2 = date.split(' ')[0]+date.split(',')[1]
                _date2 = parser.parse(_date2)
                date2 = self.format_date_as_string(_date2.year, _date2.month)
                _date1 = date.split('-')[0]+date.split(',')[1]
                _date1 = parser.parse(_date1)
                date1 = self.format_date_as_string(_date1.year, _date1.month)

                return_list += [{'acct_no':acct, 'company_name':None, 'date1': date1, 'date2':date2, '_date1':_date1, '_date2':_date2,'page':page}]
            except:
                pass
            #need to fill None with place holder then back to None for TK
        df = pd.DataFrame(return_list).fillna('None')\
            .groupby(['acct_no','company_name','date1','date2','_date1','_date2'])['page']\
            .apply(list)\
            .to_frame()\
            .reset_index()\
            .applymap(lambda x: None if x == 'None' else x)
        # print(df)      
        df_dict = df.to_dict('records')

        return df_dict
        # except:
        #     return None


    def Summit_Wealth(self):
        return_list = []

        # try:
        self.text = self.convert_pdf_to_txt_with_page()
        for page in self.text:
            try:
                split_text = [line.strip() for line in page['text'].split('\\n') if line.strip() != '']

                # company_name = split_text[8]
                acct = [a for a in split_text if re.search('Account\s*Number:', a, re.IGNORECASE)][0].split(":")[1].strip()
                
                dates = [a for a in split_text if re.search(r'(?<=PERIOD)\s*\D{3,8}\s*[0-9]{1,2}\s*,\s*20[0-9]{2}\s*TO', a, re.IGNORECASE)][0]
                split_dates = dates.upper().split(" TO ")
                
                _date1 = parser.parse(re.search(r'\D{3,9}\s*[0-9]{1,2},\s*20[0-9]{2}', split_dates[0], re.IGNORECASE).group(0))
                _date2 = parser.parse(split_dates[1])
                date1 = self.format_date_as_string(_date1.year, _date1.month)
                date2 = self.format_date_as_string(_date2.year, _date2.month)

                return_list += [{'acct_no':acct, 'company_name':None, 'date1': date1, 'date2':date2, '_date1':_date1, '_date2':_date2,'page':page['page']}]
            except:
                pass
        df = pd.DataFrame(return_list).fillna('None')\
            .groupby(['acct_no','company_name','date1','date2','_date1','_date2'])['page']\
            .apply(list)\
            .to_frame()\
            .reset_index()\
            .applymap(lambda x: None if x == 'None' else x)
        # print(df)      
        df_dict = df.to_dict('records')

        return df_dict

        # except:
        #     return None



# -=====================START SUNTRUST SPLITTING=========================================
    def SunTrust(self):
        try:
            return_list = []
            self.text = self.convert_pdf_to_txt_PDFQuery_with_page_pos()
            page_nos = list(set([a['page'] for a in self.text]))

            acct_regex = regex.compile('([0-9]{6,9})')#|[0-9]{7}|[0-9]{9})')#{6,7,9}')
            date_regex1 = regex.compile('(?<=(through|as of)\s*)[0-9]{1,2}/[0-9]{1,2}/[0-9]{2}', regex.IGNORECASE)
            date_regex2 = regex.compile('(?<=-\s*)((January|February|March|April|May|June|July|August|September|October|November|December)\s*[0-9]{1,2}\s*,\s*20[0-9]{2})', regex.IGNORECASE)
            
            

            for page_no in page_nos:
                try:
                    date2 = ''
                    acct = ''
                    page = [a for a in self.text if a['page'] == page_no and a['text'].strip() != '']
                    # print(page)
                    sorted_text = sorted(page, key = lambda x: (-x['bbox'][1], x['bbox'][0]))[:10]
                    

                    for elt in sorted_text:

                        if regex.search(acct_regex, elt['text']):
                            acct = regex.search(acct_regex, elt['text']).group(0)
                        if regex.search(date_regex2, elt['text']):
                            _date = regex.search(date_regex2, elt['text']).group(1)
                            date_ = parser.parse(_date)
                        if regex.search(date_regex1, elt['text']):
                            _date = regex.search(date_regex1, elt['text']).group(0)
                            date_ = parser.parse(_date)
                    
                    date2 = self.format_date_as_string(date_.year, date_.month)    

                    if date2 != '' and acct != '':
                        return_list += [{'acct_no':acct, 'company_name':None, 'date1': None, 'date2':date2, '_date1':None, '_date2':date_,'page':page_no}]
                except:
                    pass
            df = pd.DataFrame(return_list).fillna('None')\
                .groupby(['acct_no','company_name','date1','date2','_date1','_date2'])['page']\
                .apply(list)\
                .to_frame()\
                .reset_index()\
                .applymap(lambda x: None if x == 'None' else x)
            df_dict = df.to_dict('records')
            # we need to add page 0 back in if it is not in the page list already
            # this is for flexicapture to be able to determine which template to use
            # print(df_dict[0])
            if 0 not in df_dict[0]['page']:
                df_dict[0]['page'] = [0] + df_dict[0]['page']
            return df_dict
        except:
            return None
            
    def SunTrust_ExtraPagesRemoved(self):
        try:
            return_list = []
            self.text = self.convert_pdf_to_txt_PDFQuery_with_page_pos()
            page_nos = list(set([a['page'] for a in self.text]))

            acct_regex = regex.compile('([0-9]{6}|[0-9]{7}|[0-9]{9})')#{6,7,9}')
            date_regex1 = regex.compile('(?<=(through|as of)\s*)[0-9]{1,2}/[0-9]{1,2}/[0-9]{2}', regex.IGNORECASE)
            date_regex2 = regex.compile('(?<=-\s*)((January|February|March|April|May|June|July|August|September|October|November|December)\s*[0-9]{1,2}\s*,\s*20[0-9]{2})', regex.IGNORECASE)
            
            incl_key_words = set(['portfoliosummary','portfoliodetail','activitydetail','activitydetail-continued','transactionsummary', 'transactiondetail'])
            excl_key_words = set(['explanationofaccountstatementfeatures'])

            for page_no in page_nos:
                try:
                    date2 = ''
                    acct = ''
                    page = [a for a in self.text if a['page'] == page_no and a['text'].strip() != '']
                    # print(page)
                    sorted_text = sorted(page, key = lambda x: (-x['bbox'][1], x['bbox'][0]))[:10]

                    for elt in sorted_text:
                        # print(elt['text'])
                        if regex.search(acct_regex, elt['text']):
                            acct = regex.search(acct_regex, elt['text']).group(0)
                            # print(acct)
                        if regex.search(date_regex2, elt['text']):
                            _date = regex.search(date_regex2, elt['text']).group(1)
                            date_ = parser.parse(_date)
                        if regex.search(date_regex1, elt['text']):
                            _date = regex.search(date_regex1, elt['text']).group(0)
                            date_ = parser.parse(_date)
                    
                    date2 = self.format_date_as_string(date_.year, date_.month)    
                    kept_page = False
                    simple_page_text = ''.join([a['text'] for a in page]).strip().lower().replace(' ','').replace('(','').replace(')','')
                    for elt in incl_key_words:
                        if elt in simple_page_text:# and '' not in simple_page_text:
                            kept_page = True
                            for elt in excl_key_words:
                                if elt in simple_page_text:
                                    kept_page = False
                                    break
                    if date2 != '' and acct != '' and kept_page==True:
                        return_list += [{'acct_no':acct, 'company_name':None, 'date1': None, 'date2':date2, '_date1':None, '_date2':date_,'page':page_no}]
                except:
                    pass
            df = pd.DataFrame(return_list).fillna('None')\
                .groupby(['acct_no','company_name','date1','date2','_date1','_date2'])['page']\
                .apply(list)\
                .to_frame()\
                .reset_index()\
                .applymap(lambda x: None if x == 'None' else x)
            df_dict = df.to_dict('records')

            return df_dict
        except:
            return None

    # def SunTrust(self):
    #     ret = self.SunTrust_1()
    #     if ret is not None:
    #         return ret
    #     else:
    #         return self.SunTrust_2()
    #     return None

    # def SunTrust_1(self):
    #     return_list = []
    #     try:
    #         self.text = self.convert_pdf_to_txt_with_page()
    #         for page in self.text:
    #             try:
    #                 # print(page['text'])
    #                 split_text = page['text'].split("\\n")

    #                 acct =  [regex.search(r'(?<=ACCOUNT\s*(NUMBER:|No.)\s*)[0-9]{7}', a, re.IGNORECASE).group(0) for a in split_text if regex.search(r'(?<=ACCOUNT\s*(NUMBER:|No.)\s*)[0-9]{7}', a, re.IGNORECASE)][0]

    #                 _date2_ = [regex.search(r'(?<=(through|as of)\s*)[0-9]{1,2}/[0-9]{1,2}/[0-9]{2}', a, re.IGNORECASE).group(0) for a in split_text if regex.search(r'(?<=(through|as of)\s*)[0-9]{1,2}/[0-9]{1,2}/[0-9]{2}', a, re.IGNORECASE)][0]
    #                 _date2 = parser.parse(_date2_)
    #                 date2 = self.format_date_as_string(_date2.year, _date2.month)

    #                 return_list += [{'acct_no':acct, 'company_name':None, 'date1':None, 'date2':date2, '_date1':None, '_date2':_date2, 'page': page['page']}]
    #             except:
    #                 pass
    #         df = pd.DataFrame(return_list).fillna('None')\
    #             .groupby(['acct_no','company_name','date1','date2','_date1','_date2'])['page']\
    #             .apply(list)\
    #             .to_frame()\
    #             .reset_index()\
    #             .applymap(lambda x: None if x == 'None' else x)
    #         # print(df)      
    #         df_dict = df.to_dict('records')

    #         return df_dict
    #     except:
    #         return None
    
    # def SunTrust_2(self):
    #     return_list = []
    #     try:
    #         self.text = self.convert_pdf_to_txt_with_page()
    #         for page in self.text:
    #             # try:
    #             # print(page['text'])
    #             split_text = [line.strip() for line in page['text'].split('\\n') if line.strip() != '']
    #             dates = [a for a in split_text if re.search('[0-9]{1,2}\s*,\s*20[0-9]{2}\s*-', a)][0]
    #             dates = dates.split('-')
    #             _date1 = parser.parse(dates[0].strip())
    #             _date2 = parser.parse(dates[1].strip())
    #             date1 = self.format_date_as_string(_date1.year, _date1.month)
    #             date2 = self.format_date_as_string(_date2.year, _date2.month)
    #             acct = [a for a in split_text if re.search('[0-9]{6,9}', a)][0]

    #             return_list += [{'acct_no':acct, 'company_name':None, 'date1': date1, 'date2':date2, '_date1':_date1, '_date2':_date2,'page':page['page']}]
    #             # except:
    #             #     pass
    #         df = pd.DataFrame(return_list).fillna('None')\
    #             .groupby(['acct_no','company_name','date1','date2','_date1','_date2'])['page']\
    #             .apply(list)\
    #             .to_frame()\
    #             .reset_index()\
    #             .applymap(lambda x: None if x == 'None' else x)
    #         # print(df)      
    #         df_dict = df.to_dict('records')

    #         return df_dict
    #     except:
    #         return None

# THESE ARE FOR SUNTRUST/TRUIST - copied from US_Bank  - both need same setup since restriction to header is position sensitive and
# text does not always get read in the same order.
    def SunTrust_Holdings_Transactions_Split(self):
        text_regex = regex.compile('[a-z]',regex.IGNORECASE)
        prelim_results = self.convert_pdf_to_txt_PDFQuery_with_page_pos()
        results = [a for a in prelim_results if regex.search(text_regex, a['text']) is not None and regex.search('[0-9]',a['text']) is None]
        holdings_pages = set()
        transactions_pages = set()
        holdings_key_words = set(['portfoliodetail'])
        transaction_key_words = set(['activitydetail','activitydetail-continued'])
        
        for page in list(set([a['page'] for a in results])):
            page_elts = [a for a in results if a['page'] == page]
            sorted_page_top = sorted(page_elts, key = lambda x: (-x['bbox'][1]))[:10]#, x['bbox'][0]))[:6]
            sorted_page_top_reduced = set([a['text'].strip().lower().replace(' ','').replace('(','').replace(')','') for a in sorted_page_top])

            if holdings_key_words.intersection(sorted_page_top_reduced) != set():
                holdings_pages.add(page)
        
            elif transaction_key_words.intersection(sorted_page_top_reduced) != set():
                transactions_pages.add(page)
        return {'transactions':transactions_pages, 'holdings':holdings_pages}

    def SunTrust_Holdings(self):
        try:
            acct_split = self.SunTrust()
            transactions_holdings_split = self.SunTrust_Holdings_Transactions_Split()
            holdings_pages = transactions_holdings_split['holdings']

            for acct in acct_split:
                acct['page'] = list(holdings_pages.intersection(set(acct['page'])))
            
            return_list =  None if [a for a in acct_split if a['page'] != []] == [] else [a for a in acct_split if a['page'] != []]
            return return_list
        except:
            return None

    def SunTrust_Transactions(self):
        try:
            acct_split = self.SunTrust()
            transactions_holdings_split = self.SunTrust_Holdings_Transactions_Split()
            transactions_pages = transactions_holdings_split['transactions']

            for acct in acct_split:
                acct['page'] = list(transactions_pages.intersection(set(acct['page'])))
            
            return_list =  None if [a for a in acct_split if a['page'] != []] == [] else [a for a in acct_split if a['page'] != []]
            return return_list
        except:
            return None

# -=====================END SUNTRUST SPLITTING=========================================

# OLD RAYMOND JAMES BEFORE SPLITTING TRANSACTIONS/HOLDINGS - OLD WAY IS FASTER
    # def Raymond_James_Combined(self):
    #     try:
    #         return_list = []
    #         text_list = self.convert_pdf_to_txt_with_page()
    #         for elt in text_list:
    #             try:
    #                 acct = None
    #                 date1 = None
    #                 date2 = None
    #                 _date1 = None
    #                 _date2 = None

    #                 page = elt['page']
    #                 # print(f'Processing page #{page}.')

    #                 acct_regex_1 = r'Account\s(No.){0,1}(#){0,1}\s[0-9]{3}[0-9A-Z]{2}[0-9]{3}'
    #                 acct_regex_2 = r'[0-9]{3}[0-9A-Z]{2}[0-9]{3}'
    #                 # date_regex = r'\D{3,9}\s*[0-9]{1,2}\s*to\s*\D{3,12}[0-9]{1,2},\s20[0-9]{2}'
    #                 date_regex = r'to\s*\D{3,12}[0-9]{1,2},\s20[0-9]{2}'

    #                 split_text = elt['text'].split("\\n")

    #                 for text_elt in split_text:
    #                     if re.search(acct_regex_1, text_elt, re.IGNORECASE):
    #                         match = re.search(acct_regex_1, text_elt, re.IGNORECASE).group(0)
    #                         acct = re.search(acct_regex_2, match).group(0)
    #                     if re.search(date_regex, text_elt, re.IGNORECASE):
    #                         _dates1 = text_elt.replace('"','')
    #                         _dates = _dates1.split(" to ")
    #                         # print(_dates)

    #                         # sometimes they are in "month day to month day, year" or month day, year to month day, year" format
    #                         if re.search(re.compile(r'\D{3,12}[0-9]{1,2},\s20[0-9]{2}'), _dates[0])  and re.search(re.compile(r'\D{3,12}[0-9]{1,2},\s20[0-9]{2}'), _dates[1]):
    #                             _date1 = parser.parse(_dates[0])
    #                         else:
    #                             _date1 = parser.parse(_dates[0] +", "+_dates[1][-4:])
                            
    #                         _date2 = parser.parse(_dates[1])
    #                         date1 = self.format_date_as_string(_date1.year, _date1.month)
    #                         date2 = self.format_date_as_string(_date2.year, _date2.month)
    #                 if acct == None or date1 == None or date2 == None or _date1 == None or _date2 == None:
    #                     return_list += [{'acct_no':'Page Error', 'company_name':None, 'date1':None, 'date2':None, '_date1':None, '_date2':None, 'page':page}]
    #                 else:
    #                     return_list += [{'acct_no':acct, 'company_name':None, 'date1':date1, 'date2':date2, '_date1':_date1, '_date2':_date2, 'page':page}]
    #             except:
    #                 return_list += [{'acct_no':'Page Error', 'company_name':None, 'date1':None, 'date2':None, '_date1':None, '_date2':None, 'page':page}]
    #         return self.combine_pages(return_list) 

    #     except:
    #         return None

# =============== START RAYMOND JAMES SPLITTING ================================================
    def Raymond_James(self):
        try:
            return_list = []
            self.text = self.convert_pdf_to_txt_PDFQuery_with_page_pos()
            page_nos = list(set([a['page'] for a in self.text]))

            acct_regex = regex.compile('(?<=Account\s(No.){0,1}(#){0,1}\s*)[0-9]{3}[0-9A-Z]{2}[0-9]{3}')#{6,7,9}')
            date_regex = regex.compile('(?<=to\s*)\D{3,12}[0-9]{1,2},\s20[0-9]{2}', regex.IGNORECASE)

            for page_no in page_nos:
                try:
                    date2 = ''
                    acct = ''
                    page = [a for a in self.text if a['page'] == page_no]
                    sorted_text = sorted(page, key = lambda x: (-x['bbox'][1], x['bbox'][0]))[:10]
                    
                    for elt in sorted_text:
                        if regex.search(acct_regex, elt['text']):
                            acct = regex.search(acct_regex, elt['text']).group(0)
                        if regex.search(date_regex, elt['text']):
                            _date = regex.search(date_regex, elt['text']).group(0)
                            date_ = parser.parse(_date)
                            date2 = self.format_date_as_string(date_.year, date_.month)    

                        if date2 != '' and acct != '':
                            return_list += [{'acct_no':acct, 'company_name':None, 'date1': None, 'date2':date2, '_date1':None, '_date2':date_,'page':page_no}]
                            break
                except:
                    pass
            df = pd.DataFrame(return_list).fillna('None')\
                .groupby(['acct_no','company_name','date1','date2','_date1','_date2'])['page']\
                .apply(list)\
                .to_frame()\
                .reset_index()\
                .applymap(lambda x: None if x == 'None' else x)
            df_dict = df.to_dict('records')

            return df_dict
        except:
            return None


    def Raymond_James_Holdings_Transactions_Split(self):
        
        text_regex = regex.compile('[a-z]',regex.IGNORECASE)
        prelim_results = self.convert_pdf_to_txt_PDFQuery_with_page_pos()
        results = [a for a in prelim_results if regex.search(text_regex, a['text']) is not None and regex.search('[0-9]',a['text']) is None]
        holdings_pages = set()
        transactions_pages = set()
        holdings_key_words = set(['fixedincome(continued)','yourportfolio(continued)','fixedincomecontinued','yourportfoliocontinued'])
        transaction_key_words = set(['activitydetail','activitydetail(continued)','activitydetailcontinued','realizedcapitalgains&losses','realizedcapitalgains&losses(continued)','realizedcapitalgains&lossescontinued','youractivity','youractivity(continued)','youractivitycontinued'])
        
        for page in list(set([a['page'] for a in results])):
            page_elts = [a for a in results if a['page'] == page]
            sorted_page_top = sorted(page_elts, key = lambda x: (-x['bbox'][1], x['bbox'][0]))#[:10]#, x['bbox'][0]))[:6]
            sorted_page_top_reduced = set([a['text'].strip().lower().replace(' ','').replace('(','').replace(')','') for a in sorted_page_top])
        
            if holdings_key_words.intersection(sorted_page_top_reduced) != set():
                holdings_pages.add(page)
        
            elif transaction_key_words.intersection(sorted_page_top_reduced) != set():
                transactions_pages.add(page)
        
        return {'transactions':transactions_pages, 'holdings':holdings_pages}


    def Raymond_James_Holdings(self):
        try:
            acct_split = self.Raymond_James()
            transactions_holdings_split = self.Raymond_James_Holdings_Transactions_Split()
            holdings_pages = transactions_holdings_split['holdings']

            for acct in acct_split:
                acct['page'] = list(holdings_pages.intersection(set(acct['page'])))
            
            return_list =  None if [a for a in acct_split if a['page'] != []] == [] else [a for a in acct_split if a['page'] != []]
            return return_list
        except:
            return None

    def Raymond_James_Transactions(self):
        try:
            acct_split = self.Raymond_James()
            transactions_holdings_split = self.Raymond_James_Holdings_Transactions_Split()
            transactions_pages = transactions_holdings_split['transactions']

            for acct in acct_split:
                acct['page'] = list(transactions_pages.intersection(set(acct['page'])))
            
            return_list =  None if [a for a in acct_split if a['page'] != []] == [] else [a for a in acct_split if a['page'] != []]
            return return_list
        except:
            return None


# =============== END RAYMOND JAMES SPLITTING ================================================

    def Asset_Mark_Combined(self):
        try:
            return_list = []
            text_list = self.convert_pdf_to_txt_with_page()
            for elt in text_list:
                page = elt['page']

                acct_regex_1 = r'(?<=account\s*(number|#)\s*:\s*)([0-9]{7,8})'
                # acct_regex_2 = r'([0-9]){7}'
                date_regex = r'[0-9]{1,2}\s*-\s*\D{3,12}[0-9]{1,2},\s20[0-9]{2}'

                split_text = elt['text'].split("\\n")

                _date1 = None
                _date2 = None
                date1 = None
                date1 = None
                match = None
                acct = None

                for text_elt in split_text:
                    if regex.search(regex.compile(acct_regex_1, re.IGNORECASE), text_elt):
                        # print(regex.search(regex.compile(acct_regex_1, re.IGNORECASE), text_elt).group(0),regex.search(regex.compile(acct_regex_1, re.IGNORECASE), text_elt).group(1))
                        acct = regex.search(regex.compile(acct_regex_1, re.IGNORECASE), text_elt).group(0)
                        # acct = re.search(acct_regex_2, match).group(0)
                    if re.search(date_regex, text_elt, re.IGNORECASE):
                        date = text_elt
                        _date1 = parser.parse(date.split("-")[0].replace('"','').strip()+", "+date[-4:])
                        _date2 = parser.parse(date.split("-")[1].strip())
                        date1 = self.format_date_as_string(_date1.year, _date1.month)
                        date2 = self.format_date_as_string(_date2.year, _date2.month)

                return_list += [{'acct_no':acct, 'company_name':None, 'date1':date1, 'date2':date2, '_date1':_date1, '_date2':_date2, 'page':page}]
            

            return self.combine_pages(return_list) 

        except:
            return None

    def Asset_Mark_Combined_Holdings(self):
        try:
            identifier_page = None
            return_list = []
            text_list = self.convert_pdf_to_txt_with_page()
            for elt in text_list:
                page = elt['page']
                holdings_page = False
                acct_regex_1 = regex.compile(r'(?<=account\s*(number|#)\s*:\s*)([0-9]{7,8})', regex.IGNORECASE)
                # acct_regex_2 = r'([0-9]){7}'
                date_regex = regex.compile(r'[0-9]{1,2}\s*-\s*\D{3,12}[0-9]{1,2},\s20[0-9]{2}', regex.IGNORECASE)
                holdings_regex = regex.compile(r'account\s*holdings\s*and\s*valuations\s*\(continued\)', regex.IGNORECASE)
                identifier_page_regex = regex.compile(r'Your\s*Account\s*Information', regex.IGNORECASE)
                split_text = elt['text'].split("\\n")
                # print(split_text)
                _date1 = None
                _date2 = None
                date1 = None
                date1 = None
                match = None
                acct = None

                for text_elt in split_text:
                    if regex.search(acct_regex_1, text_elt):
                        # print(regex.search(regex.compile(acct_regex_1, re.IGNORECASE), text_elt).group(0),regex.search(regex.compile(acct_regex_1, re.IGNORECASE), text_elt).group(1))
                        acct = regex.search(acct_regex_1, text_elt).group(0)
                        # acct = re.search(acct_regex_2, match).group(0)
                    if regex.search(date_regex, text_elt):
                        date = text_elt
                        _date1 = parser.parse(date.split("-")[0].replace('"','').strip()+", "+date[-4:])
                        _date2 = parser.parse(date.split("-")[1].strip())
                        date1 = self.format_date_as_string(_date1.year, _date1.month)
                        date2 = self.format_date_as_string(_date2.year, _date2.month)
                    if regex.search(identifier_page_regex, text_elt):
                        identifier_page = page
                for text_elt in split_text:
                    if regex.search(holdings_regex, text_elt):
                        holdings_page = True
                if holdings_page == True:
                    # print(f"holdings page {page}")
                    return_list += [{'acct_no':acct, 'company_name':None, 'date1':date1, 'date2':date2, '_date1':_date1, '_date2':_date2, 'page':page}]
                if identifier_page != None and holdings_page == False:
                    return_list += [{'acct_no':acct, 'company_name':None, 'date1':date1, 'date2':date2, '_date1':_date1, '_date2':_date2, 'page':page}]
                    # print(f"identifier page {page}")
                    identifier_page = None


                for text_elt in split_text:
                    if regex.search(identifier_page_regex, text_elt):
                        identifier_page = page
                

            df = pd.DataFrame(return_list).fillna('None')\
                .groupby(['acct_no','company_name','date1','date2','_date1','_date2'])['page']\
                .apply(list)\
                .to_frame()\
                .reset_index()\
                .applymap(lambda x: None if x == 'None' else x)
            df_dict = df.to_dict('records')

            return df_dict

        except:
            return None




    def Whitney_Bank(self):
        return_list = []
        
        try:
            self.text = self.convert_pdf_to_txt_with_page()
            for page in self.text:
                # try:
                split_text = page['text'].split("\\n")
                account = [a for a in split_text if re.search(r'Account\s*Number:\s*', a, re.IGNORECASE)][0]
                date = [a for a in split_text if re.search(r'[0-9]{2},\s*20[0-9]{2}\s*TO\s*\D{3,12}\s*[0-9]{2},\s*20[0-9]{2}', a, re.IGNORECASE)][0]
                acct = account.split(":")[1].strip()
                
                _date1 = parser.parse(date.split(" TO ")[0])
                _date2 = parser.parse(date.split(" TO ")[1])
                date1 = self.format_date_as_string(_date1.year, _date1.month)
                date2 = self.format_date_as_string(_date2.year, _date2.month)

                return_list += [{'acct_no':acct, 'company_name':None, 'date1':date1, 'date2':date2, '_date1':_date1, '_date2':_date2, 'page':page['page']}]
                # except:
                #     pass
            #need to fill None with place holder then back to None for TK
            df = pd.DataFrame(return_list).fillna('None')\
                .groupby(['acct_no','company_name','date1','date2','_date1','_date2'])['page']\
                .apply(list)\
                .to_frame()\
                .reset_index()\
                .applymap(lambda x: None if x == 'None' else x)
            # print(df)      
            df_dict = df.to_dict('records')

            return df_dict

        except:
            return None
    
    def Wilmington_Trust(self):
        return_list = []
        try:
            self.text = self.convert_pdf_to_txt_with_page()
            for page in self.text:
                try:
                    split_text = page['text'].split("\\n")
                    acct =  [re.search(r'\s*[0-9]{6}-[0-9]{3}\s*', a, re.IGNORECASE).group(0).strip() for a in split_text if re.search(r'\s*[0-9]{6}-[0-9]{3}\s*', a, re.IGNORECASE)][0]
                    dates = [a for a in split_text if re.search(r'[0-9]{2},\s*20[0-9]{2}\s*-\s*\D{3,12}\s*[0-9]{2},\s*20[0-9]{2}', a, re.IGNORECASE)][0]
                    _date1 = parser.parse(dates.split("-")[0] .strip())
                    _date2 = parser.parse(dates.split("-")[1].strip())
                    date1 = self.format_date_as_string(_date1.year, _date1.month)
                    date2 = self.format_date_as_string(_date2.year, _date2.month)
                    
                    return_list += [{'acct_no':acct, 'company_name':None, 'date1':date1, 'date2':date2, '_date1':_date1, '_date2':_date2, 'page':page['page']}]
                except:
                    pass
            #need to fill None with place holder then back to None for TK
            df = pd.DataFrame(return_list).fillna('None')\
                .groupby(['acct_no','company_name','date1','date2','_date1','_date2'])['page']\
                .apply(list)\
                .to_frame()\
                .reset_index()\
                .applymap(lambda x: None if x == 'None' else x)
            df_dict = df.to_dict('records')

            return df_dict
        except:
            return None
        
    def UMB_Bank(self):
        return_list = []
        try:
            self.text = self.convert_pdf_to_txt_with_page()
            for page in self.text:
                try:
                    split_text = page['text'].split("\\n")
                    acct_regex = regex.compile(r'(?<=Account\s*Number(:){0,1}\s*)[0-9]{0,10}.[0-9]{1}', regex.IGNORECASE)
                    date_regex = regex.compile(r'Statement\s*Period(:){0,1}', regex.IGNORECASE)

                    account = [a for a in split_text if regex.search(acct_regex, a)][0]
                    acct = account.split("Number")[1].replace(':','').strip()
                    
                    dates = [a for a in split_text if regex.search(date_regex, a)][0]
                    split_dates = dates.split("-")
                    _date2 = parser.parse(split_dates[1].strip())
                    _date1 = parser.parse(split_dates[0].split("Period")[1].replace(':','').strip()+", "+str(_date2.year))
                    date1 = self.format_date_as_string(_date1.year, _date1.month)
                    date2 = self.format_date_as_string(_date2.year, _date2.month)

                    return_list += [{'acct_no':acct, 'company_name':None, 'date1':date1, 'date2':date2, '_date1':_date1, '_date2':_date2, 'page':page['page']}]
                except:
                    pass
            df = pd.DataFrame(return_list).fillna('None')\
                .groupby(['acct_no','company_name','date1','date2','_date1','_date2'])['page']\
                .apply(list)\
                .to_frame()\
                .reset_index()\
                .applymap(lambda x: None if x == 'None' else x)
            # print(df)      
            df_dict = df.to_dict('records')

            return df_dict

        except:
            return None

    def US_Bank(self):
        return_list = []

        try:
            self.text = self.convert_pdf_to_txt_with_page()
            for page in self.text:
                try:
                    split_text = page['text'].split("\\n")
                    
                    acct_regex = r'Account\s*(Number){0,1}(:){0,1}\s*[X0-9]{3,15}'
                    date_regex = r'\S{3,12}\s*[0-9]{1,2},\s*20[0-9]{2}\s*to\s*\S{3,12}\s*[0-9]{2},\s*20[0-9]{2}'

                    pre_acct = [a for a in split_text if re.search(acct_regex, a, re.IGNORECASE)][0]
                    acct = re.findall(re.compile(r'[X0-9]{3,15}', re.IGNORECASE),pre_acct)[0]
                    
                    dates = [a for a in split_text if re.search(date_regex, a, re.IGNORECASE)][0]
                    dates_list = re.findall(re.compile(r'\S{3,12}\s*[0-9]{1,2},\s*20[0-9]{2}', re.IGNORECASE), dates)
                    _date1 = parser.parse(dates_list[0])
                    _date2 = parser.parse(dates_list[1])
                    date1 = self.format_date_as_string(_date1.year, _date1.month)
                    date2 = self.format_date_as_string(_date2.year, _date2.month)
                except:
                    pass
                return_list += [{'acct_no':acct, 'company_name': None, 'date1':date1, 'date2':date2, '_date1':_date1, '_date2':_date2, 'page':page['page']}]
        
            #need to fill None with place holder then back to None for TK
            df = pd.DataFrame(return_list).fillna('None')\
                .groupby(['acct_no','company_name','date1','date2','_date1','_date2'])['page']\
                .apply(list)\
                .to_frame()\
                .reset_index()\
                .applymap(lambda x: None if x == 'None' else x)
            # print(df)      
            df_dict = df.to_dict('records')

            return df_dict
        
        except:
            return None

    def US_Bank_Holdings_Transactions_Split(self):
        text_regex = regex.compile('[a-z]',regex.IGNORECASE)
        prelim_results = self.convert_pdf_to_txt_PDFQuery_with_page_pos()
        results = [a for a in prelim_results if regex.search(text_regex, a['text']) is not None and regex.search('[0-9]',a['text']) is None]
        holdings_pages = set()
        transactions_pages = set()
        holdings_key_words = set(['assetdetail', 'assetdetailcontinued'])
        transaction_key_words = set(['cashtransactiondetail','cashtransactiondetailcontinued','purchases','salesandmaturities'])
        
        for page in list(set([a['page'] for a in results])):
            page_elts = [a for a in results if a['page'] == page]
            sorted_page_top = sorted(page_elts, key = lambda x: (-x['bbox'][1]))[:5]#, x['bbox'][0]))[:6]
            sorted_page_top_reduced = set([a['text'].strip().lower().replace(' ','').replace('(','').replace(')','') for a in sorted_page_top])
            # print(f'{page} , {sorted_page_top_reduced}')

            if holdings_key_words.intersection(sorted_page_top_reduced) != set():
                # print(f'{page} holdings page')
                holdings_pages.add(page)
        
            elif transaction_key_words.intersection(sorted_page_top_reduced) != set():
                # print(f'{page} transactions page')
                transactions_pages.add(page)
        
        return {'transactions':transactions_pages, 'holdings':holdings_pages}

    def US_Bank_Holdings(self):
        try:
            acct_split = self.US_Bank()
            transactions_holdings_split = self.US_Bank_Holdings_Transactions_Split()
            holdings_pages = transactions_holdings_split['holdings']

            for acct in acct_split:
                acct['page'] = list(holdings_pages.intersection(set(acct['page'])))
            
            return_list =  None if [a for a in acct_split if a['page'] != []] == [] else [a for a in acct_split if a['page'] != []]
            return return_list
        except:
            return None

    def US_Bank_Transactions(self):
        try:
            acct_split = self.US_Bank()
            transactions_holdings_split = self.US_Bank_Holdings_Transactions_Split()
            transactions_pages = transactions_holdings_split['transactions']

            for acct in acct_split:
                acct['page'] = list(transactions_pages.intersection(set(acct['page'])))
            
            return_list =  None if [a for a in acct_split if a['page'] != []] == [] else [a for a in acct_split if a['page'] != []]
            return return_list
        except:
            return None


    def Comerica(self):

        try:

            return_list = []            
            self.text = self.convert_pdf_to_txt_with_page()
            for page in self.text:
                try:
                    excl_page = False
                    split_text = page['text'].split("\\n")

                    acct_regex = r'\s*[0-9]{10}\s*'
                    date_regex = r'[0-9]{2}/[0-9]{2}/[0-9]{4}\s*through\s*[0-9]{2}/[0-9]{2}/[0-9]{4}'
                    excl_regex = regex.compile(r'message\s*page|table\s*of\s*contents', regex.IGNORECASE)

                    acct = [regex.search(acct_regex, a, regex.IGNORECASE).group(0) for a in split_text if regex.search(acct_regex, a, regex.IGNORECASE)][0].strip()
                    dates = [a for a in split_text if re.search(date_regex, a, re.IGNORECASE)][0]
                    _date1 = parser.parse(re.findall(re.compile(r'[0-9]{2}/[0-9]{2}/[0-9]{4}'),dates)[0])
                    _date2 = parser.parse(re.findall(re.compile(r'[0-9]{2}/[0-9]{2}/[0-9]{4}'),dates)[1])
                    date1 = self.format_date_as_string(_date1.year, _date1.month)
                    date2 = self.format_date_as_string(_date2.year, _date2.month)

                    for elt in split_text:
                        if regex.search(excl_regex, elt):
                            excl_page = True
                        else:
                            pass
                    if not excl_page:
                        return_list += [{'acct_no':acct, 'company_name':None, 'date1':date1, 'date2':date2, '_date1':_date1, '_date2':_date2, 'page':page['page']}]
                except:
                    pass
            #need to fill None with place holder then back to None for TK
            df = pd.DataFrame(return_list).fillna('None')\
                .groupby(['acct_no','company_name','date1','date2','_date1','_date2'])['page']\
                .apply(list)\
                .to_frame()\
                .reset_index()\
                .applymap(lambda x: None if x == 'None' else x)
            # print(df)      
            df_dict = df.to_dict('records')

            return df_dict        
        except:
            return None
    






    def Ford(self):
        try:
            return_list = []
            text_list = self.convert_pdf_to_txt_with_page()
            # print(text_list)
            for elt in text_list:
                try:
                    page = elt['page']
                    
                    acct_regex = '#:\s*[0-9]{1,3}'
                    date_regex = '^\D{3,9}\s*20[0-9]{2}\s*$'

                    split_text = elt['text'].split("\\n")

                    acct_found = [a for a in split_text if re.search(acct_regex, a, re.IGNORECASE)][0]
                    acct = acct_found.split("#:")[1].strip()
                    # acct = self.remove_ltd(acct)
                    acct = acct.strip()

                    date_found = [a for a in split_text if re.search(date_regex, a, re.IGNORECASE)][0]
                    _date2 = parser.parse(date_found.strip())
                    date2 = self.format_date_as_string(_date2.year, _date2.month)

                    return_list += [{'acct_no':acct, 'company_name':None, 'date1':None, 'date2':date2, '_date1':None, '_date2':_date2, 'page': [page]}]
                    # print(return_list[-1])
                except:
                    pass
            return return_list
        except:
            return None


    # This is currently not in TK's list of banks but leaving code here anyway.
    def Raymond_James_Combined_1099(self):
        try:
            # file_contents = []
            # contents = ''
            # with open(self.filename, 'rb') as pdffile:
            #     pdfReader = PyPDF2.PdfFileReader(pdffile)
            #     count = pdfReader.numPages
                
            #     for i in range(count):
            #         page = pdfReader.getPage(i)
            #         page_contents = page.extractText() 
            #         contents += page_contents
            #         file_contents += [{'page':i, 'text':page_contents}]

            file_contents, contents, count = self.convert_pdf_to_text_with_page_pypdf2()

            End_of_Statement_Page_Nos = [-1]
            for elt in file_contents:
                # print(elt['text'])
                if '*** End of Statement ***' in elt['text']:
                    End_of_Statement_Page_Nos += [elt['page']]

            stmts = []
            for start, end in zip(End_of_Statement_Page_Nos[:-1], End_of_Statement_Page_Nos[1:]):
                stmt_text = ' '.join([elt['text'] for elt in file_contents if elt['page'] > start and elt['page'] <=end])
                stmt_pages = list(range(start+1, end+1))
                stmts += [{'text':stmt_text, 'pages':stmt_pages}]

            # from dateutil import parser
            page_collection = []
            for stmt in stmts:
                try:
                    [_,acct_no] = re.findall(re.compile(r'(Account\s*)([0-9]{3,4}[a-z]{0,2}[0-9]{3,4})', re.IGNORECASE), stmt['text'])[0]
                    [_,year, stmt_date] = re.findall(re.compile(r'(Detail\s*for\s*Interest\s*Income\s*)([0-9]{4})([0-9]{2}/[0-9]{2}/[0-9]{4})', re.IGNORECASE), stmt['text'])[0]
                    _date2 = parser.parse(stmt_date)
                    date2 = str(_date2.year)+"_"+str(_date2.month)
                    page_collection += [{'acct_no':acct_no, 'date1':year, '_date1':None, 'date2':date2, '_date2':_date2, 'page':stmt['pages']}]
                except:
                    pass

            # Now for the missing pages
            
            page_set = set(range(count))
            acct_pages = []
            for acct in page_collection:
                acct_pages += acct['page']
            acct_pages_set = set(acct_pages)
            excluded_pages = sorted(list(page_set - acct_pages_set))
            
            page_collection += [{'acct_no':'XXX_ERROR_FINDING_DATA_XXX','company_name':'', 'date1':'', 'date2':'', '_date1':'', '_date2':'', 'page':excluded_pages}]

            return page_collection
        except:
            return None

    def Asset_Mark_1099(self):
        try:
            allinfo_regex = re.compile('CompanyAccount([0-9]{7})(Fees\s*and\s*Expenses|Detail\s*for\s*Dividends\s*and\s*Distributions)([0-9]{4})([0-9]{2}/[0-9]{2}/[0-9]{4})', re.IGNORECASE)
            self.text = ''        
            with open(self.filename, 'rb') as pdffile:
                pdfReader = PyPDF2.PdfFileReader(pdffile)
                count = pdfReader.numPages

                for i in range(count):
                    page = pdfReader.getPage(i)
                    self.text += page.extractText()

            match=re.findall(allinfo_regex, self.text)[0]
            date2 =match[3]
            _date2 = parser.parse(date2)

            acct_no = match[0]
            # 1099s are annual statements, 'year' is the year the stmt is for, is being returned in 'date1'
            year = match[2]
        
            return [{'acct_no': acct_no, 'company_name': None, 'date2':date2, 'date1':year, '_date2':None, '_date1':None, 'page':[0]}]
        except:
            return None


    def Wells_Fargo_1099(self):

        try:
            wf_year_regex = re.compile('([0-9]{4})(\s*Year-End\s*Account\s*Summary)', re.IGNORECASE)
            wf_year_regex2 = re.compile('([0-9]{4})(\s*Consolidated\s*Forms\s*1099)', re.IGNORECASE)
            wf_year_regex3 = re.compile('([0-9]{4})(\s*Amended\s*Forms\s*1099)', re.IGNORECASE)
            wf_date_regex = re.compile('(As\s*of\s*Date:\s*)([0-9]{2}/[0-9]{2}/[0-9]{2})', re.IGNORECASE)
            wf_date_regex3 = re.compile('(Corrected\s*Date:\s*)([0-9]{2}/[0-9]{2}/[0-9]{2})', re.IGNORECASE)
            wf_acct_regex = re.compile('(Account\s*Number:\s*)([0-9]{4}-[0-9]{4})', re.IGNORECASE)

            self.text = ''


            with open(self.filename, 'rb') as pdffile:
                pdfReader = PyPDF2.PdfFileReader(pdffile)
                count = pdfReader.numPages

                for i in range(count):
                    page = pdfReader.getPage(i)
                    self.text += page.extractText()

            # Case 1 is a standard form
            try:
                
                year = re.findall(wf_year_regex, self.text)[0][0]
                acct_no = re.findall(wf_acct_regex, self.text)[0][1]
                _date2 = parser.parse(re.findall(wf_date_regex, self.text)[0][1])
                date2 = self.format_date_as_string(_date2.year, _date2.month)
                form = 'Year-End Account Summary'
            except:
                # pass
            
                # Case 2 is a Consolidated Form
                try:
                    
                    year = re.findall(wf_year_regex2, self.text)[0][0]
                    acct_no = re.findall(wf_acct_regex, self.text)[0][1]
                    _date2 = parser.parse(re.findall(wf_date_regex, self.text)[0][1])
                    date2 = self.format_date_as_string(_date2.year, _date2.month)
                    form = 'Consolidated Form'
                except:
                    # pass

                # Case 3 is an Ammended Form
                    try:
                        
                        year = re.findall(wf_year_regex3, self.text)[0][0]
                        acct_no = re.findall(wf_acct_regex, self.text)[0][1]
                        _date2 = parser.parse(re.findall(wf_date_regex3, self.text)[0][1])
                        date2 = self.format_date_as_string(_date2.year, _date2.month)
                        form = 'Amended Form'
                    except:
                        pass
            

            return [{'acct_no': acct_no, 'company_name': None, 'date2':date2, 'date1':year, '_date2':None, '_date1':None, 'page':[0], 'form':form}]
        except:
            return None



    def Delaware_Trust(self):
        return_list = []

        # try:
        self.text = self.convert_pdf_to_txt([0])
        acct_regex = regex.compile(r'(?<=Account\s*#(:){0,1}\s*)[0-9]{6,8}')
        date_regex = regex.compile(r'[0-9]{2}/[0-9]{2}/[0-9]{4}')
        
        acct_no = None
        date2 = None
        company_name = None
        try:        
            splittext = self.text.replace("\\n\\n","\\n").split("\\n")
            
            for ii, elt in enumerate(splittext):
                if regex.search(acct_regex, elt):
                    acct_no = regex.search(acct_regex, elt).group(0)
                    company_name = splittext[ii-1]
                if re.search(re.compile(r'Account\s*Information\s*On:\s*'), elt):
                    if regex.search(date_regex, splittext[ii+1]):
                        date = regex.findall(date_regex, splittext[ii+1])[0]
                        _date2 = parser.parse(date)
                        date2 = self.format_date_as_string(_date2.year, _date2.month) 
                if acct_no and date2 and company_name:
                    break

            with open(self.filename, 'rb') as pdffile:
                pdfReader = PyPDF2.PdfFileReader(pdffile, strict=False)
                count = pdfReader.numPages
            
            return_list =  [{'acct_no': acct_no, 'company_name': company_name, 'date2':date2, '_date2':_date2, 'date1':None, '_date1':None, 'page':list(range(count))}]
            return return_list

        except:
            return None

    def Delaware_Trust_Multi(self):
        return_list = []

        try:
            self.text = self.convert_pdf_to_txt_with_page()
            acct_regex = regex.compile(r'(?<=Account\s*#(:){0,1}\s*)[0-9]{6,8}')
            date_regex = regex.compile(r'[0-9]{2}/[0-9]{2}/[0-9]{4}')
            for page in self.text:
                try:
                    splittext = page['text'].replace("\\n\\n","\\n").split("\\n")
                    for ii, elt in enumerate(splittext):
                        if regex.search(acct_regex, elt):
                            acct_no = regex.search(acct_regex, elt).group(0)
                            company_name = splittext[ii-1]
                        if re.search(re.compile(r'Account\s*Information\s*On:\s*'), elt):
                            if regex.search(date_regex, splittext[ii+1]):
                                date = regex.findall(date_regex, splittext[ii+1])[0]
                                _date2 = parser.parse(date)
                                date2 = self.format_date_as_string(_date2.year, _date2.month) 
                    return_list +=  [{'acct_no': acct_no, 'company_name': company_name, 'date2':date2, '_date2':_date2, 'date1':None, '_date1':None, 'page':page['page']}]
                except:
                    pass
            df = pd.DataFrame(return_list).fillna('None')\
                .groupby(['acct_no','company_name','date1','date2','_date1','_date2'])['page']\
                .apply(list)\
                .to_frame()\
                .reset_index()\
                .applymap(lambda x: None if x == 'None' else x)
                # print(df)      
            df_dict = df.to_dict('records')

            return df_dict

        except:
            return None

    def UBS(self):
        try:
            self.text = self.convert_pdf_to_txt_with_page()
            return_list = []

            acct_regex = regex.compile(r'FY\s*[0-9]{5}\s*(CI|18)', regex.IGNORECASE)
            date_regex = regex.compile('(January|February|March|April|May|June|July|August|September|October|November|December)\s*20[0-9]{2}')
            month_dict = {'January':'01', 'February':'02', 'March':'03', 'April':'04', 'May':'05', 'June':'06', 'July':'07', 'August':'08', 'September':'09', 'October':'10', 'November':'11', 'December':'12'}
            for page in self.text:
                acct_no = None
                _date = None
                page_text = page['text'].replace('\\n','').replace('\n','')
                if regex.search(acct_regex, page_text) and acct_no is None:
                    acct_no = regex.search(acct_regex, page_text).group(0)
                    
                if regex.search(date_regex, page_text) and _date is None:
                    _date = regex.search(date_regex, page_text).group(0)


                if acct_no is not None and _date is not None:
                    _date_parts= _date.replace("  "," ").split(" ")
                    _date_ = _date_parts[1]+"_"+month_dict[_date_parts[0]]
                    return_list +=  [{'acct_no': acct_no, 'company_name': None, 'date2':_date_, '_date2':None, 'date1':None, '_date1':None, 'page':page['page']}]
            
            df = pd.DataFrame(return_list).fillna('None')\
                    .groupby(['acct_no','company_name','date1','date2','_date1','_date2'])['page']\
                    .apply(list)\
                    .to_frame()\
                    .reset_index()\
                    .applymap(lambda x: None if x == 'None' else x)
                    # print(df)      
            df_dict = df.to_dict('records')

            return df_dict
        except:
            return None





    def search(self):
        if self.bank =='Ameritrade':
            return self.Ameritrade()
        if self.bank == "Asset Mark Combined":
            return self.Asset_Mark_Combined()
        if self.bank == 'Asset Mark Combined Holdings':
            return self.Asset_Mark_Combined_Holdings()
        if self.bank == "Bok Financial":
            return self.Bok_Financial()
        if self.bank == "Bok Holdings":
            return self.Bok_Holdings()
        if self.bank == "Bok Transactions":
            return self.Bok_Transactions()
        if self.bank == "Comerica":
            return self.Comerica()
        if self.bank == "Delaware Trust":
            return self.Delaware_Trust()
        if self.bank == 'Delaware Trust Multi':
            return self.Delaware_Trust_Multi()
        if self.bank == "First Midwest":
            return self.First_Midwest()
        if self.bank == "Fifth Third Bank":
            return self.Fifth_Third_Bank()
        if self.bank == 'Ford':
            return self.Ford()
        if self.bank == 'Honda Funds Held':
            return self.Honda_Funds_Held()
        if self.bank == "Raymond James Combined":
            return self.Raymond_James()
        if self.bank == "Raymond James":
            return self.Raymond_James()
        if self.bank == "Raymond James Transactions":
            return self.Raymond_James_Transactions()
        if self.bank == "Raymond James Holdings":
            return self.Raymond_James_Holdings()
        if self.bank == 'Regions':
            return self.Regions()
        if self.bank == 'Reinsurance Max':
            return self.Reinsurance_Max()
        if self.bank == 'Summit Wealth':
            return self.Summit_Wealth()
        if self.bank == "SunTrust":
            return self.SunTrust()
        if self.bank == "SunTrust Reduced":
            return self.SunTrust_ExtraPagesRemoved()
        if self.bank == "SunTrust Holdings":
            return self.SunTrust_Holdings()
        if self.bank == "SunTrust Transactions":
            return self.SunTrust_Transactions()
        if self.bank == "Truist":
            return self.SunTrust()
        if self.bank == "Truist Reduced":
            return self.SunTrust_ExtraPagesRemoved()
        if self.bank == "Truist Holdings":
            return self.SunTrust_Holdings()
        if self.bank == "Truist Transactions":
            return self.SunTrust_Transactions()
        if self.bank == 'UBS':
            return self.UBS()
        if self.bank == "UMB Bank":
            return self.UMB_Bank()
        if self.bank == "US Bank":
            return self.US_Bank()
        if self.bank == "US Bank Holdings":
            return self.US_Bank_Holdings()
        if self.bank == "US Bank Transactions":
            return self.US_Bank_Transactions()
        if self.bank == "Wells Fargo":
            return self.Wells_Fargo()
        if self.bank == "Whitney Bank":
            return self.Whitney_Bank()
        if self.bank == "Wilmington Trust":
            return self.Wilmington_Trust()


def main(file_full_path, bank):
    """
    returns acct number else none
    :param file_full_path: 
    :param bank: 
    :return: 
    """
    searcher = acct_searcher(file_full_path, bank)
    return searcher.search()

# if __name__ == '__main__':
#     file_full_path = os.path.abspath(r'G:\adegraw\Python\PDF_Scripts\TK\Acct_Finder\testing\testpdfs\Toyota Ceding Combined\GAP\BOREN (2).pdf')#KENDALL (1).pdf')
#     bank = 'Toyota Ceding Combined'

#     main(file_full_path, bank)