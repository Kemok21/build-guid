# build-guid
App for operating system Windows.

The app is designed to create files-guides for League of Legends.
The app receives a list of guides from the site http://www.mobafire.com.

To view the list of guides, enter name of the champion in text field, then press enter or "Show guides" button.
A list of guides for the given champion will appear in field below.

To view the guide, You need to click on the "show guide" button.
A list of items included in this guide appears in the field.

To export the selected guide to a file, click the "Export to file" button.

To get the file-guide in the required directory
(...\League of Legends\Config\Champions\{champion}\Recommended\),
You need to specify the path to the League of Legends in [settings->path].
By default, the file-guide is saved in the app directory.

After the first start, the app creates a setting file.

Images of objects and champions are taken from the web service 'http://ddragon.leagueoflegends.com/cdn/6.24.1/img/'

For one launch, the app makes 1-2 requests at 'https://ru.api.riotgames.com/lol/static-data/v3/items'
and 1 request at 'https://ap.api.riotgames.com/lol/ Static-data/v3/champions'.

The app creates 4 temporary files in the 'C:\Users\{User}\AppData\Local\Temp' directory : 'ru_RUitem.json', 'en_USitem.json', 'db_items.json' and 'lol.ico'

The app has Russian and English localization
