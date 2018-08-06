from collections import defaultdict as dt
import os
from flask import Flask, render_template, redirect, url_for, request, abort, flash, jsonify
import sys, requests, json, os
import urllib
import requests
from bs4 import BeautifulSoup
from newspaper import Article
import nltk


app = Flask (__name__)

# @app.route("/getSummary")
# def getSummary():
# 	string = request.args.get('url')
# 	#endpoint = "https://api.diffbot.com/v3/article"
# 	endpoint = "https://api.embedly.com/1/extract"
# 	key = "9722f40657d946b097b3a623d70d6d97"
# 	#developer_token = "7dc3f90609b9a4b916680182d9ae219b"
# 	response = requests.get(endpoint, {'url': "http://www.viralnova.com/woman-wears-mascara-bed-25-years-never-washes-face-see-eyelid/", 'key': key})
# 	return jsonify(response.text)


@app.route("/")
def home():
	return render_template("home.html")

@app.route("/GetCategory/", methods = ["POST"])
def getCategory():
	
	url = request.form['title']

	link = urllib.request.urlopen(url)
	
	html_soup = BeautifulSoup(link, 'html.parser')

	get_header_one = str(html_soup.find('h1').string)

	if html_soup.find('h2'):	
		
		get_header_two = str(html_soup.find('h2').string)
		
		if (len(get_header_one) > len(get_header_two)):
			
			string = get_header_one 
		
		else:
			
			string = get_header_two
	else:
		
		string = get_header_one

	file = open ("static/Classifier.csv", "rt")

	mydict = dt(list)

	asc_set = {'.', ',', '?', '/', ':', ';', '{', '}', '[', ']', '+', '=', ')', '(', '*', '&', '^', '%', '$', '#', '@', '!', '~', '`', '1', '2', '3', '4','5', '6', '7', '8', '9'}
	
	for c in file.readlines():
		
		s = c.split(",")
		
		if len(s)>1 and len(s[1])==1:
			
			title = s[0]
			
			category = s[1]
			
			mydict[category].extend(set(title.split(" ")))

	for k,v in mydict.items():
		
		mydict[k] = set(v)

	file.close()

	article = Article(url)

	article.download()

	article.parse()

	article.nlp()

	summary = article.summary

	keywords = article.keywords
	
	# print (article.text)

	# print ("Article: ",article.summary)

	# print ("Keywords: ", article.keywords)

	
	max_length, category = 0, "other"
	
	category_list = list()

	category_dict = dict()

	for k,v in mydict.items():

		matched_words = set(keywords).intersection(v)
		
		length = len(matched_words)
		
		print (k, matched_words)

		category_dict[k] = length

	max_value = max(category_dict.values())


	for k, v in category_dict.items():
		
		if v == max_value:
			
			if k == "e":
				
				category_list.append("Entertainment")
			
			elif k == "t":
				
				category_list.append("Technology")
			
			elif k == "m":
				
				category_list.append("Medical")
			
			elif k == "b":
				
				category_list.append("Business")
			
			else:
			
				category_list.append("Other")	

	category = "/".join(category_list)		

	return render_template("home.html", summary = summary, category = category)

if __name__== '__main__':
	
	port = int(os.environ.get("PORT", 8000))
	
	app.run(debug = True, host = '0.0.0.0', port = port)