import warnings
warnings.filterwarnings("ignore")
import spacy
import operator
import os
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2'
from benepar.spacy_plugin import BeneparComponent
warnings.catch_warnings()
from parse_tree import parse_tree

class RDF_triple(object):

    class RDF_SOP():
        def __init__(self, name, pos=''):
            self.name = name
            self.word = ''
            self.parent = ''
            self.grandparent = ''
            self.depth = ''
            self.predicate_list = []
            self.predicate_sibings = []
            self.pos = pos
            self.attr = []
            self.attr_trees = []

    def reset(self):
        self.first_NP=None
        self.first_VP=None
        self.parse_tree = None
        self.subject = self.RDF_SOP('subject')
        self.predicate = self.RDF_SOP('predicate', 'VB')
        self.Object = self.RDF_SOP('object') 


    def __init__(self):
        self.nlp = spacy.load('en')
        self.nlp.add_pipe(BeneparComponent("benepar_en2"))

    def extract(self,sent,parsed=False,return_json=False):
        self.reset()
        self.sent=sent
        if not parsed:
            self.parser(sent)
        else:
            self.parse_tree=parse_tree(sent)
        self.find_NP(self.parse_tree.root)
        self.find_subject(self.first_NP)
        self.find_predicate(self.first_VP)
        if (self.subject.word=="") and (self.first_NP is not None):
            self.subject.word = self.first_NP
        self.predicate.word, self.predicate.depth, self.predicate.parent, self.predicate.grandparent = self.find_deepest_predicate()
        self.find_object()
        self.subject.attr, self.subject.attr_trees = self.get_attributes(self.subject.pos, self.subject.parent, self.subject.grandparent)
        self.predicate.attr, self.predicate.attr_trees = self.get_attributes(self.predicate.pos, self.predicate.parent, self.predicate.grandparent)
        self.Object.attr, self.Object.attr_trees = self.get_attributes(self.Object.pos, self.Object.parent, self.Object.grandparent)
        if return_json:
            return self.jsonify_rdf()
        else:
            return [self.subject.word, self.predicate.word, self.Object.word]

    def jsonify_rdf(self):
        return {'sentence':self.sent,
                'parse_tree':self.parse_tree.root.org_str,
         'predicate':{'word':self.predicate.word, 'POS':self.predicate.pos,
                      'Word Attributes':self.predicate.attr, 'Tree Attributes':self.predicate.attr_trees},
         'subject':{'word':self.subject.word, 'POS':self.subject.pos,
                      'Word Attributes':self.subject.attr, 'Tree Attributes':self.subject.attr_trees},
         'object':{'word':self.Object.word, 'POS':self.Object.pos,
                      'Word Attributes':self.Object.attr, 'Tree Attributes':self.Object.attr_trees},
         'rdf':[self.subject.word, self.predicate.word, self.Object.word]
         }

    def parser(self,sent):
        parse=self.nlp(sent)
        self.parse=list(parse.sents)[0]
        self.parse_tree=parse_tree(self.parse._.parse_string)

    def find_NP(self,node):
        if node.tag == 'NP':
            if self.first_NP is None: 
                self.first_NP = node
        elif node.tag == 'VP':
            if self.first_VP is None:
                self.first_VP = node
        if not node.leaf:
            for child in node.child:
                self.find_NP(child)

    def find_subject(self, node, parent=None, grandparent=None):
        if node.tag[:2] == 'NN':
            if self.subject.word == '': 
                self.subject.word = node.string
                self.subject.pos = node.tag
                self.subject.parent = parent
                self.subject.grandparent = grandparent
        else:
            if not node.leaf:
                for child in node.child:
                    self.find_subject(child, parent=node, grandparent=parent)
                

    def find_predicate(self, node, parent=None, grandparent=None, depth=0):
        if node.tag[:2] == 'VB':
            self.predicate.predicate_list.append((node.string, depth, parent, grandparent))
            
        if not node.leaf:
            for child in node.child:
                self.find_predicate(child, parent=node, grandparent=parent, depth=depth+1)

    def find_deepest_predicate(self):
        if not self.predicate.predicate_list:
            return '','','',''
        return max(self.predicate.predicate_list, key=operator.itemgetter(1))

    def find_object(self):
        for node in self.predicate.parent.child:
            if self.Object.word == '':
                self.find_object_NP_PP(node, node.tag, self.predicate.parent, self.predicate.grandparent)

    def find_object_NP_PP(self, node, phrase_type, parent=None, grandparent=None):
        '''
        finds the object given its a NP or PP or ADJP
        '''
        if self.Object.word != '':
            return
        else:
            # Now we know that t.node is defined
            if node.tag[:2] == 'NN' and phrase_type in ['NP', 'PP',"ADVP"]:
                if self.Object.word == '': 
                    self.Object.word = node.string
                    self.Object.pos = node.tag
                    self.Object.parent = parent
                    self.Object.grandparent = grandparent
            elif node.tag[:2] == 'JJ' and phrase_type == 'ADJP':
                if self.Object.word == '': 
                    self.Object.word = node.string
                    self.Object.pos = node.tag
                    self.Object.parent = parent
                    self.Object.grandparent = grandparent
            else:
                if not node.leaf:
                    for child in node.child:
                        self.find_object_NP_PP(child, phrase_type, parent=node, grandparent=parent)

    def attr_to_words(self, attr):
        new_attr_words = []
        new_attr_trees = []
        for tup in attr:
            if type(tup[0]) != str:
                if not tup[0].leaf:
                    new_attr_words.append((tup[0].string, tup[0].tag))
                else:
                    new_attr_trees.append(tup[0].string)
            else:
                new_attr_words.append(tup)
        return new_attr_words, new_attr_trees


    def get_attributes(self, pos, sibling_tree, grandparent):
        rdf_type_attr = []
        if pos[:2] == 'JJ':
            for item in sibling_tree.child:
                if item.tag[:2] == 'RB':
                    rdf_type_attr.append((item.string, item.tag))
        else:
            if pos[:2] == 'NN':
                for item in sibling_tree.child:
                    if item.tag[:2] in ['DT', 'PR', 'PO', 'JJ', 'CD']:
                        rdf_type_attr.append((item.string, item.tag))
                    if item.tag in ['QP', 'NP']:
                        #append a tree
                        rdf_type_attr.append(item, item.tag)
            elif pos[:2] == 'VB':
                for item in sibling_tree.child:
                    if item.tag[:2] == 'AD':
                        rdf_type_attr.append((item, item.tag))
        if grandparent:
            if pos[:2] in ['NN', 'JJ']:
                for uncle in grandparent.child:
                    if uncle.tag == 'PP':
                        rdf_type_attr.append((uncle, uncle.tag))
            elif pos[:2] == 'VB':
                for uncle in grandparent.child:
                    if uncle.tag[:2] == 'VB':
                        rdf_type_attr.append((uncle, uncle.tag))
        return self.attr_to_words(rdf_type_attr)


if __name__=="__main__":
    sent="A rare black squirrel has become a regular visitor to a suburban garden"
    sent1="(S (NP (NP (DT The) (NN time)) (PP (IN for) (NP (NN action)))) (VP (VBZ is) (ADVP (RB now))))"
    sent2="A rare black squirrel has become a regular visitor to a suburban garden"
    rdf=RDF_triple()
    a=(rdf.extract(sent,parsed=False))
    a=rdf.extract(sent2,parsed=False)
    print(a)




