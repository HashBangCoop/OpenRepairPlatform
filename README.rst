Atelier Soudé
=============

Le projet a été récupéré sur github : https://github.com/AtelierSoude/OpenRepairPlatform


remote origin : git@gitlab.com:hashbangfr/ateliersoude.git

remote github : git@github.com:AtelierSoude/OpenRepairPlatform.git


---------------------------------

Lancer le projet en développement :
-----------------------------------


.. code-block:: bash
    
    createdb ateliersoude
    ./manage.py migrate
    ./manage.py createsuperuser
    ./manage.py runserver

