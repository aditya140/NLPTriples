# NLPTriples
Extract NLP (RDF) Triples from a sentence

# Overview
A minimalistic library to extract triples from sentences. Implemented [paper](http://ailab.ijs.si/dunja/SiKDD2007/Papers/Rusu_Trippels.pdf) 

Converted the [api](https://github.com/tdpetrou/RDF-Triple-API) created by [Ted Petrou](https://github.com/tdpetrou) to a simple library which can be be run directly.

# Installation 
Install using pip

```pip install nlptriples```

# Usage
```python
from nlptriples import triples,setup
rdf = triples.RDF_triple()
triple = rdf.extract(sent)
print(triple)
```

# Imeplemetation
1. Constituency Parse tree is create using Berkeley Neural Parser library. (the paper uses CoreNLP)
2. The algorithm described in the [paper](http://ailab.ijs.si/dunja/SiKDD2007/Papers/Rusu_Trippels.pdf) is used to extract triples from parse trees.
