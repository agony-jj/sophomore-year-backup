%{
    #include <stdio.h>
    #include <stdlib.h>
    #include "calc.tab.h"
%}

%option noyywrap

DIGIT   [0-9]
NUMBER  [0-9]+(\.[0-9]+)?

%%
{NUMBER}    { yylval.double_value = atof(yytext); return NUMBER; }
"+"         { return ADD; }
"-"         { return SUB; }
"*"         { return MUL; }
"/"         { return DIV; }
"("         { return LPAREN; }
")"         { return RPAREN; }
";"         { return SEMICOLON; }
"|"         { return ABS; }
\n          { return EOL; }
[ \t]       ;   /* 忽略空格和制表符 */
%%