#include <Python.h>
#include <stdio.h>
#include <stdlib.h>


static PyObject* ran(PyObject* self, PyObject* args)
{
    const char *mtx;
    int sts = 100;
    if (!PyArg_ParseTuple(args, "s", &mtx))
        return NULL;
    int idx = 0;
    int number = 0;
    for (; idx<strlen(mtx); idx++)
    {
        printf("%d ", mtx[idx]-'0');
    }
    printf("\n%s\n", mtx);
    // while(mtx[idx] != '\0')
    // {
    //     if (mtx[idx] > '0' && mtx[idx] < '9')
    //     {
    //         number = mtx[idx] - '0';
    //         printf("%d ", number);
    //         idx += 1;
    //     }
    // }
    return PyLong_FromLong(sts);
}


static PyMethodDef GofeatMethods[] = {

    {"random",  ran, METH_VARARGS,
     "Test by random function"},

    {NULL, NULL, 0, NULL}        /* Sentinel */
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
