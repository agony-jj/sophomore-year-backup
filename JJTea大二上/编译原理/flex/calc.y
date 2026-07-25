%{
    #include <stdio.h>
    #include <stdlib.h>
    extern int yylex(void);
    void yyerror(const char *s);
%}

/* 声明语义值类型 */
%union {
    double double_value;
}

/* 声明非终结符的类型 */
%type <double_value> expression
%type <double_value> term
%type <double_value> factor
%type <double_value> statement   /* 改正：不能用 void，改为 double 或直接不声明 */

/* 声明终结符 */
%token <double_value> NUMBER
%token ADD SUB MUL DIV
%token LPAREN RPAREN SEMICOLON ABS EOL

/* 定义优先级和结合性 */
%left ADD SUB
%left MUL DIV

%%
input:
      /* empty */
    | input statement
    ;

statement:
      expression EOL   { printf("= %g\n", $1); }
    ;

expression:
      expression ADD term   { $$ = $1 + $3; }
    | expression SUB term   { $$ = $1 - $3; }
    | term                  { $$ = $1; }
    ;

term:
      term MUL factor   { $$ = $1 * $3; }
    | term DIV factor   { $$ = $1 / $3; }
    | factor            { $$ = $1; }
    ;

factor:
      NUMBER                    { $$ = $1; }
    | LPAREN expression RPAREN  { $$ = $2; }
    | SUB factor                { $$ = -$2; }
    | ADD factor                { $$ = $2; }
    ;
%%

int main() {
    printf("Enter an expression or press Ctrl+C to exit (e.g., 2 + 3 * 4):\n");
    yyparse();
    return 0;
}

void yyerror(const char *s) {
    fprintf(stderr, "Error: %s\n", s);
}