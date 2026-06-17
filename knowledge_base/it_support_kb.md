# Base de Connaissances SAV Bancaire — Agent L0

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


