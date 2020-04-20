import re, json, os
from requests import get

############################################################################################
base = get('http://www.mobafire.com/league-of-legends/items')
it_base = re.findall(
    r'league-of-legends/item/.+?-(\d+)".+?LoL Item: (.+?)" />',
    base.text, flags=re.DOTALL
    )
ib_site = {n.lower().replace('&#039;', "'"): d for d, n in it_base}    #{name предмета с сайта: id предмета с сайта}
############################################################################################
f = open('data/USitem.json')
items = json.load(f)
item_dict = items['data']   #Словарь предметов, ключ: id предмета
############################################################################################
rem_list = []
for item in item_dict:
    if not item_dict[item]['maps']['11']:
        rem_list.append(item)
for item in rem_list:
    item_dict.pop(item)     #Удаление из словаря предметов не используемых в Ущелье Призывателей (maps: 11)
############################################################################################
id_keys = sorted(list(item_dict.keys()))
id_name = {Id: str(item_dict[Id]['name']).lower() for Id in id_keys}        #{id-item Лиги: name-item Лиги}
############################################################################################
for d in id_name:                       #Убирает различия имен сайта и базы Лиги
    if id_name[d][-9:] == '(trinket)':
        id_name[d] = id_name[d][:-10]
############################################################################################
L = []      #Пара (имя, id)
N = []      #Список имен
D = []      #Дублирующие имена
for k, n in id_name.items():
    L.append((n, k))
    N.append(n)
double = [(n, k) for n, k in L if N.count(n) > 1]   #Пара (имя, id), содержит только дублирующие имена
for d in double:
    D.append(d[1])
############################################################################################
for k, n in id_name.items():
    if ib_site.get(n):
        if k in D: continue
        id_name[k] = [n, ib_site[n]]
id_name_site = {}                       #Словарь с ключами id-item сайта, в значении список из имени и id-item лиги
for k, n in id_name.items():
    if isinstance(n, list):
        id_name_site[n[1]] = {'name': n[0], 'id': k}
############################################################################################
update = {
    '329': {'name': 'enchantment: bloodrazor', 'id': '1419'},
    '328': {'name': 'enchantment: bloodrazor', 'id': '1416'},
    '320': {'name': 'enchantment: runic echoes', 'id': '1414'},
    '321': {'name': 'enchantment: runic echoes', 'id': '1402'},
    '277': {'name': 'enchantment: warrior', 'id': '1400'},
    '273': {'name': 'enchantment: warrior', 'id': '1412'},
    '275': {'name': 'enchantment: cinderhulk', 'id': '1401'},
    '271': {'name': 'enchantment: cinderhulk', 'id': '1413'},
    '217': {'name': "mercury's treads", 'id': '3111'},
    '232': {'name': 'boots of swiftness', 'id': '3009'},
    '170': {'name': 'health potion', 'id': '2003'},
    '163': {'name': "archangel's staff", 'id': '3003'},
    '157': {'name': 'muramana', 'id': '3004'}
    }                                   #Добавление элементов вручную
id_name_site.update(update)
############################################################################################
with open('data/db_items.json', 'w') as f:   #Запись в файл базы предметов с ключами id-item сайта
    json.dump(id_name_site, f)
############################################################################################
if __name__ == '__main__':
    print(len(id_name_site))
    D.sort()
    for n in D:
        print(id_name[n], item_dict[n]['gold'])
        print()