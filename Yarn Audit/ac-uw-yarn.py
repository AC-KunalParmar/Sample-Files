## Import libraries
# !/usr/bin/env python
import json
import sys
import re
import os
import glob
from github import Github
from zipfile import ZipFile
from os.path import basename
from pathlib import Path
import requests

## Variable to define####
environment = "Production"
scanTool = "Yarn Audit"

repoNameRegex = re.compile('[a-zA-Z_-]*')

## Endpoint to fetch secure one-time url to upload scan files
url_upload = 'https://app.armorcode.com/client/utils/scan/upload'

## Api key to secure the access of url_upload
api_key = '1f83253e-ec7a-4166-8f7d-29c60af16527'

flag_zip = 1  # Assign 1 to upload all scan reports in a zip file else 0
zip_file_name = "armorcode_import.zip"

## Metadata of the scan tool
data_json = {
    'env': environment,
    'product': 'Demo',
    'subProduct': 'Yarn',
    'scanTool': scanTool,
    'tags': "",
    'fileName': '',
    'directory': 'E:\GFSU\ArmorCode Internship\sample-scan-files-master\Yarn audit',
    'fileExtension': '.json'
}


def get_zip_file(folder_name, file_extension):
    '''
    Purpose: This function is used to fetch all the scan file and combine them in a zap file.
    :param folder_name: Full path of the folder where scan files are getting stored
    :param file_extension: File extension of the scan files, its pre defined for all the tools.
    :return: zip_file_name, its the created zip file.
    '''
    try:
        files = []
        folder_name = folder_name.strip()
        file_extension = file_extension.strip()
        for file_name in glob.glob(folder_name + '*' + file_extension):
            files.append(file_name)
        if files:
            print("\nList of files identified for creating zip file:")
            [print(x) for x in files]
            with ZipFile(zip_file_name, "w") as newzip:
                [newzip.write(x, basename(x)) for x in files]
            print('zip of all scan files is ready : ' + zip_file_name)
        else:
            print('No such file found in the directory: ' + str(folder_name))

            return 0
    except Exception as e:
        print('Error in creating zip file: ' + str(e))
        return 0
    return zip_file_name

def get_signed_url(url, header, json_data):
    '''
    Purpose: This function returns a secure one-time url to upload the scan file
    :param url: Its the endpoint to hit for getting the signed url
    :param header: Header object to hit the above endpoint
    :param json_data: Metadata of the scan
    :return: url, its a secure one-time use url to upload the scan file
    '''
    url_signed = ''
    try:
        if 'please_insert_api_key_here' in header['Authorization']:
            print('\nAPI Key not updated!!\nKindly update the API Key to run this script.\n')
            return url_signed

        response = requests.post(url, json=json_data, headers=header)
        response_json = json.loads(response.text.encode('utf8'))
        if response.status_code != 200:
            errorMessage = response_json.get('message', '')
            print(f'Error from AC API: {errorMessage}')
        url_signed = response_json.get('signedUrl', '')
    except Exception as e:
        print(f'Error in getting signed url: {e}')
        pass
    return url_signed


def upload_file(url_api, headers, json_data):
    '''
    Purpose: This function upload the scan file to our plateform
    :param url_api: Its the endpoint to hit for getting the signed url
    :param headers: Header object to hit the above endpoint
    :param json_data: Metadata of the scan
    :return: flag, 0 or 1 to indicate the success or failure
    '''
    try:
        file_name = json_data.get('fileName', '')
        json_data['fileName'] = json_data['fileName'].split('/')[-1]
        json_data['fileName'] = json_data['fileName'].split('\\')[-1]
        url_signed = get_signed_url(url_api, headers, json_data)
        ##print(url_signed)
        if not url_signed:
            print('Signed Url not generated.')
            return 0

        contents = ''
        with open(file_name, 'rb') as f:
            contents = f.read()
        requests.put(url_signed, contents)
    except Exception as e:
        print(f'Error in uploading file: {e}')
        return 0
    return 1




def main(args):
    '''
    Purpose: This function initiates the uploading of the scan file
    :return: flag, 0 or 1 to indicate the success or failure
    '''

    global headers, api_key

    if not len(args) == 3:
        print("Format of command is ac-uw-yarn.py <GITHUB-TOKEN> <ARMORCODE-API-KEY>")
        return
    githubToken = args[1]
    if not len(githubToken) == 40:
        print("Invalid github token")
        return

    repoName = 'NodeGoat'

    api_key = args[2]

    ## Headers for accessing the upload url
    headers = {
        'Authorization': 'Bearer ' + api_key,
        'Accept': 'application/json',
        'Content-Type': 'application/json'
    }

    try:
        github = Github(githubToken)
        repoObj = github.get_organization("Rocket-pocket-singh").get_repo(
            repoName)
        os.system(
            f'git clone https://{githubToken}@github.com/Rocket-pocket-singh/{repoObj.name}')
        os.chdir(f'{repoObj.name}')
        os.mkdir("E:\GFSU\ArmorCode Internship\sample-scan-files-master\Yarn audit\Zip1")
        os.chdir('E:/GFSU/ArmorCode Internship/sample-scan-files-master/Yarn audit/NodeGoat')
        os.system(f'yarn audit --json > ../NodeGoat/NodeGoat-yarn.json')
        #os.chdir('../client_monorepo')
        os.system(
            f'yarn npm audit --all -R --json > ../NodeGoat/NG-yarn.json')
        #os.chdir('../e2e')
        #os.system(f'yarn audit --json > ../yarn-zip/e2e-yarn.json')
        file = get_zip_file('../NodeGoat/', '.json')
        data_json['fileName'] = file
        import_flag = upload_file(url_upload, headers, data_json)
        if import_flag:
            print('\nFile upload Successful.\n')
        else:
            print('\nFile upload failed.\n')

    except Exception as e:
        print('Error in processing latest file')
        print(f'Exception thrown: {e}')

    return 1


main(sys.argv)
