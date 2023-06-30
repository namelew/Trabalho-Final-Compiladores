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
```
<E'> := <E>
<E> := start <A> end
<A> := <B>|<C>|<D>|<F>
<B> := add var <G>
<G> := var | <B>
<C> := true | false | var equal var | var diff var | not <C>
<D> := if <C> then <E> <H> | <B>
<H> := else <E> | epsi
<F> := for var in var do <E>
```