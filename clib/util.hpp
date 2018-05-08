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

void mtx2str(char* str, int* board_mtx, int num_element=19*19)
{
    int idx = 0;
    int i = 0;
    for(; i<num_element; i++)
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

std::vector<Point> neighbor(int x, int y)
{
    std::vector<Point> result;
    if (x > 0)
        result.push_back((Point){x-1, y});
    if (x < 18)
        result.push_back((Point){x+1, y});
    if (y > 0)
        result.push_back((Point){x, y-1});
    if (y < 18)
        result.push_back((Point){x, y+1});

    return result;
}

std::vector<Point> get_group(int x, int y, int board_mtx[19][19],
                             int& liberty, int stones_visited[19][19])
{
    std::vector<Point> result;
    int color = board_mtx[x][y];
    if (color == 0)
    {
        liberty = 0;
        return result;
    }

    int liberty_cnt = 0;
    int visited[19][19];
    memset(visited, 0, 19*19*sizeof(int));
    std::queue<Point> q;
    q.push((Point){x, y});
    while(!q.empty())
    {
        Point current = q.front();
        result.push_back(current);
        q.pop();
        visited[current.x][current.y] = 1;
        stones_visited[current.x][current.y] = 1;
        for (const auto& pos: neighbor(current.x, current.y))
        {
            if (visited[pos.x][pos.y] == 1)
                continue;
            visited[pos.x][pos.y] = 1;
            if (board_mtx[pos.x][pos.y] == 0)
                liberty_cnt += 1;
            if (board_mtx[pos.x][pos.y] == color)
                q.push(pos);
        }
    }
    liberty = liberty_cnt;

    return result;
}


void get_liberty_feature(int board_mtx[19][19], int features[16][19][19])
{
    int stones_visited[19][19];
    memset(stones_visited, 0, 19*19*sizeof(int));

    for (int i = 0; i<19; i++)
        for (int j = 0; j<19; j++)
        {
            if (board_mtx[i][j] == 0 || stones_visited[i][j])
                continue;
            int liberty = 0;
            int color = board_mtx[i][j]; // white: 2  black: 1
            auto stones = get_group(i, j, board_mtx, liberty, stones_visited);
            liberty = liberty > 8? 8: liberty;
            for (const auto& pos: stones)
            {
                int channel = (color-1) * 8 + liberty-1;
                features[channel][pos.x][pos.y] = 1;
            }
        }
}

#endif
