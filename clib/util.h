#ifndef _UTIL_H
#define _UTIL_H

typedef struct {
    int x;
    int y;
}Point;

typedef struct {
    Point p;
    Point* next;
}Node;

typedef Node* PtrNode;
typedef PtrNode* Group;

Group get_neighbor(int x, int y)
{
    return (Group)NULL;
}


void str2mtx(const char* str, int* board_mtx)
{
    int idx = 0;
    int number = 0;
    int cnt = 0;
    for (; idx<strlen(str); idx++)
    {
        number = str[idx]-'0';
        if (0<=number && number <=2)
            board_mtx[cnt++] = number;        
    }
}

void mtx2str(char* str, int* board_mtx)
{
    int idx = 0;
    int i = 0;
    for(; i<19*19; i++)
    {
        str[idx++] = '0' + board_mtx[i];
        str[idx++] = ' ';
    }
    str[idx] = '\0';
}

void print_mtx(int* board_mtx)
{
    int i = 0, j = 0;
    for(; i<19; i++)
    {
        for(j=0; j<19; j++)
            printf("%d ", ((int**)board_mtx)[i][j]);
        printf("\n");
    }

}



#endif