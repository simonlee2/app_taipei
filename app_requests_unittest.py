import requests
from urllib.parse import urlparse
from timeit import default_timer as timer
import sys
import json
import re
import unittest

class AppLink(object):
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

def get_apps_list(app_list_id):
	url = "http://apps.taipei.gov.tw/AppList.aspx/GetAppsList"

	payload = "{'AppListID':'divHotApp','KeyWord':''}"
	headers = {
	    'host': "apps.taipei.gov.tw",
	    'connection': "keep-alive",
	    'content-length': "38",
	    'cache-control': "no-cache",
	    'accept': "application/json, text/javascript, */*; q=0.01",
	    'origin': "http://apps.taipei.gov.tw",
	    'x-requested-with': "XMLHttpRequest",
	    'user-agent': "Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/54.0.2840.71 Safari/537.36",
	    'content-type': "application/json; charset=UTF-8",
	    'referer': "http://apps.taipei.gov.tw/AppList.aspx?listid=divHotApp",
	    'accept-encoding': "gzip, deflate",
	    'accept-language': "zh-TW,zh;q=0.8,en-US;q=0.6,en;q=0.4",
	    'cookie': "_gat=1; _ga=GA1.3.281553695.1477958916",
	    'postman-token': "dc0ce627-2983-0773-de4d-eb8073a6a214"
	    }

	response = requests.request("POST", url, data=payload, headers=headers)

	decoded_string = response.text.encode(sys.stdin.encoding, "replace").decode(sys.stdin.encoding)
	return decoded_string

def load_json(decoded_string):
	return json.loads(decoded_string)

def test_app(app):
	app_name = app["name"]
	print("Testing {}...".format(app_name))

	android_status = test_android(app)
	ios_status = test_ios(app)

	if android_status == False:
		print("Android link failed")

	if ios_status == False:
		print("iOS link failed")

	if (android_status and ios_status) == True:
		print("Passed.")
	else:
		print("Failed.")

def test_android(app):
	if app["androidlink"] == "":
		return True
	
	return test_link_response(app["androidlink"])

def test_ios(app):
	if app["ioslink"] == "":
		print("No iOS link")
		return True

	return test_link_response(app["ioslink"])

def test_link_response(link):
	link_object = AppLink(link)
	r = requests.get(link)
	
	if r.status_code == 200:
		print(r.history)
		return True
	else:
		print("Bad link for {}: ({})".format(link, r.status_code))
		return False

def test_app_name(link, app_name):
	link_object = app_link(link)
	conn = http.client.HTTPSConnection(link_object.get_host())
	conn.request("GET", "{}?{}".format(link_object.get_path(), link_object.get_query()))
	res = conn.getresponse()
	data = res.read(500)
	decoded_string = data.decode("utf-8").encode(sys.stdin.encoding, 'replace').decode(sys.stdin.encoding)

	print(decoded_string)
	regex = re.compile('<title>(.*?)</title>', re.IGNORECASE|re.DOTALL)
	
	print(regex)
	return True

class TestApp(unittest.TestCase):

	def __init__(self, test_name, app):
		self.app = app
		super(TestApp, self).__init__(test_name)

	def test_link_response(self, link):
		r = requests.get(link)

		self.assertEqual(200, r.status_code, msg = "Bad link for {}: {}".format(link, r.status_code))

	def test_android(self):
		if app["androidlink"] == "":
			self.assertTrue(True)
			return

		self.test_link_response(app["androidlink"])


	def test_ios(self):
		if app["ioslink"] == "":
			self.assertTrue(True)
			return

		self.test_link_response(app["ioslink"])

if __name__ == "__main__":
	app_list_string = get_apps_list('divHotApp')
	app_list_json = load_json(app_list_string)["d"]
	test = load_json(app_list_json)

	# map each app to a test case
	app = test[0]


	# add all test cases to a test suite
	suite = unittest.TestSuite()
	android_tests = [TestApp('test_android', app) for app in test]
	ios_tests = [TestApp('test_ios', app) for app in test]
	suite.addTests(android_tests)
	suite.addTests(ios_tests)
	unittest.TextTestRunner(verbosity=2).run(suite)
	# run test suite

	# output report

	# start = timer()
	# for app in test:
	# 	test_app(app)

	# end = timer()
	# print(end - start)
