#include <stdio.h>
#include <stdlib.h>
#include <string.h>

// ==========================================
// 第一部分：从 ast.h 和 ast.c 提取的核心定义
// ==========================================

// 定义节点类型 (参考 ast.h)
typedef enum {
    TRANSLATION_UNIT = 300,
    FUNCTION_DECL = 8,
    VAR_DECL = 9,
    PARM_DECL = 10,
    COMPOUND_STMT = 202,
    IF_STMT = 205,
    WHILE_STMT = 207,
    RETURN_STMT = 214,
    BINARY_OPERATOR = 114,
    INTEGER_LITERAL = 106,
    DECL_REF_EXPR = 101,
    DECL_STMT = 231
} node_type;

// AST 节点结构 (参考 ast.h)
typedef struct _ast ast;
typedef struct _ast *past;

struct _ast {
    char* stype;        // 类型字符串 (int, float)
    int ivalue;         // 整数值 或 运算符字符
    float fvalue;
    char* svalue;       // 变量名/函数名
    node_type nodeType;
    char* snodeType;    // 节点类型描述字符串
    past left;
    past right;
    past if_cond;       // IF 语句专用：条件
    past next;          // 链表用于 BlockItems
};

// 辅助构建函数
past newAstNode() {
    past node = (past)malloc(sizeof(ast));
    if(node) memset(node, 0, sizeof(ast));
    return node;
}

// 模拟 ast.c 中的构建函数
past newInt(int val) {
    past node = newAstNode();
    node->nodeType = INTEGER_LITERAL;
    node->snodeType = "INTEGER_LITERAL";
    node->ivalue = val;
    return node;
}

past newID(char *name) {
    past node = newAstNode();
    node->nodeType = DECL_REF_EXPR;
    node->snodeType = "DECL_REF_EXPR";
    node->svalue = name;
    return node;
}

past newBinary(int op, past left, past right) {
    past node = newAstNode();
    node->nodeType = BINARY_OPERATOR;
    node->snodeType = "BINARY_OPERATOR";
    node->ivalue = op;
    node->left = left;
    node->right = right;
    return node;
}

past newVarDecl(char *name, past initVal) {
    past node = newAstNode();
    node->nodeType = VAR_DECL;
    node->snodeType = "VAR_DECL";
    node->svalue = name;
    node->right = initVal; // 在 parser.y 中 InitVal 通常传给 right
    return node;
}

past newReturn(past retVal) {
    past node = newAstNode();
    node->nodeType = RETURN_STMT;
    node->snodeType = "RETURN_STMT";
    node->left = retVal;
    return node;
}

past newIf(past cond, past body, past elseBody) {
    past node = newAstNode();
    node->nodeType = IF_STMT;
    node->snodeType = "IF_STMT";
    node->if_cond = cond;
    node->left = body;
    node->right = elseBody;
    return node;
}

past newCompound(past item) {
    past node = newAstNode();
    node->nodeType = COMPOUND_STMT;
    node->snodeType = "COMPOUND_STMT";
    node->left = item;
    return node;
}

past newFunc(char *name, char *retType, past body) {
    past node = newAstNode();
    node->nodeType = FUNCTION_DECL;
    node->snodeType = "FUNCTION_DECL";
    node->svalue = name;
    node->stype = retType;
    node->right = body; // 函数体通常在 right
    return node;
}

// ==========================================
// 第二部分：可视化打印逻辑 (仿 VSCode 截图风格)
// ==========================================

void print_tree(past node, char *prefix, int is_left) {
    if (node == NULL) return;

    printf("%s", prefix);
    printf("%s", is_left ? "|-- " : "+-- ");

    // 打印节点内容，带颜色
    // 紫色: 控制流 (IF, WHILE, FUNC, RETURN)
    // 黄色: 运算符
    // 绿色: 标识符 (变量名)
    // 青色: 字面量 (数字)
    
    switch (node->nodeType) {
        case FUNCTION_DECL:
            printf("\033[1;35mFUNCTION_DECL\033[0m: %s\n", node->svalue);
            // 额外打印函数的返回类型作为伪子节点信息
            if(node->stype) {
                char new_sub_prefix[256];
                sprintf(new_sub_prefix, "%s%s", prefix, is_left ? "|   " : "    ");
                printf("%s|-- \033[1;37mTYPE\033[0m: %s\n", new_sub_prefix, node->stype);
            }
            break;
        case VAR_DECL:
            printf("\033[1;32mVAR_DECL\033[0m: %s\n", node->svalue);
            break;
        case IF_STMT:
            printf("\033[1;35mIF_STMT\033[0m\n");
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
        case RETURN_STMT:
            printf("\033[1;35mRETURN_STMT\033[0m\n");
            break;
        case COMPOUND_STMT:
            printf("\033[1;37mCOMPOUND_STMT\033[0m\n");
            break;
        default:
            printf("Node (%d)\n", node->nodeType);
    }

    // 计算下一层前缀
    char new_prefix[256];
    sprintf(new_prefix, "%s%s", prefix, is_left ? "|   " : "    ");

    // 递归处理子节点
    if (node->nodeType == IF_STMT) {
        // IF 语句比较特殊，有 cond, left(then), right(else)
        print_tree(node->if_cond, new_prefix, 1);
        if (node->right) { // 如果有 else
            print_tree(node->left, new_prefix, 1);
            print_tree(node->right, new_prefix, 0);
        } else {
            print_tree(node->left, new_prefix, 0);
        }
    } 
    else if (node->nodeType == COMPOUND_STMT) {
        // Compound Stmt 在 parser.y 中通常是一个链表结构 (left 指向第一个 stmt, stmt->right 指向下一个)
        // 这里我们需要遍历链表打印
        past current = node->left; // 第一个语句
        if (node->right) { 
             // 如果按照 source 74: BlockItem BlockItems, 这里的结构可能比较复杂
             // 为了简化模拟，我们假设 compound 的 left 是第一个语句，
             // 而语句之间通过 right (next) 连接，或者在 parser 模拟中我们手动构建树状结构
             // 在 parser.y 源码中，BlockItems 是递归构建的，实际上是一棵右倾树
             print_tree(node->left, new_prefix, node->right != NULL);
             print_tree(node->right, new_prefix, 0);
        } else {
            print_tree(node->left, new_prefix, 0);
        }
    }
    else {
        // 普通二叉节点
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

// ==========================================
// 第三部分：主程序 - 手动构建 AST 并打印
// ==========================================

int main() {
    printf("Simulating Parser for:\n");
    printf("int main() {\n  int a = 5;\n  if (a > 0) { return a; }\n  return 0;\n}\n\n");

    // 1. 构建: int a = 5;
    past val_5 = newInt(5);
    past decl_a = newVarDecl("a", val_5);

    // 2. 构建: a > 0
    past ref_a_cond = newID("a");
    past val_0_cond = newInt(0);
    past cond_expr = newBinary('>', ref_a_cond, val_0_cond);

    // 3. 构建: return a; (If body)
    past ref_a_ret = newID("a");
    past ret_stmt_1 = newReturn(ref_a_ret);
    past if_body_block = newCompound(ret_stmt_1); // 包裹在 Block 中

    // 4. 构建: if (a > 0) ...
    past if_stmt = newIf(cond_expr, if_body_block, NULL);

    // 5. 构建: return 0;
    past val_0_ret = newInt(0);
    past ret_stmt_2 = newReturn(val_0_ret);

    // 6. 将语句链接成 BlockItems (在 parser.y 中通常是递归的右连接)
    // 结构: CompStmt -> left=decl_a, right=CompStmt(next...)
    // 这里我们手动模拟 BlockItems 的递归结构
    past block_part3 = newCompound(ret_stmt_2); // 最后的 return 0
    
    past block_part2 = newCompound(if_stmt);
    block_part2->right = block_part3; // 连接

    past block_part1 = newCompound(decl_a);
    block_part1->right = block_part2; // 连接头部

    // 7. 构建函数定义
    past func_main = newFunc("main", "int", block_part1);

    // 8. 打印 AST
    char prefix[256] = "";
    print_tree(func_main, prefix, 0);

    return 0;
}