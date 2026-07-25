
%{
#include <stdio.h>
#include "token.h"
%}

int yywrap();

LETTER  [A-Za-z_]
DIGIT   [0-9]
INTEGER  -?{DIGIT}+
HEXDIGIT 0(x|X)[0-9a-fA-F]+
FLOAT   ([+-])?{DIGIT}+(\.{DIGIT}+)?([eE][+-]?{DIGIT}+)?
IDENTIFIER {LETTER}({LETTER}|{DIGIT})*



%%

{HEXDIGIT}  {printf("<%d, %d>\n", num_INT, strtol(yytext, NULL, 16));}
{INTEGER}   {printf("<%d, %s>\n", num_INT, yytext);}
{FLOAT}   {printf("<%d, %s>\n", num_FLOAT, yytext);}

[ \t\n]+ ;
"int"   {printf("<%d,KEYWORD>\n",Y_INT);}
"float" {printf("<%d,KEYWORD>\n", Y_FLOAT);}
"void"  {printf("<%d,KEYWORD>\n", Y_VOID);}
"const" {printf("<%d,KEYWORD>\n", Y_CONST);}
"if"    {printf("<%d,KEYWORD>\n", Y_IF);}
"else"  {printf("<%d,KEYWORD>\n", Y_ELSE);}
"while" {printf("<%d,KEYWORD>\n", Y_WHILE);}
"break" {printf("<%d,KEYWORD>\n", Y_BREAK);}
"continue"  {printf("<%d,KEYWORD>\n", Y_CONTINUE);}
"return"    {printf("<%d,KEYWORD>\n", Y_RETURN);}

{IDENTIFIER}    {printf("<%d, %s>\n", Y_ID, yytext);}

"+" {printf("<%d, OPERATOR>", Y_ADD);}
"-" {printf("<%d, OPERATOR>", Y_SUB);}
"*" {printf("<%d, OPERATOR>", Y_MUL);}
"/" {printf("<%d, OPERATOR>", Y_DIV);}
"%" {printf("<%d, OPERATOR>", Y_MODULO);}
"<" {printf("<%d, OPERATOR>", Y_LESS);}
"<=" {printf("<%d, OPERATOR>", Y_LESSEQ);}
">" {printf("<%d, OPERATOR>", Y_GREAT);}
">=" {printf("<%d, OPERATOR>", Y_GREATEQ);}
"!=" {printf("<%d, OPERATOR>", Y_NOTEQ);}
"==" {printf("<%d, OPERATOR>", Y_EQ);}
"!" {printf("<%d, OPERATOR>", Y_NOT);}
"&&" {printf("<%d, OPERATOR>", Y_AND);}
"||" {printf("<%d, OPERATOR>", Y_OR);}
"=" {printf("<%d, OPERATOR>", Y_ASSIGN);}

"(" {printf("<%d, SYMBOL>", Y_LPAR);}
")" {printf("<%d, SYMBOL>", Y_RPAR);}
"{" {printf("<%d, SYMBOL>", Y_LBRACKET);}
"}" {printf("<%d, SYMBOL>", Y_RBRACKET);}
"[" {printf("<%d, SYMBOL>", Y_LSQUARE);}
"]" {printf("<%d, SYMBOL>", Y_RSQUARE);}
";" {printf("<%d, SYMBOL>", Y_SEMICOLON);}
"," {printf("<%d, SYMBOL>", Y_COMMA);}

"//"    {while (input() != '\n'); }
"/*"    {int c;while ((c = input()) != '*' || (c = input()) != '/');}
.   ;

%%

void yyerror(const char *s){
    fprintf(stderr, "%s\n", s);
}

int yywrap(){
    return 1;
}

int main(int argc, char *argv[]) {
    int token;
    while((token = yylex()) != 0){}
    return 0;
}