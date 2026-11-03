from pathlib import Path
import re
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.figure import Figure
from matplotlib.text import Text
from matplotlib.colors import to_rgba
from matplotlib.patches import Rectangle
import matplotlib.patheffects as pe
BG='#1A1E43';PANEL='#22294D';WHITE='#EEF4FF'
original_save=Figure.savefig
allowed=set()
def bright(c):
 try:
  r,g,b,a=to_rgba(c)
  if a==0:return c
  if max(r,g,b)-min(r,g,b)<.10:return '#BACAE0'
  if .2126*r+.7152*g+.0722*b<.46:return (r*.60+.40,g*.60+.40,b*.60+.40,a)
 except (ValueError,TypeError):pass
 return c
def themed_save(fig,filename,*args,**kwargs):
 name=Path(filename).name
 if not re.match(r'fig\d\d_',name):return
 n=int(name[3:5])
 if n not in allowed:
  return original_save(fig,filename,*args,**kwargs)
 fig.set_facecolor(BG)
 for ax in fig.axes:
  ax.set_facecolor(BG)
  for sp in ax.spines.values():sp.set_color('#7C8BAB')
  ax.tick_params(colors='#D8E5F5')
  if n==15:continue
  for line in ax.get_xgridlines()+ax.get_ygridlines():line.set_color('#65738F');line.set_alpha(.32)
  for line in ax.lines:
   line.set_color(line.get_color() if n==11 else bright(line.get_color()))
   if line.get_markeredgecolor()!='auto':line.set_markeredgecolor(bright(line.get_markeredgecolor()))
  for collection in ax.collections:
   for getter,setter in [(collection.get_edgecolors,collection.set_edgecolors),(collection.get_facecolors,collection.set_facecolors)]:
    colors=getter()
    if len(colors):setter([to_rgba(bright(c)) for c in colors])
  for patch in ax.patches:
   if n==12:patch.set_facecolor(['#23334F','#223845','#323448'][min(ax.patches.index(patch),2)])
   elif n==19 and isinstance(patch,Rectangle):patch.set_facecolor(PANEL)
   elif n==23:patch.set_facecolor(PANEL)
   if n!=15:patch.set_edgecolor(bright(patch.get_edgecolor()))
  leg=ax.get_legend()
  if leg:
   leg.set_frame_on(True);leg.get_frame().set_facecolor(PANEL);leg.get_frame().set_edgecolor('#72829F');leg.get_frame().set_alpha(.96)
 for t in fig.findobj(Text):
  # Matrix annotations retain dark text on the unchanged light color blocks.
  if n==15 and t.axes and t in t.axes.texts:continue
  if n==19 and t.get_text() in ['46','13','100','209']:
   t.set_color(WHITE);t.set_path_effects([pe.withStroke(linewidth=2,foreground=BG)]);continue
  t.set_color(WHITE)
 kwargs['facecolor']=BG
 original_save(fig,filename,*args,**kwargs)

from contextlib import contextmanager
@contextmanager
def dark_theme(numbers):
 global allowed
 allowed=set(numbers)
 Figure.savefig=themed_save
 try:
  yield
 finally:
  Figure.savefig=original_save
