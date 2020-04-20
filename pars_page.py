import requests as rq
import re, json, lol_guide, telebot

def pars_mf(address):
	page = rq.get(address).text.split('<div class="view-guide__build__items">')
	reg_champ = r'<p>(.+?) Passive Ability</p>'
	if len(page) > 2:
		reg_title = r'champ-id.+?<span>(.+?)</span>'
	else:
		reg_title = r'<div class="top__title">\s+?<h2>.+?\t\t\t\t\t\t\t\t\t(.+?)</h2>'
	reg_data = r'<div class="view-guide__items__bar">\s*<span>(.*?)</span>\s*?</div>\s*?</div>'
	champion = re.search(reg_champ, page[1], flags=re.DOTALL).group(1)
	title = re.findall(reg_title, page[0], flags=re.DOTALL)
	for i in range(len(title)):
			title[i] = re.sub(r'/|\\', '; ', title[i])
			title[i] = re.sub(r'[*|:"><?]', ' ', title[i])
			title[i] = re.sub(r'&#039;', "'", title[i])
			title[i] = ''.join([s for s in title[i] if ord(s) in range(65536)])
	# print(title, champion)
	set_lists = []

	for i, data_text in enumerate(page[1:]):
		data = re.findall(reg_data, data_text, flags=re.DOTALL)
		item_obsolete = []
		set_list = [champion, title[i].strip()]
		for b in data:
			b = re.sub(r'&#039;', "'", b)
			items = []
			gp = re.search(r'^(.+?)</span>', b, flags=re.DOTALL).group(1)
			item_id = re.findall(r"ajax-tooltip {t:'Item',i:'(\d+)'}", b, flags=re.DOTALL)
			db_items = json.load(open('data/db_items.json'))
			for item in item_id:
				if db_items.get(item):
					items.append(db_items[item]['id'])
				else:
					# print(item)
					itim = lol_guide.item_url(item, b)
					item_obsolete.append((itim[0], lol_guide.Item_image(itim[1], master=None, mf=True))) #Вопрос по работе master
			set_list.append((gp, items)) #Формирование set_list
		set_list.append(item_obsolete)
		set_lists.append(set_list)
	return set_lists

def pars_page(address, source='mf'):
	if source == 'mf':
		return pars_mf(address)

if __name__ == '__main__':
	pg = 'https://www.mobafire.com/league-of-legends/build/9-23-orianna-mid-fallen3s-guide-to-orianna-511643'
	data = pars_page(pg, 'mf')
	for p in data:
		print(p)