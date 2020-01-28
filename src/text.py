#!/usr/bin/env python3

from re import split as re_split
from hashlib import sha1
from collections import OrderedDict
from string import punctuation, whitespace

from signals import ContextMark
from messages import Info


class Text:
    '''Represents the contents of a text file'''

    class Marks:
        sentence_end = ('.', '!', '?')
        sentence_sep = (' ', '\n', '$')
        paragraph_skip = ['..', '*', ' ']


    def __init__(self, file_path):
        self.file_path = file_path
        self.paragraphs = Paragraphs()
        self.sentences = OrderedDict()
        self.read_lines(file_path)


    def read_lines(self, file_path):
        with open(file_path) as lines:
            collected_lines = []
            for _line_ in lines:
                if _line_.strip():
                    collected_lines.append(_line_)
                else:
                    collected_lines and self.paragraphs.add(Paragraph(collected_lines))
                    collected_lines = []


    @staticmethod
    def simplify(line):
        '''Simplifies the supplied line to enable effective comparision in such a way
        that punctuation, whitespace, and case differences are not accounted for.'''

        line = line.rstrip()
        pattern = "[{}{}]".format(whitespace, punctuation)
        processed = [each for each in re_split(pattern, line) if each]

        return ''.join(processed).lower(), line

    @staticmethod
    def split_at_token(paragraph, end_marks=None, sep_chars=None):
        '''Transform the lines of a paragraph into a collection of sentences.
        
        All lines are joined together into a string and then split using the
        traditional or supplied sentence markers.
        '''
        fragments = []
        pattern = ''
        end_marks = set(end_marks or SENTENCE_END_MARKS)
        sep_chars = set(sep_chars or SENTENCE_SEP_CHARS)
        pattern = end_marks and sep_chars and '|'.join([''.join(['[{}]'.format(mark),
                                                                 sep_char])
                                                        for mark in end_marks
                                                        for sep_char in sep_chars])
        fragments = re_split(pattern, paragraph)
        return [_ for _ in fragments if _]


    
class TextFragment:
    def __init__(self, line, simplify_fn):
        self.simplified, self.text = simplify_fn(line)
        self.signature = sha1(bytes(self.simplified,
                                    encoding='UTF-8')).hexdigest()



class Paragraph:
    def __init__(self, lines):
        sentences = [TextFragment(_sentence_, Text.simplify)
                          for _sentence_
                          in Text.split_at_token(' '.join(lines),
                                                 end_marks=Text.Marks.sentence_end,
                                                 sep_chars=Text.Marks.sentence_sep)]
        self.sentences = OrderedDict()
        for _ in sentences:
            self.sentences[_.signature] = _ 


    def __len__(self):
        return len(self.sentences)


    def __getitem__(self, signature):
        '''Searches the collection of sentences for the requested sentence signature.

        If found returns an instanc of TextFragment
        '''
        result = None
        if signature in self.sentences:
            result = self.sentences[signature]
        return result


    def find(self, target_signature):
        for _ in self.sentences:
            if target_signature == _:
                return self.sentences


    @property
    def signature(self):
        return sha1(bytes(''.join(self.sentences.keys()),
                          encoding='UTF-8')).hexdigest()



class Paragraphs:
    def __init__(self):
        self.contents = []


    def add(self, paragraph):
        self.contents.append(paragraph)


    def __len__(self):
        return len(self.contents)


    def __getitem__(self, paragraph):
        for _ in self.contents:
            if paragraph.signature == _.signature:
                return _


    def find(self, target_sentence, context=ContextMark.Sentence):
        '''Find either a specific sentence in a paragraph or the whole paragraph that
        contains the target sentence.
        '''
        result = []
        if context is ContextMark.Paragraph:
            pass
        elif context is ContextMark.Sentence:

            for _paragraph_ in self.contents:
                if _paragraph_.find(target_sentence):
                    result.append(_paragraph_[target_sentence])
        return result


    def compare(self, paragraphs):
        '''From the provided paragraph collection, find paragraphs that are found in
        this instance.
        '''
        
        own_signatures = [self[_own_].signature
                          for _own_ in self.contents]
        received_signatures = [paragraphs[_received_].signature
                               for _received_ in paragraphs.contents]
        return [_compared_
                for _compared_ in received_signatures
                if _compared_ in own_signatures]




