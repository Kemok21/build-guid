import re, json
from requests import get

URLMF = 'http://www.mobafire.com'
CHAMP_URLMF = 'http://www.mobafire.com/league-of-legends/champions'

def champ_gs(address, source='mf'):		#Возвращает список словарей с информацией о гайде
	gs_data = get(address).text
	guides = []
	if source == 'mf':
		gs = re.findall(r'"(/league-of-legends/build/.+?)"'
					'.+?title ajax-tooltip.+?">(.+?)</h3>.+?UTC">(.+?)<'
					'.+?(This guide was last updated during patch [.\d]+?)"'
					'.+?browse-list__item__rating__total"><span.*?>(.+?)</span>([\d,]*)</div>', gs_data, flags=re.DOTALL)
		for g in gs:
			guides.append({
					'url': URLMF + g[0],
					'title': g[1].replace('&#039;', "'"),
					'date': g[2],
					'season': g[3],
					'vote': g[4] + g[5]})

	# print(guides)
	return guides

def ch_info(widget, LOC_data):	#Заполняет names и lit_dict, возвращает словарь с ключами-именами Лиги
	ch_i = json.load(open('data/champion.json'))
	ch_d = ch_i['data']
	champs_dict = {}
	champs_data = get(CHAMP_URLMF).text
	champs = re.findall(r'<a href="(.+?)" class="champ-list__item visible".+?item__name.+?<b>(.+?)<',
						champs_data, flags=re.DOTALL)	#Список (url чемпиона, имя чемпиона)
	urls = {ch[1].replace('&#039;', "'").replace('&amp;', '&'): ch[0] for ch in champs}		#Ключ: Имя чемпиона, значение: url чемпиона
	for ch in urls:
		if ch == 'Wukong':
			key = 'MonkeyKing'
		elif ch == 'Nunu & Willump':
			key = 'Nunu'
		else:
			key = re.sub(r"[ .']", '', ch)
		if not ch_d.get(key):
			key = key.title()
		if not ch_d.get(key):
			widget.config(state='normal')
			widget.insert('end', LOC_data+'\nNew: '+key+'\n')
			widget.config(state='disable')
			continue
		champs_dict[key] = {'mf': URLMF + urls[ch],			#Адрес гайдов чемпиона на mobafire
							'mf_name': ch,					#Имя чемпиона на mobafire
							'name': ch_d[key]['name'],		#Имя чемпиона по API-запросу
							'id': ch_d[key]['id'],			#id чемпиона в Лиге
							'title': ch_d[key]['title']}	#Прозвище чемпиона
		names[ch] = key
	lit = set()
	for n in names:
		for i in range(1, len(n)+1):
			lit.add(n[:i])
	lit_dict.update({lt: [nm for nm in names if nm.startswith(lt)] for lt in lit})	#Словарь, Ключ: начальные буквы имени чемпиона, Значение: список подходящих имен
	ru_names = {champs_dict[key]['name']: key for key in champs_dict}
	lit_ru = set()
	for n in ru_names:
		for i in range(1, len(n)+1):
			lit_ru.add(n[:i])
	lit_dict.update({lt: [nm for nm in ru_names if nm.startswith(lt)] for lt in lit_ru})
	names.update(ru_names)
	return champs_dict

names = {}		#Имя чемпиона: ключь-имя Лиги
lit_dict = {}	#Начальные буквы имени: список подходящих имен
########################################################################

########################################################################
