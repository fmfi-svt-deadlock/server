import tests.config as config
import bootstrap
import gateserver.db
import gateserver.http_api
import requests

url = 'http://localhost:{}'.format(config.http_port)

def setup_module(module):
    gateserver.db.connect(config.db_url)
    bootstrap.db_create_tables()
    gateserver.http_api.serve(config)

def teardown_module(module):
    gateserver.http_api.stop()

def assert_req(method, url, status=200, expected_data=None, **kwargs):
    print(kwargs)
    r = requests.request(method, url, **kwargs)
    assert r.status_code == status
    if expected_data: assert r.json() == expected_data

def test_controller_crud():
    cid = '00:00:00:00:00:00'
    data = { 'id': cid, 'ip': '0.0.0.0', 'name': 'Test Controller' }
    requests.delete(url+'/controller/'+cid)  # just in case the last run didn't

    assert_req('PUT', url+'/controller/'+cid, json={'ip': data['ip'],
                                                    'name': data['name']},
               expected_data={'url': url+'/controller/'+cid})
    assert_req('GET', url+'/controller/'+cid, expected_data=data)
    assert_req('GET', url+'/controller/', expected_data=[data])
    assert_req('PUT', url+'/controller/'+cid, json={}, status=400)
    assert_req('DELETE', url+'/controller/'+cid)
    assert_req('GET', url+'/controller/'+cid, status=404)

def test_log():
    r = requests.get(url+'/log/')
    assert r.status_code == 200
    assert isinstance(r.json(), list)
