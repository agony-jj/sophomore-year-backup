/*
 ============================================================================
 Name        : rdparser.c
 Author      : 
 Version     :
 Copyright   : Your copyright notice
 Description : Hello World in C, Ansi-style
 ============================================================================
 */

#include <stdio.h>
#include <stdlib.h>
#include <string.h>

enum yytokentype {
	NUMBER = 258,
	EOL = 259  //一个特殊的宏常量，通常值为 -1，用来表示“文件结束”或“输入结束”。
};


extern int yylex();
//由 Lex/Flex 自动生成的词法分析函数。调用它时，它会从输入流中读取字符，识别下一个“词法单元”（token），并返回一个整数值（通常是 token 的类别编号）。
extern int yylval;
//用于在词法分析器（Lex/Flex）和语法分析器（Yacc/Bison）之间传递 token 的语义值。
extern char* yytext;
//Lex/Flex 提供的全局字符指针，指向当前识别出的 token 的原始文本串
extern FILE* yyin;
//一个 FILE* 类型的全局变量，指定词法分析器的输入源（默认是 stdin，可以改为文件）


int factor(); // F
int expr(); // E
int term(); // T

int tok;

/*
推进词法分析器到下一个 token，并输出该 token 的原始文本。
*/
void advance()
{
	tok = yylex();
	printf("tok: %s\n", yytext);
}

//exp: factor
//	| exp '+' factor
//	| exp '-' factor
//	;
// 即 E -> F | E+F | E-F
// 下面函数的编写与上述文法有所不同，上述文法是左递归的，下面的文法是消除左递归的
int expr()
{
	int l = factor();
	while(tok == '+' || tok == '-')
	{
		int oper = tok;
		advance();
		int r = factor();
		if( oper == '+')
			l += r;
		else
			l -= r;
	}
	return l;
}

//factor: term
//	| factor '*' term
//	| factor '/' term
//	;
// 即F -> T | F*T | F/T
// 下面函数编写时也消除了左递归

int factor()
{
	int l = term();
	while(tok == '*' || tok == '/')
	{
		int oper = tok;
		advance();
		int r = term();
		if( oper == '*')
			l *= r;
		else
			l /= r;
	}
	return l;
}


//term: NUMBER
//	| '-' term
//	;
// 即T -> number | -T

int term()
{
	if(tok == NUMBER)
	{
		advance();
		return yylval;
	}
	else if(tok == '-')
	{
		advance();
		int k = term();
		return -k;
	}
	else if(tok == 'q')
		exit(0);
	return -1;
}


typedef struct _ast ast;
typedef struct _ast *past;
struct _ast{
	int ivalue; // 节点的数值属性
	char* nodeType; // 节点的类型属性
	past left;
	past right;
};

past newAstNode()
{
	past node = malloc(sizeof(ast));
	if(node == NULL)
	{
		printf("run out of memory.\n");
		exit(0);
	}
	memset(node, 0, sizeof(ast));
	return node;
}

past newNum(int value)
{
	past var = newAstNode();
	var->nodeType = "intValue";
	var->ivalue = value;
	return var;
}
past newExpr(int oper, past left,past right)
{
	past var = newAstNode();
	var->nodeType = "expr";
	var->ivalue = oper;
	var->left = left;
	var->right = right;
	return var;
}

past astTerm()
{
	if(tok == NUMBER)
	{
		past n = newNum(yylval);
		advance();
		return n;
	}
	else if(tok == '-')
	{
		advance();
		past k = astTerm();
		past n = newExpr('-', NULL, k);
		return n;
	}
	else if(tok == 'q')
		exit(0);
	return NULL;
}


past astFactor()
{
	past l = astTerm();
	while(tok == '*' || tok == '/')
	{
		int oper = tok;
		advance();
		past r = astTerm();
		l = newExpr(oper, l, r);
	}
	return l;
}

past astExpr()
{
	past l = astFactor();
	while(tok == '+' || tok == '-')
	{
		int oper = tok;
		advance();
		past r = astFactor();
		l = newExpr(oper, l, r);
	}
	return l;
}

void showAst(past node, int nest)
{
	if(node == NULL)
		return;

	int i = 0;
	for(i = 0; i < nest; i ++)
		printf("  ");
	if(strcmp(node->nodeType, "intValue") == 0)
		printf("%s %d\n", node->nodeType, node->ivalue);
	else if(strcmp(node->nodeType, "expr") == 0)
		printf("%s '%c'\n", node->nodeType, (char)node->ivalue);
	showAst(node->left, nest+1);
	showAst(node->right, nest+1);

}

int main(int argc, char **argv)
{
//	if(argc != 2 )
//	{
//		printf("input file is needed.\n");
//		return 0;
//	}
//	FILE* f = fopen(argv[1]);
	setbuf(stdout,NULL);
	yyin = fopen("expr.txt", "r");
	advance();
	past rr = astExpr();
	showAst(rr, 0);

	return 0;
}
