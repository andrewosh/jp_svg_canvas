FROM andrewosh/binder-base

MAINTAINER Aaron Watters <awatters@simonsfoundation.org>

USER main

RUN cd jp_svg_canvas; pip install -r requirements.txt
RUN cd jp_svg_canvas; python setup.py install
RUN jupyter nbextension enable --py --sys-prefix widgetsnbextension
