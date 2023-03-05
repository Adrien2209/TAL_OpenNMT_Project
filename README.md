# TAL_OpenNMT_Project

# Expérimentation

## Vérification de l’installation d’OpenNMT sur le corpus anglais-allemand contenant 10k phrases parallèles tokenisées (toy-ende)

### Step 1 : Prepare the data

```bash
onmt_build_vocab -config toy_en_de.yaml -n_sample 10000
```

### Step 2 : Train the model

On exécute la commande suivante : 

```bash
onmt_train -config toy_en_de.yaml
```

### Step 3 : Translate

```
onmt_translate -model data/toy-ende/run/model_step_1000.pt -src data/toy-ende/src-test.txt -output data/toy-ende/pred_1000.txt -gpu 0 -verbose
```

### Calcul du score BLEU

Afin de calculer le score BLEU, nous utilisons un fichier que nous avons importer du GitHub suivante : https://github.com/ymoslem/MT-Evaluation.

Nous utilisons la commande suivante pour obtenir le score BLEU :

```
perl multi-bleu.perl data\toy-ende\tgt-test.txt < data\toy-ende\pred_1000.txt
```

Nous obtenons un score BLEU de `0.00`, ce qui est extrêmement faible. Un score BLEU peut être interpreté de cette façon :

| Score BLEU | Interprétation |
| --- | --- |
| < 10 | Traductions presque inutiles |
| 10 à 19 | L'idée générale est difficilement compréhensible |
| 20 à 29 | L'idée générale apparaît clairement, mais le texte comporte de nombreuses erreurs grammaticales |
| 30 à 40 | Résultats compréhensibles à traductions correctes |
| 40 à 50 | Traductions de haute qualité |
| 50 à 60 | Traductions de très haute qualité, adéquates et fluides |
| > 60 | Qualité souvent meilleure que celle d'une traduction humaine |

## Vérification que le moteur OpenNMT fonctionne correctement en utilisant les petits corpus TRAIN, DEV et TEST

Nous avons donc 3 corpus, à savoir le TRAIN, qui permet d'entraîner le modèle avec des données annotées, le corpus DEV, qui permet d’évaluer les performances du modèle pendant l’entraînement, le corpus TEST qui permet d’évaluer les performances une fois le modèle déployé.

Les commandes à exécuter sont les mêmes que pour la vérification vu précédèmment avec le corpus toy-ende. Je créé également un fichier .yaml associé.

Création du vocabulaire :

```
onmt_build_vocab -config Europarl.yaml -n_sample 10000
```

Entrainement du modèle :

```
onmt_train -config Europarl.yaml
```

Traduction :

```
onmt_translate -model data/Europarl_test/run/model_step_1000.pt -src data/Europarl_test/Europarl_test_500.en -output data/Europarl_test/pred_1000.txt -gpu 0 -verbose
```

Calcul du score bleu :

```
perl multi-bleu.perl data\Europarl_test\Europarl_test_500.fr < \data\Europarl_test\pred_1000.tx
```

Score BLEU : `0.00`

Le score BLEU est encore extremement faible, mais nous allons voir que, bien que due en partie au corpus de taille faible, celui-ci tiens son origine de l'absence de pré-traitement des données.

# Evaluation sur des corpus parallèles en formes fléchies à large échelle

## Pré-traitement des corpus pour l’apprentissage

Nous utilisons les scripts de `mosesdecoder` afin de préparer les corpus. Cette étape de préparation des données est essentiel afin de maximiser l’efficacité de notre modèle lors de la phase d’apprentissage, de tuning et de traduction.
Ci-dessous la marche à suivre pour un fichier, elle est à répéter pour tous les fichiers, anglais et français.

### Tokenisation du corpus Anglais-Français

```
mosesdecoder/scripts/tokenizer/tokenizer.perl -l en < data/EuroparlEMEA/EuroparlSimple/Europarl_train_100k.en > data/EuroparlEMEA/EuroparlSimple/Europarl_train_100k.tok.en
```

### Changement des majuscules en minuscules du corpus Anglais-Français

### Apprentissage du modèle de transformation

```
mosesdecoder/scripts/recaser/train-truecaser.perl --model data/EuroparlEMEA/EuroparlSimple/truecase-model.en --corpus data/EuroparlEMEA/EuroparlSimple/Europarl_train_100k.tok.en
mosesdecoder/scripts/recaser/train-truecaser.perl --model data/EuroparlEMEA/EuroparlEmea/truecase-model.en --corpus data/EuroparlEMEA/EuroparlEmea/Emea_train_10k.tok.en
```

### Transformation des majuscules en minuscules

```
mosesdecoder/scripts/recaser/truecase.perl --model data/EuroparlEMEA/EuroparlSimple/truecase-model.en < data/EuroparlEMEA/EuroparlSimple/Europarl_train_100k.tok.en > data/europarl/Europarl_train_100k.tok.true.en
```

### Nettoyage en limitant la longueur des phrases à 80 caractères

```
mosesdecoder/scripts/training/clean-corpus-n.perl data/EuroparlEMEA/EuroparlSimple/Europarl_train_100k.tok.true fr en data/EuroparlEMEA/EuroparlSimple/Europarl_train_100k.tok.true.clean 1 80
```

## Apprentissage avec OpenNMT

Nous allons effectuer deux runs en suivant ce tableau :

| N° de run | Apprentissage (nombre de phrases) | Tuning (nombre de phrases) |
| --- | --- | --- |
| 1 | 100K (Europarl) | 3,75K (Europarl) |
| 2 | 100K+10K (Europarl + EMEA) | 3,75K (Europarl) |

### Run n°1

#### Step 1 : Prepare the data

On commence avec la run n°1 en utilisant le corpus Europarl_train_100K pour l’apprentissage et le corpus Europarl_dev_3750 pour le tuning. On utilise le fichier de configuration créé au préalable Europarl_run1_flechie.yaml.

```
onmt_build_vocab -config Europarl_run1_flechie.yaml -n_sample 100000
```

#### Step 2 : Train the model

```
onmt_train -config Europarl_run1_flechie.yaml
```

#### Step 3 : Translate

Traduction dans le même domaine

```
onmt_translate -model data/EuroparlEMEA/EuroparlSimple/run_1_flechie/model_step_7500.pt -src data/EuroparlEMEA/EuroparlSimple/Europarl_test_500.tok.true.clean.en -output data/EuroparlEMEA/EuroparlSimple/run_1_flechie/pred_domaine.txt -verbose
```

Calcul du score BLEU pour le corpus du domaine :

```
perl multi-bleu.perl data/EuroparlEMEA/EuroparlSimple/Europarl_test_500.tok.true.clean.fr < data/EuroparlEMEA/EuroparlSimple/run_1_flechie/pred_domaine.txt
```

Score BLEU : `18.01`

Traduction hors domaine

```
onmt_translate -model data/EuroparlEMEA/EuroparlSimple/run_1_flechie/model_step_7500.pt -src data/EuroparlEMEA/EuroparlEmea/Emea_test_500.tok.true.clean.en -output data/EuroparlEMEA/EuroparlSimple/run_1_flechie/pred_hors_domaine.txt -verbose
```

Calcul du score BLEU pour le corpus hors domaine :

```
perl multi-bleu.perl data/EuroparlEMEA/EuroparlEmea/Emea_test_500.tok.true.clean.fr < data/EuroparlEMEA/EuroparlSimple/run_1_flechie/pred_hors_domaine.txt
```

Score BLEU : `0.00`

Le modèle de traduction est convenable sur des corpus du même domaine mais catastrophique sur des corpus de domaines différents.

### Run n°2

#### Step 1 : Prepare the data

On commence avec la run n°2 en utilisant le corpus Europarl_train_100K ainsi que le corpus Emea_train_10k pour l’apprentissage et le corpus Europarl_dev_3750 pour le tuning. On utilise le fichier de configuration créé au préalable Europarl_run2_flechie.yaml.

```
onmt_build_vocab -config Europarl_run2_flechie.yaml -n_sample 100000
```

#### Step 2 : Train the model

```
onmt_train -config Europarl_run2_flechie.yaml
```

#### Step 3 : Translate

Traduction dans le même domaine

```
onmt_translate -model data/EuroparlEMEA/EuroparlEmea/run_2_flechie/model_step_10000.pt -src data/EuroparlEMEA/EuroparlSimple/Europarl_test_500.tok.true.clean.en -output data/EuroparlEMEA/EuroparlEmea/run_2_flechie/pred_domaine.txt -verbose
```

Calcul du score BLEU pour le corpus du domaine :

```
perl multi-bleu.perl data/EuroparlEMEA/EuroparlSimple/Europarl_test_500.tok.true.clean.fr < data/EuroparlEMEA/EuroparlEmea/run_2_flechie/pred_domaine.txt
```

Score BLEU : `20.12`

Traduction hors domaine

```
onmt_translate -model data/EuroparlEMEA/EuroparlEmea/run_2_flechie/model_step_10000.pt -src data/EuroparlEMEA/EuroparlEmea/Emea_test_500.tok.true.clean.en -output data/EuroparlEMEA/EuroparlEmea/run_2_flechie/pred_hors_domaine.txt -verbose
```

Calcul du score BLEU pour le corpus hors domaine :

```
perl multi-bleu.perl data/EuroparlEMEA/EuroparlEmea/Emea_test_500.tok.true.clean.fr < data/EuroparlEMEA/EuroparlEmea/run_2_flechie/pred_hors_domaine.txt
```

Score BLEU : `81.19`

Le modèle de traduction s'est amélioré sur un corpus du même domaine mais n'est pas encore totalement au point. Par contre sur un corpus hors-domaine, celui-ci est très performant.

