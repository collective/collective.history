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

* Archetypes: Add content
* Archetypes: Edit content
* Archetypes: Rename content
* Archetypes: Delete content


How it works
============

This addon is based on event raised by Zope following this logic:

* The user do an action
* The action send at least one event using notify(SpecializedEvent)
* The event implements the IObjectEvent interface
* The addon handle this event throw an handler.
* The handler is specialized for each context (archetype content, portlet, ...)
* The handler filter some event or not valid context (temporary object, ...)
* The handler get the backend (one unique backend)
* The handler ask the backend to create one new useraction
* The handler wrap the useraction into specialized version
* The handler fill the what/when/where/who using wrapper useraction
* The handler call the useraction's update_before_add
* The handler call the backend.add(useraction) with a useraction unwrapped
* The handler ask to useraction if it's valid (get all needed information)
* If valid -> manager.add(useraction)


How to install
==============

This addon can be installed has any other addons. please follow official
documentation_

Credits
=======

Companies
---------

* `Planet Makina Corpus <http://www.makina-corpus.org>`_
* `Contact Makina Corpus <mailto:python@makina-corpus.org>`_

People
------

- JeanMichel FRANCOIS aka toutpt <toutpt@gmail.com>

.. _documentation: http://plone.org/documentation/kb/installing-add-ons-quick-how-to
