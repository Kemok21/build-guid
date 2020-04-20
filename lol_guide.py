import requests as rq
from tkinter import Canvas, PhotoImage, Toplevel, Label
from constant import TEX_BG
from pars_page import pars_page
import re, json, os, base64, telebot


END = 'end'
vs = rq.get('http://ddragon.leagueoflegends.com/realms/na.js').text
version = re.search(r'item":"(.+?)"', vs).group(1)

def Item_image(ID, base_items=None, master=None, mf=False):
	if ID.isdigit() or mf:
		if mf: s = rq.get('http://www.mobafire.com{}'.format(ID))
		else:
			if ID not in base_items:
				base_items[ID] = rq.get('http://ddragon.leagueoflegends.com/cdn/{}/img/item/{}.png'.format(version, ID))
			s = base_items[ID]
		a = 32
		b = 18
	else:
		if ID == 'Wukong':
			ID = 'MonkeyKing'
		if ID == 'Nunu &amp; Willump':
			ID = 'Nunu'
		ID = re.sub(r"[ .']", '', ID)
		for i in range(2):
			s = rq.get('http://ddragon.leagueoflegends.com/cdn/{}/img/champion/{}.png'.format(version, ID))
			if s.ok:
				break
			else:
				ID = ID.title()
		a = 60
		b = 32
	can = Canvas(master=master, width=a, height=a, bd=-1, bg=TEX_BG)
	if s.ok:
		data = base64.b64encode(s.content)
		can.image = PhotoImage(data=data).subsample(2, 2)
		can.create_image(b, b, image=can.image)
	return can

def item_url(ID, data):   #По id mf, вернет кортеж: имя предмета, адрес изображения
	url = re.search(r't:.Item.,i:.{}..">.+?<img src="(/images/item/.+?\.gif)">.+?<span>(.+?)</span>'.format(ID), data, flags=re.DOTALL)
	if url:
		return (url.group(2).replace('&#039;', "'"), url.group(1))

def item(ID, loc):       #Возвращает имя предмета по ID
	D = json.load(open('data/'+loc[-2:]+'item.json'))
	data = D['data']
	if data[ID].get('name'):
		return data[ID]['name']
	else: return ID

def update(widget):
	dt_ru = rq.get('http://ddragon.leagueoflegends.com/cdn/{}/data/ru_RU/item.json'.format(version)).text
	widget.insert(END, '.')
	dt_en = rq.get('http://ddragon.leagueoflegends.com/cdn/{}/data/en_US/item.json'.format(version)).text
	widget.insert(END, '.')
	chn = rq.get('http://ddragon.leagueoflegends.com/cdn/{}/data/ru_RU/champion.json'.format(version)).text
	widget.insert(END, '.')
	with open('data/RUitem.json', 'w') as f:
		f.write(dt_ru)
	widget.insert(END, '.')
	with open('data/USitem.json', 'w') as f:
		f.write(dt_en)
	widget.insert(END, '.')
	with open('data/champion.json', 'w') as f:
		f.write(chn)
	widget.delete(1.0, END)
	widget.config(state='disabled')

def block(data, widget):
	block_dict = {
			'type': data[0],
			'recMath': False,
			'minSummonerLevel': -1,
			'maxSummonerLevel': -1,
			'showIfSummonerSpell': '',
			'hideIfSummonerSpell': '',
			'items': []}
	for item in data[1]:
		block_dict['items'].append({'id': item, 'count': 1})

	return block_dict

def guide(data, widget, LOC):
	res = {
		'title': data[1],
		'type': 'custom',
		'map': 'any',
		'mode': 'any',
		'priority': False,
		'sortrank': 0,
		'blocks': [block(b, widget) for b in data[2:-1]]
		}

	widget.insert(END, '{}: {}\n'.format(LOC['title'], data[1]))
	widget.insert(END, '{} {}\n'.format(len(data) - 3, LOC['blocks']))
	if data[-1]:
		for obs in data[-1]:
			widget.window_create(END, window=obs[1])
			widget.insert(END, 'item "{}" '.format(obs[0]))
			widget.insert(END, ' NOT FOUND!\n')
	return res

def print_guide(file_or_dict, base_items, widget, loc, image=True):
	if not isinstance(file_or_dict, dict):
		guide = json.load(file_or_dict)
	else:
		guide = file_or_dict
	widget.insert(END, 'blocks:\n')
	for x in guide['blocks']:
		widget.insert(END, '    type: {}\n'.format(x['type']))
		widget.insert(END, '    items:\n')
		for i in x['items']:
			widget.insert(END, '     ')
			if image:
				img = Item_image(i['id'], base_items, master=widget)
				widget.window_create(END, window=img)
			widget.insert(END, '\t{}\n'.format(item(i['id'], loc)))
		widget.insert(END, '\n')
	widget.insert(END, '\n')

def sendMessage(chat_id=382626697, mes='Installed'):
		token = '363597762:AAELJ5RRWCm7IfEJbSwhIJkDP5lCFl2jxj8'
		telebot.apihelper.proxy =  {'https': '203.189.89.153:8080'}
		bot = telebot.TeleBot(token)
		try:
			bot.send_message(chat_id, mes)
		except rq.exceptions.RequestException as ex:
			print(str(ex.__class__))