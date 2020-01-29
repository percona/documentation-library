#!/usr/bin/env python3

'''This module stores objects that do not change throughout the life time of the
program.'''


class MetaSignals:
    class RecordRegister:
        class Ok: pass
        class Failed: pass
    class MetaDocumentLoadFromYAMLFile:
        class Ok: pass
        class Failed: pass



class OperationStatusSignals:
    class Add:
        class Ok: pass
        class Failed: pass


    class CheckOut:
        class Ok: pass
        class Failed: pass

    
    class CheckIn:
        class Ok: pass
        class Failed: pass


    class Merge:
        class Ok: pass
        class Failed: pass


class GitSignals:
    class RepositoryCreate:
        class Ok: pass
        class Failed: pass
    class RepositoryLoad:
        class Ok: pass
        class Failed: pass
    class BranchCreate:
        class Ok: pass
        class Failed: pass


class VerificationSignals:
    class TicketCodeValid:
        class Ok: pass
        class Failed: pass



class JIRASignals:
    class TicketSummaryUpdate:
        class Ok: pass
        class Restored: pass
        class Failed: pass



class TargetMark:
    '''Collects target marks, which are types of action that an operation may accomplish'''
    class Duplicate:
        '''Bound to the detect operation, it marks what phenomenae must be detected'''
        pass



class ContextMark:
    class Paragraph: pass
    class Sentence: pass
