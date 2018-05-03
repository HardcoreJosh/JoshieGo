#include <Python.h>
#include <stdio.h>
#include <stdlib.h>

void str2mtx(const char* str, int* board_mtx)
{
    int idx = 0;
    int number = 0;
    int cnt = 0;
    for (; idx<strlen(str); idx++)
    {
        number = str[idx]-'0';
        if (0<=number && number <=2)
        {
            board_mtx[cnt++] = number;        
        }
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

static PyObject* ran(PyObject* self, PyObject* args)
{
    const char *str;
    int board_mtx[19][19];
    
    if (!PyArg_ParseTuple(args, "s", &str))
        return NULL;
    str2mtx(str, board_mtx);
    char ret_str[361*2+1];
    mtx2str(ret_str, board_mtx);
    return Py_BuildValue("s", str);

}


static PyMethodDef GofeatMethods[] = {

    {"random",  ran, METH_VARARGS,
     "Test by random function"},

    {NULL, NULL, 0, NULL}   
};


static struct PyModuleDef gofeatmodule = {
    PyModuleDef_HEAD_INIT,
    "random",   /* name of module */
    NULL, /* module documentation, may be NULL */
    -1,       /* size of per-interpreter state of the module,
                 or -1 if the module keeps state in global variables. */
    GofeatMethods
};

PyMODINIT_FUNC
PyInit_gofeat(void)
{
    return PyModule_Create(&gofeatmodule);
}
