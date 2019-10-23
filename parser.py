#! /usr/bin/env python3

from lark import Lark,Token,Tree

from lark import Transformer

import python_types as Pt

# import logging
# logging.basicConfig(level=logging.DEBUG)


def string_num2int(tok):
    return Token.new_borrow_pos(tok.type, int(tok), tok)

callbacks = {
    'NUMBER': string_num2int,
}

with open("grammar.bnf","r") as gram:
    grammar = gram.read()



parser = Lark(grammar, parser='lalr', debug=True,start="program",lexer_callbacks = callbacks)



def load_module(name):
    if name=="lang_c":
        return Pt.CModule

class UnsugarTree(Transformer):
    def __init__(self):
        Transformer.__init__(self)
        self.lyl_scope = Pt.Module(None,None,[Pt.STD])

    def import_(self,items):
        if len(items)==1:
            items = items[0]
            if items.data =="identifier":
                name = items.children[0].value
                mod = load_module(name)
                if mod :
                    self.lyl_scope.add_module(mod)
                else :
                    raise Exception("Can't find module {}".format(name))

    def un_evaluated_function(self,items):
        name = items[0].children[0].value
        exists = self.lyl_scope.search_name(name)
        if exists:
            return Tree("un_evaluated_function",[exists[1]])
        raise Exception("Error unknown function {} at line {}".format(name,items[0].children[0].line))

    def type_context(self,items):
        variables = dict()
        for i in range(0,len(items),2):
            type_ = items[i+1]
            exists = self.lyl_scope.search_name(type_.children[0].value)
            if exists :
                variables[items[i].children[0].value]=exists[1]
            else :
                raise Exception("Bad Type {}, it doesn't exists ".format(type_.children[0].value))

            return Tree("type_context",[variables])

    def type_atom(self,items):
        if items[0].data=="identifier":
            return Tree("type_atom",[items[0].children[0].value])
        return Tree("type_atom",items) 

    def type(self,items):
        return Tree("type",items)


    def type_assumption_subroutine(self,items):
        name_tok = items[0].children[0]
        exists = self.lyl_scope.search_name(name_tok.value)
        if exists :
            raise Exception("Type {} redefined at line {} \n first definition on {}".format(name_tok.value,name_tok.line,exists[0].name))
        type_=Pt.parse_type_tree(items[1],items[2].children[0])
        f = Pt.Function(name_tok.value,type_,False)
        return Tree("type_assumption",[f])

    def subroutine_declaration(self,items):
        f=items[0].children[0]
        if len(items[1:])>2:
            cases = []
            for index,case in enumerate(items[1::3]):
                if case.children[0].value != f.name:
                    raise Exception("Bad function name {}, expected {}".format(case.children[0].value, f.name))
                cases.append(Tree("case",[case,items[index+1],items[index+2]]))
            case = Tree("cases",cases)
            f.body = case
            return Tree("subroutine_declaration",[f])
        elif len(items[1:])==2 : 
            if items[1].children[0].value != f.name:
                raise Exception("Bad function name {}, expected {}".format(items[1].children[0].value, f.name))
            f.body = items[-1]
            return Tree("subroutine_declaration",[f])
        else : 
            f.body = Tree("Empty",["Empty"])
            return Tree("subroutine_declaration",[f])

    def function_application(self,items):
        #Assuming well parsed the types for function (it's not well parsed right now, but it will done, for now we only need to work with main)
        f = items[0]
        if len(items) ==1 :
            if f.data != "identifier":
                raise Exception("Bad function evaluation at : {}".format(items[0].pretty()))
            exists = self.lyl_scope.module_search_name(f.children[0])
            if exists:
                return Tree("function_application",[exists[1]]);
        if f.data!="identifier":
            raise Exception("Bad function evaluation at : {}".format(items[0].pretty()))
        exists = self.lyl_scope.search_name(f.children[0])
        if exists:
            last = exists[1]
            for out in items[0::-1]:
                last = Tree(last,[out])
            return last;
        raise Exception("Can't find definition for function {} ".format(f.children[0]))

    def expression(self,items):
        return items[0]

class ShowFunctions(Transformer):
    def subroutine_declaration(self,items):
        print(items[0])

main_=None
class GetMain(Transformer):
    def subroutine_declaration(self,items):
        global main_
        if items[0].name =="main":
            print("Main founded",items)
            main_ = items[0]



def get_main(tree):
    GetMain().transform(tree)
    return main_

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




def appli_function(f,value):
    print(value)

def interprete_tree(tree):
    print(tree)
    if isinstance(tree,Tree):
        if tree.children:
            if len(tree.children)>0:
                result = interprete_tree(tree.children[0])
                if isinstance(tree.data,Pt.Function):
                    return appli_function(tree.data,result)
                else :
                    return tree.data
    if isinstance(tree,Token):
        return tree.value



def interprete_file(path):
    with open(path,"r") as fileP:
        source = fileP.read()
    unsugar = UnsugarTree().transform(parser.parse(source))
    # ShowFunctions().transform(unsugar)
    main = get_main(unsugar)
    # print(main)
    interprete_tree(main.body)

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