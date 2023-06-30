# Trabalho-Final-Compiladores
Trabalho final da disciplina de compiladores
## Gramática Regular
```
%reserved words
if
else
in
add
then
for
do
true
false
equal
diff
not
start
end

%values
<S> ::= a<A>|b<B>|c<B>
<A> ::= a<S>|a|b<C>|c<A>|epsi
<B> ::= a<A>|c<B>|c<S>|c|epsi
<C> ::= a<S>|a<D>|c<A>|c<C>
<D> ::= epsi
```
## Gramática Livre de Contexto
* Genérica
```
<E'> := <E>
<E> := start <A> end
<A> := <B>|<C>|<D>|<F>
<B> := add var <G>
<G> := var | <B>
<C> := true | false | var equal var | var diff var | not <C>
<D> := if <C> then <E> <H>
<H> := else <E> | epsi
<F> := for var in var do <E>
```
* Aceita pelo [Context-Free Grammar Tool](https://smlweb.cpsc.ucalgary.ca/start.html) da Universidade Calgaria em Alberta - Canadá
```
E -> start A end.
A -> B
   | C
   | D
   | F.
B -> add var G.
G -> var
   | B.
C -> true
   | false
   | var equal var
   | var diff var
   | not C.
D -> if C then E H.
H -> else E
   | ε.
F -> for var in var do E.
```
* Aceita pelo [Gold Parser](http://goldparser.org/download.htm)
```
"Start Symbol" = <E>

<E> ::= start <A> end
<A> ::= <B> | <C> | <D> | <F>
<B> ::= add var <G>
<G> ::= var | <B>
<C> ::= true | false | var equal var | var diff var | not <C>
<D> ::= if <C> then <E> <H>
<H> ::= else <E> | @Empty
<F> ::= for var in var do <E>
```
