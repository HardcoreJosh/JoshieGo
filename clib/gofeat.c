#include <Python.h>
#include <stdio.h>
#include <stdlib.h>
#include "util.h"

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
