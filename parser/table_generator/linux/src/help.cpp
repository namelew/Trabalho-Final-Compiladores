// (const char *) is used to silence linter warning.
const char *help_message = 1 + (const char *)R"(
This program reads a possibly LR grammar from <Grammar file>, takes test 
sequence from standard input stream, and stores analysis results into 
<Result Dir>.

Usage: lrparser -h|--help
       lrparser [-t<Type>] [-g<Grammar file>] [-o<Result Dir>]] <FLAGS>

Possible command: lrparser -tslr -g grammar.txt -o results

Grammar file:
  1) Use % to start a line comment.
  2) `epsilon` is reserved for epsilon. 
  3) | is reserved for separating multiple bodies of a production.
  4) You shouldn't use token $ in grammar file.
  5) Define productions as the following example shows. All symbols at the left 
     hand side of productions are automatically defined as non-terminals. The 
     first non-terminal symbol is defined as the start symbol. While symbols in 
     the same production body should be kept in the same line, multiple bodies
     can be written in consecutive lines or be separated in different 
     productions (as the definition of "fac" shows below).
     
     exp   -> exp + term  | term
     term  -> term * fac  
            | fac
     fac   -> ID
     fac   -> ( exp )

  6) Strict mode: In this mode, token naming is based on C-style variable 
     naming. Besides, \ can appear at the first character of token, and quoted 
     symbols are supported. " and ' can be used to quote a symbol, e.g. '+'. "'" 
     and '"' are okay, but you may not use them both in one symbol. Spaces in a 
     quoted string are not allowed. This mode can be turned on using argument
     `--strict`. In most cases, this mode is not necessary.

Options:
  -t        : Choose a parser type. Available: lr0, slr (default), lalr, lr1. 
  -o        : Specify output directory. (Default: ".").
  -g        : Specify grammar file path. (Default: "grammar.txt")
  -h|--help : Output help message and then exit.

Flags:
--no-test : Just generate automatons and parse table. Do not test an input 
            sequence. Program will finish as soon as the table is generated.
--no-label: Only show index of each node in dumping results.
--sep=str : Define the start of a production as the given <str>. The default 
            is "->", but you may want "::=" or ":" if your grammar is written 
            that way. This might be helpful if you are comparing several 
            different grammar parsing tools.
--strict  : This option applies to both the grammar and input sequence. See
            grammar introduction above.
--debug   : Set output level to DEBUG. Not helpful if you are not developing.
--step    : Read <stdin> step by step. If you have to process a very large input
            file, you may need this flag. But without this flag the parser can 
            provide better display for input queue (by read all input into 
            memory).
)";