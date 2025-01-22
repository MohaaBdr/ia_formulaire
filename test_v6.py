from openai import OpenAI
import tkinter as tk
from tkinter import ttk
import json
import threading
import time

client = OpenAI(api_key = "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")

# Ouvrir et lire le contenu du document
with open("transcript.txt", "r", encoding="utf-8") as fichier:
    contenu_document = fichier.read()

# Ouvrir et lire le fichier JSON
with open("formulaire.json", "r", encoding="utf-8") as fichier:
    donnees = json.load(fichier)  # Charge le contenu JSON dans une variable

messages = [
    {"role": "system", "content": "Tu es un assistant intelligent capable d'analyser un document et de répondre aux questions le concernant afin d'aider un commercant qui vend des cuisines."},
    {"role": "user", "content": f"Voici le document, c'est un dialogue entre le commercant et un couple qui veut faire une cuisine :\n{contenu_document}"}
]

def remplir_formulaire(labels_reponses):
    
    print("Analyse du document par l'API...") 
    reponse = client.chat.completions.create(
        model="gpt-4",
        messages=messages
    )
    
    # Parcourir les questions du formulaire
    for i, question in enumerate(donnees["formulaire_cuisine"]):

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

        # Mettre à jour l'interface pour afficher la réponse
        labels_reponses[i].config(text=f"Réponse : {reponse_modele}", fg="green")
        labels_reponses[i].update()  # Forcer la mise à jour de l'interface

        # Ajouter la réponse dans l'historique
        messages.append({"role": "assistant", "content": reponse_modele})

        with open("formulaire_rempli_v2.json", "w", encoding="utf-8") as fichier:
            json.dump(donnees, fichier, indent=4, ensure_ascii=False)  # Écriture avec formatage
    
        # Mettre à jour l'interface en temps réel
        fenetre.update()
    
    print("Les réponses ont été ajoutées au fichier.")

# Lancer la fonction de manière sécurisée avec un thread
def lancer_remplissage(labels_reponses):
    bouton_demarrer.config(state="disabled",bg="grey")
    thread = threading.Thread(target=remplir_formulaire, args=(labels_reponses,))
    thread.start()

# Création de la fenêtre principale
fenetre = tk.Tk()
fenetre.title("Formulaire de Cuisine")
fenetre.geometry("800x600")
fenetre.configure(bg="white")

# Création du cadre principal pour tout l'affichage
cadre_principal = tk.Frame(fenetre, bg="white")
cadre_principal.pack(fill="both", expand=True)

# Cadre pour le canvas et la scrollbar
cadre_canvas = tk.Frame(cadre_principal, bg="white")
cadre_canvas.pack(side="top", fill="both", expand=True)

# Création du canvas pour le contenu
cadre_contenu = tk.Canvas(cadre_canvas, bg="white")
scrollbar = ttk.Scrollbar(cadre_canvas, orient="vertical", command=cadre_contenu.yview)
cadre_contenu.configure(yscrollcommand=scrollbar.set)

# Placement du canvas et de la barre de défilement
cadre_contenu.pack(side="left", fill="both", expand=True, padx=10, pady=10)
scrollbar.pack(side="right", fill="y")

# Cadre interne pour positionner les questions/réponses
cadre_questions = tk.Frame(cadre_contenu, bg="white")
cadre_contenu.create_window((0, 0), window=cadre_questions, anchor="nw")

# Configurer la barre de défilement
cadre_questions.bind("<Configure>", lambda e: cadre_contenu.configure(scrollregion=cadre_contenu.bbox("all")))

# Ajouter les questions et réserver des espaces pour les réponses
labels_reponses = []

for question in donnees["formulaire_cuisine"]:
    # Afficher la question
    label_question = tk.Label(cadre_questions, text=f"Question : {question['question']}", font=("Arial", 14, "bold"), bg="white", fg="#444")
    label_question.pack(anchor="w", pady=5, padx=10)

    # Ajouter un espace pour afficher la réponse (initialement vide)
    label_reponse = tk.Label(cadre_questions, text="Réponse : En attente...", font=("Arial", 12), bg="white", fg="gray", wraplength=760, justify="left")
    label_reponse.pack(anchor="w", pady=5, padx=20)
    labels_reponses.append(label_reponse)

# Cadre pour le bouton en bas
cadre_bouton = tk.Frame(cadre_principal, bg="white")
cadre_bouton.pack(side="bottom", fill="x", pady=10)

# Bouton pour lancer le remplissage
bouton_demarrer = tk.Button(
    cadre_bouton,
    text="Démarrer le formulaire",
    command=lambda: lancer_remplissage(labels_reponses),
    font=("Arial", 12),
    bg="#4CAF50",
    fg="white"
)
bouton_demarrer.pack(pady=10)

def ouvrir_fenetre_interactive():
    # Nouvelle fenêtre pour l'interactivité
    fenetre_interactive = tk.Toplevel(fenetre)
    fenetre_interactive.title("Questions sur le dialogue")
    fenetre_interactive.geometry("600x400")
    fenetre_interactive.configure(bg="white")

    # Zone pour afficher les questions/réponses
    cadre_reponses = tk.Frame(fenetre_interactive, bg="white")
    cadre_reponses.pack(fill="both", expand=True, padx=10, pady=10)

    texte_reponses = tk.Text(cadre_reponses, wrap="word", font=("Arial", 12), bg="#f9f9f9", fg="#444", height=5)
    texte_reponses.pack(fill="both", expand=True, padx=10, pady=10)

    # Zone de texte pour afficher les questions/réponses
    #texte_reponses = tk.Text(cadre_contenu, wrap="word", font=("Arial", 12), bg="#f9f9f9", fg="#444", state="normal")
    #texte_reponses.pack(fill="both", expand=True, padx=10, pady=10)

    # Configurer les tags pour le style
    texte_reponses.tag_configure("question", foreground="#000000", font=("Arial", 12, "bold"))  # Bleu pour les questions
    texte_reponses.tag_configure("reponse", foreground="#28A745", font=("Arial", 12, "italic"))  # Vert pour les réponses
    texte_reponses.tag_configure("separation", foreground="#CCCCCC")  # Gris clair pour la séparation
    

    # Fonction pour afficher une question et une réponse
    def afficher_question_reponse(question, reponse):
        # Insérer la question
        texte_reponses.insert("end", f"Vous : {question}\n", "question")
        # Insérer une séparation
        texte_reponses.insert("end", "-" * 50 + "\n", "separation")
        # Insérer la réponse
        texte_reponses.insert("end", f"Assistant : {reponse}\n\n", "reponse")
        # Faire défiler vers le bas automatiquement
        texte_reponses.yview("end")

        #texte_reponses.update_idletasks()        
        #texte_reponses.config(state="disabled")

    # Champ de saisie pour les questions
    cadre_saisie = tk.Frame(fenetre_interactive, bg="white")
    cadre_saisie.pack(side="bottom", fill="x", padx=10, pady=10)

    entree_question = tk.Entry(cadre_saisie, font=("Arial", 14), bg="#f9f9f9", fg="#444")
    entree_question.pack(side="left", fill="x", expand=True, padx=10, pady=5)




    # Fonction pour envoyer la question
    def envoyer_question():
        question = entree_question.get()
        if question.strip():
            # Envoyer la question à l'API
            messages.append({"role": "user", "content": question})
            try:
                reponse = client.chat.completions.create(
                    model="gpt-4",
                    messages=messages
                )
                reponse_modele = reponse.choices[0].message.content
                print(f"Réponse API : {reponse_modele}")  # Vérifiez si la réponse est correcte

                # Mettre à jour la réponse finale dans la zone de texte
                afficher_question_reponse(question, reponse_modele)

                # Ajouter la réponse à l'historique
                messages.append({"role": "assistant", "content": reponse_modele})
            except Exception as e:
                # Afficher une erreur si l'API échoue
                afficher_question_reponse(question, "Erreur lors de la récupération de la réponse.")
                print(f"Erreur API : {e}")
            
            # Effacer le champ de saisie après l'envoi
            entree_question.delete(0, "end")
            

    bouton_envoyer = tk.Button(
        cadre_saisie,
        text="Envoyer",
        command=envoyer_question,
        font=("Arial", 12),
        bg="#4CAF50",
        fg="white"
    )
    bouton_envoyer.pack(side="right", padx=10, pady=5)

# Ajouter un bouton pour ouvrir la fenêtre interactive après le formulaire
bouton_interactif = tk.Button(
    cadre_bouton,
    text="Posez des questions",
    command=ouvrir_fenetre_interactive,
    font=("Arial", 12),
    bg="#2196F3",
    fg="white"
)
bouton_interactif.pack(pady=10)


# Lancer la boucle principale de Tkinter
fenetre.mainloop()


