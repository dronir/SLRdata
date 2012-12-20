
======================
python-module-skeleton
======================

A skeleton to use when crating a module. 

The skeleton wraps ``my_package``, where ``foofoo()`` function is defined. It
has one requirement ``requests``. 

There is also one entry point, the package will install ``runit`` script that
calls ``main()`` method in ``my_package.myfile``. 

Create source distribution::

     python setup.py sdist

Install::

     python setup.py install

Build source distribution::

    python setup.py sdist

Clean::

    python setup.py clean --all
