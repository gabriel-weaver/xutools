"""
copyright (c) 2013 Gabriel A. Weaver <gabriel.a.l.weaver@gmail.com>

This file is part of XUTools, Python Distribution.

This code is free software:  you can redistribute                
it and/or modify it under the terms of the GNU General Public                   
License as published by the Free Software Foundation, either version            
3 of the License, or (at your option) any later version.                        
                                                                                
XUTools is distributed in the hope that it will be useful, but WITHOUT
ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or
FITNESS FOR A PARTICULAR PURPOSE.  See the GNU General Public License
for more details.
                                                                               
You should have received a copy of the GNU General Public License               
along with this program.  If not, see http://www.gnu.org/licenses/
"""
import os
from pyparsing import *
import types
from xutools.grammar import GrammarLibrary
from xutools.grammar.pyparsing.BuiltinGrammar import BuiltinGrammar

## @package xutools.corpus
class Corpus():
    
    corpus_elements = None

    def __init__(self):
        self.corpus_elements = set()

    ## Create a corpus where each corpus element corresponds to 
    #    a file and the text of that element are the file contents.
    #
    #  @param[in] file_paths The file paths to create
    #  @return the instantiated corpus
    @staticmethod
    def create_from_files(file_paths, element_equality_fields,\
                              path_field_equality_components=None,\
                              path_field_equality_components_is_whitelist=None):
        result_corpus = Corpus()
        
        for file_path in file_paths:
            fp = open(file_path, 'r')
            
            idx_path = [ "" ]
            file_path = file_path
            basename = os.path.basename(file_path)
            label_path = [ basename ]
            language_name_path = [ BuiltinGrammar.FILE ]
            
            corpus_element = CorpusElement.create( idx_path, label_path, language_name_path, file_path, element_equality_fields )
            result_corpus.add( corpus_element )
            
        if None != path_field_equality_components and None != path_field_equality_components_is_whitelist:
            result_corpus.apply_path_field_equality_components( path_field_equality_components,\
                                                                    path_field_equality_components_is_whitelist )        
        return result_corpus

    def apply_path_field_equality_components(self, path_field_equality_components,\
                                                 path_field_equality_components_is_whitelist ):
        result_corpus_elements = set()
        for corpus_element in self.corpus_elements:
            corpus_element.set_field( CorpusElement.PATH_FIELD_EQUALITY_COMPONENTS, path_field_equality_components )
            corpus_element.set_field( CorpusElement.PATH_FIELD_EQUALITY_COMPONENTS_IS_WHITELIST, path_field_equality_components_is_whitelist )
            result_corpus_elements.add( corpus_element )
        self.corpus_elements = result_corpus_elements

    ## Return the size of the result corpus
    #
    def __len__(self):
        return len( self.corpus_elements )

    ## Add a corpus element to this corpus
    #
    #  @param[in] corpus_element
    def add(self, corpus_element):
        self.corpus_elements.add( corpus_element )

    # For each element in a corpus, extract all strings that belong to 
    #  the given language name.  
    #
    # @param[in] language_name The language that we want to extract
    # @param[in] attribute_value_path If true, retain path information
    # @return a new corpus whose elements contain strings that belong to the
    #    given language name
    def parse(self, language_name):
        new_corpus = Corpus()
        elements = list(self.corpus_elements)
        for element in elements:
            new_elements = element.parse( language_name )
            new_corpus.corpus_elements = new_corpus.corpus_elements.union(new_elements)
        return new_corpus

    # Restrict the elements in the corpus by a predicate
    #
    # @param[in] predicate The predicate function by which to filter a corpus
    # @return a new corpus whose elements satisfy the predicate
    def filter(self, predicate):
        element_list = list(self.corpus_elements)
        selected = filter( predicate, element_list )
        self.corpus_elements = selected
    
    # Order elements in a corpus by a comparator
    #
    # @param[in] comparator The comparator by which to 
    # @return a sequence of corpus elements ordered by the comparator
    def order(self, key_getter):
        raise NotImplementedError("Coming soon...")

    # Get corpus elements as a list
    # 
    def list(self):
        return list(self.corpus_elements)

    # Output elements in a corpus, using field names as keys
    # 
    # @param[in] attribute_names The names of the corpus element
    #   attribute values to output 
    # @param[in] tabulate If true, escape so that we get one line per 
    #   result
    # @return a table of output elements
    def output(self, attribute_names, tabulate):
        rows = []
        for element in self.corpus_elements:
            row = []
            for attribute_name in attribute_names:
                field = element.get_field(attribute_name)
                if isinstance( field, list ):
                    field = " ".join(field)
                row.append( field )
            row_str = "\t".join(row)
            if ( True == tabulate ):
                row_str = row_str.replace("\n", "\\n")
            rows.append( row_str )
        return rows

class CorpusElement():
    idx_path = None
    label_path = None
    language_name_path = None
    file_path = None
    text = None         # Optional place to cache text
    text_ranges = None   # The start and end bytes of a string
    grammar_library = None 
    element_equality_fields = None
    path_field_equality_components = None
    path_field_equality_components_is_whitelist = None

    IDX_PATH = "idx_path"
    LABEL_PATH = "label_path"
    LANGUAGE_NAME_PATH = "language_name_path"
    FILE_PATH = "file_path"
    TEXT = "text"
    TEXT_RANGES = "text_ranges"
    ELEMENT_EQUALITY_FIELDS = "element_equality_fields"
    PATH_FIELD_EQUALITY_COMPONENTS = "path_field_equality_components"
    PATH_FIELD_EQUALITY_COMPONENTS_IS_WHITELIST = "path_field_equality_components_is_whitelist"

    def __init__(self):
        self.idx_path = []
        self.label_path = []
        self.language_name_path = []
        self.file_path = []
        self.text = None
        self.text_ranges = []
        self.grammar_library = GrammarLibrary()
        self.element_equality_fields = None
        self.path_field_equality_components = None
        self.path_field_equality_components_is_whitelist = None

    # Factory method to Create a CorpusElement
    #
    # @param[in] idx     
    # @param[in] label
    # @param[in] language_name
    # @param[in] file_path
    # @param[in] element_equality_fields
    # @return an instantiated CorpusElement
    @staticmethod
    def create(idx_path, label_path, language_name_path, file_path, element_equality_fields):
        
        corpus_element = CorpusElement()

        corpus_element.idx_path = idx_path
        corpus_element.label_path = label_path
        corpus_element.language_name_path = language_name_path
        corpus_element.file_path = file_path
        corpus_element.element_equality_fields = element_equality_fields

        fp = open( file_path )
        text = fp.read()
        fp.close()
        text_range = [0, len( text )]        
        
        corpus_element.text = text
        corpus_element.text_ranges = [ text_range ]
        
        return corpus_element

    # Getters and setters 
    def get_field(self, field_name):
        result = None
        if self.IDX_PATH == field_name:
            result = self.get_idx_path()
        elif self.LABEL_PATH == field_name:
            result = self.get_label_path()
        elif self.LANGUAGE_NAME_PATH == field_name:
            result = self.get_language_name_path()
        elif self.FILE_PATH == field_name:
            result = self.get_file_path()
        elif self.TEXT == field_name:
            result = self.get_text()
        elif self.ELEMENT_EQUALITY_FIELDS == field_name:
            result = self.get_element_equality_fields()
        elif self.PATH_FIELD_EQUALITY_COMPONENTS == field_name:
            result = self.get_path_field_equality_components()
        elif self.PATH_FIELD_EQUALITY_COMPONENTS_IS_WHITELIST == field_name:
            result = self.get_path_field_equality_components_is_whitelist()
        else:
            raise ValueError("Unrecognized field name: " + repr(field_name))
        return result

    def set_field(self, field_name, field_value):
        if self.IDX_PATH == field_name:
            self.idx_path = field_value
        elif self.LABEL_PATH == field_name:
            self.label_path = field_value
        elif self.LANGUAGE_NAME_PATH == field_name:
            self.language_name_path = field_value
        elif self.FILE_PATH == field_name:
            self.file_path = field_value
        elif self.TEXT == field_name:
            self.text = field_value
        elif self.ELEMENT_EQUALITY_FIELDS == field_name:
            self.element_equality_fields = field_value
        elif self.PATH_FIELD_EQUALITY_COMPONENTS == field_name:
            self.path_field_equality_components = field_value
        elif self.PATH_FIELD_EQUALITY_COMPONENTS_IS_WHITELIST == field_name:
            self.path_field_equality_components_is_whitelist = field_value
        else:
            raise ValueError("Unrecognized field name: " + repr(field_name))

    def get_idx_path(self):
        return self.idx_path
    
    def get_label_path(self):
        return self.label_path

    def get_language_name_path(self):
        return self.language_name_path

    def get_file_path(self):
        return self.file_path

    def get_text_ranges(self):
        return self.text_ranges

    def get_text(self):
        return self.text
        
    ## Create a corpus element for all strings from this corpus
    #    element that belong to the given language name
    #
    #  @param[in] language_name The language that we want to extract
    #  @return a new corpus whose elements contain strings that belong to 
    #    the given language name.
    def parse(self, language_name ):
        new_corpus_elements = set()
        
        grammar_production = self.grammar_library.get_grammar( language_name )
        matches = grammar_production.scanString( self.text )

        match_idx = 0
        for match, s, e in matches:
            new_idx_path = list(self.idx_path)
            new_idx_path.append(None)
            new_label_path = list(self.label_path)
            grammar_instance = self.grammar_library.get_grammar_instance(language_name)
            new_label = grammar_instance.get_label_for_match(language_name, match, match_idx)

            new_label_path.append(new_label)
            new_language_name_path = list(self.language_name_path)
            new_language_name_path.append( language_name )
            new_file_path = self.file_path
            new_text_ranges = list(self.text_ranges)
            new_text_ranges.append( [ s, e ] )
            new_text = self.text[s:e].strip()
            new_element_equality_fields = self.element_equality_fields
            new_path_field_equality_components = self.path_field_equality_components
            new_path_field_equality_components_is_whitelist = self.path_field_equality_components_is_whitelist

            new_corpus_element = CorpusElement()
            new_corpus_element.idx_path = new_idx_path
            new_corpus_element.label_path = new_label_path
            new_corpus_element.language_name_path = new_language_name_path
            new_corpus_element.file_path = new_file_path 
            new_corpus_element.text_ranges = new_text_ranges
            new_corpus_element.text = new_text 
            new_corpus_element.element_equality_fields = new_element_equality_fields
            new_corpus_element.path_field_equality_components = new_path_field_equality_components
            new_corpus_element.path_field_equality_components_is_whitelist = new_path_field_equality_components_is_whitelist

            new_corpus_elements.add( new_corpus_element )
            match_idx = match_idx + 1

        return new_corpus_elements


    # In Python set elements must be hashable (implement __hash__())
    def __hash__(self):
        if self.element_equality_fields == None:
            raise Exception("Must invoke set_field on element_equality_fields to evaluate equality!")
        values = []
        for equality_field in self.element_equality_fields:
            value = self.get_field(equality_field)
            if None != self.path_field_equality_components and\
                    self.path_field_equality_components_is_whitelist:
                if equality_field in self.path_field_equality_components:
                    valid_idxs = self.path_field_equality_components[equality_field]
                    modified_value = []
                    for idx in valid_idxs:
                        modified_value.append( value[idx] )
                    values.append(str(modified_value))
                else:
                    values.append(str(value))
            elif None != self.path_field_equality_components and\
                    not self.path_field_equality_components_is_whitelist:
                if equality_field in self.path_field_equality_components:
                    invalid_idxs = self.path_field_equality_components[equality_field]
                    modified_value = []
                    assert isinstance(value, list)
                    for component_idx in range(0,len(value)):
                        if not component_idx in invalid_idxs:
                            modified_value.append( value[component_idx] )
                    values.append(str(modified_value))
                else:
                    values.append(str(value))
            else:
                values.append(str(value))
        # watch out for errors that stem from this
        hash = sum( map( lambda x: x.__hash__(), values ) )
        return hash

        #paths = [ idx_path, language_name_path ]

        #watch out for errors that stem from this!
        #paths = filter(lambda x:x!=None, paths)
        #path_hashes = []
        #for path in paths:
        #    path_hash = sum( map( lambda x: x.__hash__(), path ) )
        #    path_hashes.append( path_hash )
        #  label_path_hash = sum( map( lambda x: x.__hash__(), label_path[1:] ))
        #  result = sum( path_hashes ) + label_path_hash + text.__hash__()
        #   return result

    # We want to define some basic notions of equality so as to compare 
    #  elements in sets
    def __eq__(self, other):

        if self.path_field_equality_components != other.path_field_equality_components:
            raise RuntimeWarning("Path field equality components are not the same in elements!")
        if self.path_field_equality_components_is_whitelist != other.path_field_equality_components_is_whitelist:
            raise RuntimeWarning("Path field equality components are not both black|white lists!")
        if self.element_equality_fields != other.element_equality_fields:
            raise RuntimeWarning("Element equality fields are not equal in elements being compared!")

        for equality_field in self.element_equality_fields:
            self_value = self.get_field(equality_field)
            other_value = other.get_field(equality_field)

            if None != self.path_field_equality_components and\
                    self.path_field_equality_components_is_whitelist:
                if equality_field in self.path_field_equality_components:
                    valid_idxs = self.path_field_equality_components[equality_field]
                    modified_self_value = []
                    modified_other_value = []
                    for idx in valid_idxs:
                        modified_self_value.append( self_value[idx] )
                        modified_other_value.append( other_value[idx] )
                    if modified_self_value != modified_other_value:
                        return False
                else:
                    if self_value != other_value:
                        return False
            elif None != self.path_field_equality_components and\
                    not self.path_field_equality_components_is_whitelist:
                if equality_field in self.path_field_equality_components:
                    invalid_idxs = self.path_field_equality_components[equality_field]
                    modified_self_value = []
                    modified_other_value = []
                    assert isinstance(self_value, list)
                    assert isinstance(other_value, list)
                    assert len(self_value) == len(other_value)
                    for component_idx in range(0, len(self_value)):
                        if not component_idx in invalid_idxs:
                            modified_self_value.append( self_value[component_idx] )
                            modified_other_value.append( other_value[component_idx] )
                    if modified_self_value != modified_other_value:
                        return False
                else:
                    if self_value != other_value:
                        return False
            else:
                if self_value != other_value:
                    return False
        return True

    # if self.label_path[1:] != other.label_path[1:]:
    # return False
    #  elif self.language_name_path != other.language_name_path:
    #       return False
    #   elif self.text != other.text:
    #       return False
    #   else:
    #       return True

    # We want to print out the corpus element
    def __str__(self):
        result = [ ]
        result.append( "label path: " + ":".join(self.label_path) )
        result.append( "language name path " + ":".join(self.language_name_path) )
        return "\n".join(result)
        
