sue # Base de Connaissances SAV Bancaire — Agent L0

---

## KB-001 — Échec de connexion à la banque en ligne

### Problème
Le client ne peut pas se connecter à son espace bancaire.

### Symptômes
- Message "Identifiants incorrects"
- Compte temporairement bloqué
- Plusieurs tentatives échouées

### Résolution
- Demander la réinitialisation du mot de passe
- Vérifier le verrou majuscules et la langue du clavier
- Patienter 15 minutes si le compte est bloqué

### Escalade vers L1
- Si l'échec persiste après réinitialisation
- Si le client signale une activité suspecte

---

## KB-002 — Session expire immédiatement après connexion

### Problème
Le client est déconnecté quelques secondes après connexion.

### Symptômes
- Déconnexion automatique immédiate
- Reproduit sur navigateur et application mobile

### Résolution
- Activer les cookies dans le navigateur
- Vider le cache et les cookies
- Mettre à jour l'application mobile

### Escalade vers L1
- Si le problème persiste sur plusieurs appareils

---

## KB-003 — Compte bloqué après tentatives répétées

### Problème
Le compte est verrouillé par mesure de sécurité.

### Résolution
- Informer le client de la durée du blocage temporaire
- Guider vers la procédure de déblocage en ligne
- Proposer un appel conseiller si blocage permanent

### Escalade vers L1
- Si le blocage dépasse la durée normale
- Si une activité frauduleuse est suspectée

---

## KB-004 — Activité de connexion suspecte

### Problème
Le client signale des connexions non reconnues.

### Résolution
- Réinitialiser immédiatement le mot de passe
- Révoquer toutes les sessions actives
- Activer ou renforcer le MFA

### Escalade vers L1
- Si des transactions non autorisées sont détectées

---

## KB-005 — Erreur d'authentification sur application mobile

### Résolution
- Mettre à jour l'application
- Redémarrer l'appareil
- Réinstaller l'application

### Escalade vers L1
- Si l'erreur persiste après réinstallation

---

## KB-006 — Virement SEPA rejeté

### Problème
Le virement bancaire est rejeté ou n'arrive pas au destinataire.

### Symptômes
- Message "IBAN invalide"
- Virement en statut "rejeté" dans l'historique
- Délai dépassé sans arrivée des fonds

### Causes fréquentes
- IBAN mal saisi (erreur de frappe)
- Compte destinataire clôturé
- Virement hors des horaires SEPA (week-end, jours fériés)
- Plafond journalier atteint

### Résolution
- Vérifier l'IBAN auprès du destinataire
- Vérifier les plafonds de virement dans les paramètres
- Les virements SEPA sont traités en J+1 ouvré
- Les virements instantanés sont disponibles 24h/24

### Escalade vers L1
- Si le virement est bloqué pour contrôle AML (anti-blanchiment)
- Si les fonds ont été débités mais non reçus après 3 jours ouvrés

---

## KB-007 — Carte bancaire refusée

### Problème
La carte est refusée en paiement ou au distributeur.

### Symptômes
- Refus terminal de paiement
- Retrait DAB impossible
- Refus paiement en ligne

### Causes fréquentes
- Solde insuffisant
- Plafond de paiement atteint
- Restriction géographique (paiement étranger)
- Carte expirée ou non activée
- 3D Secure échoué

### Résolution
- Vérifier le solde et les plafonds dans l'application
- Activer les paiements à l'étranger dans les paramètres carte
- Pour 3D Secure : vérifier le numéro de téléphone enregistré pour recevoir le code OTP

### Escalade vers L1
- Si la carte est refusée malgré un solde suffisant et des plafonds non atteints
- Si le client signale une opposition non demandée par lui

---

## KB-008 — Opposition sur carte bancaire

### Problème
Le client souhaite faire opposition sur sa carte (perte, vol, fraude).

### Procédure
1. Confirmer l'identité du client
2. Bloquer immédiatement la carte via l'application ou le serveur vocal
3. Proposer l'émission d'une carte de remplacement (délai 5-7 jours ouvrés)
4. Si transactions frauduleuses : déclencher une réclamation

### Escalade vers L1
- Si des transactions frauduleuses doivent être contestées
- Si la carte a été utilisée après signalement de perte

---

## KB-009 — Paiement en ligne refusé (3D Secure)

### Problème
Le paiement sur un site marchand échoue lors de l'étape de validation 3D Secure.

### Causes fréquentes
- Numéro de téléphone non à jour pour recevoir le SMS
- Application bancaire non à jour pour la validation in-app
- Délai d'expiration du code OTP dépassé

### Résolution
- Vérifier le numéro de téléphone dans les paramètres du compte
- Mettre à jour l'application mobile
- Relancer le paiement et valider le code dans les 5 minutes

### Escalade vers L1
- Si le problème persiste après mise à jour des informations

---

## KB-010 — Prélèvement automatique échoué

### Problème
Un prélèvement prévu n'a pas pu être exécuté.

### Causes fréquentes
- Solde insuffisant à la date du prélèvement
- Mandat de prélèvement révoqué par erreur
- RIB obsolète transmis au créancier

### Résolution
- Vérifier le solde et alimenter le compte avant la prochaine tentative
- Vérifier la liste des mandats actifs dans l'espace bancaire
- Contacter le créancier pour mettre à jour le RIB si nécessaire

### Escalade vers L1
- Si le prélèvement a été rejeté plusieurs mois consécutifs (risque de litige)

---

## KB-011 — Découvert non autorisé / Solde négatif

### Problème
Le solde du client est négatif au-delà du découvert autorisé.

### Résolution
- Informer le client des frais d'agios applicables
- Proposer une augmentation temporaire du découvert autorisé
- Suggérer un virement depuis un autre compte pour régulariser

### Escalade vers L1
- Si le client conteste des frais ou des opérations ayant causé le découvert

---

## KB-012 — Fraude et transaction non reconnue

### Problème
Le client signale une transaction qu'il ne reconnaît pas.

### Procédure immédiate
1. Ne jamais demander de code PIN, OTP ou mot de passe au client
2. Bloquer la carte immédiatement si fraude confirmée
3. Ouvrir une réclamation de remboursement
4. Délai de traitement : 10 jours ouvrés (directive DSP2)

### Résolution
- Guider le client vers le formulaire de contestation en ligne
- Informer que les transactions frauduleuses sont remboursées sous 10 jours ouvrés si confirmées

### Escalade vers L1
- Toujours escalader les cas de fraude avérée
- Si le montant dépasse 1000€

---

## KB-013 — Demande de crédit refusée

### Problème
La demande de crédit (consommation, immobilier) a été refusée.

### Causes possibles
- Score de crédit insuffisant
- Taux d'endettement trop élevé
- Revenus insuffisants par rapport au montant demandé
- Historique d'incidents de paiement

### Résolution
- Expliquer que le refus est basé sur une analyse automatique
- Proposer une simulation avec un montant ou une durée différents
- Orienter vers un conseiller pour analyse personnalisée

### Escalade vers L1
- Si le client souhaite contester la décision et demander une révision manuelle

---

## KB-014 — Clôture de compte

### Problème
Le client souhaite clôturer son compte bancaire.

### Procédure
1. Vérifier qu'il n'existe pas de position débitrice ou de litige en cours
2. Vérifier l'absence de prélèvements actifs à migrer
3. Informer du délai de clôture (30 jours)
4. Proposer le service de mobilité bancaire si changement de banque

### Escalade vers L1
- Si la clôture est bloquée pour raison technique ou réglementaire

---

## KB-015 — Authentification à deux facteurs (MFA/2FA)

### Problème
Le client a des difficultés avec la double authentification.

### Résolution
- Si non reçu par SMS : vérifier le numéro de téléphone enregistré
- Si application d'authentification : proposer la réinitialisation du lien
- Proposer une méthode alternative (e-mail, appel vocal)

### Escalade vers L1
- Si le compte est totalement inaccessible suite à la perte du second facteur

---

## KB-016 — Débit en double

### Problème
Le client constate que le même montant a été débité deux fois pour une seule opération.

### Symptômes
- Deux lignes identiques (montant, bénéficiaire, date) dans l'historique
- Solde anormalement bas après un paiement

### Causes fréquentes
- Erreur technique du terminal de paiement (double envoi)
- Problème de synchronisation entre la banque et le marchand
- Tentative de paiement répétée par l'utilisateur lors d'un timeout

### Résolution
- Vérifier l'historique des transactions et confirmer le double débit
- Informer le client que le marchand peut avoir émis un remboursement automatique (délai 3-5 jours)
- Si aucun remboursement prévu : ouvrir une contestation de transaction

### Escalade vers L1
- Si le double débit n'est pas résolu sous 5 jours ouvrés
- Si le montant dépasse 500€

---

## KB-017 — Prélèvement inconnu ou frauduleux

### Problème
Le client identifie un prélèvement automatique qu'il ne reconnaît pas ou n'a pas autorisé.

### Symptômes
- Libellé inconnu dans l'historique
- Montant récurrent non attendu
- Prélèvement venant d'un pays étranger

### Résolution
1. Demander au client de vérifier tous ses abonnements actifs (streaming, assurances, etc.)
2. Rechercher le libellé exact sur Internet pour identifier le créancier
3. Si fraude confirmée : bloquer la carte et ouvrir une réclamation DSP2
4. Le client peut révoquer le mandat de prélèvement SEPA dans son espace bancaire

### Escalade vers L1
- Si le prélèvement est frauduleux et que la carte doit être bloquée
- Si plusieurs prélèvements non autorisés sont détectés

---

## KB-018 — Plafond de paiement insuffisant sans notification

### Problème
Le client a atteint son plafond de paiement mais n'a pas été notifié, ce qui a entraîné un refus inattendu.

### Causes fréquentes
- Notifications désactivées dans l'application
- Plafond par défaut trop bas pour les habitudes du client
- Cumul de paiements sur une courte période

### Résolution
- Vérifier et activer les alertes de plafond dans l'application mobile (Paramètres > Notifications)
- Proposer une augmentation temporaire ou permanente du plafond (délai : immédiat via app, ou J+1 via conseiller)
- Expliquer que le plafond est journalier / hebdomadaire (selon la carte)

### Escalade vers L1
- Si le client souhaite un plafond supérieur au maximum autorisé pour son type de carte

---

## KB-019 — Erreur sur le solde affiché

### Problème
Le solde visible dans l'application ou sur le relevé ne correspond pas au solde attendu par le client.

### Symptômes
- Solde différent sur l'application et au DAB
- Opérations en attente non comptabilisées
- Solde non mis à jour après un virement reçu

### Causes fréquentes
- Opérations en cours d'autorisation (non encore compensées)
- Problème de synchronisation de l'application
- Décalage entre solde comptable et solde disponible

### Résolution
- Expliquer la différence entre solde comptable et solde disponible
- Rafraîchir l'application (tirer vers le bas sur l'écran du compte)
- Vérifier les opérations en attente dans l'historique détaillé
- Vider le cache de l'application si l'affichage est figé

### Escalade vers L1
- Si le solde est inexact depuis plus de 24h sans opération en attente
- Si une opération créditrice confirmée n'apparaît pas

---

## KB-020 — Frais bancaires jugés injustifiés

### Problème
Le client conteste des frais prélevés sur son compte (frais de tenue de compte, agios, commissions).

### Types de frais fréquemment contestés
- Frais de tenue de compte
- Agios pour découvert
- Frais d'incident (rejet de chèque ou prélèvement)
- Commission d'intervention
- Frais pour retrait hors réseau

### Résolution
- Communiquer la grille tarifaire en vigueur (accessible dans l'espace bancaire > Documents > Tarifs)
- Vérifier si le client est éligible à une offre sans frais ou à une formule plus adaptée
- En cas de contestation fondée (erreur de la banque) : proposer un geste commercial ou un remboursement

### Escalade vers L1
- Si le client demande un remboursement supérieur aux limites L0
- Si les frais résultent d'une erreur système avérée

---

## KB-021 — Mauvaise catégorisation des dépenses

### Problème
Une transaction est classée dans une catégorie incorrecte (ex. : achat alimentaire classé en "Loisirs").

### Résolution
- Guider le client vers la modification manuelle : Historique > Sélectionner la transaction > Modifier la catégorie
- Expliquer que la catégorisation automatique est basée sur le libellé du marchand et peut être imprécise
- Indiquer que la correction manuelle est immédiate et persistante pour ce marchand

### Escalade vers L1
- Non applicable : ce problème est entièrement gérable en L0

---

## KB-022 — Difficulté à télécharger un relevé bancaire

### Problème
Le client ne peut pas accéder à ses relevés ou les télécharger au format PDF.

### Causes fréquentes
- Relevé pas encore disponible (génération en fin de mois)
- Bloqueur de téléchargement (popup blocker) dans le navigateur
- Session expirée lors du téléchargement
- Application mobile : autorisation de stockage non accordée

### Résolution
- Vérifier que le relevé est disponible (délai : 3 à 5 jours après fin de mois)
- Sur PC : désactiver le bloqueur de popups pour le site bancaire
- Sur mobile : vérifier Paramètres du téléphone > Applications > Banque > Autorisations > Stockage
- Proposer l'envoi par e-mail sécurisé si le téléchargement échoue

### Escalade vers L1
- Si les relevés sont manquants pour une période antérieure à 6 mois
- Si l'envoi par e-mail est demandé pour usage légal ou judiciaire

---

## KB-023 — Modification de coordonnées non prise en compte

### Problème
Le client a modifié son adresse, numéro de téléphone ou e-mail, mais le changement n'est pas effectif.

### Causes fréquentes
- Modification en attente de validation (pièce justificative non soumise)
- Délai de propagation (jusqu'à 48h)
- Erreur lors de la saisie du formulaire

### Résolution
- Vérifier le statut de la demande dans l'espace client > Mes informations personnelles
- Si pièce justificative requise (changement d'adresse) : guider le client pour soumettre le document
- Confirmer que le nouveau contact (e-mail / téléphone) est bien celui souhaité pour les alertes et le MFA

### Escalade vers L1
- Si le changement est bloqué pour raison réglementaire (vérification d'identité requise)
- Si le client ne reçoit plus aucune notification suite à la modification

---

## KB-024 — Document indisponible (RIB, attestation de compte, IBAN)

### Problème
Le client ne trouve pas ou ne peut pas générer un document officiel (RIB, attestation de solde, attestation de domiciliation).

### Résolution
- RIB / IBAN : disponible dans l'application > Mon compte > Télécharger mon RIB
- Attestation de compte : disponible dans Espace client > Documents > Attestations (génération instantanée)
- Attestation de solde : générée sur demande, délai 24h
- Si le document n'apparaît pas : vider le cache et réessayer, ou utiliser un autre navigateur

### Escalade vers L1
- Si le client a besoin d'un document certifié ou apostillé
- Si le document est requis dans un délai urgent pour une démarche administrative ou juridique

---

## KB-025 — Retard dans le traitement d'un dossier

### Problème
Le client signale qu'une demande (crédit, changement de situation, réclamation) n'a pas été traitée dans les délais annoncés.

### Délais standards de référence
- Demande de crédit consommation : 72h ouvrées
- Réclamation standard : 10 jours ouvrés (max légal : 2 mois)
- Changement de coordonnées : 48h
- Opposition carte / remboursement fraude : 10 jours ouvrés (DSP2)

### Résolution
- Vérifier le statut du dossier dans l'espace client > Mes demandes
- Confirmer la date de dépôt et le type de demande
- Informer le client du délai réglementaire applicable
- Si délai dépassé : créer un ticket d'escalade interne avec référence dossier

### Escalade vers L1
- Systématique si le délai légal est dépassé
- Si le client a fourni des pièces complémentaires non intégrées au dossier

---

## KB-026 — Temps d'attente long au service client

### Problème
Le client se plaint d'un temps d'attente excessif avant d'être pris en charge.

### Résolution
- Proposer les canaux alternatifs sans attente :
  - Chat en ligne (disponible 8h-22h en semaine)
  - Messagerie sécurisée dans l'espace client (réponse sous 24h)
  - FAQ et agent virtuel disponibles 24h/24
- Informer des horaires de faible affluence téléphonique (généralement 9h-11h et 14h-16h)
- Proposer un rappel automatique si l'option est disponible

### Escalade vers L1
- Non applicable : orienter vers les canaux disponibles

---

## KB-027 — Réponse non satisfaisante ou incomplète

### Problème
Le client estime que la réponse reçue ne résout pas son problème ou est insuffisante.

### Résolution
- Reformuler le problème avec le client pour s'assurer de bien le comprendre
- Consulter la base de connaissances pour une réponse plus complète
- Reconnaître la situation du client sans valider ni nier la plainte
- Proposer d'escalader à un conseiller spécialisé si la réponse L0 est insuffisante

### Escalade vers L1
- Si le client demande explicitement à parler à un superviseur
- Si le problème nécessite un accès à des systèmes back-office

---

## KB-028 — Difficulté à joindre un conseiller

### Problème
Le client n'arrive pas à contacter un conseiller humain.

### Résolution
- Rappeler les différents canaux de contact disponibles :
  - Téléphone : numéro dédié selon le type de carte/compte (disponible sur le site et l'application)
  - Messagerie sécurisée : espace client > Mes messages > Nouveau message
  - Chat live : disponible sur l'application mobile et le site web aux heures ouvrées
  - Rendez-vous en agence : réservable en ligne
- Informer que certains conseillers sont joignables le samedi matin

### Escalade vers L1
- Si le problème est urgent (fraude, opposition) : traitement prioritaire déclenché immédiatement sans attente conseiller

---

## KB-029 — Mauvaise gestion d'une réclamation précédente

### Problème
Le client signale qu'une réclamation antérieure n'a pas été correctement traitée (réponse erronée, dossier perdu, remboursement non effectué).

### Résolution
1. Retrouver la référence de la réclamation initiale dans l'espace client > Mes réclamations
2. Vérifier le statut et la date de clôture
3. Si le dossier a été clôturé à tort : rouvrir et escalader immédiatement en L1
4. Informer le client de son droit de saisir le Médiateur Bancaire si la réclamation n'est pas résolue sous 2 mois

### Droits du client
- Droit de saisine du Médiateur Bancaire (gratuit, obligatoire avant recours judiciaire)
- Coordonnées du médiateur disponibles dans les conditions générales et sur le site de la banque

### Escalade vers L1
- Systématique pour toute réclamation rouverte
- Si le client mentionne une action en justice ou le médiateur bancaire


