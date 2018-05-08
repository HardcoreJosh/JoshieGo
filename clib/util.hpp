#ifndef _UTIL_HPP 
#define _UTIL_HPP

#include <vector>
#include <iostream>
#include <queue>

void str2mtx(const char* str, int* board_mtx)
{
    int idx = 0;
    int number = 0;
    int cnt = 0;
    for (; idx<(int)strlen(str); idx++)
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
            printf("%d ", board_mtx[i*19+j]);
        printf("\n");
    }

}

typedef struct {
    int x;
    int y;
}Point;

std::vector<Point> get_group(int x, int y, int* board_mtx, int& num_liberty)
{
    std::vector<Point> result;
    int color = board_mtx[x*19+y];
    if (color == 0)
    {
        num_liberty = 0;
        return result;
    }

    int visited[19][19];
    memset(visited, 0, 19*19*sizeof(int));
    print_mtx((int*)visited);
    std::queue<Point> q;
    Point start;
    start.x = x;
    start.y = y;
    q.push_back(start)
    // while(!q.empty())
    // {
        
    // }

    return result;
}


#endif