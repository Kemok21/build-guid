import requests, re

url = 'http://ddragon.leagueoflegends.com/'
vs = requests.get(url + 'realms/na.js').text
version = re.search(r'item":"(.+?)"', vs).group(1)

def update():
	dt_ru = requests.get('{}cdn/{}/data/ru_RU/item.json'.format(url, version)).text
	dt_en = requests.get('{}cdn/{}/data/en_US/item.json'.format(url, version)).text
	chn = requests.get('{}cdn/{}/data/ru_RU/champion.json'.format(url, version)).text
	with open('data/RUitem.json', 'w') as f:
		f.write(dt_ru)
	with open('data/USitem.json', 'w') as f:
		f.write(dt_en)
	with open('data/champion.json', 'w') as f:
		f.write(chn)

print('Update process...')
update()
print('Finished')
input('--Press Enter--')