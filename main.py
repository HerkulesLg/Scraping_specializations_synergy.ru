import requests
import json
import time
from bs4 import BeautifulSoup

# Request to site and response code of page to scrap.
def request_main_site():
	global head
	url = 'https://synergy.ru/'
	head = {'USER-AGENT':
		'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/100.0.4896.160 YaBrowser/22.5.4.904 Yowser/2.5 Safari/537.36'
			}
	req = requests.get(url, headers=head)
	src = req.text
	return src # Returns html code to main().

# Gets href links from navigation blocks.
def navigation_href(src):
	navigation_links = []
	for i in src:
		links = i.get('href')
		navigation_links.append('https://synergy.ru/' + links)
	return navigation_links # Returns links in list to main()

# Clear data from non needed info.
def clear_form_study(triggers):
	new_form_study = []
	form_study = triggers[1].find_all('span')
	del form_study[0]
	if len(form_study) == 1:
		form_study = form_study[0].text
		return form_study
	elif len(form_study) >= 2:
		for u in form_study:
			new_form_study.append(u.text)
		return ','.join(new_form_study)

# Clear string from <0xa0>.
def clear_name(name):
	if ' ' in name:
		name = name.replace(' ', ' ')
	return name

# Scraping.
def scraping(src):
	# Set main blocks.
	col = {}
	bac = {}
	spc = {}
	mag = {}
	vvo = {}
	asp = {}
	blocks = [col, bac, spc, mag, vvo, asp] # United for a comfortable iteration
	blocks_name = ['col', 'bac', 'spc', 'mag', 'vvo', 'asp'] # List to iterate names in progress bar
	block = 0 # Index setter. 
	# Data Loss guard.
	try:
		for links in src: #Get links of specializations on each navigation page.
			getrequest_links = requests.get(links, headers=head).text
			soup = BeautifulSoup(getrequest_links, 'lxml')
			all_items = soup.find('div', class_="programs__inner")
			
			for href_links in all_items: #Gets main site links of specializations from brief cards.
				href_link_specialization = 'https://synergy.ru' + href_links.get('href')
				main_page_specialization = requests.get(href_link_specialization, headers=head).text
				soup = BeautifulSoup(main_page_specialization, 'lxml')
				# iterate correctly non-standart pages.
				try:
					specialization = soup.find('div', class_="wrapper").find('h1').text
					specialization = clear_name(specialization) # Clear string from <0xa0>.
					triggers = soup.find('section', class_="section program-triggers").find('div',class_="swiper-wrapper").find_all('div')
					form_study = clear_form_study(triggers) # Clear data from non needed info.
					time_study = triggers[2].text.replace('Срок','').strip()
				except BaseException as ex:
					# print(repr(ex))
					specialization = soup.find('h1', class_="program-top__title").text
					triggers = soup.find_all('span', class_="block-top__triggers-text")
					form_study = triggers[1].text.replace('Форма обучения ','').strip()
					time_study = triggers[0].text.replace('Срок обучения ','').strip()
				full_info = {specialization: [form_study, time_study]}
				blocks[block].update(full_info) # Updates dict of blocks
				print(f'Добавил {specialization} из блока {blocks_name[block]}') # Progress bar.
			block += 1
			print(f'Отработано блоков {block}\\6')
		all_info = {'col':col, 'bac':bac, 'spc':spc, 'mag':mag, 'vvo':vvo, 'asp':asp} # Saves blocks data in dict to return.
		return all_info

	except Exception as ex:
		print(repr(ex))

	finally:
		return all_info

# Final save json with info 
def save_json(scrap_info):
	with open('D:\\GitHub\\Scraping_specializations_synergy.ru\\data.json', 'w', encoding='utf-8') as file:
		json.dump(scrap_info, file, indent=4, ensure_ascii=False)

def main():
	start_time = time.time()
	main_site = BeautifulSoup(request_main_site(), 'lxml') # Request to site and response code of page to scrap.
	navigation_block = main_site.find('div', class_="nav-levels").find_all('a') # Finds navigation blocks on the site.
	navigation_links = navigation_href(navigation_block) # Gets href links from navigation blocks.
	del navigation_links[0:2] # Deletes hiden links from list not needed in scraping.
	del navigation_links[6:9] # Deletes mba, cources and school blocks not needed in scraping.
	scrap_info = scraping(navigation_links) # Start scraping. 
	save_json(scrap_info) # Saves scraping info to json.
	print("--- %s seconds ---" % (time.time() - start_time))

if __name__ == '__main__':
	main()
