import subprocess
import fnmatch
import os, json
import ntpath
import logging, requests
import os.path
from pathlib import Path
import configparser
#from conllu import parse
from word import Word
from itertools import zip_longest
from multiprocessing import Process
import multiprocessing

logger = logging.getLogger('Finer')
hdlr = logging.FileHandler('finer.log')
formatter = logging.Formatter('%(asctime)s %(name)s %(levelname)s %(message)s')
hdlr.setFormatter(formatter)
logger.addHandler(hdlr)
logger.setLevel(logging.INFO)

class RunFinDepParser:
    def __init__(self, input_texts, env):
        self.input_texts = list()
        if len(input_texts)>0:
            self.input_texts = input_texts

        self.folder = ""
        if not (self.folder.endswith("/")):
            self.folder += "/"

        self.file_extension = ""
        self.output_files = list()
        self.output_texts =dict()
        self.sentences_json = dict()
        self.sentences_data = dict()
        self.tool = ""
        self.chunks = 4


        self.read_configs(env)

    def read_configs(self, env):

        config = configparser.ConfigParser()
        config.read('src/config.ini')

        if env == "TEST":
            self.tool = config['TEST']['finnish_dep_parser_url']
            self.chunks = int(config['TEST']['chunking'])
        else:
            self.tool = config['DEFAULT']['finnish_dep_parser_url']
            self.chunks = int(config['DEFAULT']['chunking'])

    def run(self):
        files = None

        items = list(self.input_texts.items())
        print('url', self.tool)
        #print('items before', items)
        if len(items) > 1:
            pool = multiprocessing.Pool(4)
            chunksize = self.chunks
            chunks = [items[i:i + chunksize] for i in range(0, len(items), chunksize)]

            files = pool.map(self.execute_depparser_parallel, chunks)
            pool.close()
            pool.join()
        else:
            files = self.execute_depparser(items)

        if files != None:
            for i, j in files[0].items():
                if i in self.output_texts:
                    print('This already in', i, j)
                self.output_texts[i] = j

    def execute_depparser_parallel(self, data):

        outputtexts = dict()

        for tpl in data:
            ind =tpl[0]
            input_text = tpl[1]

            if len(input_text.split())> 1:
                output_file = str(self.folder)+"output/"+str(ind)+".txt"
                #print("IN=",input_text)
                #print("OUT=", output_file)
                #tmp_output_files.append(output_file)
                my_file = Path(output_file)
                #if not(my_file.exists()):

                output = self.summon_dep_parser(input_text)  # +str(output_file)
                outputtexts[ind] = output
                #print(ind, output)
                #self.write_output(output, output_file)
                #else:
                #    logging.info("File %s exists, moving on", output_file);
        return outputtexts



    def execute_depparser(self, input):
        for ind in self.input_texts.keys():
            input_text = self.input_texts[ind]
            if len(input_text.split())> 1:
                output_file = str(self.folder)+"output/"+str(ind)+".txt"
                self.output_files.append(output_file)
                output = self.summon_dep_parser(input_text)
                self.output_texts[ind] = output
                #print(ind, output)
                #self.write_output(output, output_file)

    def summon_dep_parser(self, input_text):
        output = ""
        command = self.contruct_command(input_text)
        if self.tool.startswith('http'):

            payload = {'text': str(input_text)}
            r = requests.get(self.tool, params=payload)
            #print("No query made, just mocking", payload, self.tool)

            #print("TEST:",r.text)
            output = json.loads(r.text) #str(r.text)
            #output = ""
        else:
            try:
                logging.info(command)
                output = subprocess.check_output(command, shell=True, executable='/bin/bash').decode("utf-8")
            except subprocess.CalledProcessError as cpe:
                logging.warning("Error: %s", cpe.output)
        return output

    def contruct_command(self, input_text):
        if self.tool.startswith('http'):
            pass
        else:
            return self.tool+str(" <<< '")+str(input_text.replace("'","").replace("\\","")) +str("'")

    def write_output(self, output, file):
        f = open(file, 'w')
        f.write(output)
        f.close()

    def find_input_files(self):
        for file in os.listdir(self.folder):
            if fnmatch.fnmatch(file, self.file_extension):
                self.input_texts.append(self.folder + str(file))

    def get_output_files(self):
        return self.output_files

    def get_input_files(self):
        return self.input_texts

    def get_tool(self):
        return self.tool

    def set_tool(self, tool):
        self.tool = tool

    def set_input_files(self, input):
        self.input_texts = input

    def parse(self):
        #print("Start to parse")
        words = list()

        for ind in self.output_texts.keys():
            data = self.output_texts[ind]
            #if not(data.startswith('<?xml version="1.0" encoding="utf-8"?>')):
                # conllu parse
            sentences = self.parse_las(data)
            #print(ind, "input",sentences)
            words_json = list()
            # Parse sentences to words
            for i, words in sentences.items():
                if len(words) > 0:
                    # Parse words to word-objects
                    for j in range(0, len(words)):
                        word = words[j]
                        words_json.insert(j, word.json())

                    # save words to a sentence, render to json
                    self.sentences_data[i] = words
                    self.sentences_json[i] = words_json
                    words_json = list()
                    print("Sentence", i, self.sentences_data[i])
            #else:
            #    return 0
        return 1

    def parse_las(self, input):
        id = 0
        sentence_id = 1
        word = None
        punct = ['.','!', '?']
        brackets = ['(',')','[',']','{','}','"','\'']
        brackets_open = ['(', '[','{','"', '\'']
        brackets_closed = [')', ']', '}', '"', '\'']
        open_brackets_counter = 0
        sentences = dict()
        sentences[sentence_id] = list()
        #print("input:", input)
        for w in input['analysis']:
            weight = 0
            proper = ""


            #print("w", w)
            analysis = w['analysis']
            orig_form = w['word']

            # check if any paired objects are open before ending a sentence
            # keep track of opening and closing brackets.
            # NOTE! cannot help if there are broken brackets
            if orig_form in brackets:
                if open_brackets_counter>0 and orig_form in brackets_closed:
                    open_brackets_counter -= 1
                elif open_brackets_counter<1 and orig_form in brackets_open:
                    open_brackets_counter += 1

            if (orig_form != " "):
                id += 1
                word = self.las_word_analysis(analysis, id, orig_form, proper, weight, word)

                #print("word",word)
                #print("original form", orig_form)
                #print("brackets",open_brackets_counter)

                # end of sentence
                if open_brackets_counter < 1 and orig_form in punct:
                    #print("Sentence:", sentence_id,sentences[sentence_id])
                    sentence_id += 1
                    sentences[sentence_id] = list()
                else:
                    sentences[sentence_id].append(word)

                # once word interpretation has been decided, word is again null
                word = None
        return sentences

    def las_word_analysis(self, analysis, id, orig_form, proper, weight, word):
        for r in analysis:
            deprel = ""
            feats = dict()

            wp = r['wordParts']
            prev_weight = weight
            prev_proper = proper
            weight = r['weight']
            if weight != prev_weight and word != None:
                return word
            # parse word token's morphological features
            for part in wp:
                lemma = part['lemma']
                upos = ""
                if 'tags' in part:
                    p = part['tags']
                    prev_upos = upos
                    upos = self.check_feature('UPOS', p)
                    feats['Tense'] = self.check_feature('TENSE', p)
                    feats['Voice'] = self.check_feature('VOICE', p)
                    feats['Mood'] = self.check_feature('MOOD', p)
                    num = self.check_feature('NUM', p)
                    if num == "SG":
                        feats['Number'] = "Sing"
                    else:
                        feats['Number'] = "Plur"
                    feats['Case'] = self.check_feature('CASE', p).capitalize()
                    feats['Person'] = self.check_feature('PERS', p)
                    feats['PronType'] = self.check_feature('PRONTYPE', p)  # PRONTYPE
                    proper = self.check_feature('PROPER', p)

                    # if 'TENSE' in p:
                    #    feats['tense'] = p['TENSE'][0]
                    # if 'VOICE' in p:
                    #    feats['voice'] = p['VOICE'][0]
                    # if 'MOOD' in p:
                    #    feats['mood'] = p['MOOD'][0]
                    # if 'NUM' in p:
                    #    if p['NUM'][0] == "SG":
                    #        feats['num'] = "Sing"
                    #    else:
                    #        feats['num'] = "Plur"
                    # if 'CASE' in p:
                    #    feats['case'] = p['CASE'][0].capitalize()
                    # if 'PERS' in p:
                    #     feats['person'] = p['PERS'][0]
                    # if 'PROPER' in p:
                    #     proper = p['PROPER'][0]
                # if upos == 'NOUN' or upos == 'PROPN':
                #    res = res + lemma + " "
            gt = r['globalTags']
            if 'DEPREL' in gt:
                deprel = gt['DEPREL']
                if proper == "FIRST":
                    deprel = "name"
                elif proper == "GEO":
                    deprel = "place"

            if word == None:
                word = Word(orig_form, upos, "", feats, "Edge", id,
                            lemma, 0, deprel, "", 0)
            elif proper != "GEO" and weight == prev_weight and word != None and upos == prev_upos:
                # if we have a better interpretation of a word
                word = Word(orig_form, upos, "", feats, "Edge", id,
                            lemma, 0, deprel, "", 0)
                return word
        return word

    def check_feature(self, label, p):
        tag = ""
        if label in p:
            p1 = p[label]
            if len(p1) > 0:
                tag = p[label][0]
        return tag

    def get_json(self):
        return self.sentences_json

    def get_json_string(self):
        return json.dumps(self.sentences_json, ensure_ascii=False)



