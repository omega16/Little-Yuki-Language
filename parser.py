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


    def type_assumption_subrutine(self,items):
        name_tok = items[0].children[0]
        exists = self.lyl_scope.search_name(name_tok.value)
        if exists :
            raise Exception("Type {} redefined at line {} \n first definition on {}".format(name_tok.value,name_tok.line,exists[0].name))
        type_=Pt.parse_type_tree(items[1],items[2].children[0])
        f = Pt.Function(name_tok.value,type_,False)
        return Tree("type_assumption",[f])

    def subrutine_declaration(self,items):
        f=items[0].children[0]
        if len(items[1:])>2:
            cases = []
            for index,case in enumerate(items[1::3]):
                if case.children[0].value != f.name:
                    raise Exception("Bad function name {}, expected {}".format(case.children[0].value, f.name))
                cases.append(Tree("case",[case,items[index+1],items[index+2]]))
            case = Tree("cases",cases)
            body = Tree("body",[case])
            f.body = body
            return Tree("subrutine_declaration",[f])
        elif len(items[1:])==2 : 
            if items[1].children[0].value != f.name:
                raise Exception("Bad function name {}, expected {}".format(items[1].children[0].value, f.name))
            body = Tree("body",[items[-1]])
            f.body = body
            return Tree("subrutine_declaration",[f])
        else : 
            body = Tree("body",["Empty"])
            f.body = body
            return Tree("subrutine_declaration",[f])

    # def function_application(self,items):
    #     counter=0
    #     while(counter<len(items))
    #         item = items[0]
    #         if item.data=="identifier":
    #             args_counter = counter+1
    #             while(args_counter<len(items)):
    #                 if items[args_counter].data!=
                        
    #     return Tree("Application",[last])


class ShowFunctions(Transformer):
    def subrutine_declaration(self,items):
        print(items[0])




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
    usugar = UnsugarTree().transform(parser.parse(source))
    ShowFunctions().transform(usugar)

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