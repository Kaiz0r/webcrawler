import requests
from bs4 import BeautifulSoup
import json
from os import path, system
import urllib.parse
from random import choice
class IMGUR:
	def __init__(self, client_id):
		self.payload = {
		'Authorization': f'Client-ID {client_id}'
		}
		
		self.search_url = "https://api.imgur.com/3/gallery/search/time/all/?q="
		self.gallery_url = "https://api.imgur.com/3/gallery/t/$TERM$/time/all/"
		self.reddit_url = "https://api.imgur.com/3/gallery/r/$TERM$/time/all/"	
		
	def search(self, term):
		resp = requests.get(f"{self.search_url}{term}", headers=self.payload).text
		return json.loads(resp)

	def getRandom(self, term):
		items = self.search(term)
		return choice(items['data'])
		
	def gallery(self, term):
		resp = requests.get(f"{self.gallery_url.replace('$TERM$', term)}", headers=self.payload).text
		return json.loads(resp)

	def reddit(self, term):
		resp = requests.get(f"{self.reddit_url.replace('$TERM$', term)}", headers=self.payload).text
		return json.loads(resp)

	def redditRandom(self, term):
		items = self.reddit(term)
		return choice(items['data'])
	
class Wolfram:
	def __init__(self, app_id):
		self.appid = app_id
		self.conv_id = ""
		
		self.url = "http://api.wolframalpha.com/v1/conversation.jsp?"
		self.simple_url = "http://api.wolframalpha.com/v1/simple?"
		
	def image(self, message):
		args = f"appid={self.appid}"
		args += f"&i={urllib.parse.quote(message)}"
		return requests.get(self.simple_url+args).content
	
	def send(self, message):
		args = f"appid={self.appid}"
		
		if self.conv_id != "":
			args += f"&conversationid={self.conv_id}"
			
		args += f"&i={urllib.parse.quote(message)}"
		
		r = requests.get(self.url+args).text
		msg = json.loads(r)
		if msg.get('error'):
			return msg['error']
		
		if self.conv_id == "":
			self.conv_id = msg['conversationID']
			
		return msg['result']


class Startpage:
	def __init__(self, useragent="Python3-Library"):
		self.useragent = useragent
		self.cache = {}
		
	def get(self, search_term):
		res = requests.get(f"https://www.startpage.com/do/search?lui=english&language=english&cat=web&query={urllib.parse.quote(search_term)}&nj=&anticache=316666").text
		data = json.loads(res)
		return data
	
	def search(self, search_term):
		if self.cache.get(search_term.lower(), None):
			print("Getting cached version.")
			return self.cache[search_term.lower()]
		payload = {
		'User-Agent':self.useragent
		}
		final_data = {'urls':[], 'descriptions':[], 'titles':[]}
		url = f"https://www.startpage.com/do/search?lui=english&language=english&cat=web&query={urllib.parse.quote(search_term)}"
		#https://www.startpage.com/do/search?lui=english&language=english&cat=web&query=deus+ex
		r = requests.get(url, headers=payload).text
		s = BeautifulSoup(r, 'html.parser')
		#print(s)
		results = s.find_all(['div'])

		for item in results:
			#print(item.get('class'))
			if item.get('class'):
				if "w-gl__result" in item.get('class'):
					#print(f"RESULT: {item.text.strip()}")
					final_data['titles'].append(item.find('h3').text.strip())
					
				if "w-gl__result" in item.get('class'):
					#print(f"RESULT SNIPPET: {item.text.strip()}")
					final_data['descriptions'].append(item.find('span').text.strip().split("\n\n")[0])
					
				if "w-gl__result" in item.get('class'):
					final_data['urls'].append(item.find('a').get('href'))
					
		sorted_data = []
		for i in range(0, len(final_data['urls'])):
			bundle_url = final_data['urls'][i]
			bundle_desc = final_data['descriptions'][i]
			bundle_title = final_data['titles'][i]
			print(f"TITLE: {bundle_title}")
			print(f"INFO: {bundle_desc}")
			print(f"URL: {bundle_url}")
			print("--------------")
			sorted_data.append({'url': bundle_url, 'description': bundle_desc, 'title': bundle_title})
		self.cache[search_term.lower()] = sorted_data 
		print(self.cache)
		return sorted_data
	
class Pokedex:
	def __init__(self, *, image_cache = "cache"):
		self.cache = {'pokemon': {}, 'type': {}, 'pokemon-species': {}}
		self.base_url = "https://pokeapi.co/api/v2/"
		self.image_cache = image_cache
		if not path.isdir(self.image_cache):
			system(f"mkdir {self.image_cache}")
			
	def get(self, _type, _search):
		try:
			return self.cache[_type.lower()][_search.lower()]
		except KeyError:
			new_url = f"{self.base_url}{_type.lower()}/{_search.lower()}/"
			res = requests.get(new_url).text
			try:
				self.cache[_type.lower()][_search.lower()] = json.loads(res)
				return json.loads(res)
			except Exception as e:
				return {'name': f"ERROR: {type(e)}", 'error': e}
	
	def getTypes(self, pokemon):
		if type(pokemon) == str:
			pokemon = self.pokemon(pokemon)
		
		s = []
		for item in pokemon['types']:
			s.append(item['type']['name'])
			
		return s
	
	def getSprite(self, pokemon):
		if type(pokemon) == str:
			pokemon = self.pokemon(pokemon)
			
		if not self.image_cache:
			print("No image cache is defined, can't save images.")
			return
		
		if path.isfile(self.image_cache+pokemon['name'].lower()+'.gif'):
			pass
		else:
			image_url = pokemon['sprites']['front_default']
			with open(self.image_cache+pokemon['name'].lower(), "wb") as file:
				response = get(image_url)
				file.write(response.content)
				
	def fetchType(self, type_name):
		return self.get('type', type_name)
	
	def typeEffectiveness(self, type_name):
		typeobj = self.get('type', type_name)
		
		effChart = {
			'double_damage_to': [],
			'double_damage_from': [],
			'half_damage_from': [],
			'half_damage_to': [],
			'no_damage_to': [],
			'no_damage_from': []
			}
		
		try:
			test = typeobj['damage_relations']['double_damage_to']
		except Exception as e:
			return {'name': type(e), 'error': e, 'dump': typeobj}
		
		for item in typeobj['damage_relations']['double_damage_to']:
			effChart['double_damage_to'].append(item['name'])

		for item in typeobj['damage_relations']['double_damage_from']:
			effChart['double_damage_from'].append(item['name'])
			
		for item in typeobj['damage_relations']['half_damage_from']:
			effChart['half_damage_from'].append(item['name'])
			
		for item in typeobj['damage_relations']['half_damage_to']:
			effChart['half_damage_to'].append(item['name'])

		for item in typeobj['damage_relations']['no_damage_to']:
			effChart['no_damage_to'].append(item['name'])
			
		for item in typeobj['damage_relations']['no_damage_from']:
			effChart['no_damage_from'].append(item['name'])			

		return effChart
	
	def fetchPokemon(self, pokemon_name):
		return Pokemon(self, self.get('pokemon', pokemon_name))
	
	def fetchSpecies(self, pokemon_name):
		return PokemonSpecies(self, self.get('pokemon-species', pokemon_name))

class PokemonSpecies:
	def __init__(self, dex, data):
		self.dex = dex
		self.data = data
		for item in self.data:
			setattr(self, item, self.data[item])
	
	def text(self, *, language='en', version=''):
		entries = self.flavor_text_entries
		results = []
		for item in entries:
			if item['language']['name'] == language:
				if version:
					if item['version']['name'] == version:
						results.append(item)
				else:
					results.append(item)
		
		return results
	
	def ftext(self, *, language='en', version=''):
		entries = self.flavor_text_entries
		results = []
		for item in entries:
			if item['language']['name'] == language:
				if version:
					if item['version']['name'] == version:
						results.append(item)
				else:
					results.append(item)
		
		return results[0]['flavor_text']
	
class Pokemon:
	def __init__(self, dex, data):
		self.dex = dex
		self.data = data
		for item in self.data:
			setattr(self, item, self.data[item])
	
		if self.species:
			self.species = self.dex.fetchSpecies(self.species['name'])
			
		self.types_list = []
		for item in self.types:
			self.types_list.append(item['type']['name'])
			
	def text(self):
		return self.species.ftext()
	
	def evolvesFrom(self):
		if self.species.evolves_from_species:
			return self.dex.fetchPokemon(self.species.evolves_from_species['name'])
	
	def sprite(self):
		self.dex.getSprite(self.name)
		
	#def species(self):
		#self.dex.fetchSpecies(self.species['name'])
		
	def spriteURL(self):
		return self.sprites['front_default']
	
	def getResists(self):
		res = []
		for item in self.types:
			for t in self.dex.typeEffectiveness(item['type']['name'])['no_damage_from']:
				res.append(t)
		return res
	
	def getDefends(self):
		res = []
		for item in self.types:
			for t in self.dex.typeEffectiveness(item['type']['name'])['half_damage_from']:
				res.append(t)
		return res	
	
	def getWeakness(self):
		res = []
		for item in self.types:
			for t in self.dex.typeEffectiveness(item['type']['name'])['double_damage_from']:
				res.append(t)
		return res		

class Wiki:
	def __init__(self):
		self.wikidata = "https://www.wikidata.org/w/api.php?"
		self.wikipedia = "https://en.wikipedia.org/w/api.php?"
		
	#Raw API call to retrieve entity information
	def data(self, search):
		res = json.loads(requests.get(f"{self.wikidata}action=wbsearchentities&format=json&search={urllib.parse.quote(search_term)}&language=en").text)
		try:
			_id = res['search'][0]['id']
			return self.dataId(_id)
		except IndexError:
			return None
		except KeyError:
			return None
	
	#Helper wrapper to get the description of any object input.
	def identify(self, obj):
		data = self.data(obj)
		for item in data['entities']:
			return data['entities'][item]['descriptions']['en']['value']
		
	#Same as .data but uses entity ID instead of searching by name
	def dataId(self, entityId):
		return json.loads(requests.get(f"{self.wikidata}action=wbgetentities&format=json&ids={entityId}").text)
	
	#Raw API call for opensearch protocol
	#Reformats the returned data because the way the API lays out the json is a bit strange
	def openSearch(self, value):
		data = json.loads(requests.get(f"{self.wikipedia}action=opensearch&search={value}").text)
		forms = {}
		ind = 0
		for item in data[1]:
			forms[item.lower()] = {'value':data[2][ind], 'url':data[3][ind]}
			ind += 1
		return forms
	
	#Helper wrapper for .openSearch to quickly get a summary of things.
	def summarize(self, value):
		try:
			return self.openSearch(value)[value]	
		except KeyError:
			return {'error': 'Invalid search.'}
	
	#Queries wikipedia, returning a list of page summaries.
	def query(self, search, markdown = True):
		ret = []
		data = json.loads(requests.get(f"{self.wikipedia}action=query&prop=extracts&format=json&exintro=&titles={search}").text)
		for item in data['query']['pages']:
			cleaned = data['query']['pages'][item]['extract']
			if markdown:
				cleaned = md(cleaned)
			ret.append({'title': data['query']['pages'][item]['title'], 'text': cleaned})
		
		return ret
	
class DuckDuckGo:
	def __init__(self, useragent="Python3-Library"):
		self.useragent = useragent
		
	def get(self, search_term):
		res = requests.get(f"https://api.duckduckgo.com/?q={search_term}&no_redirect=1&format=json&pretty=1&t=Python-library").text
		data = json.loads(res)
		return data
		
	def search(self, search_term):
		payload = {
		'User-Agent':self.useragent
		}
		final_data = {'results':[], 'snippets':[], 'urls': [], 'extras': {'snippets': [], 'urls': []}}
		url = f"https://duckduckgo.com/html?q={search_term}&t=ffab&atb=v162-6__&ia=web&iax=qa"
		r = requests.get(url, headers=payload).text
		s = BeautifulSoup(r, 'html.parser')
		#print(s)
		divs = s.find_all(['div', 'a'])
		#print(divs)
		for item in divs:
			#print(item.get('class'))
			if item.get('class'):
				if "results" in item.get('class'):
					#print(f"RESULT: {item.text.strip()}")
					final_data['results'].append(item.text.strip())
					
				if "result__snippet" in item.get('class'):
					#print(f"RESULT SNIPPET: {item.text.strip()}")
					final_data['snippets'].append(item.text.strip())
					
				if "result__url" in item.get('class'):
					#print(f"RESULT URL: {item.text.strip()}")	
					final_data['urls'].append(item.text.strip())
					
				if "result__extras" in item.get('class'):
					#print(f"RESULT EXTRA: {item.text.strip()}")
					final_data['extras']['snippets'].append(item.text.strip())
					
				if "result__extras__url" in item.get('class'):
					#print(f"RESULT EXTRA URL: {item.text.strip()}")
					final_data['extras']['urls'].append(item.text.strip())
		return final_data

class SCPSite:
	@staticmethod
	def search(term):
		base_url = f"http://www.scp-wiki.net/search:site/q/{term}"
		page = BeautifulSoup(requests.get(base_url).text, 'html5lib')
		result = None
		for div in page.find_all('div'):
			if div.get('class') and div.get('class')[0] == "search-results":
				result = div
		
		if not result:
			return None
		else:
			first = result.find_all('a')[0]
			return SCP(first.get('href'))
		
	@staticmethod		
	def fromURL(ext):
		base_url = f"http://www.scp-wiki.net/{ext}"
		return SCP(base_url)

class SCP:
	def __init__(self, url):
		self.url = url
		self.contents = []
		self.image = ""

		page = BeautifulSoup(requests.get(url).text, 'html5lib')
		self.title = page.find('head').find('title').text
		for div in page.find_all('div'):
			#print(div.get('id'))
			if div.get('id') and div.get('id') == "page-content":
				self.data = div
				
			if div.get('class') and div.get('class')[0] == "scp-image-block":
				self.image = div.find('img').get('src')

		for item in self.data.text.split('\n'):
			if item.strip():
				self.contents.append(item)
		
class ReverseImageSearch:
	def __init__(self, useragent="User-Agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:61.0) Gecko/20100101 Firefox/61.0"):
		self.useragent = useragent
	
	def get(self, img_url, count=0):
		url = "https://www.google.com/searchbyimage?hl=en-US&image_url="
		headers = {
		    'User-Agent': self.useragent,
		}

		return requests.get(f"{url}{img_url}&start={count}", headers=headers, allow_redirects=True).text

	def similar(self, img_url):
		q = self.get(img_url)
		soup = BeautifulSoup(q, 'html.parser')

		results = []

		for similar in soup.findAll('div', attrs={'rg_meta'}):
			results.append(json.loads(similar.get_text())['ou'])

		return results

	def basic(self, img_url):
		q = self.get(img_url)
		soup = BeautifulSoup(q, 'html.parser')
		for item in soup.findAll('a', attrs={'class':'fKDtNb'}):
			result = item.get_text()
		return result

	def related(self, img_url):
		count = 0
		keep_searching = True
		while keep_searching:
			q = self.get(img_url, count)
			soup = BeautifulSoup(q, 'html.parser')

			results = {
				'links': [],
				'descriptions': [],
			}
			for div in soup.findAll('div', attrs={'class':'rc'}):
				sLink = div.find('a')
				results['links'].append(sLink['href'])

			for desc in soup.findAll('span', attrs={'class':'st'}):
				results['descriptions'].append(desc.get_text())

			for link, description in zip(results["links"], results["descriptions"]):
				ret = {
					"link": link,
					"description": description
				}
				yield ret
			count += 10
			check_end_cur = soup.find("td", attrs={"class": "cur"})
			try:
				test = check_end_cur.next_sibling.td
			except AttributeError:
				keep_searching = False

class Gamefaqs:
	"""Gamefaqs.search("name") -> web scrape 
	view-source:https://gamefaqs.gamespot.com/search?game=deus+ex
	-> returns the url ID which is then passed to the parser class for a Game page"""
	def __init__(self):
		self.base_url = "https://gamefaqs.gamespot.com/search?game="
		self.headers = {
		'User-Agent':'Mozilla/5.0 (X11; Python3) Gecko/20100101 Firefox/52.0'
		}
		self.cache = {}
		
	def search(self, game, *, console=""):
		if self.cache.get(game):
			print("Pulling from cache...")
			return self.cache[game]
		
		url = f"{self.base_url}{game.replace(' ', '+')}"
		print(f"Searching {url}")
		
		searchpage = BeautifulSoup(requests.get(url, headers=self.headers).text, 'html5lib')
		#print(searchpage)
		ls = searchpage.find_all('div')

		for item in ls:
			#print(item)
			if item.get('class'):
				if item.get('class')[0] == "sr_product_name":
					nurl = item.a.get('href')
					#print(nurl)
					if console:
						if console == nurl.split("/")[1]:
							gobj = Game(nurl)
							self.cache[game] = gobj
							return gobj
					else:
						gobj = Game(nurl)
						self.cache[game] = gobj
						return gobj
					
		raise Exception("No game was found.")
		
class Game:
	def __init__(self, gamepage_url):
		self.url = f"https://gamefaqs.gamespot.com{gamepage_url}"
		self.headers = {
		'User-Agent':'Mozilla/5.0 (X11; Python3) Gecko/20100101 Firefox/52.0'
		}
		
		print(f"Parsing {self.url}")
		self.html = BeautifulSoup(requests.get(self.url, headers=self.headers).text, 'html5lib')
		self.cache = {}
		self.cheatsurl = f"{self.url}/cheats"
		self.faqsurl = f"{self.url}/faqs"
		self.reviewsurl = f"{self.url}/reviews"
		self.imagesurl = f"{self.url}/images"
		self.answersurl = f"{self.url}/answers"
		self.videosurl = f"{self.url}/videos"
		
		self.title = self.html.find('title').text

	def news(self):
		if self.cache.get('news'):
			print("Getting cache...")
			return self.cache['news']
		
		ls = self.html.find_all()
		searching = False
		found = []
		for item in ls:
			
			if item.get('class'):
				#print(item.get('class'))
				if item.get('class')[0] == "head":
					searching = False
					
				if searching:
					if item.get('class')[0] != 'name' and item.get('class')[0] != 'body' and item.get('class')[0] != 'pod' and item.get('class')[0] != 'sub':
						found.append(item)
					
				if item.text == "Game News":
					#print(item)
					searching = True
		msg = ""
		for item in found:
			#print(item)
			msg += f"{item.text.split('Updated')[0]}\n"
		
		self.cache['news'] = msg
		return msg
	
	def description(self):
		if self.cache.get('description'):
			print("Getting cache...")
			return self.cache['description']
		
		ls = self.html.find_all('div')

		for item in ls:
			if item.get('class') == ['body', 'game_desc']:
				
				#print(item.text)
				self.cache['description'] = item.text
				return item.text
			
	def ratings(self):
		pass
	
	def details(self):
		if self.cache.get('details'):
			print("Getting cache...")
			return self.cache['details']
		dets = ""
		ls = self.html.find_all('div')

		for item in ls:
			if item.get('class') == ['pod', 'pod_gameinfo']:
				print(item)
				for thing in item.find_all(['h2', 'li']):
					if thing.get_text(' ', strip=True) != "Game Detail":
						print(thing.get_text(' ', strip=True))
						dets += f"{thing.get_text(' ', strip=True)}\n"
					
		self.cache['details'] = dets
		return dets
	
	def trivia(self):
		if self.cache.get('trivia'):
			print("Getting cache...")
			return self.cache['trivia']
		
		trivs = self.html.find_all('p')
		for item in trivs:
			if item.get('class'):
				if item.get('class')[0] == 'trivia':
					self.cache['trivia'] = item.text
					return item.text
	
	def cheats(self):
		pass
	
	def faqs(self):
		pass
	
	def reviews(self):
		pass
	
	def images(self):
		pass
	
	def answers(self):
		pass	
