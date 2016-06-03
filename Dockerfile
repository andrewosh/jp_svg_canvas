FROM andrewosh/binder-base

MAINTAINER Aaron Watters <awatters@simonsfoundation.org>

USER main

RUN pip install -r $HOME/notebooks/requirements.txt
RUN python $HOME/notebooks/setup.py install
RUN jupyter nbextension enable --py --sys-prefix widgetsnbextension
