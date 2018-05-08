#include <Python.h>
#include <stdio.h>
#include <stdlib.h>
#include "util.hpp"

static PyObject* ran(PyObject* self, PyObject* args)
{
    const char *str;
    int board_mtx[19][19];
    int liberty;

    auto re = get_group(10, 10, (int*)board_mtx, liberty);
    
    if (!PyArg_ParseTuple(args, "s", &str))
        return NULL;
    str2mtx(str, (int*)board_mtx);
    char ret_str[361*2+1];
    mtx2str(ret_str, (int*)board_mtx);
    return Py_BuildValue("s", str);

}


static PyMethodDef GofeatMethods[] = {

    {"random",  ran, METH_VARARGS,
     "Test by random function"},

    {NULL, NULL, 0, NULL}   
};


static struct PyModuleDef gofeatmodule = {
    PyModuleDef_HEAD_INIT,
    "gofeat",   /* name of module */
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
