import os.path
import hashlib
import requests
import shutil
import html
import re

USE_WEBCACHE = False
WEBCACHE_PATH = os.path.join(os.path.dirname(__file__), 'webcache')
CS_LOWERS = 'aáäbcčdďeéěfghiíjklĺľmnňoóôpqrŕřsštťuúůvwxyýzž'
CS_UPPERS = 'ÁÄBCČDĎEÉĚFGHIÍJKLĹĽMNŇOÓÔPQRŔŘSŠTŤUÚŮVWXYÝZŽ'


def download(url, method='GET', data=None, url_extension=''):
	"""Downloads and returns content from the given URL.

	If global variable USE_WEBCACHE is True, caches all received content
	and uses cached file for subsequent requests.

	In case of POST request use `url_extension` to make URLs of requests
	with different data unique.
	"""
	if USE_WEBCACHE:
		key = method.lower() + url + url_extension
		hash = hashlib.md5(key.encode('utf-8')).hexdigest()
		pathname = os.path.join(WEBCACHE_PATH, hash)
		if os.path.exists(pathname):
			with open(pathname, 'r', encoding='utf-8', newline='') as f:
				return f.read()

	if method.upper() == 'GET':
		resp = requests.get(url)
	elif method.upper() == 'POST':
		resp = requests.post(url, data)
	resp.raise_for_status()

	if USE_WEBCACHE:
		if not os.path.exists(WEBCACHE_PATH):
			os.makedirs(WEBCACHE_PATH)
		with open(pathname, 'w', encoding='utf-8', newline='') as f:
			f.write(resp.text)

	return resp.text


def clear_cache():
	"""Clears the cache directory."""
	shutil.rmtree(WEBCACHE_PATH + '/', ignore_errors=True)


def plaintext(obj, skip=None):
	"""Checks all fields of `obj` structure and converts HTML entities
	to the respective characters, strips leading and trailing
	whitespace and turns non-breakable spaces to normal ones.

	If `obj` is a dictionary, a list of keys to skip may be passed
	in the `skip` argument.
	"""
	if isinstance(obj, str):
		obj = html.unescape(obj).replace('\xa0', ' ').strip()
		obj = re.sub(r'\s{2,}', ' ', obj)
	elif isinstance(obj, list):
		for i, v in enumerate(obj):
			obj[i] = plaintext(v)
	elif isinstance(obj, dict):
		for k, v in obj.items():
			if isinstance(skip, (tuple, list)) and k in skip: continue
			obj[k] = plaintext(v)
	return obj


def clear_hyphens(text, eol=''):
	"""Clear hyphen characters from the text.
	The hyphen is removed only if followed by the given end-of-line
	mark (default: empty)."""
	pattern = r'([%s])-%s([%s])' % (CS_LOWERS, eol, CS_LOWERS)
	result = re.sub(pattern, r'\1\2', text)
	return result
