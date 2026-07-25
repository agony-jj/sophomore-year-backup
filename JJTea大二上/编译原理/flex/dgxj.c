#include <stdio.h>
#include <stdlib.h>
#include <string.h>

// --- 1. 定义节点类型和结构体 (模拟 rdlab2.h) ---

typedef enum {
    BINARY_OPERATOR,
    DECL_REF_EXPR,
    WHILE_STMT,
    IF_STMT,
    INTEGER_LITERAL
} NodeType;

typedef struct astNode {
    NodeType nodeType;
    int ivalue;         // 存储操作符(char) 或 整数值
    char *svalue;       // 存储变量名
    struct astNode *left;
    struct astNode *right;
    struct astNode *if_cond; // 特殊字段：用于IF条件
} astNode, *past;

// --- 2. 辅助构造函数 (用于手动搭建 AST) ---

past newAstNode() {
    past node = (past)malloc(sizeof(astNode));
    if (node) {
        memset(node, 0, sizeof(astNode)); // 初始化内存
    }
    return node;
}

past newInt(int val) {
    past node = newAstNode();
    node->nodeType = INTEGER_LITERAL;
    node->ivalue = val;
    return node;
}

past newDeclRefExp(char *name) {
    past node = newAstNode();
    node->nodeType = DECL_REF_EXPR;
    node->svalue = strdup(name); // 复制字符串
    return node;
}

past newBinaryOper(int oper, past left, past right) {
    past node = newAstNode();
    node->nodeType = BINARY_OPERATOR;
    node->ivalue = oper;
    node->left = left;
    node->right = right;
    return node;
}

past newWhileStmt(past condition, past body) {
    past node = newAstNode();
    node->nodeType = WHILE_STMT;
    node->left = condition;
    node->right = body;
    return node;
}

// --- 3. 核心功能：AST 树状打印函数 ---

// 修改后的打印函数，使用普通ASCII字符，防止乱码
void print_tree(past node, char *prefix, int is_left) {
    if (node == NULL) return;

    printf("%s", prefix);
    // 把原来的 "├── " 和 "└── " 换成下面这种普通字符
    printf("%s", is_left ? "|-- " : "+-- ");

    switch (node->nodeType) {
        case WHILE_STMT:
            printf("\033[1;35mWHILE_STMT\033[0m\n");
            break;
        case BINARY_OPERATOR:
            printf("\033[1;33mOP\033[0m: '%c'\n", (char)node->ivalue);
            break;
        case DECL_REF_EXPR:
            printf("\033[1;32mID\033[0m: %s\n", node->svalue);
            break;
        case INTEGER_LITERAL:
            printf("\033[1;36mINT\033[0m: %d\n", node->ivalue);
            break;
        default:
            printf("Node\n");
    }

    char new_prefix[256];
    // 把原来的 "│   " 换成 "|   "
    sprintf(new_prefix, "%s%s", prefix, is_left ? "|   " : "    ");

    if (node->nodeType == WHILE_STMT) {
        print_tree(node->left, new_prefix, 1);
        print_tree(node->right, new_prefix, 0);
    } else {
        if (node->left && node->right) {
            print_tree(node->left, new_prefix, 1);
            print_tree(node->right, new_prefix, 0);
        } else if (node->left) {
            print_tree(node->left, new_prefix, 0);
        } else if (node->right) {
            print_tree(node->right, new_prefix, 0);
        }
    }
}

// --- 4. 主函数：模拟解析并输出 ---

int main() {
    printf("Simulating Parser Result for: while (i < 10) i = i + 1;\n\n");

    // 1. 构建条件: i < 10
    past var_i_1 = newDeclRefExp("i");
    past num_10 = newInt(10);
    past condition = newBinaryOper('<', var_i_1, num_10);

    // 2. 构建右侧加法: i + 1
    past var_i_2 = newDeclRefExp("i");
    past num_1 = newInt(1);
    past add_expr = newBinaryOper('+', var_i_2, num_1);

    // 3. 构建赋值语句: i = (i + 1)
    past var_i_3 = newDeclRefExp("i"); // 左值
    past assign_stmt = newBinaryOper('=', var_i_3, add_expr);

    // 4. 构建 While 语句
    past root = newWhileStmt(condition, assign_stmt);

    // 5. 打印结果
    // 根节点不需要前缀
    printf("\033[1;35mWHILE_STMT\033[0m\n"); 
    char prefix[256] = "";
    print_tree(root->left, prefix, 1);
    print_tree(root->right, prefix, 0);

    // 释放内存(简单演示略过释放过程)
    return 0;
}