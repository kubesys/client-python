"""
* Copyright (2021, ) Institute of Software, Chinese Academy of Sciences
"""

import yaml
from base64 import b64decode

__author__ = ('Tian Yu <yutian20@otcaix.iscas.ac.cn>',
              'Heng Wu <wuheng@iscas.ac.cn>')

from cryptography import x509
from cryptography.hazmat.backends import default_backend


class Config():
    def __init__(self, server, certificateAuthorityData, clientCertificateData, clientKeyData):
        self.server = server
        self.certificateAuthorityData = certificateAuthorityData
        self.clientCertificateData = clientCertificateData
        self.clientKeyData = clientKeyData


def readConfig(config='/etc/kubernetes/admin.conf'):
    file = open(config, 'r', encoding='utf-8')
    yf = yaml.load(file.read(), Loader=yaml.SafeLoader)
    return Config(server=yf['clusters'][0]['cluster']['server'],
                  certificateAuthorityData=b64decode(yf['clusters'][0]['cluster']['certificate-authority-data']),
                  clientCertificateData=b64decode(yf['users'][0]['user']['client-certificate-data']),
                  clientKeyData=b64decode(yf['users'][0]['user']['client-key-data']))


def rootCAs(certificateAuthorityData):
    return x509.load_pem_x509_csr(certificateAuthorityData, default_backend())



