import http.client
from urllib.parse import urlparse
from timeit import default_timer as timer
import sys
import json
import re

from joblib import Parallel, delayed
import multiprocessing

class app_link(object):
	def __init__(self, full_url):
		o = urlparse(full_url)
		self.host = o.netloc
		self.path = o.path
		self.query = o.query

	def get_host(self):
		return self.host

	def get_path(self):
		return self.path

	def get_query(self):
		return self.query

def green_text(string):
	return '\033[0;32m{}\033[0m'.format(string)

def red_text(string):
	return '\033[0;31m{}\033[0m'.format(string)

def get_apps_list(app_list_id):
	conn = http.client.HTTPConnection("apps.taipei")

	payload = "{'AppListID':'divHotApp','KeyWord':'','Language':'tw'}"
	headers = {
	    'accept': "application/json, text/javascript, */*; q=0.01",
	    'origin': "http://apps.taipei",
	    'x-devtools-emulate-network-conditions-client-id': "a5564768-65c5-44c5-a604-44e76590b3f3",
	    'x-requested-with': "XMLHttpRequest",
	    'user-agent': "Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/55.0.2883.95 Mobile Safari/537.36",
	    'content-type': "application/json; charset=UTF-8",
	    'dnt': "1",
	    'referer': "http://apps.taipei/AppList.aspx?listid=divHotApp",
	    'accept-encoding': "gzip, deflate",
	    'accept-language': "en-US,en;q=0.8,zh-CN;q=0.6,zh-TW;q=0.4",
	    'cookie': "Language=zh-TW",
	    'cache-control': "no-cache",
	    'postman-token': "cb83583e-adff-bf19-b919-7b2aa6c7c17b"
    }

	conn.request("POST", "/AppList.aspx/GetAppsList", payload, headers)

	res = conn.getresponse()
	data = res.read()
	decoded_string = data.decode("utf-8").encode(sys.stdin.encoding, 'replace').decode(sys.stdin.encoding)
	return decoded_string

def load_json(decoded_string):
	return json.loads(decoded_string)

def test_app(app):
	app_name = app["name"]

	android_status = test_android(app)
	ios_status = test_ios(app)

	result = generate_result(android_status, ios_status)
	print(result + ' ' + app_name )

def generate_result(android_status, ios_status):
	failed = [name for status, name in zip([android_status, ios_status], ("Android", "iOS")) if not status]
	result = ','.join(failed)
	if (android_status and ios_status) == True:
		return green_text("[ Passed ]")
	else:
		return red_text("[ Failed: " + result + "]")

def test_android(app):
	if app["androidlink"] == "":
		return True

	return test_link_response(app["androidlink"])

def test_ios(app):
	if app["ioslink"] == "":
		return True

	return test_link_response(app["ioslink"]) # and test_app_name(app["ioslink"], app["name"])

def test_link_response(link):
	link_object = app_link(link)
	conn = http.client.HTTPSConnection(link_object.get_host())
	conn.request("HEAD", "{}?{}".format(link_object.get_path(), link_object.get_query()))
	res = conn.getresponse()
	if res.status == 200:
		return True
	else:
		print("Bad link for {}: ({}) {}".format(link, res.status, res.reason))
		return False

def test_app_name(link, app_name):
	link_object = app_link(link)
	conn = http.client.HTTPSConnection(link_object.get_host())
	conn.request("GET", "{}?{}".format(link_object.get_path(), link_object.get_query()))
	res = conn.getresponse()
	data = res.read(500)
	decoded_string = data.decode("utf-8").encode(sys.stdin.encoding, 'replace').decode(sys.stdin.encoding)

	regex = re.compile('<title>(.*?)</title>', re.IGNORECASE|re.DOTALL)

	return True

if __name__ == "__main__":
	app_list_string = get_apps_list('divHotApp')
	app_list_json = load_json(app_list_string)["d"]
	test = load_json(app_list_json)

	num_cores = multiprocessing.cpu_count()
	Parallel(n_jobs=num_cores)(delayed(test_app)(app) for app in test)
