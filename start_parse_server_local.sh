#!/bin/bash
#module load java/11.0.2
scriptdir=/Users/peter/src/stanford-corenlp-full-2018-02-27

#echo java -mx5g -cp \"$scriptdir/*\" edu.stanford.nlp.pipeline.StanfordCoreNLP $*
java -mx5g -cp "$scriptdir/*" edu.stanford.nlp.pipeline.StanfordCoreNLPServer \
     -annotators tokenize,ssplit,pos,lemma,parse,depparse \
     -status_port 29000 -port 29000 -timeout 15000 &

java -mx5g -cp "$scriptdir/*" edu.stanford.nlp.pipeline.StanfordCoreNLPServer \
     -serverProperties StanfordCoreNLP-french.properties \
     -annotators tokenize,ssplit,pos,lemma,parse,depparse \
     -status_port 29001  -port 29001 -timeout 15000 &

