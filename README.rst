Introduction
============

This addon provides a way to keep track of every actions of every users
in your site.

When a user do something Zope throw an event that is catch by this addon
to save the following information:

* what
* where
* when
* who

Trackers
========

This addon track the following events:

* Archetypes: Add / Edit / Delete / Rename
* Dexterity: Add / Edit / Delete / Rename

How it works
============

This addon is based on event raised by Zope following this logic:

* The user do an action
* The action send at least one event using notify(SpecializedEvent)
* The event implements the IObjectEvent interface
* The addon handle this event throw an handler.
* The handler is specialized for each context (archetypes, dexterity)
* The handler filter some event or not valid context (temporary object, ...)
* The handler create a non persistent useraction specialized for the context
* The handler call the initialize method of the useraction (to extract data)
* The handler get the backend (one unique backend)
* The handler ask the backend to save the current useraction


How to install
==============

This addon can be installed has any other addons. please follow official
documentation_

Quality assurance (QA)
----------------------

This addon is tested and has:

* unit tests
* integration tests
* functional tests (robotframework)
* python syntax tests (flake8)
* tests coverage control
* continious integration using travis

.. image:: https://secure.travis-ci.org/collective/collective.history.png
    :target: http://travis-ci.org/collective/collective.history

.. image:: https://coveralls.io/repos/collective/collective.history/badge.png?branch=master
    :alt: Coverage
    :target: https://coveralls.io/r/collective/collective.history

.. image:: https://pypip.in/v/collective.history/badge.png
    :target: https://crate.io/packages/collective.history/
    :alt: Latest PyPI version

.. image:: https://pypip.in/d/collective.history/badge.png
    :target: https://crate.io/packages/collective.history/
    :alt: Number of PyPI downloads


Credits
=======

Companies
---------

* `Planet Makina Corpus <http://www.makina-corpus.org>`_
* `Contact Makina Corpus <mailto:python@makina-corpus.org>`_

People
------

- JeanMichel FRANCOIS aka toutpt <toutpt@gmail.com>
- Yann FOUILLAT aka Gagaro <gagaro42@gmail.com>

.. _documentation: http://plone.org/documentation/kb/installing-add-ons-quick-how-to
