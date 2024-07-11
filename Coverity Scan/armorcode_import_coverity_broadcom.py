## Import libraries
# !/usr/bin/env python
import time
import os
import glob
import json
import logging
from datetime import datetime
from urllib.request import urlopen, Request
import sys
import requests

## Variable to define
product='Demo Product'
subProduct='test_ravindra1'
environment="Production"
file_extension="xml"

#api_key='<<please_insert_api_key_here>>'  ## Kindly download the API Key from ArmorCode website and place it here.
api_key="f8e6d55d-0fcc-4e15-a886-47f1cf3d7171"
api_key_ingestion="f6099a19-2588-4785-adc6-fc4c59f248a8"

scanTool="COVERITY"
url_base = "https://app.armorcode.com/"





## Variable to define
product='new test'
subProduct='test_ravindra1'
environment="Production"
file_extension="xml"

api_key_ingestion="f58254a3-4cdc-4a28-bc39-50471eb6313a"

scanTool="COVERITY"
url_base = "https://qa.armorcode.ai/"


## Variable to define
product='TRH'
subProduct='TRH_Sub'
environment="Production"
file_extension="xml"

api_key_ingestion="4a159a9c-f6cc-4699-9d5c-f2a1f941921d"

scanTool="COVERITY"
url_base = "https://preprod.armorcode.ai/"


## Variable to define
product='TRH'
subProduct='TRH_Sub'
environment="Production"
file_extension="xml"

api_key_ingestion="36545d59-84a8-4da0-adce-057f2295b343"

scanTool="COVERITY"
url_base = "https://app.armorcode.com/"



# #Use below to pass parameters via command line arguments##
# if len(sys.argv) > 1:
#     product=sys.argv[1]
#     subProduct=sys.argv[2]
#     environment=sys.argv[3]

## Log file name
LOGFILE_NAME = "coverity" + '_import.log'
LOGFILE_NAME = LOGFILE_NAME.replace(' ', '_').lower()

## Initiating the logger
logging.basicConfig(filename=LOGFILE_NAME, level=logging.INFO, format='%(levelname)s: %(message)s -- %(asctime)s',
                    datefmt='%Y-%m-%d %I:%M:%S %p')

## Initiating the log writing
logging.info('------------------------------------------')
logging.info('Scan started')

SCRIPT_VERSION = '1.0'
logging.info('Script Version : ' + SCRIPT_VERSION)


file_content = ""

product_dict = {}
subproduct_dict = {}


# with open("Coverity_1.xml", 'r') as f:
#     file_content = f.read()

#print(file_content)

## Headers for accessing and creating subproduct
headers = {
    'Authorization': 'Bearer ' + api_key,
    'Accept': 'application/json',
    'Content-Type': 'application/json'
}

## Headers for uploading scan file
headers_ingestion = {
    'Authorization': 'Bearer ' + api_key_ingestion,
    'Accept': 'application/json',
    'Content-Type': 'application/json'
}


## Metadata of the scan tool
data_json = {
    'contentType': 'application/json',
    'triggerby': 'PUSH_UPLOAD',
    'env': environment,
    'product': product,
    'subProduct': subProduct,
    'scanTool': scanTool,
    'scanFileContent': file_content
}

#print(data_json)

data_json["scanFileContent"] = file_content

"""
coverity_base_url = "https://cov-esd-01.devops.broadcom.net:8443/"
coverity_username = "sb654881"
coverity_password = "password"
coverity_pem = "/Users/surender/cert2.pem"

coveriry_project_keyword = "NetOps" ## Its case sensative

"""

coverity_base_url = "http://18.216.155.77:8081/"
coverity_username = "admin"
coverity_password = "Python@1234"
coverity_pem = "/Users/theredhatter/Desktop/ArmorCodeInternship/sample-scan-files-master/coverity/ca-certs.pem"

coverity_project_keyword = "master"


coverity_project_dict = {}

def get_projects_coverity(coveriry_project_keyword):
    global coverity_project_dict
    #try:
    url_coverity_project = coverity_base_url + "api/v2/projects?namePattern=*"+coveriry_project_keyword+"*"

    response_coverity = requests.get(url_coverity_project, auth=(coverity_username, coverity_password), verify=coverity_pem)
    
    response_coverity_json = response_coverity.json()
    
    for item in response_coverity_json["projects"]:
        projectId = item["projectKey"]
        projectName = item["name"]

        coverity_project_dict[projectName] = projectId

        print(projectId,projectName)
    
    #except Exception as e:
    #    logging.error('Error in listing coverity projects: ' + str(e))
    #    logging.info('Finished at: ' + datetime.now().strftime('%d/%m/%Y %H:%M:%S'))
    return coverity_project_dict


def get_project_report_coverity(projectId):
    global file_content
    #try:
    #url_coverity_report = coverity_base_url + "api/v2/views/viewContents/"+str(projectId)+"?locale=en_us"
    #url_coverity_report = coverity_base_url + "api/v2/views/viewContents/"+str(projectId)+"?locale=en_us&"+"projectId="+str(projectId)
    url_coverity_report = coverity_base_url + "api/v2/views/viewContents/10006?locale=en_us&"+"projectId="+str(projectId)
    
    response_coverity_report = requests.get(url_coverity_report, auth=(coverity_username, coverity_password), verify=coverity_pem)
    
    file_content = json.loads(response_coverity_report.text)
    # except Exception as e:
    #     logging.error('Error in getting project report: ' + str(e))
    #     logging.info('Finished at: ' + datetime.now().strftime('%d/%m/%Y %H:%M:%S'))
    return 1



def get_product_dict():
    global product_dict
    url_products = url_base + "user/product/elastic/short"

    response_products = requests.request("GET", url_products, headers=headers, data=[])
    #print(response_products.text)

    response_products_json = json.loads(response_products.text.encode('utf8'))
    for temp in response_products_json:
        _name = temp.get("name").lower()
        _id = temp.get("id")
        product_dict[_name] = _id

    return product_dict


def get_product_id(product_name):
    global product_dict
    
    product_id = 0
    product_name_lower = product_name.lower()

    if product_name_lower in product_dict.keys():
        product_id = product_dict[product_name_lower]

    return product_id


def get_subproduct_dict(product_id):
    global subproduct_dict

    url_subproducts = url_base + "user/sub-product/elastic/short?productId={}".format(product_id)

    response_subproducts = requests.request("GET", url_subproducts, headers=headers, data=[])
    #print(response_subproducts.text)

    response_subproducts_json = json.loads(response_subproducts.text.encode('utf8'))
    for temp in response_subproducts_json:
        _name = temp.get("name").lower()
        _id = temp.get("id")
        subproduct_dict[_name] = _id

    return subproduct_dict


def get_subproduct_id(product_id, subproduct_name):
    global subproduct_dict
    
    subproduct_id = 0
    subproduct_name_lower = subproduct_name.lower()

    if subproduct_name_lower in subproduct_dict.keys():
        subproduct_id = subproduct_dict[subproduct_name_lower]
    else:
        subproduct_id = create_subproduct(product_id, subproduct_name)

    return subproduct_id



def create_subproduct(product_id, subproduct_name):
    global subproduct_dict

    url_subproduct = url_base + "api/sub-product"
    subproduct_id = get_subproduct_id(subproduct_name)

    if subproduct_id:
        print("Subproduct Alredy Created")
        return subproduct_id

    
    subproduct_payload = {
        "name":subproduct_name,
        "description": subproduct_name,
        "product":{"id":product_id}
    }
    

    try:
        response_subproduct = requests.post(url_subproduct,json=subproduct_payload,headers=headers)

        #print(response_subproduct.text)
        response_subproduct_json = json.loads(response_subproduct.text.encode('utf8'))

        subproduct_id = response_subproduct_json.get("id")
        if not subproduct_id:
            _message = response_subproduct_json.get("message")
            print("Error in create_subproduct : "+str(_message))
        else:
            print("subproduct_id : "+ str(subproduct_id))
    except Exception as e:
        print("Error in create_subproduct : "+str(e))
    
    return subproduct_id



def upload_scan_file():
    url_upload = url_base + "client/utils/scan/upload/v2"
    
    #try:
    response_upload = requests.post(url_upload,json=data_json,headers=headers_ingestion)
    print(response_upload.text)
    print(response_upload.status_code)
    #except Exception as e:
    #    print('Error in uploading scan.')
    #    logging.error('Failed to upload scan: ' + str(e))
    #    return 0
    return 1


def main():
    '''
    Purpose: This function initiates the uploading of the scan file
    :return: flag, 0 or 1 to indicate the success or failure
    '''

    global file_content
    global coverity_project_dict
    global data_json

    # try:

        # get_product_dict()
        # product_id = get_product_id(product)
        # print(product_id)

    get_projects_coverity(coverity_project_keyword)

    for project_name in coverity_project_dict.keys():
        project_id = coverity_project_dict[project_name]
        print(project_id)
        print(project_name)

        get_project_report_coverity(project_id)

        print(file_content)

        data_json["scanFileContent"] = json.dumps(file_content)

        upload_scan_file()


        ##subProduct = projectName.split("NetOps_")[1]

        # get_subproduct_dict(product_id)
        # subproduct_id = get_subproduct_id(product_id, subProduct)
        # print(subproduct_id)

    # except Exception as e:
    #     print('Error in processing latest file')
    #     logging.error('Error in processing latest file: ' + str(e))

    # logging.info('Finished at: ' + datetime.now().strftime('%d/%m/%Y %H:%M:%S'))

    return 1


if __name__ == '__main__':

    ## Initiate the upload of the scan file.
    main()

