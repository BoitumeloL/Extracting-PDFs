import os
from adobe.pdfservices.operation.auth.credentials import Credentials
from adobe.pdfservices.operation.exception.exceptions import ServiceApiException, ServiceUsageException, SdkException
from adobe.pdfservices.operation.execution_context import ExecutionContext
from adobe.pdfservices.operation.io.file_ref import FileRef
from adobe.pdfservices.operation.pdfops.extract_pdf_operation import ExtractPDFOperation
from adobe.pdfservices.operation.pdfops.options.extractpdf.extract_pdf_options import ExtractPDFOptions
from adobe.pdfservices.operation.pdfops.options.extractpdf.extract_element_type import ExtractElementType

import zipfile
import json
import datefinder
import nltk
#nltk.download('punkt')
#nltk.download('averaged_perceptron_tagger')
#nltk.download('maxent_ne_chunker')
#nltk.download('words')

zip_file = "./extract-scc-part-2.zip"

if os.path.isfile(zip_file):
    os.remove(zip_file)

input_pdf = "./scc-part-2.pdf"
paraList = []
chapList = []
headingList = []
dateList = []
placesList = []
#Initial setup, create credentials instance.
credentials = Credentials.service_account_credentials_builder()\
    .from_file("add the path to your json credential file") \
    .build()

#Create an ExecutionContext using credentials and create a new operation instance.
execution_context = ExecutionContext.create(credentials)

extract_pdf_operation = ExtractPDFOperation.create_new()

def extractData (input,output):
    #Set operation input from a source file.
    source = FileRef.create_from_local_file(input)
    extract_pdf_operation.set_input(source)
    #Build ExtractPDF options and set them into the operation
    extract_pdf_options: ExtractPDFOptions = ExtractPDFOptions.builder() \
        .with_element_to_extract(ExtractElementType.TEXT) \
        .build()
    extract_pdf_operation.set_options(extract_pdf_options)
    #Execute the operation.
    result: FileRef = extract_pdf_operation.execute(execution_context)
    #Save the result to the specified location.
    result.save_as(output)

    archive = zipfile.ZipFile(output, 'r')
    jsonentry = archive.open('structuredData.json')
    jsondata = jsonentry.read()
    data = json.loads(jsondata)
    return data

def paragraphs (data,list_):
    for element in data["elements"]:
        if(element["Path"].endswith("/LBody")):
            list_.append(element["Text"])
    return list_

def headings (data, list): #only brings back one heading
    i = 2
    for element in data["elements"]:
        index = str(i)
        if(element["Path"].endswith("/H3")):
            list.append(element["Text"])
        
        elif(element["Path"].endswith("/H3["+index+"]")):
            list.append(element["Text"])
        i += 1
    
    return list

def chapters (data, chapter):
    i = 2
    index = str(i)
    for element in data["elements"]:
        if element["Path"].endswith("/H1") :
            chapter.append(element["Text"])
        elif(element["Path"].endswith("/H1["+index+"]")):
            chapter.append(element["Text"])
        i += 1
    return chapter if chapter else None

def places(text):
    placesList = ['Johannesburg', 'Cape Town', 'Durban']
    found = []
    for i in placesList:
        if i in text:
            found.append(i)
    return found if found else None


def dates(data,datesList):
    for i in data:
        date = datefinder.find_dates(i)
        for d in date:
            datesList.append(d)
    return datesList if datesList else None

def extract_ne(quote):
     words = word_tokenize(quote, language=language)
     tags = nltk.pos_tag(words)
     tree = nltk.ne_chunk(tags, binary=True)
     return set(
         " ".join(i[0] for i in t)
         for t in tree
            if hasattr(t, "label") and t.label() == "NE"
     )            

jsonData = extractData(input_pdf,zip_file)
para = paragraphs(jsonData,paraList)
chap = chapters(jsonData,chapList)
heading = headings(jsonData,headingList)
date = dates(para,dateList)
place = places(para)

part ="1"
volume = '1'

data = {        "Part": part,
                "Volume": volume,
                "Chapter": chap,
                "Heading": heading,
                'Paragraph': para,
                "Place": place,
                "Date": date,
}

dataList = [ data ]
print(para[0])