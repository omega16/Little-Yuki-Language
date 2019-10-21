#! /usr/bin/env python3

from lark import Lark,Token,Tree

from lark import Transformer

# import logging
# logging.basicConfig(level=logging.DEBUG)



with open("grammar.bnf","r") as gram:
    grammar = gram.read()

parser = Lark(grammar, parser='lalr', debug=True,start="program")

class Function:
    def __init__(self,symbol,precedence,left_arity,right_arity,types,left_asociative=False,right_asociative=False):
        self.symbol = symbol
        self.precedence = precedence
        self.left_arity = left_arity
        self.right_arity = right_arity
        self.types = types
        self.left_asociative = left_asociative
        self.right_asociative = right_asociative


class Trans(Transformer):
    def function_application_simple(self,items):
        return Tree("function_application_simple",items)



def test_show(string):
    print(80*"-")
    tree =parser.parse(string)
    print(tree.pretty())
    print(80*"~")
    desugar = DesugarTransformation().transform(tree)
    print(desugar.pretty())
    print(80*"~")
    print(normal_reduction(desugar).pretty())
    print(80*"-") 


def interprete_tree(tree):
    for statement in DesugarTransformation().transform(tree):
        if isinstance(statement,Lambda):
            print("Reducing : \n")
            founded=True
            while (founded):
                founded=False
                for variable in asigned_variables:
                    if variable in statement.free:
                        # print("substituting",variable,asigned_variables[variable])
                        statement = lambda_substitution(statement, variable, asigned_variables[variable])
                        founded=True
            # print(statement.pretty())
            reduction=normal_reduction(statement)
            if reduction :
                print(reduction.pretty())
            else :
                print("Can't terminate reduction, maybe infinity? augment max reduction attempt if you know expression must terminate")
        else :
            print("defined : ",statement)

def interprete_file(path):
    with open(path,"r") as fileP:
        source = fileP.read()
    interprete_tree(parser.parse(source))

def interprete_string(string):
    return Trans().transform(parser.parse(string)).pretty()


def interpreter():
    text_buffer = []
    PS1 = "Unknow >> "
    PS2 = "-> "
    PS3 = "Command : "
    while(True):
        try :
            if len(text_buffer)>0:
                line = input("{}{}".format(PS1,"".join(text_buffer).replace("\n","")))
            else :
                line = input(PS1)
        except EOFError :
            print("\nUnknow session end")
            break
        except KeyboardInterrupt:
            line=[]
            text_buffer=[]
            print()
        for index,utf in enumerate(line) :
            text_buffer.append(utf)
            if utf==";":
                source = "".join(text_buffer)
                text_buffer=[]
                if source.find("\n"):
                    print(PS3,source.replace("\n",""))
                result = interprete_string(source)
                print(result)
        
                

if __name__ == '__main__':
    import sys 
    if (len(sys.argv)>1):
        for path in sys.argv[1:]:
            interprete_file(path)
    else :
        interpreter()