

class Type:
    def __init__(self,name,constructors):
        self.name = name 
        self.constructors = constructors
    def __str__(self):
        return "Type: {}".format(self.name)

class Compose_type:
    def __init__(self,name,types):
        self.name = name
        self.type = types

class Parametric_type:
    def __init__(self,name):
        self.name= name

class Constructor:
    def __init__(self,name,type_,args):
        self.name = name
        self.type = type_
        self.args = args


class Variable:
    def __init__(self,name,type_,mutable=False):
        self.name = name
        self.type = type_
        self.mutable = mutable

class Function:
    def __init__(self,name,type_,body):
        self.name = name 
        self.type = type_
        self.body = body 

    def __str__(self):
        if self.body :
            return("Function {} \n{}".format(self.name,self.body))
        return("Empty_Function {}".format(self.name))

class Module:
    def __init__(self,name,real_name,modules=None):
        self.name = name
        self.real_name = real_name
        self.modules=dict()
        if modules :
            for module in modules :
                self.modules[module.name]=module
        self.constructors = dict()
        self.types = dict()
        self.functions = dict()
        self.subroutines = dict()

    def add_constructor(self,constructor):
        self.constructors[constructor.name]=constructor

    def add_type(self,type_):
        self.types[type_.name] = type_

    def add_funtion(self,function):
        self.functions[function.name]=function

    def add_subroutine(self,subroutine):
        self.subroutines[subroutine.name]=subroutine

    def add_module(self,module):
        if module.name in self.modules:
            return
        self.modules[module.name] = module

    def submodule_search_name(self,name,submodule_name=None):
        if submodule_name:
            if isinstance(submodule_name,str):
                submodule_name = submodule_name.split(".")
            if len(submodule_name)>0:
                if submodule_name[0] in self.modules:
                    return self.modules[submodule_name[0]].submodule_search_name(name,submodule_name[1:])
                return False 
            else :
                return self.module_search_name(name)
        else :
            result = self.module_search_name(name)
            if result :
                return result 
            for key,module in self.modules.items():
                result = module.module_search_name(name)
                if result : 
                    return result 

        return False


    def module_search_name(self,name):
        for dic in [self.functions,self.subroutines,self.types,self.constructors]:
            if name in dic :
                return (self,dic[name])
        return False

    def search_name(self,name):
        modules = name.split(".")
        name = modules.pop()
        return self.submodule_search_name(name,modules)


def parse_type_tree(tree,context):
    if tree.data=="type_atom":
        if isinstance(tree.children[0],str):
            if tree.children[0] in context:
                return context[tree.children[0]]
            else : 
                Parametric_type(tree.children[0])
        else :
            return parse_type_tree(tree.children[0],context)
    else :
        return [parse_type_tree(node,context) for node in tree.children]

STD = Module("STD","STD",None)

Char_constructor = Constructor("Char",None,("utf8-char"))
Char = Type("Char",Char_constructor)
Char_constructor.type = Char

STD.add_constructor(Char_constructor)
STD.add_type(Char)

Complex_constructor = Constructor("Complex",None,("complex"))
Complex = Type("Complex",Complex_constructor)
Complex_constructor.type = Complex

STD_PLUS = Function("+",Complex,None)
STD.add_funtion(STD_PLUS)
STD_MINUS = Function("-",Complex,None)
STD.add_funtion(STD_MINUS)
STD_MUL = Function("*",Complex,None)
STD.add_funtion(STD_MUL)
STD_DIV = Function("/",Complex,None)
STD.add_funtion(STD_DIV)



Fprint = Function("print", (Char), None)
STD.add_subroutine(Fprint)


CModule = Module("lang_c","lang_c",None)


CUint8_constructor = Constructor("Uint8",None,("Uint8"))
CUint8 = Type("Uint8", CUint8_constructor)
CUint8_constructor.type = CUint8

CModule.add_type(CUint8)
CModule.add_constructor(CUint8_constructor)



