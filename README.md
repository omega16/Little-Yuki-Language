# Little Yuki language

**LYL** is a language in development, this is a interpreter/compiler wrote in python.

Current language status : **Unstable** (maybe never be stable)

**LYL** is based on simple typed Lambda calculus but isn't conformant to it, the current language is one with side effects (encapsulated as subroutines ) but have strong type system.

Syntax example : 

~~~
import lang_c

subroutine main:: (None -> a) -| a::lang_c.Uint8{
main = print "Hello world!";
}
~~~

**lang_c** is the name to get access to system C (only Uint8 implemented)

Text before **::** is the variable, function or subroutine name the latter is type assumption for it

Before **-|**  comes the type and after comes the types of variables on type.

So, here **main** is a subroutine that accepts None args and return a uint8 of C

The block after definition is mandatory on module/program scope, you must define (make a proof for the type) the function or subroutine after the type assumption.


Blocks can be a code inside braces or parentheses , **LYL** do not do a distinction between them. 

Inside function/subroutine definition block at first level must be a patter matching for function, since **main** is a function of type None->lang_c.Uint8 the corresponding pattern matching is 

~~~
main = expression;
~~~


To functions/subroutine with arguments it could be : 

~~~
f arg1 arg2 ... argN = expression
~~~