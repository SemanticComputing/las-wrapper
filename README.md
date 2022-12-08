# Lexical Analysis Service Wrapper

## About

The Lexical Analysis Service (LAS) is a linguistic tool that can be used for morphological analysis of Finnish text.  LAS uses existing linguistic tools such as Omorfi that have support Finnish and many other
languages. It consists of language recognition (for 95 languages), lemmatization (for 20 languages), morphological analysis (for 14 languages), inflected form generation (for 14 languages), and hyphenation (for 46 languages)9. All functionalities are available as web services, supporting both the HTTP and WebSocket protocols. All services are additionally CORS-enabled and return results in JSON for easy integration into HTML5 web applications. The wrapper unifies and packages the output.

### API

The service has also a usable API for testing. The service API description can be found from [Swagger](https://app.swaggerhub.com/apis-docs/SeCo/nlp.ldf.fi/1.0.0#/Finnish-dep-parser/).

### Publications

* Minna Tamper, Arttu Oksanen, Jouni Tuominen, Aki Hietanen and Eero Hyvönen: Automatic Annotation Service APPI: Named Entity Linking in Legal Domain. The Semantic Web: ESWC 2020 Satellite Events (Harth, Andreas, Presutti, Valentina, Troncy, Raphaël, Acosta, Maribel, Polleres, Axel, Fernández, Javier D., Xavier Parreira, Josiane, Hartig, Olaf, Hose, Katja and Cochez, Michael (eds.)), Lecture Notes in Computer Science, vol. 12124, pp. 208-213, Springer-Verlag, 2020.


## Getting Started

To execute, set environment variables:
* ``` export FLASK_APP=src/run.py ```
* ``` export LAS_CONFIG_ENV='DEFAULT' ```

Then run ``` flask run ```

### Prerequisites

Uses Python 3.5 or newer
Python libraries: flask, requests, nltk, conllu
For more information, check [requirements.txt](requirements.txt)

## Usage

Can be used using POST or GET.

For GET
```
http://127.0.0.1:5000/?text=Helsingin%20kirjamessut%20perui%20Kiuas-kirjakustantamon%20osallistumisen%20messuille%20%E2%80%93%20Kustantamon%20taustalla%20%C3%A4%C3%A4rioikeistolaisista%20kommenteista%20tunnettu%20Timo%20H%C3%A4nnik%C3%A4inen
```
For POST
```
curl -d 'Helsingin kirjamessut perui Kiuas-kirjakustantamon osallistumisen messuille – Kustantamon taustalla äärioikeistolaisista kommenteista tunnettu Timo Hännikäinen' -H "Content-type: text/plain" -X POST http://127.0.0.1:5000/
```

### Configurations

The configurations for LAS can be found in the [conf/config.ini](conf/config.ini).

* las_url (test: http://nlp.ldf.fi/fin-dep-parser-ws): service url for Lexical Analysis Service
* chunking: number of chunks to which texts are divided for parallel analysis, i.e., how many texts can be processed in parallel.

In order to use these configurations, set the environment variable LAS_CONFIG_ENV to 'DEFAULT' or to you personal setting. The value is the section name in the config.ini file where the personal settings can be set for the attributes (configurations) defined above.

#### Logging configuration

The configurations for logging are in the [conf/logging.ini](conf/logging.ini) file. In production, the configurations should be set to WARNING mode in all log files to limit the amount of logging to only errors. The INFO and DEBUG logging modes serve better the debugging in the development environment.


### Output

Example output:

```
{"0": [{"UPOS": "PROPN", "HEAD": 2, "XPOS": null, "DEPREL": "nmod:poss", "FEATS": {"Number": "Sing", "Mood": "", "PronType": "", "AdpType": "", "NumType": "", "Tense": "", "Derivation": "", "VerbForm": "", "Degree": "", "PartForm": "", "Case": "Gen"}, "MISC": null, "DEPS": null, "LEMMA": "Helsinki", "FORM": "Helsingin"}, {"UPOS": "NOUN", "HEAD": 3, "XPOS": null, "DEPREL": "nsubj", "FEATS": {"Number": "Plur", "Mood": "", "PronType": "", "AdpType": "", "NumType": "", "Tense": "", "Derivation": "", "VerbForm": "", "Degree": "", "PartForm": "", "Case": "Nom"}, "MISC": null, "DEPS": null, "LEMMA": "kirja#messut", "FORM": "kirjamessut"}, {"UPOS": "VERB", "HEAD": 0, "XPOS": null, "DEPREL": "root", "FEATS": {"Number": "Sing", "Mood": "Ind", "PronType": "", "AdpType": "", "NumType": "", "Tense": "Past", "Derivation": "", "VerbForm": "Fin", "Degree": "", "PartForm": "", "Case": ""}, "MISC": null, "DEPS": null, "LEMMA": "perua", "FORM": "perui"}, {"UPOS": "NOUN", "HEAD": 5, "XPOS": null, "DEPREL": "nmod:gsubj", "FEATS": {"Number": "Sing", "Mood": "", "PronType": "", "AdpType": "", "NumType": "", "Tense": "", "Derivation": "", "VerbForm": "", "Degree": "", "PartForm": "", "Case": "Gen"}, "MISC": null, "DEPS": null, "LEMMA": "kiuas#kirja#kustantamo", "FORM": "Kiuas-kirjakustantamon"}, {"UPOS": "NOUN", "HEAD": 3, "XPOS": null, "DEPREL": "dobj", "FEATS": {"Number": "Sing", "Mood": "", "PronType": "", "AdpType": "", "NumType": "", "Tense": "", "Derivation": "Minen", "VerbForm": "", "Degree": "", "PartForm": "", "Case": "Gen"}, "MISC": null, "DEPS": null, "LEMMA": "osallistua", "FORM": "osallistumisen"}, {"UPOS": "NOUN", "HEAD": 5, "XPOS": null, "DEPREL": "nmod", "FEATS": {"Number": "Plur", "Mood": "", "PronType": "", "AdpType": "", "NumType": "", "Tense": "", "Derivation": "", "VerbForm": "", "Degree": "", "PartForm": "", "Case": "All"}, "MISC": null, "DEPS": null, "LEMMA": "messut", "FORM": "messuille"}, {"UPOS": "PUNCT", "HEAD": 3, "XPOS": null, "DEPREL": "punct", "FEATS": {"Number": "", "Mood": "", "PronType": "", "AdpType": "", "NumType": "", "Tense": "", "Derivation": "", "VerbForm": "", "Degree": "", "PartForm": "", "Case": ""}, "MISC": null, "DEPS": null, "LEMMA": "–", "FORM": "–"}, {"UPOS": "NOUN", "HEAD": 9, "XPOS": null, "DEPREL": "nmod:poss", "FEATS": {"Number": "Sing", "Mood": "", "PronType": "", "AdpType": "", "NumType": "", "Tense": "", "Derivation": "", "VerbForm": "", "Degree": "", "PartForm": "", "Case": "Gen"}, "MISC": null, "DEPS": null, "LEMMA": "kustantamo", "FORM": "Kustantamon"}, {"UPOS": "NOUN", "HEAD": 5, "XPOS": null, "DEPREL": "nmod", "FEATS": {"Number": "Sing", "Mood": "", "PronType": "", "AdpType": "", "NumType": "", "Tense": "", "Derivation": "", "VerbForm": "", "Degree": "", "PartForm": "", "Case": "Ade"}, "MISC": null, "DEPS": null, "LEMMA": "tausta", "FORM": "taustalla"}, {"UPOS": "ADJ", "HEAD": 11, "XPOS": null, "DEPREL": "amod", "FEATS": {"Number": "Plur", "Mood": "", "PronType": "", "AdpType": "", "NumType": "", "Tense": "", "Derivation": "", "VerbForm": "", "Degree": "Pos", "PartForm": "", "Case": "Ela"}, "MISC": null, "DEPS": null, "LEMMA": "ääri#oikeistolainen", "FORM": "äärioikeistolaisista"}, {"UPOS": "NOUN", "HEAD": 9, "XPOS": null, "DEPREL": "nmod", "FEATS": {"Number": "Plur", "Mood": "", "PronType": "", "AdpType": "", "NumType": "", "Tense": "", "Derivation": "", "VerbForm": "", "Degree": "", "PartForm": "", "Case": "Ela"}, "MISC": null, "DEPS": null, "LEMMA": "kommentti", "FORM": "kommenteista"}, {"UPOS": "ADJ", "HEAD": 14, "XPOS": null, "DEPREL": "amod", "FEATS": {"Number": "Sing", "Mood": "", "PronType": "", "AdpType": "", "NumType": "", "Tense": "", "Derivation": "", "VerbForm": "", "Degree": "Pos", "PartForm": "", "Case": "Nom"}, "MISC": null, "DEPS": null, "LEMMA": "tunnettu", "FORM": "tunnettu"}, {"UPOS": "PROPN", "HEAD": 14, "XPOS": null, "DEPREL": "name", "FEATS": {"Number": "Sing", "Mood": "", "PronType": "", "AdpType": "", "NumType": "", "Tense": "", "Derivation": "", "VerbForm": "", "Degree": "", "PartForm": "", "Case": "Nom"}, "MISC": null, "DEPS": null, "LEMMA": "Timo", "FORM": "Timo"}, {"UPOS": "PROPN", "HEAD": 11, "XPOS": null, "DEPREL": "nmod", "FEATS": {"Number": "Sing", "Mood": "", "PronType": "", "AdpType": "", "NumType": "", "Tense": "", "Derivation": "", "VerbForm": "", "Degree": "", "PartForm": "", "Case": "Nom"}, "MISC": null, "DEPS": null, "LEMMA": "Hännikäinen", "FORM": "Hännikäinen"}]}
```

For each sentence, the api returns set of identified named entities. The sentences are index from 0 to n.

## Running in Docker

`docker-compose up`: builds and runs LAS-Wrapper and LAS webservice (see [repository](https://github.com/jiemakel/las-ws))

The following configuration parameters must be passed as environment variables to the LAS-Wrapper container:

* IP_BACKEND_LAS
* PORT_BACKEND_LAS

Other configuration parameters should be set by using a config.ini (see section Configurations above) which can be e.g. bind mounted to container's path `/app/conf/config.ini`.

The log level can be specified by passing the following environment variable to the container:

* LOG_LEVEL

## Deployment in Rahti

Updates are automatically deployed into `http://nlp.ldf.fi` when commits are pushed to this repo.
