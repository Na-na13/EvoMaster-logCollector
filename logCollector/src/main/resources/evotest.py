import json
import unittest
import requests
import os
import sys
if os.name == 'nt':


    class timeout_decorator:

        @staticmethod
        def timeout(*args, **kwargs):
            return lambda f: f
else:
    import timeout_decorator
from em_test_utils import *


class EvoMaster_faults_Test(unittest.TestCase):
    baseUrlOfSut = 'https://localhost:6884'

    @timeout_decorator.timeout(60)
    def test_0_with500(self):
        headers = {}
        headers['content-type'] = 'application/json'
        body = {}
        body = (' { ' + ' "clientType": "confidential", ' +
            ' "clientProfile": "browser", ' + ' "clientName": "kPuP1ZY", ' +
            ' "clientDesc": "Nf", ' + ' "ownerId": "tTq", ' +
            ' "host": "LZO9jgwUM0bjM", ' + ' "scope": "rWgxeULPmpEEtP", ' +
            ' "customClaim": "Fx0_5", ' +
            ' "redirectUri": "bZuymnnxb8oS6Z1", ' +
            ' "authenticateClass": "WOPk" ' + ' } ')
        headers['Accept'] = 'application/json'
        res_0 = requests.put(self.baseUrlOfSut + '/oauth2/client', verify=
            False, headers=headers, data=body)
        assert res_0.status_code == 500
        assert 'application/json' in res_0.headers['content-type']
        assert res_0.json()['statusCode'] == 500.0
        assert res_0.json()['code'] == 'ERR10010'
        assert res_0.json()['message'] == 'RUNTIME_EXCEPTION'
        assert res_0.json()['description'] == 'Unexpected runtime exception'
        assert res_0.json()['severity'] == 'ERROR'

    @timeout_decorator.timeout(60)
    def test_1(self):
        headers = {}
        headers['Accept'] = 'application/json'
        res_0 = requests.get(self.baseUrlOfSut + '/oauth2/client?' +
            'page=981&' + 'pageSize=365&' + 'clientName=CefxeppACx9FWB',
            verify=False, headers=headers)
        assert res_0.status_code == 200
        assert 'application/json' in res_0.headers['content-type']
        assert res_0.json()['total'] == 6.0
        assert len(res_0.json()['clients']) == 0

    @timeout_decorator.timeout(60)
    def test_2(self):
        headers = {}
        headers['content-type'] = 'application/json'
        body = {}
        body = (' { ' + ' "clientSecret": "dyAj", ' +
            ' "clientType": "public", ' + ' "clientProfile": "mobile", ' +
            ' "clientName": "YAz_a", ' + ' "clientDesc": "DT8vLF_", ' +
            ' "ownerId": "vhXiH54Jor", ' + ' "host": "AHfcRBZC", ' +
            ' "scope": "a59rtNNQD", ' +
            ' "customClaim": "_9uGCM6_jbvAln", ' +
            ' "redirectUri": "W5m", ' +
            ' "derefClientId": "Zblf6tc8U_OfxKp" ' + ' } ')
        headers['Accept'] = 'application/json'
        res_0 = requests.post(self.baseUrlOfSut + '/oauth2/client', verify=
            False, headers=headers, data=body)
        assert res_0.status_code == 400
        assert 'application/json' in res_0.headers['content-type']
        assert res_0.json()['statusCode'] == 400.0
        assert res_0.json()['code'] == 'ERR12043'
        assert res_0.json()['message'] == 'DEREF_NOT_EXTERNAL'
        assert res_0.json()['description'
            ] == 'Only external client type needs optional deref client id'
        assert res_0.json()['severity'] == 'ERROR'

    @timeout_decorator.timeout(60)
    def test_3(self):
        headers = {}
        headers['Accept'] = '*/*'
        res_0 = requests.delete(self.baseUrlOfSut +
            '/oauth2/client/fVdflevYY8j/service/1eQgAMLnkrxfXbNH', verify=
            False, headers=headers)
        assert res_0.status_code == 404
        assert 'application/json' in res_0.headers['content-type']
        assert res_0.json()['statusCode'] == 404.0
        assert res_0.json()['code'] == 'ERR12014'
        assert res_0.json()['message'] == 'CLIENT_NOT_FOUND'
        assert res_0.json()['description'
            ] == 'Client fVdflevYY8j is not found.'
        assert res_0.json()['severity'] == 'ERROR'

    @timeout_decorator.timeout(60)
    def test_4(self):
        headers = {}
        headers['Accept'] = '*/*'
        res_0 = requests.get(self.baseUrlOfSut +
            '/oauth2/client/D0nicl/service/kZ5', verify=False, headers=headers)
        assert res_0.status_code == 404
        assert 'application/json' in res_0.headers['content-type']
        assert res_0.json()['statusCode'] == 404.0
        assert res_0.json()['code'] == 'ERR12014'
        assert res_0.json()['message'] == 'CLIENT_NOT_FOUND'
        assert res_0.json()['description'] == 'Client D0nicl is not found.'
        assert res_0.json()['severity'] == 'ERROR'

    @timeout_decorator.timeout(60)
    def test_5(self):
        headers = {}
        headers['Accept'] = '*/*'
        res_0 = requests.delete(self.baseUrlOfSut +
            '/oauth2/client/7/service', verify=False, headers=headers)
        assert res_0.status_code == 404
        assert 'application/json' in res_0.headers['content-type']
        assert res_0.json()['statusCode'] == 404.0
        assert res_0.json()['code'] == 'ERR12014'
        assert res_0.json()['message'] == 'CLIENT_NOT_FOUND'
        assert res_0.json()['description'] == 'Client 7 is not found.'
        assert res_0.json()['severity'] == 'ERROR'

    @timeout_decorator.timeout(60)
    def test_6(self):
        headers = {}
        headers['Accept'] = '*/*'
        res_0 = requests.get(self.baseUrlOfSut +
            '/oauth2/client/79sxEaW18AD/service', verify=False, headers=headers
            )
        assert res_0.status_code == 404
        assert 'application/json' in res_0.headers['content-type']
        assert res_0.json()['statusCode'] == 404.0
        assert res_0.json()['code'] == 'ERR12014'
        assert res_0.json()['message'] == 'CLIENT_NOT_FOUND'
        assert res_0.json()['description'
            ] == 'Client 79sxEaW18AD is not found.'
        assert res_0.json()['severity'] == 'ERROR'

    @timeout_decorator.timeout(60)
    def test_7(self):
        headers = {}
        headers['Accept'] = '*/*'
        res_0 = requests.delete(self.baseUrlOfSut + '/oauth2/client/utBp50',
            verify=False, headers=headers)
        assert res_0.status_code == 404
        assert 'application/json' in res_0.headers['content-type']
        assert res_0.json()['statusCode'] == 404.0
        assert res_0.json()['code'] == 'ERR12014'
        assert res_0.json()['message'] == 'CLIENT_NOT_FOUND'
        assert res_0.json()['description'] == 'Client utBp50 is not found.'
        assert res_0.json()['severity'] == 'ERROR'

    @timeout_decorator.timeout(60)
    def test_8(self):
        headers = {}
        headers['Accept'] = 'application/json'
        res_0 = requests.get(self.baseUrlOfSut + '/oauth2/client/Di',
            verify=False, headers=headers)
        assert res_0.status_code == 404
        assert 'application/json' in res_0.headers['content-type']
        assert res_0.json()['statusCode'] == 404.0
        assert res_0.json()['code'] == 'ERR12014'
        assert res_0.json()['message'] == 'CLIENT_NOT_FOUND'
        assert res_0.json()['description'] == 'Client Di is not found.'
        assert res_0.json()['severity'] == 'ERROR'

    @timeout_decorator.timeout(60)
    def test_9(self):
        headers = {}
        headers['content-type'] = 'application/json'
        body = {}
        body = ' [ ' + ' "wDbeuXgLrgO" ' + ' ] '
        headers['Accept'] = '*/*'
        res_0 = requests.post(self.baseUrlOfSut +
            '/oauth2/client/P3YOEMbhZz2psL9/service/gZsaQja_4f2RdVo',
            verify=False, headers=headers, data=body)
        assert res_0.status_code == 404
        assert 'application/json' in res_0.headers['content-type']
        assert res_0.json()['statusCode'] == 404.0
        assert res_0.json()['code'] == 'ERR12014'
        assert res_0.json()['message'] == 'CLIENT_NOT_FOUND'
        assert res_0.json()['description'
            ] == 'Client P3YOEMbhZz2psL9 is not found.'
        assert res_0.json()['severity'] == 'ERROR'


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python evotest.py <test_number>")
        sys.exit(1)
    test_number = sys.argv[1]
    test_name = f"EvoMaster_faults_Test.test_{test_number}"
    import unittest
    loader = unittest.TestLoader()
    suite = unittest.TestLoader().loadTestsFromName(test_name, module=sys.modules[__name__])
    result = unittest.TextTestRunner().run(suite)

    if not result.wasSuccessful():
        print("The test was not successful")
        sys.exit(1)