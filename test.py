from openai import OpenAI

import tkinter as tk

import json


# Ouvrir et lire le contenu du document
with open("transcript.txt", "r", encoding="utf-8") as fichier:
    contenu_document = fichier.read()

# Ouvrir et lire le fichier JSON
with open("formulaire.json", "r", encoding="utf-8") as fichier:
    donnees = json.load(fichier)  # Charge le contenu JSON dans une variable

client = OpenAI(api_key = "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")

messages = [
    {"role": "system", "content": "Tu es un assistant intelligent capable d'analyser un document et de répondre aux questions le concernant afin d'aider un commercant qui vend des cuisines."},
    {"role": "user", "content": f"Voici le document, c'est un dialogue entre le commercant et un couple qui veut faire une cuisine :\n{contenu_document}"}
]

print("Analyse du document par l'API...") 
reponse = client.chat.completions.create(
    model="gpt-4",
    messages=messages
)

# Parcourir les questions du formulaire
for question in donnees["formulaire_cuisine"]:

    q = question["question"] if question["options"] is None else question["question"] + " Choisis parmis " + ", ".join((question["options"]))
    print("Question :", q)

    messages.append({"role": "user", "content": q})

    reponse = client.chat.completions.create(
    model="gpt-4",
    messages=messages
    )

    reponse_modele = reponse.choices[0].message.content
    print("Réponse :", reponse_modele)
    question["réponse"] = reponse_modele
    # Ajouter la réponse dans l'historique
    messages.append({"role": "assistant", "content": reponse_modele})

with open("formulaire_rempli.json", "w", encoding="utf-8") as fichier:
    json.dump(donnees, fichier, indent=4, ensure_ascii=False)  # Écriture avec formatage
    print("Les réponses ont été ajoutées au fichier.")