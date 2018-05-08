#include <Python.h>
#include <stdio.h>
#include <stdlib.h>
#include "util.hpp"

static PyObject* get_liberty(PyObject* self, PyObject* args)
{
    const char *str;
    int board_mtx[19][19];
    if (!PyArg_ParseTuple(args, "s", &str))
        return NULL;
    str2mtx(str, (int*)board_mtx);

    int liberty_feature[16][19][19];
    memset(liberty_feature, 0, 16*19*19*sizeof(int));
    
    get_liberty_feature(board_mtx, liberty_feature);

    // for (int i = 0; i< 8; i++)
    // {
    //     std::cout<< "white liberty " << i+1 << std::endl;
    //     print_mtx((int*)(liberty_feature+8+i));
    // }

    char ret_str[16*361*2+1];
    mtx2str(ret_str, (int*)liberty_feature, 16*19*19);
    return Py_BuildValue("s", ret_str);

}


static PyMethodDef GofeatMethods[] = {

    {"get_liberty",  get_liberty, METH_VARARGS,
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
