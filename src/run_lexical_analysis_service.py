import subprocess
import fnmatch
import os, json
import ntpath
import logging, requests
import os.path
from pathlib import Path
import configparser
#from conllu import parse
from configparser import Error, ParsingError, MissingSectionHeaderError, NoOptionError, DuplicateOptionError, DuplicateSectionError, NoSectionError
from word import Word
from itertools import zip_longest
from multiprocessing import Process
import multiprocessing
import traceback, sys
from flask import abort
import logging, logging.config

logging.config.fileConfig(fname='conf/logging.ini', disable_existing_loggers=False)
logger = logging.getLogger('las')


class RunLexicalAnalysisService:
    def __init__(self, input_texts, env):
        self.input_texts = list()
        if len(input_texts)>0:
            self.input_texts = input_texts

        self.folder = ""
        if not (self.folder.endswith("/")):
            self.folder += "/"

        self.file_extension = ""
        self.output_files = list()
        self.output_texts = dict()
        self.sentences_json = dict()
        self.sentences_data = dict()
        self.json_data = dict()
        self.tool = ""
        self.chunks = 4


        self.read_configs(env)

    def read_configs(self, env):
        try:
            config = configparser.ConfigParser()
            config.read('conf/config.ini')

            if env in config:
                self.tool = config[env]['las_url']
                self.chunks = int(config[env]['chunking'])
            elif env == None or len(env) == 0:
                err_msg = 'The environment is not set: %s' % (env)
                raise Exception(err_msg)
            else:
                if 'DEFAULT' in config:
                    self.tool = config['DEFAULT']['las_url']
                    self.chunks = int(config['DEFAULT']['chunking'])
                else:
                    err_msg = 'Cannot find section headers: %s, %s' % (env, 'DEFAULT')
                    raise MissingSectionHeaderError(err_msg)

        except Error as e:
            logger.error("[ERROR] ConfigParser error: %s", sys.exc_info()[0])
            logger.error(traceback.print_exc())
            abort(500)
        except Exception as err:
            logger.error("[ERROR] Unexpected error: %s", sys.exc_info()[0])
            logger.error(traceback.print_exc())
            abort(500)

    def run(self):
        files = None

        items = list(self.input_texts.items())
        if len(items) > 1:
            pool = multiprocessing.Pool(4)
            chunksize = self.chunks
            chunks = [items[i:i + chunksize] for i in range(0, len(items), chunksize)]

            files = pool.map(self.execute_las_parallel, chunks)
            pool.close()
            pool.join()
        else:
            files = self.execute_las(items)

        if files != None:
            for i, j in files[0].items():
                if i in self.output_texts:
                    logger.debug('This already in %s, %s', i, j)
                self.output_texts[i] = j

    def execute_las_parallel(self, data):

        outputtexts = dict()

        for tpl in data:
            ind = tpl[0]
            input_text = tpl[1]

            if len(input_text.split())> 0:
                output_file = str(self.folder)+"output/"+str(ind)+".txt"
                logger.info("IN=%s",input_text)
                logger.info("OUT=%s", output_file)
                my_file = Path(output_file)

                output = self.summon_las(input_text)  # +str(output_file)
                outputtexts[ind] = output
                logger.debug("%s, %s",ind, output)
        return outputtexts

    def execute_las(self, input):
        for ind in self.input_texts.keys():
            input_text = self.input_texts[ind]
            if input_text != None:
                if len(input_text.split())> 0:
                    logger.debug("IN=%s", input_text)
                    output = self.summon_las(input_text)
                    self.output_texts[ind] = output
                    logger.debug("OUT=%s", output)

    def summon_las(self, input_text):
        output = ""
        command = self.contruct_command(input_text)
        if self.tool.startswith('http'):

            payload = {'text': str(input_text)}
            r = requests.get(self.tool, params=payload)

            output = json.loads(r.text) #str(r.text)
        else:
            try:
                logging.info(command)
                output = subprocess.check_output(command, shell=True, executable='/bin/bash').decode("utf-8")
            except subprocess.CalledProcessError as cpe:
                logger.warning("Error: %s", cpe.output)
        return output

    def contruct_command(self, input_text):
        if self.tool.startswith('http'):
            pass
        else:
            return self.tool+str(" <<< '")+str(input_text.replace("'","").replace("\\","")) +str("'")

    # def write_output(self, output, file):
    #     f = open(file, 'w')
    #     f.write(output)
    #     f.close()

    # def find_input_files(self):
    #     for file in os.listdir(self.folder):
    #         if fnmatch.fnmatch(file, self.file_extension):
    #             self.input_texts.append(self.folder + str(file))

    # def get_output_files(self):
    #     return self.output_files

    # def get_input_files(self):
    #     return self.input_texts

    # def get_tool(self):
    #     return self.tool

    # def set_tool(self, tool):
    #     self.tool = tool

    # def set_input_files(self, input):
    #     self.input_texts = input

    def parse(self, parallel=True):
        words = list()
        self.json_data['morphology'] = list()

        for paragraph_ord in self.output_texts.keys():
            data = self.output_texts[paragraph_ord]

            words_json = list()
            for sentences in self.parse_las(data):
                paragraph_ord += 1
                self.sentences_json[paragraph_ord] = dict()
                self.sentences_data[paragraph_ord] = dict()
                # Parse sentences to words
                for sentence_ord, words in sentences.items():
                    if len(words) > 0:
                        # Parse words to word-objects
                        for j in range(0, len(words)):
                            word = words[j]
                            words_json.insert(j, word.json())

                        # save words to a sentence, render to json
                        self.sentences_data[paragraph_ord][sentence_ord] = words
                        self.sentences_json[paragraph_ord][sentence_ord] = words_json
                        data = {'paragraph':paragraph_ord,
                                'sentence':sentence_ord,
                                'text':'',
                                'words':words_json}
                        self.json_data['morphology'].append(data)

                        words_json = list()
                        logger.debug("%s: sentence %s, %s", paragraph_ord, sentence_ord, self.sentences_data[paragraph_ord][sentence_ord])

        return 1

    def parse_las(self, input):
        skip_punct = False
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
        logger.debug("input:%s", input)
        for w in input['analysis']:
            weight = 0
            proper = ""


            logger.debug("w=%s", w)
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

            logger.debug("%s, %s, %s, %s",len(orig_form), orig_form, skip_punct, (orig_form in punct))
            if "\n" in orig_form:
                logger.info("There's a newline in variable...")

            if (orig_form != " " and not("\n" in orig_form)) and not(skip_punct == True and orig_form in punct):
                id += 1
                word, skip_punct = self.las_word_analysis(analysis, id, orig_form, proper, weight, word)

                # end of sentence
                if open_brackets_counter < 1 and orig_form in punct:
                    sentence_id += 1
                    id = 0
                    sentences[sentence_id] = list()
                else:
                    sentences[sentence_id].append(word)

                # once word interpretation has been decided, word is again null
                word = None
            elif "\n" in orig_form and len(sentences) > 0:
                # change of paragraph has been identified, return sentences of the previous paragraph
                yield sentences
                sentence_id = 1
                sentences = dict()
                sentences[sentence_id] = list()
            else:
                skip_punct = False
        yield sentences

    def las_word_analysis(self, analysis, id, orig_form, proper, weight, word):
        for r in analysis:
            deprel = ""
            feats = dict()
            punct_skip = False
            lemma=""

            wp = r['wordParts']
            prev_weight = weight
            prev_proper = proper
            weight = r['weight']
            if weight != prev_weight and word != None:
                return word, punct_skip
            # parse word token's morphological features
            for part in wp:
                lemma += part['lemma']
                upos = ""
                if 'tags' in part:
                    p = part['tags']

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

            gt = r['globalTags']
            if 'DEPREL' in gt:
                deprel = gt['DEPREL']
                if proper == "FIRST" or proper == "LAST":
                    deprel = "name"
                elif proper == "GEO":
                    deprel = "place"

            if word == None:
                if self.check_abbrv(orig_form):
                    orig_form = orig_form + "."
                    lemma = lemma + "."
                    punct_skip = True
                    upos = "NOUN"
                word = Word(orig_form, upos, "", feats, "Edge", id,
                            lemma, 0, deprel, "", 0)
                prev_upos = upos
            elif proper != "GEO" and weight == prev_weight and word != None and upos == prev_upos:
                # if we have a better interpretation of a word
                word = Word(orig_form, upos, "", feats, "Edge", id,
                            lemma, 0, deprel, "", 0)
                return word, punct_skip
        return word, punct_skip

    def check_abbrv(self, abbr):
        abbrv = ['ao', 'eaa', 'eKr', 'em', 'eo', 'esim', 'huom', 'jaa', 'jKr', 'jms', 'jne', 'ks', 'l', 'ma', 'ml', 'mm', 'mrd', 'n', 'nk', 'no', 'ns', 'o.s', 'oto', 'puh', 'so', 'tjsp', 'tjms', 'tm', 'tms', 'tmv', 'ts', 'v', 'va', 'vrt', 'vs', 'vt', 'ym', 'yms', 'yo', 'V', 'RN:o', 'p', 'fp', 'ipu', 'kp', 'kok', 'lib', 'liik', 'ps', 'peruss', 'sin', 'pp', 'tl', 'ske', 'kesk', 'kd', 'r', 'sd', 'vas', 'vihr', 'ktp', 'komm', 'ref']
        if abbr in abbrv:
            return True
        return False

    def check_feature(self, label, p):
        tag = ""
        if label in p:
            p1 = p[label]
            if len(p1) > 0:
                tag = p[label][0]
        return tag

    def get_sentence_json(self):
        return self.sentences_json

    def get_json(self):
        return self.json_data
    #
    # def get_json_string(self):
    #     return json.dumps(self.sentences_json, ensure_ascii=False)
